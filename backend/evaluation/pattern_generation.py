from numpy.lib.function_base import average
import app.composition as oracle_constr
import music21
import os
import bz2
import datetime

from app.composition.representation.events.linear_event import PartEvent
import app.composition.generation.generation.VMO as gen
import app.composition.representation.parsers.segmentation as segm
import app.composition.representation.utils.printing as print_utils

import random
import itertools
import numpy as np


def get_index_viewpoint(oracle, viewpoint, extra=''):
    if viewpoint in oracle['information']['original_features_names']:
        return oracle['information']['original_features_names'].index(viewpoint)

    for i, name in enumerate(oracle['information']['original_features_names']):
        if viewpoint in name:
            if '=' in name and extra in name:
                return i


def merge_streams(stream_1, stream_2):
    flatten_stream_1 = stream_1.flat
    for n in stream_2.recurse(classFilter=('Note', 'Rest'), restoreActiveSites=False):
        flatten_stream_1.append(n)

    flatten_stream_1.makeNotation()
    return flatten_stream_1


def get_avg_phrase_lengths(oracle):
    phrase_length_index = oracle['information']['original_features_names'].index(
        'phrase.length')
    phrase_lengths = [row[phrase_length_index] for row in oracle['information']
                      ['original_features'] if row[phrase_length_index] != 0.0]
    unique_phrase_lengths = list(set(phrase_lengths))
    frequency = [(pl, phrase_lengths.count(pl) / (pl - 1))
                 for pl in unique_phrase_lengths]
    average_phrase_length = sum(
        [freq[0] * freq[1] for freq in frequency]) / sum([freq[1] for freq in frequency])
    return phrase_length_index, average_phrase_length


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
    return beatStrength


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

    event.add_viewpoint('derived.beat_strength',
                        get_beat_strength(event, timesignature))
    return event


def all_possibilities(s, k, ktrace, combs, trn, sfx, lrs, rsfx):

    old_k = k
    old_s = s.copy()
    old_ktrace = ktrace.copy()

    possible_ks = {}

    for cob in combs:
        k = gen.step_generation(s, k, ktrace, trn, sfx,
                                lrs, rsfx, cob[0], int(len(s)), cob[1], cob[2])

        if isinstance(k, (list, np.ndarray)):
            for j in k:
                if j not in possible_ks:
                    possible_ks[j] = []
                possible_ks[j].append((cob, ktrace + [j]))
        else:
            if k not in possible_ks:
                possible_ks[k] = []
            possible_ks[k].append((cob, ktrace))

        k = old_k
        s = old_s.copy()
        ktrace = old_ktrace.copy()

    total_ex = sum([len(l) for l in possible_ks.values()])
    sorted_ks = sorted([(k, len(i) / total_ex)
                        for k, i in possible_ks.items()], key=lambda item: item[1], reverse=True)
    return possible_ks, sorted_ks


def filter_sync(ev, time_signature):
    last_mod_1 = ev.get_offset() % time_signature.barDuration.quarterLength
    last_mod_2 = (ev.get_offset() + ev.get_viewpoint('duration.length')
                  ) % time_signature.barDuration.quarterLength
    return last_mod_2 >= last_mod_1


