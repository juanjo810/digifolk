import random
import itertools
import copy

from numpy.lib.arraysetops import _isin_dispatcher, isin

import app.composition as oracle_constr
import app.composition.generation.generation.VMO as gen
import app.composition.representation.parsers.segmentation as segm
import app.composition.melodyGameAux as auxiliar
import music21


def fb(ev_k):
    """
    """
    return ev_k.get_viewpoint('derived.posinbar') % 1 == 0.0 or ev_k.get_viewpoint('derived.beat_strength') == 1.0


def segmenting(seq1, optimal_length):
    """
    """
    segm.segmentation(seq1, method='Grouper',
                      step_segmentation=True, optimal_length=optimal_length)
    bounds = [ev.get_viewpoint('phrase.boundary')
              for ev in seq1 if not isinstance(ev, str)]
    end_bounds = [i for i, b in enumerate(bounds) if b == -1.0]

    for i in end_bounds:
        if i > (optimal_length / 2.0):
            return True, i + 1
        if i == len(end_bounds) - 1 and len(bounds) > (2 * optimal_length):
            return True, None
    return False, None


def direct_forward(poss_ks, oracle, time_signature, l_pitch, last_event, offset_i):
    """
    """
    k = poss_ks['direct-forward']
    ev_k = auxiliar.event_extract(
        oracle, number=k - 1, timesignature=time_signature, last_pitch=l_pitch, last_event=last_event, offset_i=offset_i)
    return [k], [ev_k]


def gen_first_part_of_beat(k, trn, sfx, rsfx, lrs, oracle, time_signature, l_pitch, last_event, offset_i, pattern_level=1, num_alternatives=3, max_lrs=True):
    """
    """
    poss_ks = gen.all_possible_ks(k, trn, sfx, rsfx, lrs)

    if len(poss_ks['backward']) == 0:
        if num_alternatives == 1:
            return direct_forward(poss_ks, oracle, time_signature, l_pitch, last_event, offset_i)
        else:
            filter_max_lrs, events, filter_level = filter_possibilities(
                oracle, time_signature, l_pitch, last_event, offset_i, pattern_level, poss_ks, type='forward')
            filter_level = filter_next_evs(oracle, time_signature, l_pitch,
                                           offset_i, filter_max_lrs, events, filter_level)
            final_ks = random.sample(filter_level, num_alternatives if len(
                filter_level) >= num_alternatives else len(filter_level))
            return [f + 1 for f in final_ks], [events[filter_max_lrs.index(ks)] for ks in final_ks]
    else:
        filter_max_lrs, events, filter_level = filter_possibilities(
            oracle, time_signature, l_pitch, last_event, offset_i, pattern_level, poss_ks)
        filter_level = filter_next_evs(oracle, time_signature, l_pitch,
                                       offset_i, filter_max_lrs, events, filter_level)

        if len(filter_level) == 0 or filter_level == [0]:
            filter_max_lrs, events, filter_level = filter_possibilities(
                oracle, time_signature, l_pitch, last_event, offset_i, pattern_level, poss_ks, type='forward')
            filter_level = filter_next_evs(oracle, time_signature, l_pitch,
                                           offset_i, filter_max_lrs, events, filter_level)
            if len(filter_level) == 0 or filter_level == [0]:
                return direct_forward(poss_ks, oracle, time_signature, l_pitch, last_event, offset_i)

            final_ks = random.sample(filter_level, num_alternatives if len(
                filter_level) >= num_alternatives else len(filter_level))
        else:
            lrs_bc = [poss_ks['lrs-backward'][poss_ks['backward'].index(fl)] for fl in filter_level]
            lrs_fl = [x for _, x in sorted(zip(lrs_bc, filter_level), key=lambda pair: pair[0])]
            lrs_fl.reverse()

            if max_lrs:
                final_ks = lrs_fl[0:num_alternatives]
            else:
                final_ks = random.sample(lrs_fl[1:], num_alternatives if len(
                    filter_level) >= num_alternatives else len(filter_level))

        return [f + 1 for f in final_ks], [events[filter_max_lrs.index(ks)] for ks in final_ks]

def new_cycled_poss(oracle, time_signature, l_pitch, last_event, offset_i, pattern_level, num_alternatives, poss_ks, type='forward'):
    """
    """
    i = 0
    ks = []
    fevs = []
    alread = []
    while i < num_alternatives:
        pk = random.choice(poss_ks[type])
        if not pk in alread:
            ev = auxiliar.event_extract(
                oracle, number=pk-1, timesignature=time_signature, last_pitch=l_pitch, last_event=last_event, offset_i=offset_i)
            if auxiliar.level_pc(ev.get_viewpoint('pitch.cpitch'), pattern_level):
                if check_next_evs(oracle, time_signature, offset_i,
                                  ev, poss=pk, lp=l_pitch):
                    ks.append(pk)
                    fevs.append(ev)
                    i += 1
        alread.append(pk)
    return ks, fevs


