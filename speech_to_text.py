from pydub import AudioSegment
from pathlib import Path
import io
import os
import collections
import contextlib
import sys
import wave
import webrtcvad
import torch
from transformers import AutoProcessor, AutoModelForCTC
import srt
from datetime import timedelta

#import model
processor = AutoProcessor.from_pretrained("airesearch/wav2vec2-large-xlsr-53-th")

model = AutoModelForCTC.from_pretrained("airesearch/wav2vec2-large-xlsr-53-th")

#Segmentation audio wav using py-webrtcvad
timestamp_array = []

def read_wave(path):
    """Reads a .wav file.

    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    """Writes a .wav file.

    Takes path, PCM audio data, and sample rate.
    """
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    """Represents a "frame" of audio data."""
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.

    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.

    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    """Filters out non-voiced audio frames.

    Given a webrtcvad.Vad and a source of audio frames, yields only
    the voiced audio.

    Uses a padded, sliding window algorithm over the audio frames.
    When more than 90% of the frames in the window are voiced (as
    reported by the VAD), the collector triggers and begins yielding
    audio frames. Then the collector waits until 90% of the frames in
    the window are unvoiced to detrigger.

    The window is padded at the front and back to provide a small
    amount of silence or the beginnings/endings of speech around the
    voiced frames.

    Arguments:

    sample_rate - The audio sample rate, in Hz.
    frame_duration_ms - The frame duration in milliseconds.
    padding_duration_ms - The amount to pad the window, in milliseconds.
    vad - An instance of webrtcvad.Vad.
    frames - a source of audio frames (sequence or generator).

    Returns: A generator that yields PCM audio data.
    """
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    # We use a deque for our sliding window/ring buffer.
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
    # NOTTRIGGERED state.
    triggered = False

    voiced_frames = []
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)

        sys.stdout.write('1' if is_speech else '0')
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            # If we're NOTTRIGGERED and more than 90% of the frames in
            # the ring buffer are voiced frames, then enter the
            # TRIGGERED state.
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                sys.stdout.write('+(%s)' % (ring_buffer[0][0].timestamp,))
                timestamp_array.append(ring_buffer[0][0].timestamp)
                # We want to yield all the audio we see from now until
                # we are NOTTRIGGERED, but we have to start with the
                # audio that's already in the ring buffer.
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            # We're in the TRIGGERED state, so collect the audio data
            # and add it to the ring buffer.
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            # If more than 90% of the frames in the ring buffer are
            # unvoiced, then enter NOTTRIGGERED and yield whatever
            # audio we've collected.
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                timestamp_array.append(frame.timestamp + frame.duration)
                triggered = False
                yield b''.join([f.bytes for f in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []
    if triggered:
        sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
    sys.stdout.write('\n')
    # If we have any leftover voiced audio when we run out of input,
    # yield it.
    if voiced_frames:
        yield b''.join([f.bytes for f in voiced_frames])

timestamp_dict = {}

def main(aggressiveness,path_to_wav,directory_to_place_wav):
    audio, sample_rate = read_wave(path_to_wav)
    vad = webrtcvad.Vad(int(aggressiveness))
    path_directory = str(directory_to_place_wav)
    frames = frame_generator(30, audio, sample_rate)
    frames = list(frames)
    segments = vad_collector(sample_rate, 30, 300, vad, frames)
    os.system('mkdir ' + path_directory)
    for i, segment in enumerate(segments):
        path = 'chunk-%002d.wav' % (i,)
        print(' Writing %s' % (path,))
        write_wave(path_directory + path, segment, sample_rate)
    print(timestamp_array);
    print(len(timestamp_array))
    j=0
    for p in range(0,len(timestamp_array),2):
        timestamp_dict[j] = {"start": timestamp_array[p],"end": timestamp_array[p+1]}
        j = j+1
    print(timestamp_dict)

#Segmenting
main(3,'Test2.wav','Chunk/')

final_text = []
path_to_chunk = "./" + "Chunk/"
pathlist = Path(path_to_chunk).rglob('*.wav')
pathlist = sorted(pathlist)
for path in pathlist:
  path_in_str = str(path)
  clip = AudioSegment.from_wav(path_in_str)
  clip = clip.set_frame_rate(16000)
  x = torch.FloatTensor(clip.get_array_of_samples())
  inputs = processor(x, sampling_rate = 16000, return_tensors='pt', padding = True).input_values
  with torch.no_grad():
    logits = model(inputs).logits
  token = torch.argmax(logits, dim=-1)
  text = processor.batch_decode(token)
  print(text[0].replace(" ", ""))
  final_text.append(text[0].replace(" ",""))

srt_array = []


for i in range(len(final_text)):
    start = timedelta(seconds = timestamp_dict[i]['start'])
    end = timedelta(seconds = timestamp_dict[i]['end'])
    srt_array.append(srt.Subtitle(index = i+1, start = start, end = end, content = final_text[i]))

print(srt_array)

srt = srt.compose(srt_array)
print(srt)

f = open('test.srt',"w")
f.write(srt)
f.close()
