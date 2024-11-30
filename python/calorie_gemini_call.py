import google.generativeai as genai
import PIL.Image
import sys, os
import argparse
from dotenv import load_dotenv
from pathlib import Path
import mimetypes
import json

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
  parser.add_argument('mode', type=str, choices=['txt', 'img', 'read', 'parse', 'drop', '?'], help='実行するモードを選択')
  parser.add_argument('question', type=str, nargs='?', help='あなたの質問内容')
  parser.add_argument('files', type=str, nargs='*', help='List of files to process')

  # 引数を解析
  args = parser.parse_args()
  if args.mode == 'read' and args.question is not None:
    if not args.files:
      parser.error('ファイル選択は必須')
    fileCall(args.question, args.files)
  if args.mode == 'parse':
    if not args.files:
      parser.error('ファイル選択は必須')
    imgConvertJsonPrompt(args.files)
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

  prompt = 'format.jsonの形式に従って、画像からデータを抽出してください。結果にはjsonのみを含めてください。'
  print("トークン：" + gemini.calcToken(model, [prompt, *arr]))
  response = model.generate_content([prompt, *arr])
  json_data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
  with open('./file/result/export.json', 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=4)

  gemini.dropUploadFile()

if __name__ == "__main__":
  main()