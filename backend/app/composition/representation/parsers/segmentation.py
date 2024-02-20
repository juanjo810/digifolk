#!/usr/bin/env python3.7
"""
This script presents the necessary functions for dealing with segmentation of musical phrases
"""

import math

import numpy as np

import app.composition.representation.parsers.utils as basic_utils
import app.composition.representation.utils.features as utils

INTERPART_WEIGHTS = {  # candidates for phrasing discovery (harmonic)
    "basic.root": 1,
    "pitches": 1,
    "cardinality": 1,
    "quality": 1,
    "prime_form": 1,
    "inversion": 1,
    "pitch_class": 1,
    "forte_class": 1,
    "pc_ordered": 1,
    "keysig": 1,
    "signatures.function": 1,
    "measure.function": 1,
}

LINE_WEIGHTS = {  # candidates for phrasing discovery (melodic)
    'pitch.cpitch': 4,
    'basic.rest': 5,
    'expressions.fermata': 5,
    'bioi_ratio': 4,
    'key.signatures.scale_degree': 2.5,
    'derived.dur_ratio': 3.5,
    'time.barlines.repeat.exists_before': 1,
    'time.barlines.repeat.is_end': 1,
}


def change_degree(event_1, event_2):
    """
    Returns degree of change between
    two events for each feature of event
    """
    return [abs(a - b) / (a + b) if abs(a) != abs(b) else 0 for a, b in zip(event_1, event_2)]


def strength(nf_im1, nf_i, nf_ip1):
    """
    Gets Strength for each feature of an event from the its
    normalized feature list representation,
    and the normalized feature list
    representations of the previous and posteriors events
    """
    degree_1 = change_degree(nf_im1, nf_i)
    degree_2 = change_degree(nf_i, nf_ip1)
    sum_nf = [a + b for a, b in zip(degree_1, degree_2)]
    return [a * b for a, b in zip(nf_i, sum_nf)]


def threshold_peak_picking(i, window, k, boundary_strengths):
    """
    Calculates the threshold value, using standard deviation and mean
    In a specific Window of Time
    """
    if window is None:
        window = i

    start = 0
    if (i - window) > start:
        start = i - window

    bs_window = boundary_strengths[start:i]
    xbar = [sum(bs) / len(bs_window) for bs in zip(*bs_window)]
    deviations = [
        [(a - b) ** 2 for a, b in zip(bs, xbar)] for bs in boundary_strengths[:i]
    ]

    sum_dev = [sum(dev) for dev in zip(*deviations)]
    sum_mean = [sum(bs) for bs in zip(*boundary_strengths[:i])]

    variances = [math.sqrt(dev / (i - 1)) for dev in sum_dev]
    means = [(mean / (i - 1)) for mean in sum_mean]

    return [(k * v + m) for v, m in zip(variances, means)]


def double_threshold_peak_picking(i, window, k, boundary_strengths):
    """
    Calculates the threshold value, using standard deviation and mean
    In a specific Window of Time
    """
    start = 0
    if window and (i - window) > start:
        start = i - window

    end = len(boundary_strengths)
    if window and (i + window) < len(boundary_strengths):
        end = i + window + 1

    bounds_except_i = boundary_strengths[start:i] + boundary_strengths[i + 1:]

    bs_window = bounds_except_i
    xbar = [sum(bs) / len(bs_window) for bs in zip(*bs_window)]
    deviations = [
        [(a - b) ** 2 for a, b in zip(bs, xbar)] for bs in bounds_except_i
    ]

    sum_dev = [sum(dev) for dev in zip(*deviations)]
    sum_mean = [sum(bs) for bs in zip(*bounds_except_i)]

    variances = [math.sqrt(dev / (i - 1)) for dev in sum_dev]
    means = [(mean / (i - 1)) for mean in sum_mean]

    return [(k * v + m) for v, m in zip(variances, means)]


