import array
from collections import Counter

import numpy as np
import scipy
from pydub.utils import get_array_type
from Levenshtein import distance

NOTES = {
    "A": 440,
    "A#": 466.1637615180899,
    "B": 493.8833012561241,
    "C": 523.2511306011972,
    "C#": 554.3652619537442,
    "D": 587.3295358348151,
    "D#": 622.2539674441618,
    "E": 659.2551138257398,
    "F": 698.4564628660078,
    "F#": 739.9888454232688,
    "G": 783.9908719634985,
    "G#": 830.6093951598903,
}


def frequency_spectrum(sample, max_frequency=500):
    """
    Derive frequency spectrum of a signal pydub.AudioSample
    Returns an array of frequencies and an array of how prevelant that frequency is in the sample
    """
    # Convert pydub.AudioSample to raw audio data
    bit_depth = sample.sample_width * 8
    array_type = get_array_type(bit_depth)
    raw_audio_data = array.array(array_type, sample._data)
    n = len(raw_audio_data)

    # Compute FFT and frequency value for each index in FFT array
    freq_array = np.arange(n) * (float(sample.frame_rate) / n) 
    freq_array = freq_array[: (n // 2)]  

    freq_magnitude = scipy.fft.fft(raw_audio_data)                       # fft computing and normalization
    freq_magnitude = freq_magnitude[: (n // 2)]  

    if max_frequency:
        max_index = int(max_frequency * n / sample.frame_rate) + 1
        freq_array = freq_array[:max_index]
        freq_magnitude = freq_magnitude[:max_index]

    freq_magnitude = abs(freq_magnitude)
    freq_magnitude = freq_magnitude / np.sum(freq_magnitude)
    return freq_array, freq_magnitude


def classify_note_attempt(freq_array, freq_magnitude):
    min_freq = 82
    note_counter = Counter()
    for i in range(len(freq_magnitude)):
        if freq_magnitude[i] < 0.01:
            continue

        for freq_multiplier, credit_multiplier in [
            (1, 1),
            (1 / 3, 3 / 4),
            (1 / 5, 1 / 2),
            (1 / 6, 1 / 2),
            (1 / 7, 1 / 2),
        ]:
            freq = freq_array[i] * freq_multiplier
            if freq < min_freq:
                continue
            note = get_note_for_freq(freq)
            if note:
                note_counter[note] += freq_magnitude[i] * credit_multiplier

    return note_counter.most_common(1)[0][0]




def get_note_for_freq(f, tolerance=33):
    # Calculate the range for each note
    tolerance_multiplier = 2 ** (tolerance / 1200)
    note_ranges = {
        k: (v / tolerance_multiplier, v * tolerance_multiplier) for (k, v) in NOTES.items()
    }

    # Get the frequence into the 440 octave
    range_min = note_ranges["A"][0]
    range_max = note_ranges["G#"][1]
    if f < range_min:
        while f < range_min:
            f *= 2
    else:
        while f > range_max:
            f /= 2

    # Check if any notes match
    for (note, note_range) in note_ranges.items():
        if f > note_range[0] and f < note_range[1]:
            return note
    return None

