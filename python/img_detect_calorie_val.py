from paddleocr import PaddleOCR

import sys
import numpy as np
from pathlib import Path
import csv

pfc_label = ["たんぱく質", "脂質", "糖質"]
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

        # 距離を計算
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
        if any(target in text for target in pfc_label)
    ]

    pfc_value = []
    for detect in filter_paddle:
        near = findNearestText(detect, tmp)
        pfc_value.append((detect[0], parseValue(near[0])))

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

    exportCsv(result_list)

def exportCsv(rows):
    with open('./csv/export.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # ヘッダー行を書き込む
        writer.writerow(pfc_label)
        
        # 各行のデータを書き込む
        for row in rows:
            # rowは [('たんぱく質', '28.2'), ('脂質', '23.0'), ...] の形式
            row_data = [value for _, value in row]
            writer.writerow(row_data)

    print("CSVファイルに書き込みました。")


print("*************** Paddle **************")
detectAllImg()
#detectByPaddle(img_path)
