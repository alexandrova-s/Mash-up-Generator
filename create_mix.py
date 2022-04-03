from create_fragments import create_fragments

''' function for interleaving every other fragments of two songs '''
def create_mix(sound1, sound2, fragmented_by=6):
    fragments_song1 = create_fragments(sound1, duration=60000, fragmented_by=fragmented_by)
    fragments_song2 = create_fragments(sound2, duration=60000, fragmented_by=fragmented_by)
    new_song = fragments_song1[0]
    for index, (fragment_song1, fragment_song2) in enumerate(zip(fragments_song1, fragments_song2), start=0):
        if index%2 == 1:
            new_song += fragment_song2
        else:
            new_song += fragment_song1
    return new_song