from pydub import AudioSegment
from pydub import silence as sn
import os
import librosa, pydub
import numpy as np
import pickle
import pyrubberband as pyrb
import soundfile as sf
import matplotlib.pyplot as plt

''' script for songs tempo adjustment  '''


''' helping function for data type change and connection between pydub and librosa '''
def audiosegment_to_librosawav(audiosegment):
    channel_sounds = audiosegment.split_to_mono()
    samples = [s.get_array_of_samples() for s in channel_sounds]

    fp_arr = np.array(samples).T.astype(np.float32)
    fp_arr /= np.iinfo(samples[0].typecode).max
    fp_arr = fp_arr.reshape(-1)

    return fp_arr


''' Time adjustment algorithm '''
def time_stretcher(sound1, sound2, sr=22050):
    tempo1, beats1 = librosa.beat.beat_track(y=sound1, sr=sr)
    tempo2, beats2 = librosa.beat.beat_track(y=sound2, sr=sr)
    yield

    Coefs = [-2, -1.5, -1.2, -1, -0.7, -0.5, -0.2, 0, 0.2, 0.5, 0.7, 1, 1.2, 1.5, 2]

    tempo_coefs = [(2 ** c) * tempo1 for c in Coefs]
    opt_coefs_index = np.argmin(np.absolute(tempo_coefs - tempo2))
    tempo_opt = tempo_coefs[opt_coefs_index]
    yield

    tempo_low = min(tempo_opt, tempo2)
    tempo_high = max(tempo_opt, tempo2)

    a, b = 0.765, 1
    target = (a - b) * tempo_low + np.sqrt(((a - b) ** 2) * (tempo_low ** 2) + 4 * a * b * tempo_high * tempo_low)
    target = target / (2 * a)

    print("First song ratio=", target / tempo_opt)
    print("Second song ratio=", target / tempo2)
    print("Middle=", target)
    yield

    sound_stretch1 = pyrb.time_stretch(sound1, sr, target / tempo_opt)
    sound_stretch2 = pyrb.time_stretch(sound2, sr, target / tempo2)
    yield

    tempo_s1, beats_1 = librosa.beat.beat_track(y=sound_stretch1, sr=sr)
    tempo_s2, beats_2 = librosa.beat.beat_track(y=sound_stretch2, sr=sr)
    yield

    print('TEMPO after change:')
    print(tempo_s1)
    print(tempo_s2)

    yield sound_stretch1, sound_stretch2
