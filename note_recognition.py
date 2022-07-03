import argparse

from pydub import AudioSegment
import pydub.scipy_effects
import numpy as np
import scipy
import matplotlib.pyplot as plt

# from note_prediction import (
#     frequency_spectrum,
#     classify_note_attempt,
# )


def main(file, note_file=None, note_starts_file=None, plot_starts=False):
    # If a note file and/or actual start times are supplied read them in
    actual_starts = []
    if note_starts_file:
        with open(note_starts_file) as f:
            for line in f:
                actual_starts.append(float(line.strip()))

    actual_notes = []
    if note_file:
        with open(note_file) as f:
            for line in f:
                actual_notes.append(line.strip())

    song = AudioSegment.from_file(file)
    song = song.high_pass_filter(80, order=4)

    starts = predict_note_starts(song, plot_starts, actual_starts)

    # predicted_notes = predict_notes(song, starts, actual_notes)

    print("")
    if actual_notes:
        print("Actual Notes")
        print(actual_notes)
    print("Predicted Notes")
    # print(predicted_notes)


# Returns perdicted starts in ms
def predict_note_starts(song, plot, actual_starts):
    # Size of segments to break song into for volume calculations
    SEGMENT_MS = 50
    # Minimum volume necessary to be considered a note
    VOLUME_THRESHOLD = -35
    # The increase from one sample to the next required to be considered a note
    EDGE_THRESHOLD = 5
    # Throw out any additional notes found in this window
    MIN_MS_BETWEEN = 100

    # Filter out lower frequencies to reduce noise
    song = song.high_pass_filter(80, order=4)
    # dBFS is decibels relative to the maximum possible loudness
    volume = [segment.dBFS for segment in song[::SEGMENT_MS]]

    predicted_starts = []
    for i in range(1, len(volume)):
        if volume[i] > VOLUME_THRESHOLD and volume[i] - volume[i - 1] > EDGE_THRESHOLD:
            ms = i * SEGMENT_MS
            # Ignore any too close together
            if len(predicted_starts) == 0 or ms - predicted_starts[-1] >= MIN_MS_BETWEEN:
                predicted_starts.append(ms)

    # If actual note start times are provided print a comparison
    if len(actual_starts) > 0:
        print("\nApproximate actual note start times ({})".format(len(actual_starts)))
        print(" ".join(["{:5.2f}".format(s) for s in actual_starts]))
    print("\nPredicted note start times ({})".format(len(predicted_starts)))
    print(" ".join(["{:5.2f}".format(ms / 1000) for ms in predicted_starts]))

    # Plot the volume over time (sec)
    if plot:
        x_axis = np.arange(len(volume)) * (SEGMENT_MS / 1000)
        plt.plot(x_axis, volume)

        # Add vertical lines for predicted note starts
        for ms in predicted_starts:
            plt.axvline(x=(ms / 1000), color="g", linewidth=0.5, linestyle=":")

        plt.show()

    return predicted_starts


# def predict_notes(song, starts, actual_notes):
#     predicted_notes = []
#     for i, start in enumerate(starts):
#         sample_from = start + 50
#         sample_to = start + 550
#         if i < len(starts) - 1:
#             sample_to = min(starts[i + 1], sample_to)
#         segment = song[sample_from:sample_to]
#         freqs, freq_magnitudes = frequency_spectrum(segment)
#
#         predicted = classify_note_attempt(freqs, freq_magnitudes)
#         predicted_notes.append(predicted or "U")
#
#         # Print general info
#         print("")
#         print("Note: {}".format(i))
#         if i < len(actual_notes):
#             print("Predicted: {} Actual: {}".format(predicted, actual_notes[i]))
#         else:
#             print("Predicted: {}".format(predicted))
#         print("Predicted start: {}".format(start))
#         length = sample_to - sample_from
#         print("Sampled from {} to {} ({} ms)".format(sample_from, sample_to, length))
#
#     return predicted_notes


if __name__ == "__main__":

    main(
        file="/Users/kartikeyaranjan/Desktop/Kartikeya/Major Projects/Musical Note Recognition Tool/Sample Music/sample.mp3",
        note_file="/Users/kartikeyaranjan/Desktop/Kartikeya/Major Projects/Musical Note Recognition Tool/Notes Text files/actual_notes.txt",
        # note_file=None,
        note_starts_file="/Users/kartikeyaranjan/Desktop/Kartikeya/Major Projects/Musical Note Recognition Tool/Notes Text files/sample_half_notes",
        # note_starts_file=None,
        plot_starts=False,
    )
