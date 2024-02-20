import math
from collections import Counter
import random
import sys

import music21
import numpy as np
from app.composition.representation.conversor.score_conversor import \
    parse_single_line
from app.composition.representation.events.linear_event import PartEvent

np.set_printoptions(threshold=sys.maxsize)


def filter_poss_ts(ts):
    if ts == 2:
        poss = ['2/2', '2/4', '4/4']
    elif ts == 3:
        poss = ['3/4', '3/8', '6/8', '9/8']
    elif ts == 'poli':
        poss = ['5/8', '7/8']
    else:
        poss = ['2/4', '3/4', '4/4', '6/8', '9/8', '5/8', '7/8']
    return poss


def get_mode_of_original(oracle, st_points, choice):
    """Get Mode of Original at Point"""
    offset_mode = get_index_viewpoint(oracle, 'key.analysis.mode')
    find_mode = filter_index_viewpoints(
        oracle, offset_mode, st_points[choice[0]])
    return find_mode[0].split('=')[1]


def get_key_of_original(oracle, st_points, choice):
    """Get Key of Original at Point"""
    offset_key = get_index_viewpoint(oracle, 'analysis.key')
    find_key = filter_index_viewpoints(
        oracle, offset_key, st_points[choice[0]])
    return find_key[0].split('=')[1]


def get_first_pitch_of_original(oracle, st_points, choice):
    """Get Key of Original at Point"""
    offset_key = get_index_viewpoint(oracle, 'pitch.cpitch')
    pitch = oracle['information']['original_features'][st_points[choice[0]], offset_key]
    return music21.pitch.Pitch(midi=int(pitch))


def get_key_for_song(oracle, st_points, choice):
    """
    Get Key for Song
    """
    mode = get_mode_of_original(oracle, st_points, choice)
    key = get_key_of_original(oracle, st_points, choice)

    fpitch = get_first_pitch_of_original(oracle, st_points, choice)
    nfpitch = music21.pitch.Pitch(midi=int(choice[1]))
    interval = music21.interval.Interval(noteStart=fpitch, noteEnd=nfpitch)

    r_key = music21.key.Key(key, mode.lower())
    return r_key.transpose(interval), interval


def correct_stream_scale(m21_stream, scale, more_pitches=[], direction='ascending'):
    """Correct the Notes of a stream according to scale pitches"""

    pitches_stream = [n.pitch.name for n in m21_stream.flat.notes]
    sc_p = [p.name for p in scale.pitches]
    i_in_scale = [i for i, p in enumerate(pitches_stream) if p not in sc_p]

    pitches_more = { music21.pitch.Pitch(x[0]).name : x[1] for x in more_pitches}
    print(pitches_more)

    for n in i_in_scale:
        p = random.random()
        if n in pitches_more and p < pitches_more[n]:
            continue

        act_p = m21_stream.flat.notes[n].pitch
        next_p = scale.next(act_p.name, direction)
        next_p.octave = act_p.octave
        m21_stream.flat.notes[n].pitch = next_p


def get_real_timesignature(ts):
    """
    Get Real Time Signature,
    According to the one inputed
    """
    return random.choice(filter_poss_ts(ts))


def get_timesig_stats(oracle, ts):
    """
    Get Number of Songs that share timesignature
    """
    ex = ''.join(oracle['information']
                 ['original_features_names'][ts].split('=')[1:])
    stat = np.where(oracle['information']
                    ['original_features'][oracle['indexes'], ts] == 1.0)
    res = [i for f, i in enumerate(oracle['indexes']) if f in stat[0]]
    return (ex, len(stat[0]), res)


def get_real_timesignatures_prob(ts, oracle):
    """
    Get Real Time Signature,
    According to the one inputed
    and Probability in Oracle
    """
    poss = filter_poss_ts(ts)

    ts_index = get_index_viewpoint(oracle, 'time.timesig')
    existent_tss = [get_timesig_stats(oracle, tss) for tss in ts_index]

    filter = [p for p in existent_tss if p[0] in poss]
    total_filtered = sum([pt[1] for pt in filter])
    chosen_ts = np.random.choice(
        range(len(filter)), p=[ps[1]/total_filtered for ps in filter])

    return filter[chosen_ts][0], filter[chosen_ts][2]


def curve_from_points(points):
    """
    Get General Curve from points
    """
    points.sort()
    phrases = {}
    for p in points:
        phrase = p[5]
        if phrase not in phrases:
            phrases[phrase] = []
        phrases[phrase].append(int(p[-1]))
    return phrases


def level_of_pitch(pc):
    """
    Get Level for Pitch
    """
    if 71 < pc < 78:
        return 1
    elif 64 < pc < 72:
        return 2
    elif 56 < pc < 65:
        return 3
    else:
        return None


def level_pc(pc, level):
    """
    Check if Pitch is included in Pitch-Level
    """
    if pc is None:
        return True
    if level_of_pitch(pc) == level:
        return True
    return False


