import numpy as np
import numba as nb
import app.composition.representation.utils.features as utils

DNOTES = {
    'C': 2,
    'D': 3,
    'E': 4,
    'F': 5,
    'G': 6,
    'A': 0,
    'B': 1
}


def transposeSimToDist(matrix):
    import numpy as np
    max_sim = np.amax(matrix)
    return abs(matrix - max_sim)


def create_datapoint_sets(sequence, type='2d-mel'):
    data_points = []

    for event in sequence:
        if event.not_rest_or_grace():

            point = []
            if 'OFF' in type:
                onset = float(event.get_offset())
                point.append(onset)

            if 'INT' in type:
                interval = float(event.get_viewpoint('derived.seq_int'))
                point.append(interval)

            if 'PITCH' in type:
                chr_pitch = float(event.get_viewpoint('pitch.cpitch') - 21)
                point.append(chr_pitch)

            if 'DUR' in type:
                rit_dur = float(event.get_viewpoint('duration.length'))
                point.append(rit_dur)

            if 'DUR_RATIO' in type:
                dur_rat = float(event.get_viewpoint('derived.dur_ratio'))
                point.append(dur_rat)

            if 'BS' in type:
                metric_position = float(
                    event.get_viewpoint('derived.beat_strength'))
                point.extend([metric_position])

            if 'PS' in type:
                metric_position = float(
                    event.get_viewpoint('derived.posinbar'))
                point.extend([metric_position])

            if 'DN' in type:
                diat_pitch = float(DNOTES[event.get_viewpoint(
                    'pitch.dnote')] + event.get_viewpoint('pitch.octave') * 7)
                point.extend([diat_pitch])

            if 'V' in type:
                voice = int(event.get_viewpoint(
                    'metadata.voice').replace('v', ''))
                point.extend([voice])

            if 'TS' in type:
                timesig = event.get_viewpoint(
                    'time.timesig')
                point.extend([timesig])

            if 'KN' in type:
                d_note = float(DNOTES[event.get_viewpoint(
                    'pitch.dnote')])
                k_note = float(DNOTES[event.get_viewpoint(
                    'key.analysis.key').replace('#', '').replace('b', '')])

                if d_note < k_note:
                    scale_degree = d_note + k_note
                else:
                    scale_degree = k_note - d_note

                point.extend([scale_degree])

            data_points.append(
                np.array(point))

    if 'BIOI' in type:
        biois = get_real_biois_wout_rests(sequence)
        data_points = np.array(data_points)
        data_points = np.c_[data_points, biois]

    return data_points


def get_real_biois_wout_rests(sequence):
    import bisect

    non_rests = [[i, ev.get_viewpoint('basic.bioi')]
                 for i, ev in enumerate(sequence) if ev.not_rest_or_grace()]
    if len(non_rests) < len(sequence):
        rest_indexes = [[i, ev.get_viewpoint('basic.bioi')] for i, ev in enumerate(
            sequence) if ev.is_rest()]
        for (i, bioi) in rest_indexes:
            near = bisect.bisect_left(non_rests, [i, ])
            non_rests[near - 1][1] += bioi
    return [ev[1] for ev in non_rests]


def create_vector_table(datapoints_1, datapoints_2):
    vector_table = np.empty(
        (len(datapoints_1), len(datapoints_2), len(datapoints_1[0])))

    for i, vec_1 in enumerate(datapoints_1):
        for j, vec_2 in enumerate(datapoints_2):
            vector_table[i][j] = vec_1 - vec_2

    return vector_table


def MTP(vector_table, trans_vector):
    return np.count_nonzero(np.all(vector_table == trans_vector, axis=2))


def SIAM(seq_1, seq_2):
    """
    Structure induction algorithms's pattern matching algorithm
    """
    vector_table = create_vector_table(seq_1, seq_2)
    return max([MTP(vector_table, T) for T in vector_table[::]]) / len(seq_1)


def pitch_rater(seq1, seq2, variances=[]):
    """ subsitution score for local alignment"""
    if np.all(seq1 == seq2):
        return 1.0
    else:
        return -1.0


def local_alignment(seq_1, seq_2, insert_score=-.5, delete_score=-.5,
                    sim_score=pitch_rater, variances=[]):
    """
    Local Alignent Algorithm (Janssen/Kranenburg/Volk)
    based on https://github.com/BeritJanssen/MelodicOccurrences/blob/master/similarity.py
    """
    if len(seq_1) > len(seq_2):
        temp_seq = seq_1
        seq_1 = seq_2
        seq_2 = temp_seq

    # initialize dynamic programming matrix
    dyn_matrix = np.zeros([len(seq_1) + 1, len(seq_2) + 1])
    # initialize backtrace matrix
    back_matrix = np.zeros([len(seq_1) + 1, len(seq_2) + 1])

    max_score = 0.0

    for i, ev_1 in enumerate(seq_1):
        for j, ev_2 in enumerate(seq_2):
            from_left = dyn_matrix[i + 1, j] + delete_score
            from_top = dyn_matrix[i, j - 1] + insert_score

            diag = dyn_matrix[i, j] + sim_score(ev_1[0:], ev_2[0:], variances)
            dyn_matrix[i + 1, j + 1] = max(from_top, from_left, diag, 0.0)

            if dyn_matrix[i + 1, j + 1] > max_score:
                max_score = dyn_matrix[i + 1, j + 1]
            # store where the current entry came from in the backtrace matrix
            if dyn_matrix[i + 1, j + 1] == from_left:
                # deletion from longer sequence
                backtrace = 0
            elif dyn_matrix[i + 1, j + 1] == from_top:
                # insertion into longer sequence
                backtrace = 1
            elif dyn_matrix[i + 1, j + 1] == diag:
                # substitution
                backtrace = 2
            else:
                backtrace = -1
            back_matrix[i + 1, j + 1] = backtrace

    return max_score / float(min(len(seq_1), len(seq_2)))
