import random
import itertools
import copy

import numpy as np

import app.composition as oracle_constr
import app.composition.generation.generation.VMO as gen
import app.composition.generation.plot_fo as plot
import app.composition.representation.parsers.segmentation as segm
import app.composition.melodyGameAux as auxiliar
import app.composition.melodyGame as melodyGame
import app.api.routes.utils as utils

import music21


def print_oracle(oracle):
    image = plot.start_draw(oracle["oracle"], size=(900*40, 600*4))
    image.show(title='Portuguese Oracle')

def get_key_map(oracle, st_points, rt_key, interval):
    song_i = auxiliar.get_index_viewpoint(oracle, 'song')
    song = auxiliar.filter_index_viewpoints(oracle, song_i, st_points[0])[0].split('=')[1]

    music21_song = utils.retrieve_score(song)
    music21_song = music21_song.transpose(interval)

    song_histo = music21.analysis.pitchAnalysis.pitchAttributeCount(music21_song.flat.notes, 'pitchClass')
    scale_histo = [p.pitchClass for p in rt_key.pitches]

    more_pitches = []
    for k, count in song_histo.items():

        if k not in scale_histo:
            neighbor_count = count # Take into account the number of times it appears related to consecutive neighbors
            if k-1 in song_histo:
                neighbor_count += song_histo[k-1]
            if k+1 in song_histo:
                neighbor_count += song_histo[k+1]

            more_pitches.append((k, count/neighbor_count))

    return more_pitches


def query_points(oracle_path, time_signature, curves):
    """
    Generation Near to Original
    """
    oracle = oracle_constr.load_model_oracle(oracle_path)

    # Get Time Signature and Possible Starting and respective Ending Phrase Points
    ts, st_points = auxiliar.get_real_timesignatures_prob(
        time_signature, oracle)
    end_points = auxiliar.get_next_end_bound_ind(oracle, st_points)

    fp = auxiliar.map_first_pitch(curves['1'])
    choice = get_possible_start(curves, oracle, st_points, end_points, fp)

    rt_key, interval = auxiliar.get_key_for_song(oracle, st_points, choice)

    time_signature = music21.meter.TimeSignature(ts)
    key_signature = music21.key.KeySignature(sharps=0)

    more_pitches = get_key_map(oracle, st_points, rt_key, interval)

    offset_i = auxiliar.get_index_viewpoint(oracle, 'offset')
    last_pitch, events, list_ks, new_score1 = get_first_original_score(
        time_signature, oracle, st_points, end_points, choice, key_signature, offset_i)

    new_score2, new_score3 = get_second_and_third_alternatives(
        time_signature, oracle, key_signature, offset_i, last_pitch, events, list_ks, new_score1)

    auxiliar.correct_stream_scale(new_score2, rt_key, more_pitches, direction='ascending')
    auxiliar.correct_stream_scale(new_score3, rt_key, more_pitches, direction='descending')

    # auxiliar.show_phrase_alts(0, {'alt_1': new_score1, 'alt_2': new_score2, 'alt_3': new_score3})

    return {'alt_1': new_score1, 'alt_2': new_score2, 'alt_3': new_score3}, list_ks[-1], time_signature, rt_key.tonic.name, rt_key.mode, more_pitches


def query_points_cont_L(oracle_path, ts, curves, end_point, last_pitch, alt='2'):
    """
    Generate Continuations
    """
    oracle = oracle_constr.load_model_oracle(oracle_path)
    time_signature = music21.meter.TimeSignature(ts)
    key_signature = music21.key.KeySignature(sharps=0)

    offset_i = auxiliar.get_index_viewpoint(oracle, 'offset')
    end_points = auxiliar.get_next_end_bound_ind(oracle, [end_point])
    last_pitch, events, list_ks, new_score1 = get_first_original_score(
        time_signature, oracle, [end_point], end_points, [0, last_pitch], key_signature, offset_i)

    new_score2, new_score3 = get_second_and_third_alternatives(
        time_signature, oracle, key_signature, offset_i, last_pitch, events, list_ks, new_score1)

    return {'alt_1': new_score1, 'alt_2': new_score2, 'alt_3': new_score3}, list_ks[-1], time_signature


