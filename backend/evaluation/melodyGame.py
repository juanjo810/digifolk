from hashlib import new
import itertools
import logging
import random
from os import name
from typing_extensions import final

import app.composition as oracle_constr
import app.composition.generation.generation.VMO as gen
import music21
import numpy as np
from app.composition.representation.conversor.score_conversor import \
    parse_single_line
from app.composition.representation.events.linear_event import PartEvent


def get_real_timesignature(ts):

    if ts == 1:
        return ''
    if ts == 2:
        return '2/4'
    if ts == 3:
        return '3/4'
    if ts == 4:
        return '4/4'
    if ts == 6:
        return '6/8'


def curve_from_points(points):
    points.sort()

    phrases = {}

    for p in points:
        phrase = p[5]
        if phrase not in phrases:
            phrases[phrase] = []
        phrases[phrase].append(int(p[-1]))

    return phrases


def get_index_viewpoint(oracle, viewpoint, extra=''):

    if viewpoint in oracle['information']['original_features_names']:
        return oracle['information']['original_features_names'].index(viewpoint)

    for i, name in enumerate(oracle['information']['original_features_names']):
        if viewpoint in name:
            if '=' in name and extra in name:
                return i


def get_beat_strength(event, timesignature):

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


def event_extract(oracle_info, number, timesignature, last_event=None, last_pitch=65, first=False, offset_i=0):
    event = PartEvent(
        from_list=oracle_info["information"]["selected_original"][number],
        features=oracle_info["information"]["selected_features_names"],
    )

    if first:
        event.add_viewpoint('basic.bioi', 0.0)
        event.add_viewpoint('pitch.cpitch', last_pitch)
        event.add_viewpoint('derived.seq_int', 0.0)

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


def get_logger():
    import datetime
    t = datetime.datetime.now()
    rt = t.strftime("%y-%m-%d--%H-%M-%S")

    logFormatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.DEBUG)
    fileHandler = logging.FileHandler(
        "{0}/{1}.log".format(r'D:\Projects\COPOEM\coPoem\Backend\logs', 'gen-{}'.format(rt)))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    return rootLogger


# def othercode():
#     next_poss_k = [(pk, gen.all_possible_ks(pk, trn, sfx, rsfx, lrs)) for pk in random.sample(filter_max_lrs, 10)]
#     filt_ks_1 = [(pk, pks['backward']) for (pk, pks) in next_poss_k if len(pks['backward']) > 0]


#     rootLogger.info(filt_ks_1)

def level_pc(pc, level):
    if pc is None:
        return True
    if level == 1 and 71 < pc < 78:
        return True
    if level == 2 and 64 < pc < 72:
        return True
    if level == 3 and 56 < pc < 65:
        return True
    return False


def cont_generation(k, trn, sfx, rsfx, lrs, oracle, time_signature, l_pitch, last_event, offset_i, max_time, rootLogger=None):
    poss_ks = gen.all_possible_ks(k, trn, sfx, rsfx, lrs)

    if len(poss_ks['backward']) == 0:
        k = poss_ks['direct-forward']
        ev_k = event_extract(
            oracle, number=k - 1, timesignature=time_signature, last_pitch=l_pitch, last_event=last_event, offset_i=offset_i)
        return k, ev_k
    else:
        rootLogger.info('MAX TIME: ' + str(max_time))
        best_lrs = max(poss_ks['lrs-backward']) - 1
        ks = [pk for i, pk in enumerate(
            poss_ks['backward']) if poss_ks['lrs-backward'][i] >= best_lrs]

        events = [event_extract(
            oracle, number=ev, timesignature=time_signature, last_pitch=l_pitch, last_event=last_event, offset_i=offset_i) for ev in ks]
        durations_events = [ev.get_viewpoint(
            'duration.length') for ev in events]
        id_de = [i for i, dur in enumerate(
            durations_events) if 0.25 <= dur <= max_time]

        if len(id_de) > 0:
            ki = random.choice(id_de)
            return ks[ki], events[ki]

        k = poss_ks['direct-forward']
        ev_k = event_extract(
            oracle, number=k - 1, timesignature=time_signature, last_pitch=l_pitch, last_event=last_event, offset_i=offset_i)
        return k, ev_k