def filter_next_evs(oracle, time_signature, l_pitch, offset_i, filter_max_lrs, events, filter_level, window=3):
    """
    Filter Options that have a strong beat in the next few events
    """
    filter_2 = []
    for poss in filter_level:
        ev = events[filter_max_lrs.index(poss)]
        check_next_evs(oracle, time_signature, offset_i,
                       ev, window, filter_2, poss, l_pitch)
    return filter_2


def check_next_evs(oracle, time_signature, offset_i, ev, window=3, filter_2=[], poss=0, lp=65):
    if not ev.is_rest() and ev.get_viewpoint('pitch.cpitch'):
        lp = ev.get_viewpoint('pitch.cpitch')
    for i in range(1, window):
        if poss + i - 1 >= len(oracle["information"]["selected_original"]):
            filter_2.append(poss)
            return True
        ne = auxiliar.event_extract(
            oracle, number=poss + i - 1, timesignature=time_signature, last_pitch=lp, last_event=ev, offset_i=offset_i)
        if fb(ne):
            filter_2.append(poss)
            return True
        ev = ne
        if not ev.is_rest() and ev.get_viewpoint('pitch.cpitch'):
            lp = ev.get_viewpoint('pitch.cpitch')


def filter_possibilities(oracle, time_signature, l_pitch, last_event, offset_i, pattern_level, poss_ks, type="backward"):
    """
    FILTER POSSIBILITIES
    """
    events = [auxiliar.event_extract(
        oracle, number=ev-1, timesignature=time_signature, last_pitch=l_pitch, last_event=last_event, offset_i=offset_i) for ev in poss_ks[type]]
    pitch_events = [ev.get_viewpoint('pitch.cpitch') for ev in events]
    seq_pc = {pc: [poss_ks[type][i] for i, val in enumerate(
        pitch_events) if val == pc] for pc in sorted(set(pitch_events), key=lambda x: (x is None, x)) if auxiliar.level_pc(pc, pattern_level)}
    spc = list(itertools.chain.from_iterable([*seq_pc.values()]))
    return poss_ks[type], events, spc


def gen_a_beat(k, trn, sfx, rsfx, lrs, oracle, time_signature, l_pitch, last_event, offset_i, pattern_level=3, num_alternatives=3):
    """
    Generate a Beat
    """
    ks = {}
    events = {}

    first_beat_ks, first_beat_evs = gen_first_part_of_beat(
        k, trn, sfx, rsfx, lrs, oracle, time_signature, l_pitch, last_event, offset_i, pattern_level, num_alternatives)

    for i, kb in enumerate(first_beat_ks):
        alt_name = 'alt_{}'.format(str(i + 1))
        ks[alt_name] = [kb]

        new_event = first_beat_evs[i]
        events[alt_name] = [new_event]

        if not new_event.is_rest() and new_event.get_viewpoint('pitch.cpitch'):
            l_pitch = new_event.get_viewpoint('pitch.cpitch')

        s_kb = kb + 1
        flag_end_beat = False
        while not flag_end_beat:
            ev_k = auxiliar.event_extract(
                oracle, number=s_kb - 1, timesignature=time_signature, last_pitch=l_pitch, last_event=events[alt_name][-1], offset_i=offset_i)

            if fb(ev_k):
                flag_end_beat = True
                break

            ks[alt_name].append(s_kb)
            events[alt_name].append(ev_k)

            if not ev_k.is_rest() and new_event.get_viewpoint('pitch.cpitch'):
                l_pitch = new_event.get_viewpoint('pitch.cpitch')

            s_kb += 1

    alt_durations = {alt: sum(
        [ev.get_viewpoint('duration.length') for ev in evs]) for alt, evs in events.items()}
    max_duration = max(list(alt_durations.values()))
    print(max_duration)
    for alt, dur in alt_durations.items():
        if dur < max_duration:
            events[alt].append(
                'N_' + str(max_duration-dur)
            )
    return ks, events


