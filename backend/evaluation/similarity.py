import os
import math
from collections import Counter

from app.composition.representation.parsers.music_parser import MusicParser
import app.composition.representation.utils.printing as print_utils
import app.composition.representation.utils.similarity as simil


def get_events_music(path):
    parser = MusicParser()
    parser.from_pickle(path, folders=[])
    keys = parser.get_part_events().keys()
    return parser.get_part_events()[list(keys)[0]]


def cosine_similarity(l1, l2):
    return len(set(l1) & set(l2)) / float(len(set(l1) | set(l2))) * 100


def level_events(events_1, events_2, level='top'):

    thresh = 0.0
    if level == 'top':
        thresh = 1.0
    elif level == 'mid-1':
        thresh = 0.5
    elif level == 'mid-2':
        thresh = 0.25

    filter_1 = [ev for ev in events_1 if ev.get_viewpoint(
        'derived.beat_strength') >= thresh]
    filter_2 = [ev for ev in events_2 if ev.get_viewpoint(
        'derived.beat_strength') >= thresh]

    return filter_1, filter_2


def similar(events_1, events_2, elements='PITCH DUR INT KN', alg='LA'):

    scores = {}

    for el in elements.split(' '):
        el_ev_1 = simil.create_datapoint_sets(
            events_1, type=el)
        el_ev_2 = simil.create_datapoint_sets(
            events_2, type=el)

        if alg == 'LA':
            scores[el] = simil.local_alignment(el_ev_1, el_ev_2)
        # else:
        #     scores[el] = cosine_similarity(el_ev_1, el_ev_2)

    return scores


def similarity_metric(events_1, events_2, level_scores={'top': 5, 'mid-1': 4, 'mid-2': 3, 'all': 1}, comparison_elements={'PITCH': 10, 'DUR': 8, 'INT': 2, 'KS': 1, 'TS': 1}, alg='LA'):

    sim_scores = {}

    for level, score in level_scores.items():

        filtered_ev1, filtered_ev2 = level_events(events_1, events_2, level)
        sim = similar(filtered_ev1, filtered_ev2, ' '.join(
            list(comparison_elements.keys())), alg=alg)

        for el, sc in sim.items():
            if not el in sim_scores:
                sim_scores[el] = 0
            sim_scores[el] += score * sc

    sim_scores = {k: v / sum(level_scores.values())
                  for k, v in sim_scores.items()}
    print(sim_scores)

    weighted_sim_scores = {
        k: v * comparison_elements[k] for k, v in sim_scores.items()}
    return sum(weighted_sim_scores.values()) / sum(comparison_elements.values())


def test_similarity_metric(name_1='ES-2012-CO-AN-006', name_2='ES-1948-FP-GUI-017(2)', path="D:\Projects\COPOEM\MEI Materials\ALL_MUSIC\Viewpoints"):

    import music21
    env = music21.environment.Environment()
    env['musicxmlPath'] = r'D:\MuseScorePortable\App\MuseScore\bin\MuseScore3.exe'

    score = music21.converter.parse(
        "D:\Projects\COPOEM\MEI Materials\ALL_MUSIC\Scores\\" + name_1 + '.mei', format='MEI')
    score.show()

    events_1 = get_events_music(path + os.sep + name_1)
    print(len(events_1))
    print(print_utils.show_sequence_of_viewpoint_without_offset(
        events_1, 'derived.beat_strength'))

    events_2 = get_events_music(path + os.sep + name_2)
    # events_2 = events_1

    events_3 = events_2[15:] + events_1[:15]
    result = similarity_metric(events_1, events_3, alg='LA')
    print('SIM: ' + str(result))

    events_3 = events_1[:15] + events_2[15:]
    result = similarity_metric(events_1, events_3, alg='LA')
    print('SIM: ' + str(result))


def test_similarity_all(path="D:\Projects\COPOEM\MEI Materials\ALL_MUSIC\Viewpoints"):
    import glob
    import numpy as np
    import pandas as pd

    folder = glob.glob(path + "\**\*.pbz2", recursive=True)
    events_all = {}

    for music in folder:
        name = str(music[music.rfind(os.sep) + 1: -5])
        events_all[name] = get_events_music(music[:-5])

    import time
    start_time = time.time()

    list_events = list(events_all.values())
    simil_matrix = np.ones(
        (len(list_events), len(list_events)))

    level_scores = {'top': 5, 'mid-1': 4, 'mid-2': 3, 'all': 1}
    comparison_elements = {'INT': 1} #{'PITCH': 10, 'DUR': 8, 'INT': 2, 'KS': 1, 'TS': 1}

    for i, music_1 in enumerate(list_events):
        for j, music_2 in enumerate(list_events[:i]):
            simil_matrix[i, j] = similarity_metric(
                music_1, music_2, level_scores, comparison_elements, alg='LA')
            simil_matrix[j, i] = simil_matrix[i, j]
            print('P {}, {} : {}\n'.format(i, j, simil_matrix[i, j]))

    print("--- %s seconds ---" % (time.time() - start_time))

    path_to_save = os.sep.join([
        path.replace('Viewpoints', 'DistResults'),
        'NEW_LA_LEVELS'
    ])
    merged_dicts = {**level_scores, **comparison_elements}
    for key, score in merged_dicts.items():
        path_to_save += '_' + key + '_' + str(score)

    df = pd.DataFrame(simil.transposeSimToDist(simil_matrix), columns=list(
        events_all.keys()), index=list(events_all.keys()))
    df.to_csv(path_to_save)
