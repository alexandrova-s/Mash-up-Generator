from pydub import silence as sn

''' Volume adjustment '''
def adjust_volume(sound1, sound2):
    dBFS1 = sound1.dBFS
    dBFS2 = sound2.dBFS

    if dBFS1 > dBFS2:
        sound2 = sound2 + (dBFS1 - dBFS2)
    else:
        sound1 = sound1 + (dBFS2 - dBFS1)

    return sound1, sound2