def tempo_generation(k, trn, sfx, rsfx, lrs, oracle, time_signature, l_pitch, last_event, offset_i, pattern_level=1, rootLogger=None):

    if rootLogger:
        rootLogger.info('GENERATION STEP {}'.format(str(k)))
        rootLogger.info('TIME {}'.format(
            str(time_signature.beatDuration.quarterLength)))

    poss_ks = gen.all_possible_ks(k, trn, sfx, rsfx, lrs)

    if len(poss_ks['backward']) == 0:
        k = poss_ks['direct-forward']
        ev_k = event_extract(
            oracle, number=k - 1, timesignature=time_signature, last_pitch=l_pitch, last_event=last_event, offset_i=offset_i)
        return [k], [ev_k]
    else:
        # Filter BEST LRSs
        best_lrs = max(poss_ks['lrs-backward']) - 1
        filter_max_lrs = [pk for i, pk in enumerate(
            poss_ks['backward']) if poss_ks['lrs-backward'][i] >= best_lrs]

        # GET EVENTS
        events = [event_extract(
            oracle, number=ev, timesignature=time_signature, last_pitch=l_pitch, last_event=last_event, offset_i=offset_i) for ev in filter_max_lrs]

        durations_events = [ev.get_viewpoint(
            'duration.length') for ev in events]
        pitch_events = [ev.get_viewpoint('pitch.cpitch') for ev in events]

        seq_pc = {pc: [filter_max_lrs[i] for i, val in enumerate(
            pitch_events) if val == pc] for pc in sorted(set(pitch_events), key=lambda x: (x is None, x)) if level_pc(pc, pattern_level)}

        real_poss_ks = list(itertools.chain.from_iterable([*seq_pc.values()]))
        real_poss_durs = sorted([(durations_events[filter_max_lrs.index(
            ks)], ks) for ks in real_poss_ks], key=lambda x: x[0])

        dur_dic = {}
        for i, j in real_poss_durs:
            dur_dic.setdefault(i, []).append(j)

        if rootLogger:
            rootLogger.info(real_poss_ks)

        final_ks = random.sample(real_poss_ks, 3 if len(
            real_poss_ks) >= 3 else len(real_poss_ks))
        if len(dur_dic.keys()) > 3:
            one_for_each_ks = []
            for k, v in dur_dic.items():
                if k >= 0.25:
                    one_for_each_ks.append(random.choice(v))
            final_ks = random.sample(one_for_each_ks, 3)

        if rootLogger:
            rootLogger.info(final_ks)

        if len(final_ks) == 0:
            k = poss_ks['direct-forward']
            ev_k = event_extract(
                oracle, number=k - 1, timesignature=time_signature, last_pitch=l_pitch, last_event=last_event, offset_i=offset_i)
            return [k], [ev_k]

        return final_ks, [events[filter_max_lrs.index(ks)] for ks in final_ks]


