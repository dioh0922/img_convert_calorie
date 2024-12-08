from flask import Flask, render_template, request, url_for, redirect, jsonify
from calorie_gemini_call import main
import magic
import os

app = Flask(__name__)
mime = magic.Magic(mime=True)


@app.errorhandler(405)
def method_not_allowed(error):
    # 405エラー時に '/' にリダイレクト
    return redirect(url_for('index'))

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/request', methods=['POST'])
def api():
  mode = request.form['mode']
  prompt = request.form['prompt']
  file = request.files['file']

  file_path = ''
  if mode != 'dump':
    mime_type = mime.from_buffer(file.read())  # file.read() でファイルの内容を取得
    file.seek(0)
    allowed_mime_types = {
      'image/jpeg': '.jpg',
      'image/png': '.png',
      'image/bmp': '.bmp',
    }
    if mime_type not in allowed_mime_types:
      return jsonify({'error': 'Invalid file type'}), 400
    
    filename = file.filename
    file_path = os.path.join('tmp', filename)
    file.save(file_path)

  result = main(mode, prompt, [file_path])
  if os.path.exists(file_path):
    os.remove(file_path)

  return render_template('api_result.html', data=result)

if __name__ == "__main__":
  app.run(debug=True)