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

def main(mode, question, files):
  script_dir = Path(__file__).parent
  env_file = script_dir.parent / 'env' / '.env'
  load_dotenv(dotenv_path=env_file)


  if mode == 'read':
    return 'deprecated'
    #return gemini.fileCall(question, files)
  elif mode == 'parse':
    return gemini.imgConvertJsonPrompt(files)
  elif mode == 'dump':
    return gemini.imgConvertJsonDump()
  elif mode == 'drop':
    return gemini.dropUploadFile()
  elif mode == 'ask':
    return gemini.fileCall(question, files)
  else:
    print('invalid')
    return 'invalid'


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="モード")
  parser.add_argument('mode', type=str, choices=['img', 'read', 'parse', 'drop', 'dump', '?'], help='実行するモードを選択')
  parser.add_argument('question', type=str, nargs='?', help='あなたの質問内容')
  parser.add_argument('files', type=str, nargs='*', help='List of files to process')

  # 引数を解析
  args = parser.parse_args()

    # 必須のチェック
  if args.mode in ['img', 'read', 'ask']:
    if not args.question:
      parser.error('質問内容（question）が必要です。')

  elif args.mode in ['parse', 'img', 'read', 'ask']:
    if not args.files:
      parser.error('処理するファイル（files）が必要です。')

  main(args.mode, args.question, args.files)