def query_points_cont(oracle_path, ts, curves, end_point, last_pitch, alt='2', key='C', mode='major', more_pitches=[]):
    """
    Generate Continuations
    """
    oracle = oracle_constr.load_model_oracle(oracle_path)
    time_signature = music21.meter.TimeSignature(ts)
    key_signature = music21.key.KeySignature(sharps=0)

    rt_key = music21.key.Key(key, mode.lower())

    offset_i = auxiliar.get_index_viewpoint(oracle, 'offset')
    last_pitch, events, list_ks, new_score1 = gen_non_original_score(
        time_signature, oracle, [end_point], [0, last_pitch], key_signature, offset_i, curves[alt])

    auxiliar.correct_stream_scale(new_score1, rt_key, more_pitches=more_pitches)
    last_pitch = new_score1.flat.notes[-1].pitch.ps

    new_score2, new_score3 = get_second_and_third_alternatives(
        time_signature, oracle, key_signature, offset_i, last_pitch, events, list_ks, new_score1)

    auxiliar.correct_stream_scale(new_score2, rt_key, more_pitches, direction='ascending')
    auxiliar.correct_stream_scale(new_score3, rt_key, more_pitches, direction='descending')

    return {'alt_1': new_score1, 'alt_2': new_score2, 'alt_3': new_score3}, list_ks[-1], time_signature


def get_first_original_score(time_signature, oracle, st_points, end_points, choice, key_signature, offset_i):
    last_pitch = choice[1]

    k = st_points[choice[0]]
    ev = auxiliar.event_extract(oracle, k, time_signature,
                                last_pitch=choice[1], first=True, offset_i=offset_i)
    if not ev.is_rest():
        last_pitch = ev.get_viewpoint('pitch.cpitch')

    events = [ev]
    list_ks = range(k, end_points[choice[0]]+1)

    for i in list_ks[1:]:
        nev = auxiliar.event_extract(oracle, i, time_signature,
                                     last_event=events[-1], last_pitch=last_pitch, offset_i=offset_i)
        events.append(nev)

    new_score1 = auxiliar.extract_score(
        last_pitch, time_signature, key_signature, events)

    return last_pitch, events, list_ks, new_score1


def gen_non_original_score(time_signature, oracle, st_points, choice, key_signature, offset_i, pattern):
    last_pitch = choice[1]
    l_pitch = last_pitch

    k = st_points[choice[0]]
    ev = auxiliar.event_extract(oracle, k+1, time_signature,
                                last_pitch=choice[1], first=True, offset_i=offset_i)

    if ev.get_viewpoint('duration.length') % time_signature.beatDuration.quarterLength != 0.0:
        events, k1, last_pitch = auxiliar.get_first_event(
            oracle, time_signature, l_pitch, offset_i, None, k+1)
        list_ks = [k, k1]
        k = k1
    else:
        events = [ev]
        list_ks = [k]
        if not ev.is_rest():
            last_pitch = ev.get_viewpoint('pitch.cpitch')

    trn = oracle['oracle'].basic_attributes["trn"][:]
    sfx = oracle['oracle'].basic_attributes["sfx"][:]
    lrs = oracle['oracle'].basic_attributes["lrs"][:]
    rsfx = oracle['oracle'].basic_attributes["rsfx"][:]

    i = 0
    tempo = 1
    optimal_length = 10
    end_phrase = False
    while not end_phrase:
        poss_k_1, k_ev_1 = melodyGame.gen_a_beat(k, trn, sfx, rsfx, lrs, oracle,
                                                 time_signature, last_pitch, events[-1], offset_i, pattern_level=pattern[tempo], num_alternatives=1)
        events.extend(k_ev_1['alt_1'])
        k = poss_k_1['alt_1'][-1]
        list_ks.extend(poss_k_1['alt_1'])

        if k_ev_1['alt_1'][-1] and not isinstance(k_ev_1['alt_1'][-1], str) and not k_ev_1['alt_1'][-1].is_rest() and k_ev_1['alt_1'][-1].get_viewpoint('pitch.cpitch'):
            last_pitch = k_ev_1['alt_1'][-1].get_viewpoint('pitch.cpitch')

        end_phrase, last_i = melodyGame.segmenting(events, optimal_length)
        if last_i:
            events = events[:last_i]
            list_ks = list_ks[:last_i]
        if tempo < len(pattern) - 1:
            tempo += 1
        i += 1

    if not events[-1].is_rest():
        last_pitch = events[-1].get_viewpoint('pitch.cpitch')

    new_score1 = auxiliar.extract_score(
        l_pitch, time_signature, key_signature, events)

    return last_pitch, events, list_ks, new_score1


