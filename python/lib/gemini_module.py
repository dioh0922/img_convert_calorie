from google import genai
#import google.generativeai as genai
import PIL.Image
import sys, os
import argparse
from pathlib import Path
import mimetypes
import re

import img_module as img

model_type = os.getenv("USE_GEMINI_MODEL", 'gemini-2.0-flash')

def initGemini():
  return genai.Client(api_key=os.getenv('GEMINI_API'))

def fileCall(q, files):
  client = initGemini()
  print(q)
  arr = []
  for path in files:
    if os.path.exists(path):
      target_file = img.loadRequestFile(path)
      arr.append(target_file)
    else:
      continue

  prompt = createPrompt(q)
  request = [q, *arr]
  print("トークン：" + calcToken(request))
  response = client.models.generate_content(
    model=model_type,
    contents=request
  )
  print(response.text)
  dropUploadFile()
  return response.text

def imgConvertJsonPrompt(files):
  client = initGemini()
  arr = []
  base_dir = Path(__file__).parent
  file_path = base_dir.parent / 'file' / 'template' / 'format.json'
  with open(file_path, 'r') as file:
    content = file.read()
    arr.append(content)
  
  for path in files:
    if os.path.exists(path):
      target_file = img.loadRequestFile(path)
      arr.append(target_file)
    else:
      continue

  print(arr)

  prompt = 'format.jsonの形式に従って、それぞれの画像からデータを抽出してください。結果にはjsonのみを含めてください。複数ある場合は配列にしてすべて返してください。'
  print("トークン：" + calcToken([prompt, *arr]))
  response = client.models.generate_content(
    model=model_type,
    contents=[prompt, *arr]
  )

  # TODO: 複数ダンプの調整

  json_pattern = r'```json\n(.*?)\n```'
  match = re.search(json_pattern, response.text, re.DOTALL)

  print(response.text)
  if match:
    json_data = match.group(1)
    print(json_data)
    img.exportJson(json_data)
    dropUploadFile()
    return json_data
  else: 
    print("JSON部分が見つかりませんでした。")
    return None

def imgConvertJsonDump():
  arr = img.getImageFiles('./img')
  result = imgConvertJsonPrompt(arr)
  return result

def dropUploadFile():
  client = initGemini()
  for file in client.files.list():
    print(f"{file.display_name}, URI: {file.uri}')")
    client.files.delete(name=file.name)
    print(f'Deleted file {file.uri}')

def createPrompt(q):
  return "日本語で回答して\n" + q

def calcToken(request):
  client = initGemini()
  response = client.models.count_tokens(model=model_type, contents=request)
  return str(response.total_tokens)
