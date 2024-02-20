import bz2
import datetime
import glob
import math
import os
import pickle
import random
from statistics import mean, median, stdev

import app.composition as oracle_constr
import app.composition.representation.utils.similarity as similarity
import app.composition.representation.utils.statistics as statistics
import music21
import numpy as np
import pandas as pd
import progressbar
from app.composition.representation.parsers.music_parser import MusicParser
from scipy import integrate, stats
from scipy.stats.stats import iqr
from sklearn import preprocessing

widgets = [
    ' [', progressbar.Timer(), '] ',
    progressbar.Bar(),
    ' (', progressbar.ETA(), ') ',
]


def merge_streams(stream_1, stream_2):
    flatten_stream_1 = stream_1.flat
    for n in stream_2.recurse(classFilter=('Note', 'Rest'), restoreActiveSites=False):
        flatten_stream_1.append(n)

    flatten_stream_1.makeNotation()
    return flatten_stream_1


def generate_phrases(label, num, phrases=4):

    env = music21.environment.Environment()
    env['musicxmlPath'] = r'D:\MuseScorePortable\App\MuseScore\bin\MuseScore3.exe'

    path = "D:\Projects\COPOEM\Mei Materials\db phrases only\Models\\" + \
        str(label) + ".pbz2"

    date = datetime.datetime.now()
    gen_folder = r"D:\Projects\COPOEM\Mei Materials\db phrases only\Generations\{}\{}".format(
        label, date.strftime("%Y-%m-%d--%H-%M-%S"))
    os.makedirs(gen_folder, exist_ok=True)

    print()
    print('STARTING GENERATION')
    print()

    for i in range(int(num)):
        score, end_event, r_lrs, r_p = oracle_constr.main_oracle(
            path, random_lrs=random.choice(range(1, 11, 1)), random_p=random.random())

        score.insert(0, music21.metadata.Metadata())
        score.metadata.title = ''
        score.metadata.composer = ''

        score.insert(0, music21.instrument.Piano())

        for _ in range(int(phrases) - 1):
            score_2, end_event, _, _ = oracle_constr.main_oracle(
                path, starting_point=end_event, first_sequence=score, random_lrs=random.choice(range(1, 11, 1)), random_p=random.random())

            score = merge_streams(score, score_2)
            # score.show()
            # input('CONTINUE ?')

        score.write(fp="{}\gen_{}_lrs_{}_p_{}.xml".format(
            gen_folder, str(i), str(r_lrs), str(round(r_p, 3))), fmt="xml")


###########################################

def normalized_euclidean_distance(hist_1, hist_2):
    """
    Normalized Euclidean Distance across two histograms
    """
    sum = 0
    n = len(hist_1)
    for i in range(len(hist_1)):
        sum += math.pow(hist_1[i] - hist_2[i], 2) / n

    return math.sqrt(sum)


def distance_calc(music_1, music_2, histograms, features, LA):
    for feat in features:
        if LA:
            feats_1 = [[ev.get_viewpoint(feat)] for ev in music_1]
            feats_2 = [[ev.get_viewpoint(feat)] for ev in music_2]
            dist = similarity.local_alignment(feats_1, feats_2)
        else:
            feats_1 = [ev.get_viewpoint(feat) for ev in music_1]
            feats_2 = [ev.get_viewpoint(feat) for ev in music_2]

            feats_1 = [e if e else 10000000 for e in feats_1]
            feats_2 = [e if e else 10000000 for e in feats_2]

            set_feats = [e if e else 10000000 for e in list(
                set(feats_1 + feats_2))]
            unique = sorted(set_feats)

            if len(unique) == 1:
                dist = 0.0
                continue

            hist_1 = np.histogram(feats_1, bins=unique)
            hist_2 = np.histogram(feats_2, bins=unique)

            n_hist_1 = preprocessing.normalize(
                hist_1[0].reshape(1, -1), norm='l1')[0]
            n_hist_2 = preprocessing.normalize(
                hist_2[0].reshape(1, -1), norm='l1')[0]

            dist = stats.wasserstein_distance(n_hist_1, n_hist_2)

        histograms[feat].append(dist)


def get_statistics(dataset, filter_feats=[]):
    """
    Get Statistics of Dataset
    """
    flatten_dataset = [item for sublist in dataset for item in sublist]
    return statistics.statistic_features(flatten_dataset, filter_feats)


def calculate_interset_distances(training, generated, features, LA=False):
    """
    Calculate list of distances
    for each feature across all music in different datasets
    """
    interset_distances_histograms = dict((k, []) for k in features)
    bar = progressbar.ProgressBar(max_value=len(training) * len(generated),
                                  widgets=widgets).start()
    progress = 0
    for music_1 in training:
        for music_2 in generated:
            distance_calc(
                music_1, music_2, interset_distances_histograms, features, LA)
            progress += 1
            bar.update(progress)
    bar.finish(end='\n\n')

    if LA:
        for feat, dists in interset_distances_histograms.items():
            interset_distances_histograms[feat] = similarity.transposeSimToDist(
                dists)

    return interset_distances_histograms


