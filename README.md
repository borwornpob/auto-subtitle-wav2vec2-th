# auto-subtitle-wav2vec2-th
This is auto subtitle script made using python and wav2vec2.0 pretrained by airesearch (wav2vec2-large-xlsr-53-th)

# Installation
```python
python3 -m venv venv
. venv/bin/activate
pip install pydub ffmpeg webrtcvad torch transformers srt
```

# How to use
Please activate venv before using this script
```python
python speech_to_text.py <aggresiveness> <path_to_wav_file> <directory_to_place_subtitle_file> <subtitle_file_name>
```