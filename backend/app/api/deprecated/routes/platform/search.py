import os
from xml.etree import ElementTree as ET

import pandas as pd

from app.core.config import DATABASE_PATH
from app.db.db_session import database_instance
from app.models.country import Country

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy import exc
from starlette.status import HTTP_400_BAD_REQUEST

router = APIRouter()


def get_data_from_rows(rows, option):
    data = [{'info': {}}]
    for row in rows:
        data[0]['info'][row[0]] = {
            'name': row[1],
            'title': row[2],
            'xml': row[3],
            'midi': row[4],
        }

        if isinstance(option, list):
            data[0]['info'][row[0]]['option'] = {}
            for i, o in enumerate(option):
                data[0]['info'][row[0]]['option'][o] = row[5 + i]
        elif option not in ['Melody', 'Rhythm', 'Global']:
            data[0]['info'][row[0]]['option'] = row[6]
        else:
            data[0]['info'][row[0]]['option'] = None

    return data


def get_vis_results(file_name='LA_distances.csv', vis_option='umap'):
    path_of_dist_matrix = os.sep.join(
        [DATABASE_PATH[:-1], 'PreComputed', vis_option.upper() + 'Points', file_name])
    df = pd.read_csv(path_of_dist_matrix, sep=',', index_col=0, header=0)

    return df.values


@router.get("/visSearch")
async def searchMusicUsingVisualization(option, fixed_option='country', vis_option='umap'):
    print('GETTING {} VIS INFO FOR {} WITH FIXED {}'.format(
        vis_option, option, fixed_option))

    query = """SELECT music_id, name, title, xml, midi, {} FROM music;""".format(
        fixed_option.lower())
    if option not in ['Melody', 'Rhythm', 'Global']:
        query = """SELECT music_id, name, title, xml, midi, {}, {} FROM music;""".format(
            option.lower(), fixed_option.lower())

    print(query)
    rows = await database_instance.fetch_rows(query)
    if not rows or len(rows) == 0:
        return [{"msg": "No music"}]

    data = get_data_from_rows(rows, option)
    data[0]['fixed_option'] = [row[-1] for row in rows]

    filename = '{}.csv'.format(option.upper())
    if option == 'Melody':
        filename = 'LA_MEL_CPITCH.csv'
    elif option == 'Rhythm':
        filename = 'LA_RYT_5D.csv'
    elif option == 'Global':
        filename = 'SIAM_GLB_5D.csv'

    data[0]['vis'] = get_vis_results(
        file_name=filename, vis_option=vis_option)

    import numpy as np
    data[0]['vis'] = np.float64(data[0]['vis']).tolist()
    return data


@router.get("/queryValues")
async def get_possible_values(option):
    query = """SELECT music_id, xml, midi, {} FROM music;""".format(
            option.lower())

    rows = await database_instance.fetch_rows(query)
    if not rows or len(rows) == 0:
        return [{"msg": "No music"}]

    unique_values = set([row[-1] for row in rows if row[-1]])
    if option.lower() == 'time_signature':
        sep_time_signatures = [row[-1].split(', ') for row in rows]
        unique_values = set(
            [item for sublist in sep_time_signatures for item in sublist if item != 'none/none'])

    unique_values = list(unique_values)
    unique_values.sort()
    return unique_values


@router.post("/search")
async def search_for_values(queries: dict):

    organized_values = {}
    for query in queries['queries']:
        field = query['field']
        if field == 'key':
            field = 'real_key'
        field = field.lower()

        if field in organized_values:
            if query['value'] not in organized_values[field]:
                organized_values[field].extend(query['value'])
        else:
            organized_values[field] = query['value']

    processed_queries = []
    for field, values in organized_values.items():
        if field == 'time_signature':
            query = ' OR '.join(
                ['{} LIKE ("%{}%")'.format(field, val) for val in values])
        else:
            query = ' OR '.join(['{} = "{}"'.format(field, val)
                                 for val in values])

        if query != "":
            processed_queries.append(query)

    conditions = '*'
    if len(processed_queries) == 1:
        conditions = processed_queries[0]
    elif len(processed_queries) > 1:
        conditions = '(' + processed_queries[0]
        for q in processed_queries[1:]:
            conditions += ') AND (' + q
        conditions += ')'

    query = """SELECT music_id, name, title, xml, midi, {} FROM music WHERE {};""".format(
        ', '.join(list(organized_values.keys())),
        conditions)
    print(query)

    rows = await database_instance.fetch_rows(query)
    if not rows or len(rows) == 0:
        return [{"msg": "No music"}]

    data = get_data_from_rows(rows, list(organized_values.keys()))
    return data
