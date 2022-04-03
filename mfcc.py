import librosa
import librosa.display
import sklearn

''' script extracting song MFCCs '''
def extract_mfcc(path):
    signal, sample_rate = librosa.load(path)
    mfcc = librosa.feature.mfcc(signal,
                                # n_mfcc=num_coefficients,
                                # n_fft=frame_size,
                                # hop_length=hop_length,
                                sr=sample_rate)

    mfcc = sklearn.preprocessing.scale(mfcc, axis=1)
    return mfcc