def phrase_generation_pattern(oracle, oracle_info, pattern, time_signature, average_phrase_length, last_pitch=65.0, k=None, pli=0, offset_i=0):

    trn = oracle.basic_attributes["trn"][:]
    sfx = oracle.basic_attributes["sfx"][:]
    lrs = oracle.basic_attributes["lrs"][:]
    rsfx = oracle.basic_attributes["rsfx"][:]

    a = [list(np.arange(0.0, 1.05, 0.05)), list(
        set(lrs)), ['weight', 'max', '']]
    combs = list(itertools.product(*a))

    print('LAST_PITCH: {}'.format(str(last_pitch)))

    new_seq_as_events = []
    s = [k]
    ktrace = [k]

    if not k:
        tsi = get_index_viewpoint(
            oracle_info, 'time.timesig', time_signature.ratioString)

        filtered_ind = [i for i in oracle_info["indexes"]]

        print('AT')
        print(oracle_info['information']['original_features'][s[0], tsi])

        k = random.choice(filtered_ind) + 1  # 3836  #
        s[0] = k
        ktrace[0] = k

        first_event = event_extract(
            oracle_info, number=s[-1] - 1, timesignature=time_signature, last_pitch=last_pitch, first=True, offset_i=offset_i)
        new_seq_as_events.append(first_event)
    else:
        cob = random.choice(combs)

        k = gen.step_generation_2(s, k + 1, ktrace, trn, sfx,
                                  lrs, rsfx, cob[0], 0, cob[1], cob[2])
        first_event = event_extract(
            oracle_info, number=s[-1] - 1, timesignature=time_signature, last_pitch=last_pitch, first=True, offset_i=offset_i)
        new_seq_as_events.append(first_event)

    phrase_length_first_event = oracle_info['information']['original_features'][s[-1] - 1, pli]
    optimal_length = phrase_length_first_event
    if optimal_length == 0:
        optimal_length = average_phrase_length

    l_pitch = last_pitch
    last_bTS = 0
    last_bTS_pitch = last_pitch

    end_phrase = False
    while not end_phrase:
        old_s = s.copy()

        dict_ks, sorted_ks = all_possibilities(
            s, k, ktrace, combs, trn, sfx, lrs, rsfx)

        print('SK: ' + str(sorted_ks))

        poss_events = [event_extract(
            oracle_info, number=poss_k[0] - 1, timesignature=time_signature, last_pitch=l_pitch, last_event=new_seq_as_events[-1], offset_i=offset_i) for poss_k in sorted_ks]

        print(poss_events[0].get_viewpoint('derived.beat_strength'))

        if poss_events[0].get_viewpoint('derived.beat_strength') >= 0.5:
            curve_tendency = pattern[-1]
            if last_bTS < len(pattern):
                curve_tendency = pattern[last_bTS]

            filtered = [sorted_ks[i] for i, p_e in enumerate(poss_events) if not p_e.is_rest(
            ) and np.sign(p_e.get_viewpoint('pitch.cpitch') - last_bTS_pitch) == curve_tendency and filter_sync(p_e, time_signature)]
            print('FT: ' + str(filtered))

            # Check if Pattern is being followed
            poss_k = sorted_ks[0]
            if len(filtered) > 0:
                poss_k = random.choices(
                    filtered, weights=[item[1] for item in filtered])[0]

            last_bTS += 1
            last_bTS_pitch = poss_events[sorted_ks.index(
                poss_k)].get_viewpoint('pitch.cpitch')
            if not last_bTS_pitch:
                last_bTS_pitch = l_pitch
        else:
            filtered = [sorted_ks[i] for i, p_e in enumerate(
                poss_events) if filter_sync(p_e, time_signature)]

            poss_k = sorted_ks[0]
            if len(filtered) > 0:
                # Chose a random one according to probabilities or other choice
                poss_k = random.choices(
                    filtered, weights=[item[1] for item in filtered])[0]

        print()

        k = poss_k[0]
        s = old_s.copy()
        s.append(k)
        ktrace = random.choice(dict_ks[k])[1].copy()

        new_event = poss_events[sorted_ks.index(poss_k)]

        if not new_event.is_rest():
            l_pitch = new_event.get_viewpoint('pitch.cpitch')

        new_seq_as_events.append(new_event)

        segm.segmentation(new_seq_as_events, method='Grouper',
                          step_segmentation=True, optimal_length=optimal_length)

        bounds = [ev.get_viewpoint('phrase.boundary')
                  for ev in new_seq_as_events]
        end_bounds = [i for i, b in enumerate(bounds) if b == -1.0]

        for i in end_bounds:
            if i > (optimal_length / 2.0):
                k = s[i]
                new_seq_as_events = new_seq_as_events[:i + 1]
                end_phrase = True
                break
            if i == len(end_bounds) - 1 and len(bounds) > (2 * optimal_length):
                end_phrase = True

    kend = k
    return new_seq_as_events, kend, ktrace


