import google.generativeai as genai
import PIL.Image
import sys, os
import argparse
from dotenv import load_dotenv
from pathlib import Path
import mimetypes


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
  parser.add_argument('mode', type=str, choices=['txt', 'img', 'read', 'drop', '?'], help='実行するモードを選択')
  parser.add_argument('question', type=str, nargs='?', help='あなたの質問内容')
  parser.add_argument('files', type=str, nargs='*', help='List of files to process')

  # 引数を解析
  args = parser.parse_args()
  if args.mode == 'read' and args.question is not None:
    if args.mode == 'read' and not args.files:
      parser.error('ファイル選択は必須')
    fileCall(args.question, args.files)
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

if __name__ == "__main__":
  main()