def get_index_viewpoint(oracle, viewpoint, extra=''):
    """
    Get Index of a Feature in Viewpoints List
    """
    if viewpoint in oracle['information']['original_features_names']:
        return oracle['information']['original_features_names'].index(viewpoint)

    inds = []
    for i, name in enumerate(oracle['information']['original_features_names']):
        if viewpoint in name:
            if '=' in name and extra == '':
                inds.append(i)
            elif '=' in name and extra in name:
                return i
    return inds


def filter_index_viewpoints(oracle, indexes, k):
    """
    Filter Indexes of a Feature in Viewpoints List
    """
    names = []
    for i in indexes:
        if oracle['information']['original_features'][k, i] == 1.0:
            names.append(oracle['information']['original_features_names'][i])
    return names


def get_beat_strength(event, timesignature):
    """
    Get Beat Strength and Position in Bar of Event
    """
    stream = music21.stream.Stream()
    stream.insert(0, timesignature)

    note = music21.note.Note(
        duration=music21.duration.Duration(event.get_viewpoint('duration.length')))

    stream.insert(event.offset_time, note)
    meterModulus = timesignature.getMeasureOffsetOrMeterModulusOffset(note)
    beatStrength = timesignature.getAccentWeight(meterModulus,
                                                 forcePositionMatch=True,
                                                 permitMeterModulus=False)
    posinbar = note.beat - 1
    return beatStrength, posinbar


def event_extract(oracle_info, number, timesignature, last_event=None, last_pitch=65, first=False, offset_i=0, offset_last=None):
    """
    Extract Event according to chosen state
    """
    if number >= len(oracle_info["information"]["selected_original"]):
        event = PartEvent(
            from_list=oracle_info["information"]["selected_original"][-1],
            features=oracle_info["information"]["selected_features_names"],
        )
    else:
        event = PartEvent(
            from_list=oracle_info["information"]["selected_original"][number],
            features=oracle_info["information"]["selected_features_names"],
        )

    if first:
        event.add_viewpoint('basic.bioi', 0.0)
        event.add_viewpoint('pitch.cpitch', last_pitch)
        event.add_viewpoint('derived.seq_int', 0.0)

        if offset_last:
            event.offset_time = offset_last
        else:
            get_offset_i = oracle_info["information"]["original_features"][number, offset_i]
            event.offset_time = get_offset_i
    else:
        if not event.is_rest():
            if last_event.get_viewpoint(
                    'pitch.cpitch'):
                new_pitch = last_event.get_viewpoint(
                    'pitch.cpitch') + event.get_viewpoint('derived.seq_int')
            else:
                new_pitch = last_pitch + event.get_viewpoint('derived.seq_int')
            event.add_viewpoint('pitch.cpitch', new_pitch)

        event.offset_time = last_event.offset_time + \
            last_event.get_viewpoint('duration.length')
        event.add_viewpoint(
            'basic.bioi', event.get_viewpoint('duration.length'))

    beatStrength, posinbar = get_beat_strength(event, timesignature)
    event.add_viewpoint('derived.beat_strength', beatStrength)
    event.add_viewpoint('derived.posinbar', posinbar)

    return event


def extract_score(last_pitch, time_signature, key_signature, sequence, onset=None):
    """
    Extract Score from Sequence of Events
    """
    new_score = parse_single_line(sequence, start_pitch=last_pitch,
                                  time_signature=time_signature, key_signature=key_signature,
                                  end_position_last_phrase=onset,
                                  show_segmentation=True, contour=False)

    new_score.makeAccidentals(inPlace=True, overrideStatus=True)
    new_score.insert(0.0, music21.clef.TrebleClef())

    if len(new_score.measure(1).flat.notes) == 0:
        new_score.measure(2).keySignature = new_score.measure(1).keySignature
        new_score.measure(2).timeSignature = new_score.measure(1).timeSignature
        new_score.remove(new_score.measure(1), shiftOffsets=True)

    return new_score


def map_first_pitch(pattern):
    if len(pattern) < 1 or (pattern[0] < 1 or pattern[0] > 3):
        return list(range(60, 76, 1))
    if pattern[0] == 1:
        return list(range(71, 74, 1))
    if pattern[0] == 2:
        return list(range(66, 69, 1))
    if pattern[0] == 3:
        return list(range(59, 62, 1))
    return list(range(60, 76, 1))


def get_first_pitch_level(pattern):
    """
    Get a Random Start Pitch According to Level
    """
    return random.choice(map_first_pitch(pattern))


def get_starting_point(time_signature, oracle):
    """
    Get Starting Point According To Selected Time Signature
    """
    tsi = get_index_viewpoint(
        oracle, 'time.timesig', time_signature.ratioString)
    filter = oracle['information']['original_features'][:, tsi]

    if isinstance(filter[0], float):
        filtered_ind = [ind for ind in oracle["indexes"] if filter[ind] == 1.0]
    else:
        filtered_ind = [ind for ind in oracle["indexes"]
                        if np.any(filter[ind] == 1.0)]

    if len(filtered_ind) == 0:
        filtered_ind = oracle["indexes"]

    return random.choice(filtered_ind) + 1