def generate_by_beat(path, pattern, st_point=None, last_pitch=None, timesignature='4/4', keysignature=0, offset_last=None):
    '''
    # NEXT TASK:
    # * DO NOW A BEAT PER BEAT GENERATION
    # * INSIDE BEAT DO DIRECT FORWARD CONNECTIONS
    # * ON BEAT STRENGTH CAN DO JUMPS
    '''
    time_signature = music21.meter.TimeSignature(timesignature)
    key_signature = music21.key.KeySignature(sharps=keysignature)

    oracle = oracle_constr.load_model_oracle(path)

    offset_i = auxiliar.get_index_viewpoint(oracle, 'offset')

    trn = oracle['oracle'].basic_attributes["trn"][:]
    sfx = oracle['oracle'].basic_attributes["sfx"][:]
    lrs = oracle['oracle'].basic_attributes["lrs"][:]
    rsfx = oracle['oracle'].basic_attributes["rsfx"][:]

    if not st_point and not last_pitch:
        last_pitch = auxiliar.get_first_pitch_level(pattern)
        st_point = auxiliar.get_starting_point(time_signature, oracle)

    k = st_point
    events, k, l_pitch = auxiliar.get_first_event(
        oracle, time_signature, last_pitch, offset_i, offset_last, k)

    seq1 = copy.deepcopy(events)
    seq2 = copy.deepcopy(events)
    seq3 = copy.deepcopy(events)

    last_note_end = seq1[-1].get_offset() + \
        seq1[-1].get_viewpoint('duration.length') - seq1[0].get_offset()
    old_last_note_end = last_note_end

    tempo = 1

    chosen_beat = [2, 4]
    i = 2
    end_phrase = False
    optimal_length = 8 * 2
    last_event = seq1[-1]
    while not end_phrase:
        n = 3 if i in chosen_beat else 1
        poss_k_1, k_ev_1 = gen_a_beat(k, trn, sfx, rsfx, lrs, oracle,
                                      time_signature, l_pitch, last_event, offset_i, pattern_level=pattern[tempo], num_alternatives=n)

        for alt in poss_k_1:
            if alt == 'alt_1':
                seq1.extend(k_ev_1[alt])
            if alt == 'alt_2':
                seq2.extend(k_ev_1[alt])
            if alt == 'alt_3':
                seq3.extend(k_ev_1[alt])

        if 'alt_2' not in poss_k_1:
            seq2.extend(k_ev_1['alt_1'])
        if 'alt_3' not in poss_k_1:
            seq3.extend(k_ev_1['alt_1'])

        k = poss_k_1['alt_1'][-1]

        old_last_note_end = last_note_end
        last_note_end, last_event = auxiliar.get_ending_note(seq1, seq2, seq3)

        if not isinstance(k_ev_1['alt_1'][-1], str) and not k_ev_1['alt_1'][-1].is_rest() and k_ev_1['alt_1'][-1].get_viewpoint('pitch.cpitch'):
            l_pitch = k_ev_1['alt_1'][-1].get_viewpoint('pitch.cpitch')

        end_phrase, last_i = segmenting(seq1, optimal_length)
        print(last_i)
        if tempo < len(pattern) - 1:
            tempo += 1
        if last_note_end < old_last_note_end:
            break
        i += 1

    new_score1 = auxiliar.extract_score(
        last_pitch, time_signature, key_signature, seq1)
    new_score2 = auxiliar.extract_score(
        last_pitch, time_signature, key_signature, seq2)
    new_score3 = auxiliar.extract_score(
        last_pitch, time_signature, key_signature, seq3)

    return {'alt_1': new_score1, 'alt_2': new_score2, 'alt_3': new_score3}, k + 1


def generate_by_beat_original(path, pattern, st_point=None, last_pitch=None, timesignature='4/4', keysignature=0, offset_last=None):
    """
    Generate alternatives for a start phrase
    """
    time_signature = music21.meter.TimeSignature(timesignature)
    key_signature = music21.key.KeySignature(sharps=keysignature)

    oracle = oracle_constr.load_model_oracle(path)

    offset_i = auxiliar.get_index_viewpoint(oracle, 'offset')

    trn = oracle['oracle'].basic_attributes["trn"][:]
    sfx = oracle['oracle'].basic_attributes["sfx"][:]
    lrs = oracle['oracle'].basic_attributes["lrs"][:]
    rsfx = oracle['oracle'].basic_attributes["rsfx"][:]

    if not st_point and not last_pitch:
        last_pitch = auxiliar.get_first_pitch_level(pattern)
        st_point = auxiliar.get_starting_point(time_signature, oracle)

    k = st_point
    events, k, l_pitch = auxiliar.get_first_event(
        oracle, time_signature, last_pitch, offset_i, offset_last, k)

    seq1 = copy.deepcopy(events)
    seq2 = copy.deepcopy(events)
    seq3 = copy.deepcopy(events)

    last_event = seq1[-1]
    end_phrase = False
    i = 0
    while not end_phrase:
        k += 1
        ev = auxiliar.event_extract(
            oracle, number=k-1, timesignature=time_signature, last_pitch=l_pitch, last_event=last_event, offset_i=offset_i)

        if not ev.is_rest() and ev.get_viewpoint('pitch.cpitch'):
            l_pitch = ev.get_viewpoint('pitch.cpitch')

        seq1.append(ev)
        seq2.append(ev)
        seq3.append(ev)

        print(ev.get_viewpoint('phrase.boundary'))
        if ev.get_viewpoint('phrase.boundary') == -1.0:
            end_phrase = True
        i += 1

    new_score1 = auxiliar.extract_score(
        last_pitch, time_signature, key_signature, seq1, onset=seq1[0].offset_time)
    new_score2 = auxiliar.extract_score(
        last_pitch, time_signature, key_signature, seq2, onset=seq1[0].offset_time)
    new_score3 = auxiliar.extract_score(
        last_pitch, time_signature, key_signature, seq3, onset=seq1[0].offset_time)

    return {'alt_1': new_score1, 'alt_2': new_score2, 'alt_3': new_score3}, k + 1