# auto-subtitle-wav2vec2-th
This is auto subtitle script made using python and wav2vec2.0 pretrained by airesearch (wav2vec2-large-xlsr-53-th)

# Installation
```python
python3 -m venv venv
. venv/bin/activate
pip install -r requirement.txt
```

# How to use
## For command line interface
Please activate venv before using this script
```python
python speech_to_text.py <aggresiveness> <path_to_wav_file> <subtitle_file_name>
```
## For running server
Please Install Redis before running the server
```python
#start Redis server for queueing task
redis-server
```
```python
#start worker to run task simultaneously
python worker.py
```
```python
#start flask server
export FLASK_APP=app.py
flask run
```
