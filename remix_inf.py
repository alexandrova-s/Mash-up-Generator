import os

''' Infinite remixer tool '''

def segment_songs(songs_path, beat_path):
    os.system('segment {} {}'.format(songs_path, beat_path))
    print('SUCCEED SEPARATE')

def create_dataset(beat_path, data_path):
    os.system('create_dataset {} {}'.format(beat_path, data_path))

def fit_nn(data_path):
    dataset_path = os.path.join(data_path, 'dataset.pkl')
    fitted_path = os.path.join(data_path, 'nearestneighbour.pkl')
    os.system('fit_nearest_neighbours {} {}'.format(dataset_path, fitted_path))

def generate_remix(jump_rate, number_of_beats, save_path, mashup_name):
    mixed_path = os.path.join(save_path, f'{mashup_name}.wav')
    os.system('generate_remix {} {} {}'.format(jump_rate, number_of_beats, mixed_path))