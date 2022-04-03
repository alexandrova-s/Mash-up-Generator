import librosa.display
import librosa

''' script extracting song chromagram '''
def extract_chromogram(path):
    signal, sample_rate = librosa.load(path)
    chromogram = librosa.feature.chroma_stft(signal,
                                             # n_fft=frame_size,
                                             # hop_length=hop_length,
                                             sr=sample_rate)
    return chromogram
