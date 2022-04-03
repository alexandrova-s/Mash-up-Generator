import librosa
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
import madmom
import librosa.display

''' script for beat tracking and beats adjustment '''

''' dynamic beat tracking using librosa package '''
def beat_track_dynamic(sound, sr):
    tempo, beat_times = librosa.beat.beat_track(sound, sr=sr, start_bpm=60, units='time')
    clicks = librosa.clicks(beat_times, sr=sr, length=len(sound))

    return sound+clicks, clicks

''' Plotting beats course overlaid on envelope '''
def plot_beats(sound, clicks, sr):
    plt.figure(figsize=(14, 5))
    librosa.display.waveshow(sound, sr=sr, alpha=0.5, label='Signal')
    librosa.display.waveshow(clicks, sr=sr, color='r', alpha=0.5, label='Beats')
    plt.show()

''' function finding first beat in song '''
def find_beats_start(clicks):
    clicks_indicies = scipy.signal.find_peaks(clicks)
    return clicks_indicies[0]

''' function adjusting songs, so their beats overly in time '''
def overlay_beat_songs(song1, song2, ind1, ind2, sr=22050):
    if ind1 > ind2:
        diff = ind1 - ind2
        adjusted_song2 = np.concatenate([np.array([0]*diff), song2])
        return song1, adjusted_song2
    else:
        diff = ind2 - ind1
        adjusted_song1 = np.concatenate([np.array([0]*diff), song1])
        return adjusted_song1, song2

''' beat tracking function using madmom package - DBN and RNN networks, machine learning techniques '''
def rnn_beattrack(sound, song_wav, sr):
    proc = madmom.features.beats.DBNBeatTrackingProcessor(fps=100)
    act = madmom.features.beats.RNNBeatProcessor()(song_wav)

    beat_times = proc(act)

    clicks = librosa.clicks(beat_times, sr=sr, length=len(sound))
    return sound, clicks
