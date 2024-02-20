import json

import app.composition.representation.utils.printing as printing
import app.composition.representation.utils.statistics as statistics
import music21
import numpy as np
from app.composition.representation.parsers.music_parser import MusicParser
from app.composition.representation.parsers.segmentation import \
    apply_segmentation_info
from app.composition.representation.parsers.segmentation import \
    get_phrases_from_events
from app.composition.representation.parsers.segmentation import segmentation


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


def feature_selection(events, selection=None):
    import app.composition.representation.utils.features as utils
    from sklearn import preprocessing

    stats, original, feat_names = statistics.statistic_features(events)

    from sklearn.feature_selection import VarianceThreshold

    sel = VarianceThreshold(threshold=(0.75 * (1 - 0.75)))
    _ = sel.fit_transform(original)  # selected features in matrix already
    support = sel.get_support()

    selected_features = []
    for i, sel_value in enumerate(support):
        if sel_value:
            selected_features.append(feat_names[i])

    new_stats = {"parts": stats}
    statistics.calculate_part_weights(new_stats)

    weights = {}

    SELECT_FEATS = [
        "basic.bioi",
        "basic.rest",
        "derived.beat_strength",
        "derived.bioi_contour",
        "derived.contour",
        "derived.dur_contour",
        "derived.dur_ratio",
        "derived.tactus",
        "derived.posinbar",
        "derived.seq_int",
        "derived.closure",
        "derived.registral_direction",
        "derived.intervallic_difference",
        "duration.length",
        "phrase.boundary",
        "key.keysig",
        "time.meter",
        "time.pulses",
        "time.tempo",
        "time.timesig",
        "metada.genre",
        # "pitch.cpitch"
    ]

    if selection == 'ALL':
        SELECT_FEATS = feat_names
    elif selection:
        SELECT_FEATS = selection

    for key, n_dict in new_stats["parts"].items():
        if any(key in s for s in SELECT_FEATS):
            weights[key] = {
                "weight": n_dict["weight"],
                "fixed": n_dict["fixed"],
            }

    return original, feat_names, weights


def separate_weight_dict(weight_dict):
    weights = {}
    fixed = {}
    for viewpoint, wgths in weight_dict.items():
        weights[viewpoint] = wgths["weight"]
        fixed[viewpoint] = wgths["fixed"]
    return weights, fixed


def feature_extraction(features, names, weights):
    import app.composition.representation.utils.features as feat_utils

    information = {"original_features_names": names,
                   "original_features": features}

    w, f = separate_weight_dict(weights)

    cols, weights, fixed_weights, feature_names = feat_utils.get_columns_from_weights(
        w, f, information["original_features_names"]
    )

    information["fixed_weights"] = fixed_weights
    information["selected_features_names"] = feature_names
    sel_part_features = information["original_features"][:, cols]
    information["selected_original"] = sel_part_features
    information["selected_normed"] = feat_utils.normalize(
        sel_part_features, -1, 1)
    information["normed_weights"] = feat_utils.normalize_weights(weights)

    return information


def create_model_oracle(
    information, indexes, thresh_calc=None, country="Portugal", all=False, path='', other_path_info='', verbose=False, plot=False, thresh_range=(0.05, 1.0, 0.05), ir_type='cum'
):
    import app.composition.generation.utils as gen_utils
    import matplotlib.pyplot as plt

    fixed_weights_cols = [
        col for col, value in enumerate(information["fixed_weights"]) if value
    ]

    thresh = []
    if not thresh_calc:
        thresh = gen_utils.find_threshold(
            _r=thresh_range,
            ir_type=ir_type,
            input_data=np.array(information["selected_normed"]),
            weights=np.array(information["normed_weights"]),
            fixed_weights=np.array(fixed_weights_cols),
            dim=len(information["selected_features_names"]),
            verbose=verbose,
        )

        thresh_calc = thresh[0][1]

        if plot:
            x = np.array([i[1] for i in thresh[1]])
            y = np.array([i[0] for i in thresh[1]])
            _ = plt.figure(figsize=(10, 3))
            plt.plot(x, y, linewidth=2)
            plt.title("IR vs. Threshold Value(vmo)", fontsize=18)
            plt.grid(b="on")
            plt.xlabel("Threshold", fontsize=14)
            plt.ylabel("IR", fontsize=14)
            plt.xlim(0, 1.0)
            plt.tight_layout()
            plt.show()

    print("Starting Oracle Construction")

    oracle = gen_utils.build_oracle(
        np.array(information["selected_normed"]),
        flag="a",
        features=np.array(information["selected_features_names"]),
        weights=np.array(information["normed_weights"]),
        fixed_weights=fixed_weights_cols,
        dim=len(information["selected_features_names"]),
        dfunc="cosine",
        threshold=thresh_calc,
    )

    print("Generated Oracle")

    oracles_information = {
        "oracle": oracle,
        "threshold_used": thresh_calc,
        "information": information,
        "indexes": indexes,
    }

    if len(thresh) > 0:
        oracles_information['all_thresholds'] = thresh

    import bz2
    import pickle

    country_string = "portuguese"
    if country == "Spain":
        country_string = "spanish"
    elif country == "Italy":
        country_string = "italian"
    elif country == "All":
        country_string = "all"

    oracle_path = '{}_{}oracle{}.pbz2'.format(
        country_string, ("", "all_")[all], other_path_info)
    with bz2.BZ2File(
        path + oracle_path,
        "wb",
    ) as handle:
        pickle.dump(oracles_information, handle)
        # protocol=pickle.HIGHEST_PROTOCOL)
        handle.close()
    print("Dumped to pickle")

    return oracle_path