def generate_from_pattern(path, pattern, st_point=None, last_pitch=None, timesignature='4/4', keysignature=0):

    time_signature = music21.meter.TimeSignature(timesignature)
    key_signature = music21.key.KeySignature(sharps=keysignature)

    oracle = oracle_constr.load_model_oracle(path)
    offset_i = get_index_viewpoint(oracle, 'offset')

    trn = oracle['oracle'].basic_attributes["trn"][:]
    sfx = oracle['oracle'].basic_attributes["sfx"][:]
    lrs = oracle['oracle'].basic_attributes["lrs"][:]
    rsfx = oracle['oracle'].basic_attributes["rsfx"][:]

    if not st_point and not last_pitch:
        last_pitch = random.choice(range(60, 76, 1))

        tsi = get_index_viewpoint(
            oracle, 'time.timesig', time_signature.ratioString)
        filter = oracle['information']['original_features'][:, tsi]
        filtered_ind = [ind for ind in oracle["indexes"] if filter[ind] == 1.0]
        st_point = random.choice(filtered_ind) + 1

    #st_point = 4664
    k = st_point
    s = [k]

    rootLogger = get_logger()

    pbi = get_index_viewpoint(
        oracle, 'derived.posinbar')
    fil = oracle['information']['original_features'][k - 1, pbi]
    rootLogger.info('FPB: ' + str(fil))
    rootLogger.info('FIRST: ' + str(PartEvent(from_list=oracle['information']['original_features']
                                              [k - 1], features=oracle['information']['original_features_names'])))

    first_event = event_extract(
        oracle, number=s[-1] - 1, timesignature=time_signature, last_pitch=last_pitch, first=True, offset_i=offset_i)

    seq1 = [first_event]
    seq2 = [first_event]
    seq3 = [first_event]

    l_pitch = last_pitch
    last_bTS = 0
    last_bTS_pitch = last_pitch

    last_note_end = seq1[-1].get_offset() + \
        seq1[-1].get_viewpoint('duration.length') - seq1[0].get_offset()

    rootLogger.info('START GENERATION')

    # GENERATE
    while last_note_end < time_signature.barDuration.quarterLength:

        last_event = seq1[-1]
        poss_k, k_ev = tempo_generation(k, trn, sfx, rsfx, lrs, oracle,
                                        time_signature, l_pitch, last_event, offset_i, rootLogger=rootLogger)

        if not k_ev[0].is_rest():
            l_pitch = k_ev[0].get_viewpoint('pitch.cpitch')

        if len(poss_k) == 1:
            s.append(poss_k[0])
            seq1.append(k_ev[0])
            seq2.append(k_ev[0])
            seq3.append(k_ev[0])
        else:
            rootLogger.info(str([(ev.get_viewpoint('pitch.cpitch'), ev.get_viewpoint(
                'duration.length')) for ev in k_ev]))
            durs = [ev.get_viewpoint('duration.length') for ev in k_ev]
            dur_max = max(durs)

            if durs[0] < dur_max:
                s.append(poss_k[0])
                seq1.append(k_ev[0])

                dur_max_aux = dur_max - durs[0]
                while dur_max_aux > 0:
                    k1, k1_ev = cont_generation(poss_k[0], trn, sfx, rsfx, lrs, oracle,
                                                time_signature, l_pitch, last_event, offset_i, max_time=dur_max_aux, rootLogger=rootLogger)

                    s.append(k1)
                    seq1.append(k1_ev)
                    dur_max_aux -= k1_ev.get_viewpoint('duration.length')

            else:
                s.append(poss_k[0])
                seq1.append(k_ev[0])

            if durs[1] < dur_max:
                seq2.append(k_ev[1])

                dur_max_aux = dur_max - durs[1]
                while dur_max_aux > 0:
                    _, k1_ev = cont_generation(poss_k[1], trn, sfx, rsfx, lrs, oracle,
                                               time_signature, l_pitch, last_event, offset_i, max_time=dur_max_aux, rootLogger=rootLogger)
                    seq2.append(k1_ev)
                    dur_max_aux -= k1_ev.get_viewpoint('duration.length')
            else:
                seq2.append(k_ev[1])

            if len(durs) > 2:
                if durs[2] < dur_max:
                    seq3.append(k_ev[2])
                    dur_max_aux = dur_max - durs[2]
                    while dur_max_aux > 0:
                        _, k1_ev = cont_generation(poss_k[2], trn, sfx, rsfx, lrs, oracle,
                                                   time_signature, l_pitch, last_event, offset_i, max_time=dur_max_aux, rootLogger=rootLogger)
                        seq3.append(k1_ev)
                        dur_max_aux -= k1_ev.get_viewpoint('duration.length')
                else:
                    seq3.append(k_ev[2])
            else:
                if durs[1] < dur_max:
                    seq3.append(k_ev[1])

                    dur_max_aux = dur_max - durs[1]
                    while dur_max_aux > 0:
                        _, k1_ev = cont_generation(poss_k[1], trn, sfx, rsfx, lrs, oracle,
                                                   time_signature, l_pitch, last_event, offset_i, max_time=dur_max_aux, rootLogger=rootLogger)
                        seq3.append(k1_ev)
                        dur_max_aux -= k1_ev.get_viewpoint('duration.length')
                else:
                    seq3.append(k_ev[1])

        last_note_end = k_ev[0].get_offset() + k_ev[0].get_viewpoint('duration.length') - \
            seq1[0].get_offset()
        k = s[-1]

    new_sequence = seq1
    new_score = parse_single_line(new_sequence, start_pitch=last_pitch,
                                  time_signature=time_signature, key_signature=key_signature,
                                  end_position_last_phrase=None,
                                  show_segmentation=True, contour=True)
    new_score.makeAccidentals(inPlace=True, overrideStatus=True)
    new_score.insert(0.0, music21.clef.TrebleClef())

    new_score2 = parse_single_line(seq2, start_pitch=last_pitch,
                                   time_signature=time_signature, key_signature=key_signature,
                                   end_position_last_phrase=None,
                                   show_segmentation=True, contour=True)
    new_score2.makeAccidentals(inPlace=True, overrideStatus=True)
    new_score2.insert(0.0, music21.clef.TrebleClef())

    new_score3 = parse_single_line(seq3, start_pitch=last_pitch,
                                   time_signature=time_signature, key_signature=key_signature,
                                   end_position_last_phrase=None,
                                   show_segmentation=True, contour=True)
    new_score3.makeAccidentals(inPlace=True, overrideStatus=True)
    new_score3.insert(0.0, music21.clef.TrebleClef())

    # logging.info('Finished')

    new_score.show()
    new_score2.show()
    new_score3.show()

    return new_score, k, l_pitch


