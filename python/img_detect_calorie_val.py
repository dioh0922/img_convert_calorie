from paddleocr import PaddleOCR

import sys
import numpy as np
from pathlib import Path
import csv
import pandas as pd
import argparse
from PIL import Image, ImageDraw
import re
import json


total_label = "カロリ"
today_label = "日付"
csv_label = [total_label]
pfc_label = ["たんぱく質", "脂質", "糖質"]

csv_label.extend(pfc_label)

#resultCsv = './ext/export.csv'
resultJson = './ext/export.json'

image_extensions = ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp')
img_dir = './img/'
paddleOcr = None

def main():
    parser = argparse.ArgumentParser(description="モード")
    
    parser.add_argument(
        'mode', 
        type=str, 
        choices=['sample', 'all', '?'], 
        help='実行するモードを選択', 
        nargs='?',
        default='all'
    )

    args = parser.parse_args()
    if args.mode == 'sample':
      print("*************** sample **************")
      detectTargetImg("./sample.png")
    else:
      print("*************** Paddle **************")
      detectAllImg()


def findNearestText(target, arr):
  min_distance = float('inf')
  
  result = []
  for word_info in arr:
    text = word_info[0]
    box = word_info[1]
    coords = np.array(box[0])  # 左上の座標を取得

    # 自分自身は無視
    if text == target[0]:
      continue

    # 距離を計算(右下にある中で一番近いもの)
    if target[1][0][1] <= coords[1] and target[1][0][0] <= coords[0] and len(text) > 1:
      distance = np.linalg.norm(target[1][0] - coords)
      if distance < min_distance:
        min_distance = distance
        closest_string = text
        result = (text, box)
  return result

def findDateArea(target, arr):
  min_distance = float('inf')
  result = None
  for word_info in arr:
    text = word_info[0]
    box = word_info[1]
    coords = np.array(box[0])  # 左上の座標を取得

    # 自分自身は無視
    if text == target[0]:
      continue

    # 距離を計算(左にある中で一番近いもの)
    if target[0][0][0] >= coords[0] and re.search(r'\d{1,2}/\d{1,2}', text):
      distance = np.linalg.norm(target[0][0] - coords)
      if distance < min_distance:
        min_distance = distance
        result = re.search(r'\d{1,2}/\d{1,2}', text).group()
  return result

def parseValue(value):
  return value.split('/')[0] 

def detectByPaddle(img_path, ocr, draw_flg=None):
  paddleResult = ocr.ocr(img_path, cls=True)
  tmp = []
  if draw_flg:
    image = Image.open(img_path)
    draw = ImageDraw.Draw(image)
  
  for result in paddleResult:
    for line in result:
      tmp.append((line[1][0], line[0]))

  week = findWeekPosition(paddleResult)
  date = findDateArea(week, tmp)

  filter_paddle = [
    (text, coords) 
    for text, coords in tmp 
    if any(target in text for target in csv_label)
  ]

  pfc_value = []
  pfc_value.append((today_label, date))
  for detect in filter_paddle:
    near = findNearestText(detect, tmp)
    if detect[0] in pfc_label:
      result = parseValue(near[0])
    else:
      result = near[0]

    if draw_flg : draw.rectangle([tuple(map(int, near[1][0])), tuple(map(int, near[1][2]))], outline='green', width=2)
    pfc_value.append((detect[0], result))

  if draw_flg : image.save("./detect_img/" + img_path)

  print(pfc_value)
  return pfc_value

def detectTargetImg(target_path):
    paddleOcr = PaddleOCR(use_angle_cls=True, lang='japan')
    target_result = detectByPaddle(target_path, paddleOcr, True)
    print(target_result)
    exportCsv(target_result)

def detectAllImg():
  dir_content = Path(img_dir)
  file_list = []
  for extension in image_extensions:
    file_list.extend(dir_content.glob(extension))

  paddleOcr = PaddleOCR(use_angle_cls=True, lang='japan')

  result_list = []
  for x in file_list:
    result_list.append(detectByPaddle(img_dir + x.name, paddleOcr))

  exportCsv(result_list)

def exportCsv(rows):
  with open(resultJson, 'w', encoding='utf-8') as json_file:

    json_content = []
    for row in rows:
      for i, (key, value) in enumerate(row):
        if key == total_label:
          match = re.match(r'(\d+)(?:/(\d+))(?:[a-zA-Z]*)?', value)
          if match:
              # XX/ZZ形式の場合
              if match.group(2):  # もしZZが存在する場合
                  p1, p2 = match.group(1), match.group(2)
              else:  # 1つの数字の場合
                  p1, p2 = match.group(1), None
              row[i] = ('摂取', p1)
              row.append(('最大cal', p2))
          elif re.match(r'^[-+]?\d+(\.\d+)?$', value):
              # 数値の場合そのまま格納
              row[i] = ('摂取', value)
              row.append(('最大cal', value))
          else:
            continue
      json_content.append(dict(row))
    
    json.dump(json_content, json_file, ensure_ascii=False, indent=4)
  


  #with open(resultCsv, mode='w', newline='', encoding='utf-8') as file:
  #  writer = csv.writer(file)
    
  #parseTotalCalorie()
  print("CSVファイルに書き込みました。")

def parseTotalCalorie():
  df = pd.read_csv(resultCsv)
  
  
  if re.search(r'^-?\d+(\.\d+)?$', df[total_label].astype(str)):
    df[['摂取', '最大cal']] = df[total_label]
  elif re.search(r'(\d+)/(\d+)', df[total_label]):
    print(df[total_label].str.extract(r'(\d+)/(\d+)'))
    df[['摂取', '最大cal']] = df[total_label].str.extract(r'(\d+)/(\d+)')
  df = df.drop(columns=[total_label])
  df.to_csv(resultCsv, index=False)

def findWeekPosition(arr):
  for item in arr:
    for line in item:
      if re.search(r'(月|火|水|木|金|土|日)', line[1][0]) and line[0][2][1] > 100:
        return line

if __name__ == "__main__":
    main()