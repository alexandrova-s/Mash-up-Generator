from pydub import silence as sn

''' script for splitting vocals based on silent moments 
    and creating fragment to join in this way '''

class Fragment:

    def __init__(self, start, stop, duration):
        self.start = start
        self.stop = stop
        self.duration = duration

    def __str__(self):
        return f"start= {self.start}, stop={self.stop}, duration ={self.duration}"

class Fragments:

    def __init__(self):
        self.fragments = []

    def __len__(self):
        return len(self.fragments)

    def append_fragment(self, start, stop, duration):
        self.fragments.append(Fragment(start, stop, duration))


def silences_detection(sound):
    dBFS = sound.dBFS
    print(dBFS)
    silence = sn.detect_silence(sound, min_silence_len=500, silence_thresh=dBFS-16)

    silence = [(start, stop) for start, stop in silence] #in sec

    return silence


def vocal_detection(sound, time_threshold = 5000):
    dBFS = sound.dBFS
    silence = sn.detect_silence(sound, min_silence_len=500, silence_thresh=dBFS-16)

    silence = [(start, stop) for start, stop in silence]
    voice = Fragments()
    for index, x in enumerate(silence):
        try:
            if abs(silence[index+1][0]-x[1]) > time_threshold:
                try:
                    voice.append_fragment(x[1], silence[index+1][0], silence[index+1][0]-x[1])
                except:
                    voice.append_fragment(x[1], silence[-1][1], silence[-1][1] - x[1])

        except IndexError as e:
            return voice
    print('vocal detection complited', type(voice))
    return voice