def gen_first_beat(k, trn, sfx, rsfx, lrs, oracle, time_signature, l_pitch, last_event, offset_i, pattern_level=1, num_alternatives=3):
    poss_ks = gen.all_possible_ks(k, trn, sfx, rsfx, lrs)

    if len(poss_ks['backward']) == 0:
        k = poss_ks['direct-forward']
        ev_k = event_extract(
            oracle, number=k - 1, timesignature=time_signature, last_pitch=l_pitch, last_event=last_event, offset_i=offset_i)
        return [k], [ev_k]
    else:
        best_lrs = max(poss_ks['lrs-backward']) - 1
        filter_max_lrs = [pk for i, pk in enumerate(
            poss_ks['backward']) if poss_ks['lrs-backward'][i] >= best_lrs]
        # GET EVENTS
        events = [event_extract(
            oracle, number=ev, timesignature=time_signature, last_pitch=l_pitch, last_event=last_event, offset_i=offset_i) for ev in filter_max_lrs]
        pitch_events = [ev.get_viewpoint('pitch.cpitch') for ev in events]
        seq_pc = {pc: [filter_max_lrs[i] for i, val in enumerate(
            pitch_events) if val == pc] for pc in sorted(set(pitch_events), key=lambda x: (x is None, x)) if level_pc(pc, pattern_level)}
        filter_level = list(itertools.chain.from_iterable([*seq_pc.values()]))

        if len(filter_level) == 0:
            k = poss_ks['direct-forward']
            ev_k = event_extract(
                oracle, number=k - 1, timesignature=time_signature, last_pitch=l_pitch, last_event=last_event, offset_i=offset_i)
            return [k], [ev_k]

        final_ks = random.sample(filter_level, num_alternatives if len(
            filter_level) >= num_alternatives else len(filter_level))
        return [f+1 for f in final_ks], [events[filter_max_lrs.index(ks)] for ks in final_ks]