def peak_picking(i, boundary_strengths, weights, window=None, k=1.28, total=False):
    """
    Peak Picking Boundary Location Witten and Pearce

    Principles:
    - Note following a boundary should have greater/equal strength than following note
    - Note following a boundary should have greater/equal strength than preciding note
    - Note following a boundary should have higher (> k) strength

    Returns 1 for existent boundary before note
    Returns 0 for not existent boundary before note
    """
    if i < 2:  # First note is always a note following a boundary
        return 1 - i  # Second note is not a candidate
    if i == len(boundary_strengths) - 1:  # Penultimate note is not candidate
        return 0

    w_bs_i = np.dot(boundary_strengths[i], weights)
    w_bs_ip1 = np.dot(boundary_strengths[i + 1], weights)
    w_bs_im1 = np.dot(boundary_strengths[i - 1], weights)

    thresh_p_p = []
    if total:
        thresh_p_p = double_threshold_peak_picking(
            i, window, k, boundary_strengths)
    else:
        thresh_p_p = threshold_peak_picking(
            i, window, k, boundary_strengths)

    w_value = np.dot(thresh_p_p, weights)

    if w_bs_i >= w_bs_ip1 and w_bs_i >= w_bs_im1 and w_bs_i > w_value:
        return 1
    return 0


def calculate_boundary_strengths(normed_features, weights):
    """
    Calculate and Normalize Boundary Strengths
    """
    # Calculate boundary strengths
    boundary_strengths = [
        strength(normed_features[i - 1],
                 normed_features[i], normed_features[i + 1])
        for i, _ in enumerate(normed_features[1:-1])
    ]
    boundary_strengths.insert(0, np.zeros(len(weights)))

    # Normalize strenghs and weights
    normalized_bss = utils.normalize(np.array(boundary_strengths), 0, 1)
    normalized_weights = utils.normalize_weights(weights)

    return normalized_bss, normalized_weights


def process_weights(events, i_weights, line=True):
    """
    Process Segmentation Weights for Line Viewpoints
    """
    if i_weights is None or i_weights == {}:
        if line:
            i_weights = LINE_WEIGHTS
        else:
            i_weights = INTERPART_WEIGHTS

    # Get all events as a set of normalized features
    features, _, _, weights = utils.events_to_features(
        events,
        weights=i_weights,
        normalization="from_0",
        offset=False,
        flatten_feat=False,
    )
    return features, weights


def process_incoming_weights(
    events, weights_line=None, interpart_events=None, weights_vert=None, indexes=None
):
    """
    Process Incoming Weights
    """
    features, weights = process_weights(events, weights_line)
    if interpart_events is not None and indexes is not None:
        vert_features, vert_weights = process_weights(
            interpart_events, weights_vert, line=False
        )
        for i, ind in enumerate(indexes):
            features[i] = np.concatenate((features[i], vert_features[ind]))
            weights = np.concatenate((weights, vert_weights))
    return features, weights


def apply_phrasing_PPBL(events, normalized_bss, normalized_weights):
    """
    Apply boundaries to Events
    """
    for i, event in enumerate(events):
        if i == len(events) - 1:
            events[-1].add_viewpoint("phrase.boundary", -1)
            break

        # Calculate presence of boundary
        boundary = peak_picking(
            i, normalized_bss, normalized_weights, total=True, k=1.28, window=5)

        if i != 0 and (events[i - 1].get_viewpoint('expressions.fermata')
                       or events[i - 1].get_viewpoint('basic.rest')):
            boundary = 1

        event.add_viewpoint("phrase.boundary", boundary)
        if boundary == 1 and i != 0:
            events[i - 1].add_viewpoint("phrase.boundary", -boundary)


def gap_score(events, index_event):
    """
    GAP_SCORE
    """
    ioi = events[index_event].get_viewpoint('basic.bioi')
    ooi = events[index_event].get_viewpoint('duration.length')

    prev_iois = [event.get_viewpoint('basic.bioi')
                 for event in events[:index_event + 1]]
    media_iois = sum(prev_iois) / len(prev_iois)

    if media_iois == 0:
        return 0
    return 500 * (ioi + ooi) / media_iois

