import os
import librosa
import matplotlib.pyplot as plt
import numpy as np
import librosa.display

''' script using AI Spleeter tool to split songs into stems '''

def split_voc_acc(path, out_folder):
    cline = r'spleeter separate {} -o ./{}/ &'.format(path, out_folder)
    os.system(cline)

def split_stems(path, out_folder, stems_number):
    valid = {2, 4, 5}
    if stems_number not in valid:
        raise ValueError("results: number of stems to split must be in %r." % valid)
    cline = r'spleeter separate -o output {} -o ./{}/ -p spleeter:{}stems &'.format(path, out_folder, stems_number)
    os.system(cline)

''' functions for spectrogram generation '''
def generate_spectrum(signal, sr=22050):

    S_full, phase = librosa.magphase(librosa.stft(signal))

    idx = slice(*librosa.time_to_frames([30, 35], sr=sr))
    plt.figure(figsize=(12, 4))
    librosa.display.specshow(librosa.amplitude_to_db(S_full[:, idx], ref=np.max),
                             y_axis='log', x_axis='time', sr=sr)
    plt.colorbar()
    plt.tight_layout()
    plt.show()
    return S_full