def gen_a_beat(k, trn, sfx, rsfx, lrs, oracle, time_signature, l_pitch, last_event, offset_i, pattern_level=3, num_alternatives=3, rootLogger=None):

    if rootLogger:
        rootLogger.info('GENERATION STEP {}'.format(str(k)))
        rootLogger.info('TIME TO GEN {}'.format(
            str(time_signature.beatDuration.quarterLength)))

    ks = {}
    events = {}

    first_beat_ks, first_beat_evs = gen_first_beat(
        k, trn, sfx, rsfx, lrs, oracle, time_signature, l_pitch, last_event, offset_i, pattern_level, num_alternatives)

    for i, kb in enumerate(first_beat_ks):
        alt_name = 'alt_{}'.format(str(i + 1))
        ks[alt_name] = [kb]

        new_event = first_beat_evs[i]
        events[alt_name] = [new_event]

        if not new_event.is_rest():
            l_pitch = new_event.get_viewpoint('pitch.cpitch')

        s_kb = kb + 1
        flag_end_beat = False
        while not flag_end_beat:
            ev_k = event_extract(
                oracle, number=s_kb - 1, timesignature=time_signature, last_pitch=l_pitch, last_event=events[alt_name][-1], offset_i=offset_i)

            if ev_k.get_viewpoint('derived.posinbar') % 1 == 0.0:
                flag_end_beat = True
                break

            ks[alt_name].append(s_kb)
            events[alt_name].append(ev_k)

            if not ev_k.is_rest():
                l_pitch = new_event.get_viewpoint('pitch.cpitch')

            s_kb += 1

    return ks, events