def grouper(events, optimal_length=10, step_segmentation=False, second=False):
    """
    Grouper algorithm for segmentation
    """
    num_notes = len(events)

    gaps = []
    beat_scores = []
    for i, event in enumerate(events):
        gaps.append(gap_score(events, i))
        beat_scores.append(event.get_viewpoint('derived.beat_strength'))
    gaps.append(0)

    best_score = 0
    length_penalty = 0

    best_values = np.zeros(shape=(num_notes))
    analysis = np.zeros(shape=(num_notes))
    score = np.zeros(shape=(num_notes,20))

    for z in range(1, num_notes):
        best_score = -1000000.0
        for i in range(1, num_notes):
            if z - i >= 0 and i < 20:
                length_penalty = abs(
                    600 * (3.32 * math.log10(i / optimal_length)))

                """
                Try meter penalty too
                """
                if not step_segmentation:
                    phase_penalty = 300
                    if beat_scores[z] == beat_scores[z-i]:
                        phase_penalty = 0.0
                    elif beat_scores[z] - 0.5 == beat_scores[z-i] or beat_scores[z] + 0.5 == beat_scores[z-i]:
                        phase_penalty = 150
                else:
                    phase_penalty = 0

                gaps_score = ((((gaps[z - i] / 2) + (gaps[z] / 2) -
                                                   length_penalty) - phase_penalty) * math.sqrt(i))

                score[z][i] = analysis[z - i] + gaps_score

                if score[z][i] > best_score:
                    best_score = score[z][i]
                    analysis[z] = score[z][i]
                    best_values[z] = i
            else:
                break

    final = np.zeros(shape=num_notes+1)
    final[-1] = -1
    z = num_notes - 1
    while z > 0:
        val = int(z - best_values[z])
        final[val] = -1
        z = val
    final[0] = 1
    final[1] = 0

    # print(final)

    index_1s = [i for i, el in enumerate(final) if el == 1.0 or el == -1.0]
    phrase_lengths = np.diff(index_1s)

    from statistics import mean

    if len(phrase_lengths) > 1:
        # print(phrase_lengths)
        length_mode = int(mean(phrase_lengths))
        #print('LM: ' + str(length_mode))
        #print('PL: ' + str(phrase_lengths))

        if not step_segmentation and not second and (max(phrase_lengths) - min(phrase_lengths) > 4): #and min(phrase_lengths) > 4:
            return grouper(events, optimal_length=length_mode, second=True)

    return final

def apply_boundaries_grouper(events, final, step_segmentation=False):
    """
    """
    for i, event in enumerate(events):

        event.add_viewpoint("phrase.boundary", final[i])

        if event.is_rest():
            # search the nearby events to see if any is boundary
            nearby = final[i-3:i]
            if any(s==-1.0 for s in nearby):
                #print('Here ' + str(i))
                #print(nearby)
                last_fin = np.where(nearby == -1.0)
                #print(last_fin)
                if not isinstance(last_fin, int):
                    if isinstance(last_fin[0], int):
                        last_fin = last_fin[0]
                    else:
                        last_fin = last_fin[0][0]
                    #print(last_fin)
                events[i - 3 + last_fin].add_viewpoint("phrase.boundary", 0.0)

            if i > 0 and events[i-1].is_rest():
                events[i-1].add_viewpoint("phrase.boundary", 0.0)

            # Force the rest as "end" boundary
            event.add_viewpoint("phrase.boundary", -1.0)

        if i > 0 and events[i-1].get_viewpoint("phrase.boundary") == -1.0:
            event.add_viewpoint("phrase.boundary", 1.0)

    if not step_segmentation:
        events[-1].add_viewpoint("phrase.boundary", -1.0)

    bounds_start = [i for i, ev in enumerate(events) if ev.get_viewpoint("phrase.boundary") == 1.0]
    for bound in bounds_start:
        if bound > 0 and events[bound - 1].get_viewpoint("phrase.boundary") != -1.0:
            events[bound].add_viewpoint("phrase.boundary", 0.0)
        if bound < len(events) -2 and events[bound + 1].get_viewpoint("phrase.boundary") == -1.0:
            events[bound + 1].add_viewpoint("phrase.boundary", 0.0)
            events[bound + 2].add_viewpoint("phrase.boundary", 0.0)

    events[0].add_viewpoint("phrase.boundary", 1.0)
    events[1].add_viewpoint("phrase.boundary", 0.0)

