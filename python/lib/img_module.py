import google.generativeai as genai
import mimetypes
import json
import PIL.Image

def loadRequestFile(path):
  mime_type, _ = mimetypes.guess_type(path)
  print(mime_type)
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