def load_model_oracle(path):
    import bz2
    import pickle

    oracles_information = {}
    with bz2.BZ2File(
        path,
        "rb",
    ) as handle:
        oracles_information = pickle.load(handle)
        handle.close()
    print("Loaded from pickle")
    return oracles_information


def phrase_gen(oracle, features, feat_names, p=0.5, k=1, LRS=0, weight="max"):

    import app.composition.generation.generation.VMO as gen
    import app.composition.representation.parsers.segmentation as segm

    trn = oracle.basic_attributes["trn"][:]
    sfx = oracle.basic_attributes["sfx"][:]
    lrs = oracle.basic_attributes["lrs"][:]
    rsfx = oracle.basic_attributes["rsfx"][:]

    s = []
    ktrace = [k]

    SEGMENTATION_FEATURES = ["pitch.cpitch",
                             "derived.closure",
                             "basic.rest",
                             "key.keysig",
                             "time.pulses"]
    SEGMENTATION_WEIGHTS = [5, 3, 1, 2, 1]
    cols = [feat_names.index(name) for name in SEGMENTATION_FEATURES]
    segm_features = np.array(features)[:, cols]

    k = gen.step_generation(s, k, ktrace, trn, sfx,
                            lrs, rsfx, p, 0, LRS, weight)

    dur_index = feat_names.index('duration.length')
    durations = np.array(features)[:, dur_index]

    #s_durations = np.array(durations)[[i-1 for i in s], :]

    end_phrase = False
    # for j in range(25):
    while not end_phrase:
        k = gen.step_generation(s, k, ktrace, trn, sfx,
                                lrs, rsfx, p, 0, LRS, weight)

        if len(s) > 2:
            new_s = [i - 1 for i in s]
            bss, n_w = segm.calculate_boundary_strengths(
                np.array(segm_features)[new_s, :], SEGMENTATION_WEIGHTS
            )

            boundaries = [segm.peak_picking(i, bss, n_w)
                          for i, _ in enumerate(new_s[:-1])]
            print(boundaries)
            print()

            #s_durations = np.array(durations)[[i-1 for i in s], :]
            # print(s_durations)

            seq = "".join([str(elem) for elem in boundaries]).rindex("1")
            if boundaries.count(1) > 1 and seq > 8:
                end_phrase = True
                s = s[:seq]
            elif len(s) > 20:
                end_phrase = True

    kend = k
    return s, kend, ktrace


