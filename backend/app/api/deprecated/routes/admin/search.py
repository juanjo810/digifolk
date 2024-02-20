import os

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import umap.umap_ as umap

import app.composition.representation.utils.similarity as simil
from app.composition.representation.parsers.music_parser import MusicParser

from app.core.config import DATABASE_PATH
from app.db.db_session import database_instance

from fastapi import APIRouter
from sklearn import preprocessing
from sqlalchemy import exc
from starlette.status import HTTP_400_BAD_REQUEST

router = APIRouter()

NAME_MATRIX = {
    'MEL_CPITCH': 'PITCH',
    'MEL_CPITCH_OFF': 'OFF PITCH',
    'MEL_INT': 'INT',
    'MEL_INT_OFF': 'OFF INT',
    'RYT_2D': 'DUR',
    'RYT_2D_OFF': 'OFF DUR',
    'RYT_2D_RT': 'DUR_RATIO',
    'RYT_BS': 'DUR BS',
    'RYT_BS_OFF': 'OFF DUR BS',
    'RYT_PS': 'DUR PS',
    'RYT_PS_OFF': 'OFF DUR PS',
    'RYT_4D': 'DUR BS PS',
    'RYT_4D_OFF': 'OFF DUR BS PS',
    'RYT_4D_RT': 'DUR_RATIO BS PS',
    'RYT_5D': 'DUR BS PS BIOI',
    'RYT_5D_OFF': 'OFF DUR BS PS BIOI',
    'GLB_5D': 'PITCH DN DUR V',
    'GLB_5D_OFF': 'OFF PITCH DN DUR V',
    'GLB_8D': 'PITCH DN DUR V BS PS KN BIOI',
    'GLB_8D_OFF': 'OFF PITCH DN DUR V BS PS KN BIOI',
}


@router.get("/calculateSIAMDistMatrix")
async def calculate_SIAM_Distance_Matrix(info, collect_time=True):
    """
    Calculate SIAM Distance Matrix from Pieces
    """
    rows = await database_instance.fetch_rows("""SELECT music_id, name, title FROM music;""")
    if not rows or len(rows) == 0:
        return [{"error": "There is no music in the database."}]

    data_point_sets = {}
    for row in rows:
        music_path = os.sep.join(
            [DATABASE_PATH[:-1], 'Viewpoints', row[1]])

        parser = MusicParser()
        parser.from_pickle(filename=music_path, folders=[])

        if len(parser.get_part_events().keys()) > 0:
            part_key = list(parser.get_part_events().keys())[0]
            events = parser.get_part_events()[part_key]
            data_point_sets[row[1]] = simil.create_datapoint_sets(
                events, type=NAME_MATRIX[info])

    start_time = None
    if collect_time:
        import time
        start_time = time.time()

    dist_matrix = np.ones(
        (len(data_point_sets.keys()), len(data_point_sets.keys())))

    vals = list(data_point_sets.values())
    for i, ev in enumerate(vals):
        for j, ev2 in enumerate(vals):
            dist_matrix[i, j] = simil.SIAM(ev, ev2)
            print('P {}, {} : {}\n'.format(i, j, dist_matrix[i, j]))

    max_value = np.amax(dist_matrix)
    np.fill_diagonal(dist_matrix, max_value + 0.25)
    dist_matrix = preprocessing.minmax_scale(dist_matrix, feature_range=(0, 1))

    if collect_time:
        start_time = (time.time() - start_time)
        print("--- %s seconds ---" % start_time)

    path_to_save = os.sep.join(
        [DATABASE_PATH[:-1], 'PreComputed', 'DistanceMatrices', 'SIAM_{}.csv'.format(info)])
    df = pd.DataFrame(simil.transposeSimToDist(dist_matrix), columns=list(
        data_point_sets.keys()), index=list(data_point_sets.keys()))
    df.to_csv(path_to_save)

    return [{"msg": "Created SIAM Distance Matrix{}.".format(('in %s seconds' % start_time) if collect_time else '')}]


@router.get("/calculateLADistMatrix")
async def calculate_LA_Distance_Matrix(info, collect_time=True):
    """
    Calculate Local Alignemt Distance Matrix from Songs
    """
    rows = await database_instance.fetch_rows("""SELECT music_id, name, title FROM music;""")
    if not rows or len(rows) == 0:
        return [{"error": "There is no music in the database."}]

    data_point_sets = {}
    for row in rows:
        music_path = os.sep.join(
            [DATABASE_PATH[:-1], 'Viewpoints', row[1]])

        parser = MusicParser()
        parser.from_pickle(filename=music_path, folders=[])

        if len(parser.get_part_events().keys()) > 0:
            part_key = list(parser.get_part_events().keys())[0]
            events = parser.get_part_events()[part_key]
            data_point_sets[row[1]] = simil.create_datapoint_sets(
                events, type=NAME_MATRIX[info])

    start_time = None
    if collect_time:
        import time
        start_time = time.time()

    dist_matrix = np.ones(
        (len(data_point_sets.keys()), len(data_point_sets.keys())))

    vals = list(data_point_sets.values())
    for i, ev in enumerate(vals):
        for j, ev2 in enumerate(vals[:i]):
            dist_matrix[i, j] = simil.local_alignment(ev, ev2)
            dist_matrix[j, i] = dist_matrix[i, j]
            print('P {}, {} : {}\n'.format(i, j, dist_matrix[i, j]))

    if collect_time:
        start_time = (time.time() - start_time)
        print("--- %s seconds ---" % start_time)

    path_to_save = os.sep.join(
        [DATABASE_PATH[:-1], 'PreComputed', 'DistanceMatrices', 'LA_{}.csv'.format(info)])
    df = pd.DataFrame(simil.transposeSimToDist(dist_matrix), columns=list(
        data_point_sets.keys()), index=list(data_point_sets.keys()))
    df.to_csv(path_to_save)

    return [{"msg": "Created LA Distance Matrix{}.".format(('in %s seconds' % start_time) if collect_time else '')}]


