import google.generativeai as genai
import PIL.Image
import sys, os
import argparse
from dotenv import load_dotenv
from pathlib import Path
import mimetypes

import img_module as img


def initGemini():
  genai.configure(api_key=os.getenv('GEMINI_API'))
  model_type = os.getenv("USE_GEMINI_MODEL", 'gemini-1.5-flash')
  model = genai.GenerativeModel(model_type)
  return model

def dropUploadFile():
  initGemini()
  for file in genai.list_files():
    print(f"{file.display_name}, URI: {file.uri}')")
    genai.delete_file(file.name)
    print(f'Deleted file {file.uri}')

def createPrompt(q):
  return q + "日本語で回答して"

def calcToken(model, request):
  token_res = model.count_tokens(request)
  return str(token_res.total_tokens)