def segmentation(
    events, weights_line=None, interpart_events=None, weights_vert=None, indexes=None, method='Grouper', step_segmentation=False, optimal_length=10
):
    """
    Segmentation for a set of events, using method:
    'PPBL': Peak Picking Boundary Location by Witten and Pearce
    'Grouper': Grouper Segmentation
    """
    if method == 'PPBL':
        features, weights = process_incoming_weights(
            events, weights_line, interpart_events, weights_vert, indexes
        )
        normalized_bss, normalized_weights = calculate_boundary_strengths(
            features, weights)
        apply_phrasing_PPBL(events, normalized_bss, normalized_weights)
    elif method == 'Grouper':
        apply_ev = [ev for ev in events if not isinstance(ev, str)]
        final = grouper(apply_ev, step_segmentation=step_segmentation, optimal_length=optimal_length)
        apply_boundaries_grouper(apply_ev, final, step_segmentation)

"""
GENERAL FUNCTIONS TO USE AFTER BOUNDARY SETTING
"""
def get_last_bound_index_and_length(boundary_indexes, len_events, i):
    """
    Get Index for Last Phrase Boundary
    """
    index = boundary_indexes.index(
        min(boundary_indexes, key=lambda x: abs(x - i)))
    last_index = (index, index - 1)[bool(i < boundary_indexes[index])]

    length = len_events - boundary_indexes[last_index]
    if last_index < len(boundary_indexes) - 1:
        length = boundary_indexes[last_index + 1] - \
            boundary_indexes[last_index]
    if i in boundary_indexes:
        last_index = boundary_indexes.index(i) - 1
        length = len_events - i
        if last_index < len(boundary_indexes) - 2:
            length = boundary_indexes[last_index + 2] - i

    return last_index, length


def apply_segmentation_info(events):
    """
    Apply information to events from boundaries information
    """
    # print('Parse Segmentation')
    boundary_indexes = [
        i
        for i, event in enumerate(events)
        if event.get_viewpoint("phrase.boundary") == 1
    ]

    for i, event in enumerate(events):
        if i != 0:
            last_index, length = get_last_bound_index_and_length(
                boundary_indexes, len(events), i
            )
            intphrase = basic_utils.seq_int(
                event.get_viewpoint("pitch.cpitch"),
                events[last_index].get_viewpoint("pitch.cpitch"),
            )
            event.add_viewpoint("intphrase", intphrase)
            event.add_viewpoint("phrase.length", length)


def get_phrases_from_events(events, return_rest_phrases=False):
    """
    Get Phrases from events, calculated using boundaries
    """
    phrase_begins = [
        i
        for i, event in enumerate(events)
        if event.get_viewpoint("phrase.boundary") == 1
    ]

    phrases = []
    for i, begin in enumerate(phrase_begins):
        if i < len(phrase_begins) - 1:
            phrases.append(events[begin: phrase_begins[i + 1]])
        else:
            phrases.append(events[begin:])

    if not return_rest_phrases:
        new_phrases = []
        for phrase in phrases:
            rests_of_phrase = [event for event in phrase if event.is_rest()]
            if len(rests_of_phrase) != len(phrase):
                new_phrases.append(phrase)
        phrases = new_phrases

    return phrases
