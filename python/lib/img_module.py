import google.generativeai as genai
import mimetypes
import json
import PIL.Image
import os
from datetime import datetime
from pathlib import Path

def loadRequestFile(path):
  mime_type, _ = mimetypes.guess_type(path)
  if mime_type and mime_type.startswith('image'):
    return PIL.Image.open(path)
  elif mime_type and mime_type.startswith('audio'):
    return preLoadFile(path)
  else:
    return loadFile(path)


def preLoadFile(path):
  return genai.upload_file(path)

def loadJson(path):
  with open(path, 'r', encoding='utf-8') as file:
    return file.read()

def loadFile(path):
  with open(path, 'r', encoding='utf-8') as file:
    return file.read()

def exportJson(text):
  base_dir = Path(__file__).parent
  file_name = 'export' + datetime.now().strftime("%Y%m%d") + '.json'
  file_path = base_dir.parent / 'file' / 'result' / file_name

  json_data = json.loads(text.replace('```json', '').replace('```', '').strip())
  with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=4)

def getImageFiles(directory):
  image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
  image_files = []

  for file_name in os.listdir(directory):
    file_path = os.path.join(directory, file_name)
    if os.path.isfile(file_path) and any(file_name.lower().endswith(ext) for ext in image_extensions):
      image_files.append(file_path)

  return image_files