def calculate_distance_matrix(option_values):
    import numpy as np
    from Levenshtein import distance
    from scipy.spatial.distance import pdist, squareform

    transformed_strings = np.array(option_values).reshape(-1, 1)
    transformed_strings = [x if not x == [None] else ['None']
                           for x in transformed_strings]

    dist_matrix = pdist(transformed_strings, lambda x,
                        y: distance(str(x[0]), str(y[0])))
    return squareform(dist_matrix).tolist()


def get_distance_matrix(file_name='LA_distances.csv'):
    import pandas as pd

    path_of_dist_matrix = os.sep.join(
        [DATABASE_PATH[:-1], 'PreComputed', 'DistanceMatrices', file_name])
    df = pd.read_csv(path_of_dist_matrix, sep=',', index_col=0, header=0)

    return df.values


def calculate_rhythm_dist_matrix(rows):
    import app.composition.representation.utils.similarity as simil
    from app.composition.representation.parsers.music_parser import MusicParser

    bioi_strings = []
    for row in rows:
        music_path = os.sep.join(
            [DATABASE_PATH[:-1], 'Scores', row[1]])
        parser = MusicParser()
        parser.from_pickle(music_path.replace(
            'Scores', 'Viewpoints'), folders=[])
        part_key_1 = list(parser.get_part_events().keys())[0]
        sequence_1 = parser.get_part_events()[part_key_1]
        real_biois = simil.get_real_biois_wout_rests(sequence_1)
        bioi_strings.append(real_biois)

    return calculate_distance_matrix(bioi_strings)


def draw_tsne(data, perplexity=15, n_iter=10000, n_components=2, title='', plot=False):

    fit = TSNE(perplexity=perplexity, n_iter=n_iter,
               n_components=n_components, metric="precomputed", square_distances=True)
    tsne_res = fit.fit_transform(data)

    if plot:
        fig = plt.figure()
        if n_components == 1:
            ax = fig.add_subplot(111)
            ax.scatter(tsne_res[:, 0], range(len(tsne_res)))
        if n_components == 2:
            ax = fig.add_subplot(111)
            ax.scatter(tsne_res[:, 0], tsne_res[:, 1])
        if n_components == 3:
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(tsne_res[:, 0], tsne_res[:, 1], tsne_res[:, 2], s=100)
        plt.title(title, fontsize=18)
        plt.show()

    return tsne_res


def draw_umap(data, n_neighbors=15, min_dist=0.02, n_components=2, metric='euclidean', title='', plot=False):

    fit = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=n_components,
        metric=metric
    )
    umap_res = fit.fit_transform(data)

    if plot:
        fig = plt.figure()
        if n_components == 1:
            ax = fig.add_subplot(111)
            ax.scatter(umap_res[:, 0], range(len(umap_res)))
        if n_components == 2:
            ax = fig.add_subplot(111)
            ax.scatter(umap_res[:, 0], umap_res[:, 1])
        if n_components == 3:
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(umap_res[:, 0], umap_res[:, 1], umap_res[:, 2], s=100)
        plt.title(title, fontsize=18)
        plt.show()

    return umap_res


@router.get("/calculateVisSearch")
async def calculate_visualization(option, vis_option='umap', LA=False, option_2='5D'):
    print('CALCULATING {} VIS INFO FOR {}'.format(vis_option, option))

    filename = '{}.csv'.format(option.upper())
    if option.lower() in ['melody', 'rhythm', 'global']:
        ind = 'MEL'
        if option.lower() == 'rhythm':
            ind = 'RYT'
        elif option.lower() == 'global':
            ind = 'GLB'
        alg = 'LA' if eval(LA.capitalize()) else 'SIAM'
        dist_matrix = get_distance_matrix(
            file_name='{}_{}_{}.csv'.format(alg, ind, option_2.upper()))
        filename = '{}_{}_{}.csv'.format(alg, ind, option_2.upper())
    elif option.lower() == 'rhythm_lev':
        query = """SELECT music_id, name, title, xml, midi FROM music;"""
        rows = await database_instance.fetch_rows(query)
        if not rows or len(rows) == 0:
            return [{"msg": "No music"}]

        dist_matrix = calculate_rhythm_dist_matrix(rows)
        from sklearn import preprocessing
        dist_matrix = preprocessing.minmax_scale(
            dist_matrix, feature_range=(0, 1))

        ids = [row[1] for row in rows]

        path_to_save = os.sep.join(
            [DATABASE_PATH[:-1], 'PreComputed', 'DistanceMatrices', 'RYT_LEV.csv'])
        df = pd.DataFrame(dist_matrix, columns=ids, index=ids)
        df.to_csv(path_to_save)

        filename = 'RYT_LEV.csv'
    else:
        query = """SELECT music_id, name, {} FROM music;""".format(
            option.lower())
        rows = await database_instance.fetch_rows(query)
        if not rows or len(rows) == 0:
            return [{"msg": "No music"}]
        dist_matrix = calculate_distance_matrix([row[2] for row in rows])
        filename = '{}.csv'.format(option.upper())

    vis_data = []
    if vis_option == 'umap':
        vis_data = draw_umap(dist_matrix, metric='precomputed', plot=False)
    elif vis_option == 'tsne':
        vis_data = draw_tsne(dist_matrix)

    path_to_save = os.sep.join(
        [DATABASE_PATH[:-1], 'PreComputed', vis_option.upper() + 'Points', filename])

    df = pd.DataFrame(vis_data)
    df.to_csv(path_to_save)

    return [{"msg": "Calc Done"}]