def phrase_generation_pattern_2(oracle, oracle_info, pattern, time_signature, average_phrase_length, last_pitch=65.0, k=None, pli=0, offset_i=0):

    trn = oracle.basic_attributes["trn"][:]
    sfx = oracle.basic_attributes["sfx"][:]
    lrs = oracle.basic_attributes["lrs"][:]
    rsfx = oracle.basic_attributes["rsfx"][:]

    a = [list(np.arange(0.0, 1.05, 0.05)), list(
        set(lrs)), ['weight', 'max', '']]
    combs = list(itertools.product(*a))

    print('LAST_PITCH: {}'.format(str(last_pitch)))

    new_seq_as_events = []
    s = [k]
    ktrace = [k]

    if not k:
        k = random.choice(oracle_info["indexes"]) + 1  # 3836  #
        s[0] = k
        ktrace[0] = k

        first_event = event_extract(
            oracle_info, number=s[-1] - 1, timesignature=time_signature, last_pitch=last_pitch, first=True, offset_i=offset_i)
        new_seq_as_events.append(first_event)
    else:
        cob = random.choice(combs)

        k = gen.step_generation(s, k + 1, ktrace, trn, sfx,
                                lrs, rsfx, cob[0], 0, cob[1], cob[2])
        first_event = event_extract(
            oracle_info, number=s[-1] - 1, timesignature=time_signature, last_pitch=last_pitch, first=True, offset_i=offset_i)
        new_seq_as_events.append(first_event)

    phrase_length_first_event = oracle_info['information']['original_features'][s[-1] - 1, pli]
    optimal_length = phrase_length_first_event
    if optimal_length == 0:
        optimal_length = average_phrase_length

    l_pitch = last_pitch
    last_bTS = 0
    last_bTS_pitch = last_pitch

    end_phrase = False
    while not end_phrase:
        old_s = s.copy()

        # GET SFX and RSFX


def generate_from_pattern(path, pattern, timesignature='4/4', keysignature=0):

    time_signature = music21.meter.TimeSignature(timesignature)
    key_signature = music21.key.KeySignature(sharps=keysignature)
    end_position_last_phrase = None
    last_pitch = random.choice(range(60, 76, 1))  # 65

    from app.composition.representation.conversor.score_conversor import \
        parse_single_line

    oracle = oracle_constr.load_model_oracle(path)

    offset_i = oracle['information']['original_features_names'].index(
        'offset')
    phrase_length_index, average_phrase_length = get_avg_phrase_lengths(oracle)

    seq = phrase_generation_pattern(
        oracle['oracle'], oracle, [1, 0, 1, 1, -1, -1],
        time_signature, average_phrase_length, last_pitch=last_pitch,
        pli=phrase_length_index, offset_i=offset_i)

    new_sequence = seq[0]
    new_score = parse_single_line(new_sequence, start_pitch=last_pitch,
                                  time_signature=time_signature, key_signature=key_signature,
                                  end_position_last_phrase=end_position_last_phrase,
                                  show_segmentation=True, contour=True)
    new_score.makeAccidentals(inPlace=True, overrideStatus=True)
    new_score.insert(0.0, music21.clef.TrebleClef())

    return new_score, seq[1], 0, 0.0


def generate_phrases(label, num=1, phrases=1):

    env = music21.environment.Environment()
    env['musicxmlPath'] = r'D:\MuseScorePortable\App\MuseScore\bin\MuseScore3.exe'

    path = "D:\Projects\COPOEM\Mei Materials\ALL_MUSIC\Models\\" + \
        str(label) + ".pbz2"

    # date = datetime.datetime.now()
    # gen_folder = r"D:\Projects\COPOEM\Mei Materials\ALL_MUSIC\Generations\{}\{}".format(
    #     label, date.strftime("%Y-%m-%d--%H-%M-%S"))
    # os.makedirs(gen_folder, exist_ok=True)

    print()
    print('STARTING GENERATION')
    print()

    for i in range(int(num)):
        score, end_event, r_lrs, r_p = generate_from_pattern(
            path, pattern='')

        score.insert(0, music21.metadata.Metadata())
        score.metadata.title = ''
        score.metadata.composer = ''

        score.insert(0, music21.instrument.Piano())

        for _ in range(int(phrases) - 1):
            score_2, end_event, _, _ = oracle_constr.main_oracle(
                path, starting_point=end_event, first_sequence=score, random_lrs=random.choice(range(1, 11, 1)), random_p=random.random())

            score = merge_streams(score, score_2)

        score.show()

        # score.write(fp="{}\gen_{}_lrs_{}_p_{}.xml".format(
        #     gen_folder, str(i), str(r_lrs), str(round(r_p, 3))), fmt="xml")