def get_possible_start(curves, oracle, st_points, end_points, fp):
    possibilities = []

    for i, st in enumerate(st_points):
        ints, beats = auxiliar.get_phrase_interval_beat(
            oracle, st, end_points[i])
        cum_ints = np.cumsum(ints)

        for pc in fp:
            pcs = cum_ints + pc
            b_pcs = [pcs[i]
                     for i, b in enumerate(beats) if b == 1.0 or b == 0.5]
            levels = [auxiliar.level_of_pitch(px) for px in b_pcs]
            sim = auxiliar.similarity_score(curves['1'], levels)
            possibilities.append((i, pc, sim))

    possibilities = sorted(possibilities, key=lambda x: x[2], reverse=True)
    return possibilities[0]


def get_second_and_third_alternatives(time_signature, oracle, key_signature, offset_i, last_pitch, events, list_ks, new_score1):
    """
    """
    beats = [
        n.beat for n in new_score1.flat.notesAndRests if not n.tie or n.tie.type == 'start']
    whole_beats = [i for i, b in enumerate(beats) if float(b).is_integer()]

    if len(whole_beats) < 3:
        to_rem = random.sample(whole_beats, k=len(whole_beats))
    else:
        to_rem = random.sample(whole_beats, k=3)

    events2 = copy.deepcopy(events)
    list_ks2 = copy.deepcopy(list(list_ks))

    events3 = copy.deepcopy(events)
    list_ks3 = copy.deepcopy(list(list_ks))

    changed_2 = []
    changed_3 = []

    for z, ind in enumerate(sorted(to_rem)):
        # get index of last event for substituting
        end, beat_duration = get_ending_note(beats, events, whole_beats, ind)

        start_alts = [list_ks[ind]]

        # generate 2 alternative beats
        alternative_gen(time_signature, oracle, offset_i, events,
                        list_ks, events2, list_ks2, changed_2, ind, end, reachable_dur=beat_duration, start_alts=start_alts)

        last_changed_2 = changed_2[z].split('-')
        start_alts.append(list_ks2[int(last_changed_2[0])])

        alternative_gen(time_signature, oracle, offset_i, events,
                        list_ks, events3, list_ks3, changed_3, ind, end, reachable_dur=beat_duration, start_alts=start_alts)

        last_changed_3 = changed_3[z].split('-')
        start_alts.append(list_ks3[int(last_changed_3[0])])

        print(start_alts)

        # force same position in bar as first sequence
        if ind == 0:
            events2[0].add_viewpoint(
                'derived.posinbar', events[0].get_viewpoint('derived.posinbar'))
            events3[0].add_viewpoint(
                'derived.posinbar', events[0].get_viewpoint('derived.posinbar'))

    new_score2 = auxiliar.extract_score(
        last_pitch, time_signature, key_signature, events2)
    new_score3 = auxiliar.extract_score(
        last_pitch, time_signature, key_signature, events3)

    print('changed 2: {}'.format(changed_2))
    print('changed 3: {}'.format(changed_3))
    return new_score2, new_score3


def get_ending_note(beats, events, whole_beats, ind):
    """
    """
    ind_end = whole_beats.index(ind)+1
    end = len(beats)
    if ind_end < len(whole_beats):
        end = whole_beats[ind_end]
    beat_duration = sum(ev.get_viewpoint('duration.length')
                        for ev in events[ind:end])
    if end == len(beats):
        end = 'END'
    return end, beat_duration