def contine_until_new_bs(oracle, time_signature, offset_i, l_pitch, seq, k):
    """
    Get The Continuation of FS_BEAT
    """
    k += 1
    flag_end_beat = False
    while not flag_end_beat:
        ev_k = event_extract(
            oracle, number=k - 1, timesignature=time_signature, last_pitch=l_pitch, last_event=seq[-1], offset_i=offset_i)
        if ev_k.get_viewpoint('derived.posinbar') % 1 == 0.0:
            flag_end_beat = True
            break
        seq.append(ev_k)
        if not ev_k.is_rest() and ev_k.get_viewpoint('pitch.cpitch'):
            l_pitch = ev_k.get_viewpoint('pitch.cpitch')
        k += 1
    return seq, k, l_pitch


def get_first_event(oracle, time_signature, last_pitch, offset_i, offset_last, k):
    """
    Get First Event
    """
    first_event = event_extract(
        oracle, number=k - 1, timesignature=time_signature, last_pitch=last_pitch, first=True, offset_i=offset_i, offset_last=offset_last)
    if not first_event.is_rest():
        last_pitch = first_event.get_viewpoint('pitch.cpitch')
    return contine_until_new_bs(oracle, time_signature, offset_i, last_pitch, [first_event], k)


def get_ending_note(seq1, seq2, seq3):
    """
    """
    if not isinstance(seq1[-1], str):
        return seq1[-1].get_offset() + seq1[-1].get_viewpoint('duration.length') - \
            seq1[0].get_offset(), seq1[-1]
    elif not isinstance(seq2[-1], str):
        return seq2[-1].get_offset() + seq2[-1].get_viewpoint('duration.length') - \
            seq2[0].get_offset(), seq2[-1]
    return seq3[-1].get_offset() + seq3[-1].get_viewpoint('duration.length') - \
        seq3[0].get_offset(), seq3[-1]


def bisection(array, value):
    '''Given an ``array`` , and given a ``value`` , returns an index j such that ``value`` is between array[j]
    and array[j+1]. ``array`` must be monotonic increasing. j=-1 or j=len(array) is returned
    to indicate that ``value`` is out of range below and above respectively.'''
    n = len(array)
    if (value < array[0]):
        return -1
    elif (value > array[n-1]):
        return n
    jl = 0  # Initialize lower
    ju = n-1  # and upper limits.
    while (ju-jl > 1):  # If we are not yet done,
        jm = (ju+jl) >> 1  # compute a midpoint with a bitshift
        if (value >= array[jm]):
            jl = jm  # and replace either the lower limit
        else:
            ju = jm  # or the upper limit, as appropriate.
        # Repeat until the test condition is satisfied.
    if (value == array[0]):  # edge cases at bottom
        return 0
    elif (value == array[n-1]):  # and top
        return n-1
    else:
        return jl


def get_next_end_bound_ind(oracle, indexes):
    """
    Get Next Ending Point for an Array of Starting Points
    """
    bound_ind = get_index_viewpoint(oracle, 'phrase.boundary')
    ends = np.where(oracle['information']
                    ['original_features'][:, bound_ind] == -1.0)[0]
    return [ends[bisection(ends, ind)+1] for ind in indexes]


def get_phrase_interval_beat(oracle, st, end):
    """
    Get intervals for whole Phrase
    """
    int_ind = get_index_viewpoint(oracle, 'derived.seq_int')
    beat_ind = get_index_viewpoint(oracle, 'derived.beat_strength')
    return oracle['information']['original_features'][st:end+1, int_ind], oracle['information']['original_features'][st:end+1, beat_ind]


def counter_cosine_similarity(c1, c2):
    terms = set(c1).union(c2)
    dotprod = sum(c1.get(k, 0) * c2.get(k, 0) for k in terms)
    magA = math.sqrt(sum(c1.get(k, 0)**2 for k in terms))
    magB = math.sqrt(sum(c2.get(k, 0)**2 for k in terms))
    if magA == 0 or magB == 0 or dotprod == 0:
        return 0
    return dotprod / (magA * magB)


def length_similarity(c1, c2):
    lenc1 = sum(c1.values())
    lenc2 = sum(c2.values())
    return min(lenc1, lenc2) / float(max(lenc1, lenc2))


def similarity_score(l1, l2):
    c1, c2 = Counter(l1), Counter(l2)
    return length_similarity(c1, c2) * counter_cosine_similarity(c1, c2)


def show_phrase_alts(key, alternatives):
    """
    Auxiliar Function To SHOW alternatives as parts of score
    """
    new_score = music21.stream.Score()

    for name, score in alternatives.items():
        score.partAbbreviation = name
        if score not in new_score.parts:
            new_score.insert(0, score)

    new_score.insert(0, music21.metadata.Metadata())
    new_score.metadata.title = 'PHRASE ' + str(key)
    new_score.metadata.composer = ''

    new_score.show()
