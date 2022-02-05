from crypt import methods
from fileinput import filename
import os
from flask import Flask, request, jsonify, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename


import speech_to_text

UPLOAD_FOLDER = './Upload'
ALLOWED_EXTENSIONS = {'wav'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#TODO: support more extensions
def allowed_file(filename):
    # some.wav
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


#Main route
@app.route('/', methods = ['GET','POST'])
def predict():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            os.system('rm -r Chunk/')
            os.system('rm result/*')
            os.system('rm Upload/*')
            filename = secure_filename(file.filename)
            path_to_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path_to_file)
            os.system('rm -rf Chunk/')
            name_without_extension = filename.rsplit('.',1)[0]
            name_srt = name_without_extension + '.srt'
            speech_to_text.main(3, path_to_file, 'result/', name_without_extension)
            return redirect(url_for('download_file', name=name_srt))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
    </form>
    '''

@app.route('/download/<name>')
def download_file(name):
    try:
        return send_from_directory('./result/', name)
    except:
        flash({'error': 'error while downloading file'})

app.add_url_rule(
    "/download/<name>", endpoint="download_file", build_only=True
)

