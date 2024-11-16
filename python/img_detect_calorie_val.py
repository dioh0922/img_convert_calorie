from paddleocr import PaddleOCR

import sys
import numpy as np
from pathlib import Path
import csv
import pandas as pd

total_label = "カロリ"
today_label = "今日"
csv_label = [today_label, total_label]
pfc_label = ["たんぱく質", "脂質", "糖質"]

csv_label.extend(pfc_label)

resultCsv = './csv/export.csv'
image_extensions = ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp')
img_dir = './img/'
paddleOcr = None

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
    if target[1][0][1] <= coords[1] and target[1][0][0] <= coords[0]:
      distance = np.linalg.norm(target[1][0] - coords)
      if distance < min_distance:
        min_distance = distance
        closest_string = text
        result = (text, box)
  return result

def parseValue(value):
  return value.split('/')[0] 

def detectByPaddle(img_path, ocr):
  paddleResult = ocr.ocr(img_path, cls=True)
  tmp = []
  for result in paddleResult:
    for line in result:
      tmp.append((line[1][0], line[0]))

  filter_paddle = [
    (text, coords) 
    for text, coords in tmp 
    if any(target in text for target in csv_label)
  ]
  pfc_value = []
  for detect in filter_paddle:
    near = findNearestText(detect, tmp)
    if detect[0] in pfc_label:
      result = parseValue(near[0])
    else:
      result = near[0]

    pfc_value.append((detect[0], result))

  print(pfc_value)
  return pfc_value

def detectAllImg():
  dir_content = Path(img_dir)
  file_list = []
  for extension in image_extensions:
    file_list.extend(dir_content.glob(extension))

  paddleOcr = PaddleOCR(use_angle_cls=True, lang='japan')

  result_list = []
  for x in file_list:
    result_list.append(detectByPaddle(img_dir + x.name, paddleOcr))

  #print(result_list)
  exportCsv(result_list)

def exportCsv(rows):
  print(rows)
  with open(resultCsv, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # ヘッダー行を書き込む
    writer.writerow(csv_label)
    
    # 各行のデータを書き込む
    for row in rows:
      # rowは [('たんぱく質', '28.2'), ('脂質', '23.0'), ...] の形式
      row_data = [value for _, value in row]
      writer.writerow(row_data)

  parseTOtalCalorie()
  print("CSVファイルに書き込みました。")

def parseTOtalCalorie():
  df = pd.read_csv(resultCsv)
  df[['摂取', '最大cal']] = df[total_label].str.extract(r'(\d+)/(\d+)kca')
  df = df.drop(columns=[total_label])
  df.to_csv(resultCsv, index=False)

print("*************** Paddle **************")
detectAllImg()
