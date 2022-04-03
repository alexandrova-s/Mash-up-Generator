import os.path

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import ruptures as rpt  # our package

''' script for splitting songs into plain parts using Kernel Change-point Detection algorithm'''

''' helping function for figures generations '''
def fig_ax(figsize=(15, 5), dpi=150):
    return plt.subplots(figsize=figsize, dpi=dpi)

''' function plotting song envelope '''
def plot_envelope(signal, sr=22050):
    fig, ax = fig_ax()
    ax.plot(np.arange(signal.size) / sr, signal)
    ax.set_xlim(0, signal.size / sr)
    ax.set_xlabel("Time (s)")
    _ = ax.set(title="Sound envelope")
    # plt.show()

''' function computing and returning song tempogram '''
def generate_tempogram(signal, sr=22050):

    hop_length_tempo = 256

    oenv = librosa.onset.onset_strength(
        y=signal, sr=sr, hop_length=hop_length_tempo
    )

    tempogram = librosa.feature.tempogram(
        onset_envelope=oenv,
        sr=sr,
        hop_length=hop_length_tempo,
    )
    # # Display the tempogram
    # fig, ax = fig_ax()
    # _ = librosa.display.specshow(
    #     tempogram,
    #     ax=ax,
    #     hop_length=hop_length_tempo,
    #     sr=sr,
    #     x_axis="s",
    #     y_axis="tempo",
    # )
    # plt.show()
    return tempogram

''' function counting cost of parts split '''
def get_sum_of_cost(model, n_bkps) -> float:
    bkps = model.predict(n_bkps=n_bkps)
    return model.cost.sum_of_costs(bkps)

''' function applying proper Kernel CPD algorithm and defining places of split;
    responsible also for generating plots showing split song '''
def number_of_changes_in_song(tempogram, n_bkps_max=20, sr=22050):
    hop_length_tempo = 256
    model = rpt.KernelCPD(kernel="linear").fit(tempogram.T)

    _ = model.predict(n_bkps_max)

    n_bkps_arr = np.arange(1, n_bkps_max + 1)

    # fig, ax = fig_ax((7, 4))
    # ax.plot(
    #     n_bkps_arr,
    #     [get_sum_of_cost(model=model, n_bkps=n_bkps) for n_bkps in n_bkps_arr],
    #     "-*",
    #     alpha=0.5,
    # )
    # ax.set_xticks(n_bkps_arr)
    # ax.set_xlabel("Number of change points")
    # ax.set_title("Sum of costs")
    # ax.grid(axis="x")
    # ax.set_xlim(0, n_bkps_max + 1)

    n_bkps = 13
    # _ = ax.scatter([13], [get_sum_of_cost(model=model, n_bkps=13)], color="r", s=100)

    # Segmentation
    bkps = model.predict(n_bkps=n_bkps)
    bkps_times = librosa.frames_to_time(bkps, sr=sr, hop_length=hop_length_tempo)

    # # Displaying results
    # fig, ax = fig_ax()
    # _ = librosa.display.specshow(
    #     tempogram,
    #     ax=ax,
    #     x_axis="s",
    #     y_axis="tempo",
    #     hop_length=hop_length_tempo,
    #     sr=sr,
    # )

    # for b in bkps_times[:-1]:
    #     ax.axvline(b, ls="--", color="white", lw=4)
    #
    # plt.show()
    return bkps_times

''' function spiting songs into parts and optionally saving them as particular wave files '''
def split_segments(song_name, signal, bkps_times, save_path, sr=22050, save_segments=False):
    bkps_time_indexes = (sr * bkps_times).astype(int).tolist()

    i = 1
    all_segments = []
    segments_indexes = []
    for (segment_number, (start, end)) in enumerate(
        rpt.utils.pairwise([0] + bkps_time_indexes), start=1
    ):
        segment = signal[start:end]
        # print(f"Segment n°{segment_number} (duration: {segment.size/sr:.2f} s)")
        all_segments.append(segment)
        segments_indexes.append((start, end))
        if save_segments:
            sf.write(os.path.join(save_path, 'segmented', f'{song_name}_segment_{i}.wav'), segment, sr, format='wav')
        i += 1
    return all_segments, segments_indexes