def calculate_intraset_distances(dataset, features, LA=False):
    """
    Calculate list of distances
    for each feature across all music in the same dataset
    """
    intraset_distances_histograms = dict((k, []) for k in features)

    n = len(dataset)
    bar = progressbar.ProgressBar(maxval=int(n * (n - 1) / 2),
                                  widgets=widgets).start()
    progress = 0
    for i, music_1 in enumerate(dataset):
        for music_2 in dataset[:i]:
            distance_calc(
                music_1, music_2, intraset_distances_histograms, features, LA)
            progress += 1
            bar.update(progress)
    bar.finish(end='\n\n')

    if LA:
        for feat, dists in intraset_distances_histograms.items():
            intraset_distances_histograms[feat] = similarity.transposeSimToDist(
                dists)

    return intraset_distances_histograms


def overlap_area(A, B):
    pdf_A = stats.gaussian_kde(A)
    pdf_B = stats.gaussian_kde(B)
    min_AB = np.min((np.min(A), np.min(B)))
    max_AB = np.max((np.max(A), np.max(B)))
    return integrate.quad(lambda x: min(pdf_A(x), pdf_B(x)), min_AB, max_AB)


def kl_distance(A, B, num_sample=1000):
    pdf_A = stats.gaussian_kde(A)
    pdf_B = stats.gaussian_kde(B)
    sample_A = np.linspace(np.min(A), np.max(A), num_sample)
    sample_B = np.linspace(np.min(B), np.max(B), num_sample)
    return stats.entropy(pdf_A(sample_A), pdf_B(sample_B))


def plot_kdes(intraset_distances_training, intraset_distances_generated, interset_distances, feat, LA, folder):
    import matplotlib.pyplot as plt
    import seaborn as sns

    plt.figure(feat)

    sns.kdeplot(intraset_distances_training[feat], label='training_set')
    sns.kdeplot(intraset_distances_generated[feat], label='generated_set')
    sns.kdeplot(interset_distances[feat], label='inter_set')

    plt.title('Feature: {}'.format(feat))
    plt.grid(b="on")
    if LA:
        plt.xlabel('Local Alignent Distance')
    else:
        plt.xlabel('Euclidean Distance')

    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig(folder + os.sep +
                'KDE_{}_{}.png'.format(feat.upper(), 'LA' if LA else 'ED'))
    plt.close()


def get_pairwise_crossvalidation(training_dataset, generated_dataset, features, LA=False, folder='', IA_TRAIN=False):
    '''
    1. Calculate Intra-set distances for each feature
    2. Calculate Inter-set distances for each feature
    3. Kernel Density Estimation (return MEAN, STD within each intra-set PDFs)
    4. Measure Distributions using KLD, overlap area for each intra-set PDF with inter-set PDF
    '''
    if IA_TRAIN:
        print('Retrieving Intraset Distances Training')
        with bz2.BZ2File(r'D:\Projects\COPOEM\Mei Materials\db phrases only\Evaluation\intraset-train-{}.pbz2'.format('LA' if LA else 'ED'), 'rb') as handle:
            intraset_distances_training = pickle.load(handle)
            handle.close()
    else:
        print('Calculating Intraset Distances Training')
        intraset_distances_training = calculate_intraset_distances(
            training_dataset, features, LA)
        with bz2.BZ2File(r'D:\Projects\COPOEM\Mei Materials\db phrases only\Evaluation\intraset-train-{}.pbz2'.format('LA' if LA else 'ED'), 'wb') as handle:
            pickle.dump(intraset_distances_training, handle)
            handle.close()

    print('Calculating Intraset Distances Generations')
    intraset_distances_generated = calculate_intraset_distances(
        generated_dataset, features, LA)
    print('Calculating Interset Distances')
    interset_distances = calculate_interset_distances(
        training_dataset, generated_dataset, features, LA)

    stats = dict((k, {}) for k in features)

    for feat in features:
        plot_kdes(intraset_distances_training,
                  intraset_distances_generated, interset_distances, feat, LA, folder)

        extract_statistics(intraset_distances_training,
                           intraset_distances_generated, interset_distances, stats, feat)

    return stats


def stats_get(feat, dataset_name, dataset, stats):
    stats[feat][dataset_name] = {
        'mean': mean(dataset[feat]),
        'median': median(dataset[feat]),
        'min': min(dataset[feat]),
        'max': max(dataset[feat]),
        'iqr': iqr(dataset[feat]),
        'std': stdev(dataset[feat]),
    }