def alternative_gen(time_signature, oracle, offset_i, events, list_ks, events2, list_ks2, changed_2, ind, end, reachable_dur=None, start_alts=None):
    """
    """
    l_pitch = None
    if ind != 0 and not events[ind].get_viewpoint('pitch.cpitch'):
        l_pitch = events[ind-1].get_viewpoint('pitch.cpitch')

    evs2, ks2, type = gen_beat_for_k(
        oracle, list_ks[ind], events[ind], last_pitch=l_pitch, offset_i=offset_i, time_signature=time_signature, reachable_dur=reachable_dur, first=ind == 0, start_alts=start_alts)

    ind2 = ind
    end2 = end

    ind2 += len(list_ks2)-len(list_ks)
    if end2 == 'END':
        events2[ind2:] = evs2
        list_ks2[ind2:] = ks2
    else:
        end2 += len(list_ks2)-len(list_ks)
        events2[ind2:end2] = evs2
        list_ks2[ind2:end2] = ks2

    changed_2.append('{}-{}-{}'.format(ind2, end2, type))


def gen_beat_for_k(oracle, k, ev_k, last_pitch=None, offset_i=0, time_signature=None, reachable_dur=None, first=False, t_rand=True, start_alts=None):

    trn = oracle['oracle'].basic_attributes["trn"][:]
    sfx = oracle['oracle'].basic_attributes["sfx"][:]
    lrs = oracle['oracle'].basic_attributes["lrs"][:]
    rsfx = oracle['oracle'].basic_attributes["rsfx"][:]

    if ev_k.get_viewpoint('pitch.cpitch'):
        last_pitch = ev_k.get_viewpoint('pitch.cpitch')
    pt = auxiliar.level_of_pitch(last_pitch)

    all_poss_ks = gen.all_possible_ks(k, trn, sfx, rsfx, lrs)

    type = 'backward'
    if t_rand:
        posss = all_poss_ks['backward']
        if start_alts:
            _ = [posss.remove(alt) for alt in start_alts if alt in posss]
        if len(posss) > 0:
            poss_k = random.choice(posss)
        else:
            posss = all_poss_ks['forward']
            if start_alts:
                _ = [posss.remove(alt) for alt in start_alts if alt in posss]
            if len(posss) > 0:
                poss_k = random.choice(posss)
                type = 'forward'
            else:
                poss_k = all_poss_ks['direct-forward']
                type = 'direct-forward'

        ev = auxiliar.event_extract(
            oracle, number=poss_k - 1, timesignature=time_signature, last_pitch=last_pitch, last_event=ev_k, offset_i=offset_i, first=first)
    else:
        poss_ks, evs = melodyGame.gen_first_part_of_beat(
            k, trn, sfx, rsfx, lrs, oracle, time_signature, last_pitch, ev_k, offset_i, pattern_level=pt, num_alternatives=1, max_lrs=False)
        poss_k = poss_ks[0]
        ev = evs[0]

    events = [ev]
    ks = [poss_k]

    l_pitch = ev_k.get_viewpoint('pitch.cpitch')
    if ev.get_viewpoint('pitch.cpitch'):
        l_pitch = ev.get_viewpoint('pitch.cpitch')

    total_duration = ev.get_viewpoint('duration.length')
    while total_duration < reachable_dur:
        nk = ks[-1]
        lev = events[-1]

        if lev.get_viewpoint('pitch.cpitch'):
            l_pitch = lev.get_viewpoint('pitch.cpitch')

        nev = auxiliar.event_extract(
            oracle, number=nk, timesignature=time_signature, last_pitch=l_pitch, last_event=lev, offset_i=offset_i)
        ks.append(nk+1)
        events.append(nev)
        total_duration += nev.get_viewpoint('duration.length')

    if total_duration > reachable_dur:
        last_dur = events[-1].get_viewpoint('duration.length')
        rest = total_duration - reachable_dur
        events[-1].add_viewpoint('duration.length', last_dur - rest)

    return events, ks, type
