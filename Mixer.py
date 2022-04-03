from pydub import AudioSegment
from scipy.io import wavfile
from parts_detections import vocal_detection
import librosa
import os, shutil, io
import pickle
import pyrubberband as pyrb
from adjust_tempo import time_stretcher
import song_decomposition as decomp
import beat_tracker as bt
import soundfile as sf
import remix_inf as ri
import shutil
import parts_of_song_extraction as pse
from read_blobs import download_blob
import connection_azure as conn_az


class Mixer:
    path = r".\songs"
    export_path = r'.\mixed_songs'
    temporary_path = r'.\temporary_files'

    ''' function preparing temporary directory for helping subproducts of mash-up generation '''
    def prepare_temp_directory(self):
        os.mkdir(self.temporary_path)
        # directories inside temp
        os.mkdir(os.path.join(self.temporary_path, 'downloaded_songs'))
        os.mkdir(os.path.join(self.temporary_path, 'beat_songs'))
        os.mkdir(os.path.join(self.temporary_path, 'speed_songs'))
        os.mkdir(os.path.join(self.temporary_path, 'decomposition4'))
        os.mkdir(os.path.join(self.temporary_path, 'segmented'))
        os.mkdir(os.path.join(self.temporary_path, 'mixed_songs'))

    ''' function reading songs using librosa package '''
    def read_songs_to_np(self, song1, song2):
        song1_path = os.path.join(self.path, song1)
        song2_path = os.path.join(self.path, song2)
        sound1, sr = librosa.load(song1_path)
        sound2, sr = librosa.load(song2_path)
        return sound1, sound2, sr

    ''' read songs lists to from azure data storage '''
    def read_songs_form_azure(self, song1, song2):
        song1_path = download_blob(song1, os.path.join(self.temporary_path, 'downloaded_songs'))
        song2_path = download_blob(song2, os.path.join(self.temporary_path, 'downloaded_songs'))
        yield
        sound1, sr = librosa.load(song1_path)
        sound2, sr = librosa.load(song2_path)
        yield sound1, sound2, sr

    ''' function for beat tracking and matching them in both songs
        returning two songs with beats matching in tim '''
    def beats_tracking(self, sound1, sound2, sr=22050):
        sound_with_beats1, beats1 = bt.rnn_beattrack(sound1, os.path.join(self.temporary_path, 'speed_songs', '1.wav'),
                                                     sr)
        yield
        sound_with_beats2, beats2 = bt.rnn_beattrack(sound2, os.path.join(self.temporary_path, 'speed_songs', '2.wav'),
                                                     sr)
        yield

        beat_start1 = bt.find_beats_start(beats1)[0]
        yield
        beat_start2 = bt.find_beats_start(beats2)[0]
        yield

        new_song1, new_song2 = bt.overlay_beat_songs(sound_with_beats1, sound_with_beats2, beat_start1, beat_start2)

        yield new_song1, new_song2

    ''' function completing accompaniment - takes others, bass and drums from spleeter decomposition
        and returns overlaid ready accompaniment '''
    def get_drum_bass(self, bass_from=1, drums_from=1):
        print('DOING ACCOMPANIMENT!!')
        accompaniment1_path = os.path.join(self.temporary_path, 'decomposition4', '1_to_2', 'other.wav')
        accompaniment2_path = os.path.join(self.temporary_path, 'decomposition4', '2_to_1', 'other.wav')
        yield
        if bass_from == 1:
            bass_path = os.path.join(self.temporary_path, 'decomposition4', '1_to_2', 'bass.wav')
        else:
            bass_path = os.path.join(self.temporary_path, 'decomposition4', '2_to_1', 'bass.wav')
        yield

        if drums_from == 1:
            drums_path = os.path.join(self.temporary_path, 'decomposition4', '1_to_2', 'drums.wav')
        else:
            drums_path = os.path.join(self.temporary_path, 'decomposition4', '2_to_1', 'drums.wav')
        yield

        accompaniment1 = AudioSegment.from_file(accompaniment1_path)
        accompaniment2 = AudioSegment.from_file(accompaniment2_path)
        yield
        bass = AudioSegment.from_file(bass_path)
        drums = AudioSegment.from_file(drums_path)
        drums = drums - 6
        yield

        combined = drums.overlay(bass)
        combined = combined.overlay(accompaniment2)

        yield combined

    ''' just optional function using infinite remixer tool for accompaniment generation '''
    def get_accompaniment2(self, songs_path, beats_path, data_path, remix_path):
        ri.segment_songs(songs_path, beats_path)
        ri.create_dataset(beats_path, data_path)
        ri.fit_nn(data_path)
        ri.generate_remix(0.01, 300, remix_path, 'accompaniment')

        self.delete_files_from_directory(songs_path)
        self.delete_files_from_directory(beats_path)
        self.delete_files_from_directory(data_path)

    ''' function generating vocal line - reads vocals stems from both songs,
        split them into parts with machine learning algorithm and join particular fragments.
        It returns ready vocal line '''
    def vocals_by_parts(self, sr=22050):
        vocal1_path = os.path.join(self.temporary_path, 'decomposition4', "1_to_2", 'vocals.wav')
        vocal2_path = os.path.join(self.temporary_path, 'decomposition4', '2_to_1', 'vocals.wav')
        yield

        vocal1, sr = librosa.load(vocal1_path)
        vocal2, sr = librosa.load(vocal2_path)
        yield

        voc_audio1 = AudioSegment.from_wav(vocal1_path)
        voc_audio2 = AudioSegment.from_wav(vocal2_path)
        yield

        def match_target_amplitude(sound, target_dBFS):
            change_in_dBFS = target_dBFS - sound.dBFS
            return sound.apply_gain(change_in_dBFS)

        vol_voc1 = voc_audio1.dBFS
        vol_voc2 = voc_audio2.dBFS
        yield

        mean_volume = (vol_voc1 + vol_voc2) / 2

        voc_audio1 = match_target_amplitude(voc_audio1, mean_volume)
        voc_audio2 = match_target_amplitude(voc_audio2, mean_volume)
        yield

        # Song parts segmentation vocal1
        # pse.plot_envelope(vocal1)
        signal_tempogram1 = pse.generate_tempogram(vocal1)
        yield
        changes_number1 = pse.number_of_changes_in_song(signal_tempogram1)
        yield
        signal_segments1, indexes1 = pse.split_segments('vocal1', vocal1, changes_number1, self.temporary_path,
                                                        save_segments=False)
        yield

        # # Song parts segmentation vocal2
        # # pse.plot_envelope(vocal2)
        # signal_tempogram2 = pse.generate_tempogram(vocal2)
        yield
        # changes_number2 = pse.number_of_changes_in_song(signal_tempogram2)
        yield
        # signal_segments2, indexes2 = pse.split_segments('vocal2', vocal2, changes_number2, self.temporary_path,
        #                                                 save_segments=False)
        yield

        indexes1_sec = []
        indexes2_sec = []

        for start, end in indexes1:
            start = start / sr * 1000
            end = end / sr * 1000
            indexes1_sec.append((start, end))
        yield

        # for start, end in indexes2:
        #     start = start / sr * 1000
        #     end = end / sr * 1000
        #     indexes2_sec.append((start, end))
        yield

        new_parts1 = indexes1_sec
        # new_parts2 = indexes2_sec

        parts1 = []

        for start, end in new_parts1[0::2]:
            if start == 0.0:
                s = voc_audio1[start:end].fade_in(1000).fade_out(300)
                parts1.append(s)
            else:
                s = voc_audio1[start - 3500:end + 1000].fade_in(1000).fade_out(300)
                parts1.append(s)
        yield

        parts2 = []

        for start, end in new_parts1[1::2]:
            s = voc_audio2[start - 3500:end + 1000].fade_in(1000).fade_out(300)
            parts2.append(s)

        yield

        def countList(lst1, lst2):
            return [sub[item] for item in range(len(lst2))
                    for sub in [lst1, lst2]]

        result = countList(parts1, parts2)
        yield

        vocals = sum(result)

        additional_vocs = []
        duration = new_parts1[10][0]
        s = AudioSegment.silent(duration)
        yield
        additional_vocs.append(s)
        yield
        s = AudioSegment.silent(duration)
        additional_vocs.append(s)
        x = voc_audio1[new_parts1[10][0] - 5000:new_parts1[10][1] + 1000].fade_in(2000).fade_out(1000)
        additional_vocs.append(x)
        yield

        additional_vocs = sum(additional_vocs)

        vocals = vocals.overlay(additional_vocs)

        yield vocals

    ''' optional function for vocal line splitting vocals based on silent moments '''
    def get_vocals(self):
        vocal1_path = os.path.join(self.temporary_path, 'decomposition2', "1_to_2", 'vocals.wav')
        vocal2_path = os.path.join(self.temporary_path, 'decomposition2', '2_to_1', 'vocals.wav')

        vocal_1 = AudioSegment.from_wav(vocal1_path)
        vocal_2 = AudioSegment.from_wav(vocal2_path)

        vocals1 = vocal_detection(vocal_1)
        vocals2 = vocal_detection(vocal_2)

        return vocals1, vocals2, vocal_1, vocal_2

    ''' just optional function using infinite remixer tool for vocal line generation '''
    def get_vocals2(self, songs_path, beats_path, data_path, remix_path):
        rate, voc1 = wavfile.read(os.path.join(songs_path, 'vocals1.wav'))
        os.remove(os.path.join(songs_path, 'vocals1.wav'))
        sf.write(os.path.join(songs_path, 'vocals1.wav'), voc1, rate, format='wav')

        rate, voc2 = wavfile.read(os.path.join(songs_path, 'vocals.wav'))
        os.remove(os.path.join(songs_path, 'vocals.wav'))
        sf.write(os.path.join(songs_path, 'vocals.wav'), voc2, rate, format='wav')

        ri.segment_songs(songs_path, beats_path)
        ri.create_dataset(beats_path, data_path)
        ri.fit_nn(data_path)
        ri.generate_remix(0.01, 400, remix_path, 'vocals')

        self.delete_files_from_directory(songs_path)
        self.delete_files_from_directory(beats_path)
        self.delete_files_from_directory(data_path)

    ''' the complete function combining all mash-up generation process,
        it is called in flask script;
        takes two songs as an input and returns ready completed mash-up '''
    def mix(self, song1, song2, mashup_name, bass_from=1, drums_from=2):
        progress = 0
        yield "data:" + str(progress) + "\n\n"
        if os.path.isdir('temporary_files') == False:
            self.prepare_temp_directory()

        with open(os.path.join(self.temporary_path, 'mashup_name.txt'), 'w') as f:
            f.write(mashup_name)
        reader_songs_from_azure = self.read_songs_form_azure(song1, song2)
        next(reader_songs_from_azure)
        progress = 5
        yield "data:" + str(progress) + "\n\n"

        sound1, sound2, sr = next(reader_songs_from_azure)
        progress = 10
        yield "data:" + str(progress) + "\n\n"

        generator_time_stretch = time_stretcher(sound1, sound2, sr)
        progress_logs = [12, 15, 17, 20, 22]
        for i in range(0, len(progress_logs)):
            next(generator_time_stretch)
            progress = progress_logs[i]
            yield "data:" + str(progress) + "\n\n"
        sound1, sound2 = next(generator_time_stretch)
        progress = 25
        yield "data:" + str(progress) + "\n\n"

        sf.write(os.path.join(self.temporary_path, 'speed_songs', '1.wav'), sound1, sr, format='wav')
        sf.write(os.path.join(self.temporary_path, 'speed_songs', '2.wav'), sound2, sr, format='wav')
        progress = 28
        yield "data:" + str(progress) + "\n\n"

        generator_beat_track = self.beats_tracking(sound1, sound2, sr)
        progress_logs = [30, 32, 35, 38]
        for i in range(0, len(progress_logs)):
            next(generator_beat_track)
            progress = progress_logs[i]
            yield "data:" + str(progress) + "\n\n"
        sound1, sound2 = next(generator_beat_track)
        progress = 39
        yield "data:" + str(progress) + "\n\n"

        sf.write(os.path.join(self.temporary_path, 'beat_songs', '1_to_2.wav'), sound1, sr, format='wav')
        sf.write(os.path.join(self.temporary_path, 'beat_songs', '2_to_1.wav'), sound2, sr, format='wav')
        progress = 40
        yield "data:" + str(progress) + "\n\n"

        # decompose first song
        decomp.split_stems(os.path.join(self.temporary_path, 'beat_songs', '1_to_2.wav'),
                           os.path.join(self.temporary_path, 'decomposition4'), 4)
        progress = 50
        yield "data:" + str(progress) + "\n\n"

        # decompose second song
        decomp.split_stems(os.path.join(self.temporary_path, 'beat_songs', '2_to_1.wav'),
                           os.path.join(self.temporary_path, 'decomposition4'), 4)
        progress = 60
        yield "data:" + str(progress) + "\n\n"

        generator_accomp = self.get_drum_bass()
        progress_logs = [61, 63, 65, 67, 68]
        for i in range(0, len(progress_logs)):
            next(generator_accomp)
            progress = progress_logs[i]
            yield "data:" + str(progress) + "\n\n"
        output_accompaniment = next(generator_accomp)
        progress = 70
        yield "data:" + str(progress) + "\n\n"

        generator_vocals = self.vocals_by_parts()
        progress_logs = [71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]
        for i in range(0, len(progress_logs)):
            next(generator_vocals)
            progress = progress_logs[i]
            yield "data:" + str(progress) + "\n\n"
        vocals = next(generator_vocals)
        progress = 90
        yield "data:" + str(progress) + "\n\n"

        output = output_accompaniment.overlay(vocals)

        output.export(os.path.join(self.temporary_path, 'mixed_songs', f'{mashup_name}.wav'), format='wav')
        progress = 95
        yield "data:" + str(progress) + "\n\n"

        config = conn_az.load_config()
        mashup = conn_az.get_files(os.path.join(self.temporary_path, 'mixed_songs'))
        conn_az.upload(mashup, config['azure_storage_connectionstring'], config['mixed_container_name'])
        progress = 100
        yield "data:" + str(progress) + "\n\n"

        print('DELETING......')
        try:
            shutil.rmtree(self.temporary_path)
        except OSError:
            os.remove(self.temporary_path)

    ''' functions to delete content of temporary files - helping functions'''

    def delete_temporary_files(self):
        list_dirs_to_clear = ['beat_songs', 'speed_songs', 'combined_accompaniment', 'decomposition2', 'decomposition4',
                              'decomposition5']
        for directory in list_dirs_to_clear:
            dir_path = os.path.join(self.temporary_path, directory)
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

    @staticmethod
    def delete_files_from_directory(path):
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