def extract_statistics(intraset_distances_training, intraset_distances_generated, interset_distances, stats, feat):
    """
    Extract Statistics from Relative Pairwise Cross-Validation
    """
    stats_get(feat, 'training', intraset_distances_training, stats)
    stats_get(feat, 'generated', intraset_distances_generated, stats)
    stats_get(feat, 'interset', interset_distances, stats)

    stats[feat]['training']['overlap_area'] = overlap_area(
        intraset_distances_training[feat], interset_distances[feat])
    stats[feat]['training']['KL_distance'] = kl_distance(
        intraset_distances_training[feat], interset_distances[feat])

    stats[feat]['generated']['overlap_area'] = overlap_area(
        intraset_distances_generated[feat], interset_distances[feat])
    stats[feat]['generated']['KL_distance'] = kl_distance(
        intraset_distances_generated[feat], interset_distances[feat])


def get_generated_dataset(path):
    parsers = []
    folder = glob.glob(path + "\**\*.xml", recursive=True)
    bar = progressbar.ProgressBar(maxval=len(folder),
                                  widgets=widgets).start()
    for i, music in enumerate(folder):
        parser = MusicParser(filename=music, folders=[])
        parser.parse(parts=True, interpart=False,
                     number_parts=1, verbose=False)
        parsers.append(parser)
        bar.update(i + 1)
    bar.finish(end='\n\n')
    return parsers


def get_training_dataset(path):
    parsers = []
    folder = glob.glob(path + "\**\*.pbz2", recursive=True)
    bar = progressbar.ProgressBar(maxval=len(folder),
                                  widgets=widgets).start()
    for i, music in enumerate(folder):
        parser = MusicParser()
        parser.from_pickle(music[:-5], folders=[])
        parsers.append(parser)
        bar.update(i + 1)
    bar.finish(end='\n\n')
    return parsers


def dataframe_from_nesteddict(nested_dict):
    newdict = {}
    for k1, v1 in nested_dict.items():
        newdict[k1] = {}
        newdict[k1] = {**newdict[k1], **{(k2, k3): v3
                                         for k2, v2 in v1.items() for k3, v3 in v2.items()}}

    return pd.DataFrame.from_dict(newdict, orient='index').reset_index()


def Lerch_Work_Flow():
    date = datetime.datetime.now()
    folder = r"D:\Projects\COPOEM\Mei Materials\db phrases only\Evaluation\{}".format(
        date.strftime("%Y-%m-%d--%H-%M-%S"))
    os.makedirs(folder, exist_ok=True)

    """
    Get Training Dataset
    """
    print('Get Training Dataset')
    training_parsers = get_training_dataset(
        r"D:\Projects\COPOEM\Mei Materials\db phrases only\Viewpoints")
    training_events = [parser.get_part_events()[list(parser.get_part_events().keys())[0]]
                       for parser in training_parsers]

    """
    Get Generated Dataset
    """
    print('Get Generated Dataset')
    generated_parsers = get_generated_dataset(
        r"D:\Projects\COPOEM\Mei Materials\db phrases only\Generations\____spanish_oracle-PHR-ANNOTATED-2\2021-05-01--18-11-25")
    generated_events = [parser.get_part_events()['Piano']
                        for parser in generated_parsers]

    features = [
        # "basic.bioi",
        # "basic.rest",
        "derived.beat_strength",
        # "derived.bioi_contour",
        # "derived.contour",
        # "derived.dur_contour",
        # "derived.dur_ratio",
        # "derived.tactus",
        #"derived.posinbar",
        #"derived.seq_int",
        # "derived.closure",
        # "derived.registral_direction",
        # "derived.intervallic_difference",
        #"duration.length",
        # "phrase.boundary",
        "key.keysig",
        "time.meter",
        "time.pulses",
        # "time.tempo",
        "time.timesig",
        #"pitch.cpitch",
        #"pitch.pitch_class"
    ]

    """
    Pairwise Cross-Validation
    """
    print('Cross Validation LA')
    stats_LA = get_pairwise_crossvalidation(
        training_events, generated_events, features, LA=True, folder=folder, IA_TRAIN=False)
    df_LA = dataframe_from_nesteddict(stats_LA)

    print('Cross Validation ED')
    stats_ED = get_pairwise_crossvalidation(
        training_events, generated_events, features, LA=False, folder=folder, IA_TRAIN=False)
    df_ED = dataframe_from_nesteddict(stats_ED)

    """
    Statistics Analysis
    """
    training_statistics = get_statistics(
        training_events, filter_feats=features)
    df_train_stats = pd.DataFrame.from_dict(
        training_statistics[0], orient='index')

    generated_statistics = get_statistics(
        generated_events, filter_feats=features)
    df_gen_stats = pd.DataFrame.from_dict(
        generated_statistics[0], orient='index')

    with pd.ExcelWriter(folder + os.sep + "evaluation.xlsx") as writer:
        df_LA.to_excel(writer, sheet_name="Cross-Validation LA")
        df_ED.to_excel(writer, sheet_name="Cross-Validation ED")
        df_train_stats.to_excel(writer, sheet_name="Abs. Stats. Training Set")
        df_gen_stats.to_excel(writer, sheet_name="Abs. Stats. Generated Set")