def generate_by_beat(path, pattern, st_point=None, last_pitch=None, timesignature='4/4', keysignature=0):
    '''
    # NEXT TASK:
    # * DO NOW A BEAT PER BEAT GENERATION
    # * INSIDE BEAT DO DIRECT FORWARD CONNECTIONS
    # * ON BEAT STRENGTH CAN DO JUMPS
    '''

    time_signature = music21.meter.TimeSignature(timesignature)
    key_signature = music21.key.KeySignature(sharps=keysignature)

    oracle = oracle_constr.load_model_oracle(path)
    offset_i = get_index_viewpoint(oracle, 'offset')

    trn = oracle['oracle'].basic_attributes["trn"][:]
    sfx = oracle['oracle'].basic_attributes["sfx"][:]
    lrs = oracle['oracle'].basic_attributes["lrs"][:]
    rsfx = oracle['oracle'].basic_attributes["rsfx"][:]

    if not st_point and not last_pitch:
        last_pitch = random.choice(range(60, 76, 1))

        tsi = get_index_viewpoint(
            oracle, 'time.timesig', time_signature.ratioString)
        filter = oracle['information']['original_features'][:, tsi]
        filtered_ind = [ind for ind in oracle["indexes"] if filter[ind] == 1.0]
        st_point = random.choice(filtered_ind) + 1

    #st_point = 4664
    k = st_point
    s = [k]

    rootLogger = get_logger()
    first_event = event_extract(
        oracle, number=s[-1] - 1, timesignature=time_signature, last_pitch=last_pitch, first=True, offset_i=offset_i)

    seq1 = [first_event]
    seq2 = [first_event]
    seq3 = [first_event]

    l_pitch = last_pitch

    k += 1
    flag_end_beat = False
    while not flag_end_beat:
        ev_k = event_extract(
            oracle, number=k - 1, timesignature=time_signature, last_pitch=l_pitch, last_event=seq1[-1], offset_i=offset_i)

        if ev_k.get_viewpoint('derived.posinbar') % 1 == 0.0:
            flag_end_beat = True
            break

        s.append(k)
        seq1.append(ev_k)
        seq2.append(ev_k)
        seq3.append(ev_k)

        if not ev_k.is_rest():
            l_pitch = ev_k.get_viewpoint('pitch.cpitch')

        k += 1

    last_note_end = seq1[-1].get_offset() + \
        seq1[-1].get_viewpoint('duration.length') - seq1[0].get_offset()

    rootLogger.info('START GENERATION')

    last_event = seq1[-1]
    while last_note_end < time_signature.barDuration.quarterLength:

        poss_k_1, k_ev_1 = gen_a_beat(k, trn, sfx, rsfx, lrs, oracle,
                                    time_signature, l_pitch, last_event, offset_i, rootLogger=rootLogger)
        tries = 5
        while not poss_k_1 and tries > 0:
            poss_k_1, k_ev_1 = gen_a_beat(k, trn, sfx, rsfx, lrs, oracle,
                            time_signature, l_pitch, last_event, offset_i, rootLogger=rootLogger)
            tries -= 1

        for alt, ks in poss_k_1.items():
            rootLogger.info(str(alt) + ' ' + str(ks))
            if alt == 'alt_1':
                s.extend(ks)
                seq1.extend(k_ev_1[alt])
            if alt == 'alt_2':
                seq2.extend(k_ev_1[alt])
            if alt == 'alt_3':
                seq3.extend(k_ev_1[alt])

        if 'alt_2' not in poss_k_1:
            seq2.extend(k_ev_1['alt_1'])
        if 'alt_3' not in poss_k_1:
            seq3.extend(k_ev_1['alt_1'])

        last_note_end = seq1[-1].get_offset() + seq1[-1].get_viewpoint('duration.length') - \
            seq1[0].get_offset()
        rootLogger.info('LAST NOTE BAR: {}'.format(str(last_note_end)))
        k = s[-1]

    new_sequence = seq1
    new_score = parse_single_line(new_sequence, start_pitch=last_pitch,
                                  time_signature=time_signature, key_signature=key_signature,
                                  end_position_last_phrase=None,
                                  show_segmentation=True, contour=True)
    new_score.makeAccidentals(inPlace=True, overrideStatus=True)
    new_score.insert(0.0, music21.clef.TrebleClef())

    new_score2 = parse_single_line(seq2, start_pitch=last_pitch,
                                   time_signature=time_signature, key_signature=key_signature,
                                   end_position_last_phrase=None,
                                   show_segmentation=True, contour=True)
    new_score2.makeAccidentals(inPlace=True, overrideStatus=True)
    new_score2.insert(0.0, music21.clef.TrebleClef())

    new_score3 = parse_single_line(seq3, start_pitch=last_pitch,
                                   time_signature=time_signature, key_signature=key_signature,
                                   end_position_last_phrase=None,
                                   show_segmentation=True, contour=True)
    new_score3.makeAccidentals(inPlace=True, overrideStatus=True)
    new_score3.insert(0.0, music21.clef.TrebleClef())

    # logging.info('Finished')

    new_score.show()
    new_score2.show()
    new_score3.show()

    return None, 0, None

def test_mel():

    import music21
    env = music21.environment.Environment()
    env['musicxmlPath'] = r'D:\MuseScorePortable\App\MuseScore\bin\MuseScore3.exe'

    curves = {'1': [1, 1, 3, 3], '2': [3, 3, 3, 3], '3': [1, 1, 1, 3]}
    real_ts = '4/4'

    # oracle_path = "D:\Projects\COPOEM\Mei Materials\ALL_MUSIC\Models\Subsets-1\spanish_oracle-SUBSETS-0.pbz2"
    oracle_path = "D:\Projects\COPOEM\MEI Materials\ALL_MUSIC\Models\spanish_oracle-TEST-WS-0.pbz2"

    scores = {
        'beats_phrase': music21.meter.TimeSignature(real_ts).beatCount,
    }

    start_event = None
    last_pitch = None

    for key, curve in list(curves.items())[0:1]:

        score, end_event, l_pitch = generate_by_beat(
            oracle_path, pattern=curve, st_point=start_event, last_pitch=last_pitch, timesignature=real_ts)

        start_event = end_event + 1
        last_pitch = l_pitch
