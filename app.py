from crypt import methods
from fileinput import filename
from multiprocessing import connection
import os
from flask import Flask, request, jsonify, flash, redirect, send_file, url_for, send_from_directory
from werkzeug.utils import secure_filename

from rq import Queue
from rq.job import Job
from worker import conn

from flask_cors import CORS, cross_origin

from speech_to_text import main

UPLOAD_FOLDER = './Upload'
ALLOWED_EXTENSIONS = {'wav'}

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

q = Queue(connection=conn)

#TODO: support more extensions
def allowed_file(filename):
    # some.wav
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


#Main route
@app.route('/predict', methods = ['POST'])
@cross_origin()
def predict():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path_to_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path_to_file)
        name_without_extension = filename.rsplit('.',1)[0]
        job = q.enqueue(main, 3, path_to_file, name_without_extension,)
        print(job.get_id())
        return {"message": job.get_id()}, 201

@app.route('/download/<job_key>', methods=['GET'])
@cross_origin()
def download_file(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        return send_file(job.result, as_attachment=True), 200
    else:
        return jsonify({'message':'Not finished yet or has an error Please wait till 5000 seconds'}), 202

