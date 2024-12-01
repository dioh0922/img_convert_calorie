import google.generativeai as genai
import PIL.Image
import sys, os
import argparse
from dotenv import load_dotenv
from pathlib import Path
import mimetypes
import json
from datetime import datetime
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib')))

import img_module as img
import gemini_module as gemini

model = None
api_key = ''

def main():
  script_dir = Path(__file__).parent
  env_file = script_dir.parent / 'env' / '.env'
  load_dotenv(dotenv_path=env_file)

  parser = argparse.ArgumentParser(description="モード")
  parser.add_argument('mode', type=str, choices=['txt', 'img', 'read', 'parse', 'drop', 'dump', '?'], help='実行するモードを選択')
  parser.add_argument('question', type=str, nargs='?', help='あなたの質問内容')
  parser.add_argument('files', type=str, nargs='*', help='List of files to process')

  # 引数を解析
  args = parser.parse_args()

  # 必須のチェック
  if args.mode in ['txt', 'img', 'read']:
    if not args.question:
      parser.error('質問内容（question）が必要です。')

  elif args.mode in ['parse', 'img', 'read']:
    if not args.files:
      parser.error('処理するファイル（files）が必要です。')


  if args.mode == 'read':
    fileCall(args.question, args.files)
  elif args.mode == 'parse':
    imgConvertJsonPrompt(args.files)
  elif args.mode == 'dump':
    imgConvertJsonDump()
  elif args.mode == 'drop':
    dropUploadFile()
  else:
    print('invalid')

def fileCall(q, files):
  model = gemini.initGemini()
  print(q)
  arr = []
  for path in files:
    if os.path.exists(path):
      target_file = img.loadRequestFile(path)
      arr.append(target_file)
    else:
      continue

  prompt = q
  print("トークン：" + gemini.calcToken(model, [q, *arr]))
  response = model.generate_content([prompt, *arr])
  print(response.text)
  gemini.dropUploadFile()

def imgConvertJsonPrompt(files):
  model = gemini.initGemini()
  arr = []
  with open('./file/template/format.json', 'r') as file:
    content = file.read()
    arr.append(content)
  
  for path in files:
    if os.path.exists(path):
      target_file = img.loadRequestFile(path)
      arr.append(target_file)
    else:
      continue

  print(arr)

  prompt = 'format.jsonの形式に従って、画像からデータを抽出してください。結果にはjsonのみを含めてください。'
  print("トークン：" + gemini.calcToken(model, [prompt, *arr]))
  response = model.generate_content([prompt, *arr])

  json_pattern = r'```json\n(.*?)\n```'
  match = re.search(json_pattern, response.text, re.DOTALL)

  #print(response.text)
  if match:
    json_data = match.group(1)
    print(json_data)
      #print(response.text)
    img.exportJson(json_data)
    gemini.dropUploadFile()
  else: print("JSON部分が見つかりませんでした。")


def imgConvertJsonDump():
  arr = img.getImageFiles('./img')
  imgConvertJsonPrompt(arr)


if __name__ == "__main__":
  main()