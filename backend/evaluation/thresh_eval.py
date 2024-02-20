def create_test_oracle_combs():
    """
    TEST ORACLE:
    """
    import glob

    from app.composition.representation.parsers.music_parser import MusicParser
    from app.composition.representation.parsers.segmentation import (
        apply_segmentation_info, segmentation)

    base_dir = r"D:\Projects\COPOEM\MEI Materials\ALL_MUSIC\Viewpoints"
    folder = glob.glob(base_dir + "\**\*.pbz2", recursive=True)

    print('PARSING AND SEGMENTATION: \n')

    indexes = []
    events = []
    for music in folder:
        parser = MusicParser()
        parser.from_pickle(music[:-5], folders=[])

        keys = parser.get_part_events().keys()
        if len(keys) == 1:
            indexes.append(len(events))

            m_ev = parser.get_part_events()[list(keys)[0]]

            # segmentation(m_ev)
            # apply_segmentation_info(m_ev)

            events.extend([ev for ev in m_ev if not ev.is_grace_note() or ev.get_viewpoint('duration.length') >= 0.25])

    import app.composition as oracle_constr

    print('\nORACLE CONSTRUCTION: \n')

    SELECT_FEATS = [
        "basic.rest",
        "basic.grace",
        "derived.seq_int",
        "derived.beat_strength",
        "duration.length",
        "phrase.boundary",
    ]

    other_feats = [
        "basic.bioi",
        "derived.bioi_contour",
        "derived.contour",
        "derived.dur_contour",
        "derived.dur_ratio",
        "derived.tactus",
        "derived.posinbar",
        "derived.closure",
        "derived.registral_direction",
        "derived.intervallic_difference",
        "phrase.cadence",
        "phrase.type",
        "key.keysig",
        "time.meter",
        "time.pulses",
        "time.tempo",
        "time.timesig",
        # "metada.genre",
        # "pitch.cpitch"
    ]

    from itertools import chain, combinations
    all_subsets = list(combinations(other_feats, 2)) #chain(*map(lambda x: , range(1, len(other_feats)+1)))
    print('\nCOMBS: ' + str(len(all_subsets)))

    for i, subset in enumerate(all_subsets):
        print('SUBSET ' + str(subset))
        # Return from feature selection
        features, names, weights = oracle_constr.feature_selection(
            events, SELECT_FEATS + list(subset))

        weights['derived.beat_strength']['fixed'] = True
        information = oracle_constr.feature_extraction(features, names, weights)
        print("Extracted Features")

        oracle_path = oracle_constr.create_model_oracle(
            information, indexes,
            path=r"D:\Projects\COPOEM\MEI Materials\ALL_MUSIC\Models\Subsets-1\\", country="Spain", other_path_info='-SUBSETS-{}'.format(str(i)),
            all=False, verbose=True, plot=False, thresh_range=(0.05, 1.05, 0.05), ir_type='cum')

        print('DONE: ' + oracle_path)

def create_test_oracle():
    """
    TEST ORACLE:
    """
    import glob

    from app.composition.representation.parsers.music_parser import MusicParser
    from app.composition.representation.parsers.segmentation import (
        apply_segmentation_info, segmentation)

    base_dir = r"D:\Projects\COPOEM\MEI Materials\ALL_MUSIC\Viewpoints"
    folder = glob.glob(base_dir + "\**\*.pbz2", recursive=True)

    print('PARSING AND SEGMENTATION: \n')

    indexes = []
    events = []
    for music in folder:
        parser = MusicParser()
        parser.from_pickle(music[:-5], folders=[])

        keys = parser.get_part_events().keys()
        if len(keys) == 1:
            indexes.append(len(events))

            m_ev = parser.get_part_events()[list(keys)[0]]

            # segmentation(m_ev)
            # apply_segmentation_info(m_ev)

            events.extend([ev for ev in m_ev if not ev.is_grace_note() or ev.get_viewpoint('duration.length') >= 0.25])

    import app.composition as oracle_constr

    print('\nORACLE CONSTRUCTION: \n')

    SELECT_FEATS = [
        "basic.rest",
        "basic.grace",
        "derived.seq_int",
        "derived.beat_strength",
        "duration.length",
        "phrase.boundary",
    ]

    other_feats = [
        "basic.bioi",
        "derived.bioi_contour",
        "derived.contour",
        "derived.dur_contour",
        "derived.dur_ratio",
        "derived.tactus",
        "derived.posinbar",
        "derived.closure",
        "derived.registral_direction",
        "derived.intervallic_difference",
        "phrase.cadence",
        "phrase.type",
        "key.keysig",
        "time.meter",
        "time.pulses",
        "time.tempo",
        "time.timesig",
        # "metada.genre",
        # "pitch.cpitch"
    ]


    # Return from feature selection
    features, names, weights = oracle_constr.feature_selection(
        events, SELECT_FEATS)

    weights['derived.beat_strength']['fixed'] = True
    information = oracle_constr.feature_extraction(features, names, weights)
    print("Extracted Features")

    num_oracle = 0

    oracle_path = oracle_constr.create_model_oracle(
        information, indexes,
        path=r"D:\Projects\COPOEM\MEI Materials\ALL_MUSIC\Models\Subsets-1\\", country="Spain", other_path_info='-TEST-WS-{}'.format(str(num_oracle)),
        all=False, verbose=True, plot=False, thresh_range=(0.05, 1.05, 0.05), ir_type='cum')



def oracle_comparison(num):
    import glob
    import os

    import app.composition as oracle_constr
    import matplotlib.pyplot as plt
    import numpy as np

    base_dir = r"D:\Projects\COPOEM\MEI Materials\db phrases only\Models"
    folder = glob.glob(base_dir + "\**\*.pbz2", recursive=True)

    _ = plt.figure(figsize=(10, 3))

    oracles = {}
    for path in folder:
        label = path[path.rfind(os.sep) + 1: -5]

        if num in label:
            oracle = oracle_constr.load_model_oracle(path)
            oracles[label] = oracle

            print(label + ' : ' + str(oracle['threshold_used']))

            x = np.array([i[1] for i in oracle['all_thresholds'][1]])
            y = np.array([i[0] for i in oracle['all_thresholds'][1]])

            i_thresh = np.where(x == oracle['threshold_used'])
            plt.plot(x[i_thresh], y[i_thresh], '*')

            plt.plot(x, y, linewidth=2, label=label)

    plt.title("IR vs. Threshold Value (VMO)", fontsize=18)
    plt.grid(b="on")
    plt.xlabel("Threshold", fontsize=14)
    plt.ylabel("IR", fontsize=14)
    plt.xlim(0, 1.0)
    plt.tight_layout()
    plt.legend(loc='best')
    plt.show()