def phrase_gen_grouper(oracle, oracle_info, p=0.5, k=1, LRS=0, weight="max", last_pitch=65.0):

    import app.composition.generation.generation.VMO as gen
    import app.composition.representation.parsers.segmentation as segm
    import app.composition.representation.utils.printing as print_utils
    from app.composition.representation.events.linear_event import PartEvent

    import random

    trn = oracle.basic_attributes["trn"][:]
    sfx = oracle.basic_attributes["sfx"][:]
    lrs = oracle.basic_attributes["lrs"][:]
    rsfx = oracle.basic_attributes["rsfx"][:]

    s = [k + 1]
    ktrace = [k]

    k = gen.step_generation(s, k + 1, ktrace, trn, sfx,
                            lrs, rsfx, p, 0, LRS, weight)

    first_event = PartEvent(
        from_list=oracle_info["information"]["selected_original"][s[-1] - 1],
        features=oracle_info["information"]["selected_features_names"],
    )
    first_event.add_viewpoint('basic.bioi', 0.0)
    first_event.add_viewpoint('pitch.cpitch', last_pitch)

    new_seq_as_events = [
        first_event
    ]

    end_phrase = False
    # for j in range(25):
    while not end_phrase:
        last_s = s
        last_k = k
        last_ktrace = ktrace

        k = gen.step_generation(s, k, ktrace, trn, sfx,
                                lrs, rsfx, p, 0, LRS, weight)

        new_event = PartEvent(
            from_list=oracle_info["information"]["selected_original"][s[-1] - 1],
            features=oracle_info["information"]["selected_features_names"],
        )
        # calculate bioi
        new_event.add_viewpoint(
            'basic.bioi', new_event.get_viewpoint('duration.length'))

        if not new_event.is_rest():
            new_pitch = last_pitch + \
                new_seq_as_events[-1].get_viewpoint('derived.seq_int')
            new_event.add_viewpoint('pitch.cpitch', new_pitch)
            last_pitch = new_pitch

        if (54.0 < last_pitch or last_pitch > 80.0):
            # print('HERE')

            s = last_s
            k = last_k
            ktrace = last_ktrace

            new_p = random.random()

            k = gen.step_generation(s, k, ktrace, trn, sfx,
                                    lrs, rsfx, new_p, 0, LRS, weight)

            new_event = PartEvent(
                from_list=oracle_info["information"]["selected_original"][s[-1] - 1],
                features=oracle_info["information"]["selected_features_names"],
            )
            # calculate bioi
            new_event.add_viewpoint(
                'basic.bioi', new_event.get_viewpoint('duration.length'))

            if not new_event.is_rest():
                new_pitch = last_pitch + \
                    new_seq_as_events[-1].get_viewpoint('derived.seq_int')
                new_event.add_viewpoint('pitch.cpitch', new_pitch)
                last_pitch = new_pitch

        new_seq_as_events.append(new_event)

        segm.segmentation(new_seq_as_events, method='Grouper',
                          step_segmentation=True)

        bounds = [ev.get_viewpoint('phrase.boundary')
                  for ev in new_seq_as_events]
        end_bounds = [i for i, b in enumerate(bounds) if b == -1.0]

        for i in end_bounds:
            if i > 4:
                k = s[i]
                new_seq_as_events = new_seq_as_events[:i + 1]
                end_phrase = True
                break
            if i == len(end_bounds) - 1 and len(bounds) > 20:
                end_phrase = True

    kend = k
    return new_seq_as_events, kend, ktrace


def main_oracle(path, starting_point=None, first_sequence=None, random_lrs=3, random_p=0.5):

    oracle_info = load_model_oracle(path)

    import random
    if starting_point is None:
        starting_point = random.choice(oracle_info["indexes"]) - 1

    time_signature = None
    key_signature = None
    end_position_last_phrase = None
    last_pitch = 65.0

    if first_sequence:
        if isinstance(first_sequence, music21.stream.Stream):
            stream = first_sequence
        else:
            stream = music21.converter.parse(first_sequence)

        time_signature = stream.recurse().timeSignature
        key_signature = stream.recurse().keySignature
        # print(key_signature)

        last_note_or_rest = stream.recurse().notesAndRests[-1]
        end_position_last_phrase = last_note_or_rest.beat - \
            1 + last_note_or_rest.duration.quarterLength

        last_note = stream.recurse().notes[-1]
        last_pitch = last_note.pitch.ps

    seq = phrase_gen_grouper(
        oracle_info["oracle"],
        oracle_info,
        k=int(starting_point) - 1,
        LRS=random_lrs,
        p=random_p,
        last_pitch=last_pitch
    )

    from app.composition.representation.conversor.score_conversor import \
        parse_single_line

    new_sequence = seq[0]
    new_score = parse_single_line(new_sequence, start_pitch=last_pitch,
                                  time_signature=time_signature, key_signature=key_signature,
                                  end_position_last_phrase=end_position_last_phrase,
                                  show_segmentation=True, contour=True)
    new_score.makeAccidentals(inPlace=True, overrideStatus=True)

    new_key = key_signature
    if not first_sequence:
        key_analysis = music21.analysis.floatingKey.KeyAnalyzer(new_score)
        keys = key_analysis.run()
        # print('KA: ' + str(keys))

        if len(keys) > 0:
            new_key = keys[0]

        # print(new_key)
        if len(keys) > 1 and new_key and new_score.flat.notes[0] not in new_key.getScale(new_key.mode).pitches:
            # print('HERE')
            pass

    if new_score.measure(1).keySignature and new_key:
        new_score.measure(1).keySignature.sharps = new_key.sharps
    elif new_key:
        new_score.measure(1).keySignature = music21.key.KeySignature(
            new_key.sharps)

    for n in new_score.recurse().notes:
        if n.getContextByClass('KeySignature'):
            n.pitch.accidental = n.getContextByClass(
                'KeySignature').accidentalByStep(n.step)

    if len(new_score.measure(1).flat.notes) == 0:
        new_score.measure(2).keySignature = new_score.measure(1).keySignature
        new_score.measure(2).timeSignature = new_score.measure(1).timeSignature
        new_score.remove(new_score.measure(1))

    """
    env = music21.environment.Environment()
    env['musicxmlPath'] = r'D:\MuseScorePortable\App\MuseScore\bin\MuseScore3.exe'

    new_score.show()
    """

    return new_score, seq[1], random_lrs, random_p
