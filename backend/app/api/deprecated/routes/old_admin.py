import glob
import os
from xml.etree import ElementTree as ET

from app.core.config import DATABASE_PATH
from app.db.db_session import database_instance
from fastapi import APIRouter
from sqlalchemy import exc
from starlette.status import HTTP_400_BAD_REQUEST

router = APIRouter()


@router.get("/getSchema")
async def getSchema():
    schema = await database_instance.fetch_rows("SELECT * FROM sqlite_master WHERE type='table';")
    return [{"schema": schema}]

@router.get("/getGraceNoteList")
async def getGraceNoteList():
    import music21
    import numpy as np

    to_return = []
    rows = await database_instance.fetch_rows("""SELECT music_id, name FROM music;""")
    for row in rows:
        music_path = os.sep.join(
            [DATABASE_PATH[:-1], 'Scores', row[1]])

        score = music21.converter.parse(music_path + '.mxl')
        grace_notes = [n.duration.isGrace for n in score.flat.notes]

        if np.count_nonzero(grace_notes) > 0:
            to_return.append(music_path + '.mxl')

    return to_return


@router.get("/update_mode_scale")
async def batch_edit_mode_scale():
    import pandas as pd

    excel_info = pd.read_excel(
        r"D:\Projects\COPOEM\MEI Materials\CorregidasCanciones2.xls")
    rows = await database_instance.fetch_rows("""SELECT music_id, name FROM music;""")

    ns = {'mei': 'http://www.music-encoding.org/ns/mei'}
    for row in rows:
        music_path = os.sep.join(
            [DATABASE_PATH[:-1], 'Scores', row[1]])
        file = ET.parse(music_path + ".mei")

        excel_line = excel_info.loc[excel_info['Nombre fichero'] == row[1]]
        if not excel_line.empty:
            new_mode = excel_line['Mode'].item()
            new_key = excel_line['Note'].item()
            for elem in file.getroot().findall(".//mei:key", ns):
                if isinstance(new_key, str):
                    elem.text = new_key
                if isinstance(new_mode, str):
                    elem.attrib['mode'] = new_mode

            file.write(music_path + ".mei")

    return [{"msg": "Updated Database"}]

"""
Create and Populate Models
"""

@router.get("/createModel")
async def createModel(country, all=False):
    """
    Create Model for Music
    """
    query = 'SELECT music_id, name FROM music WHERE country="{}";'.format(
        country)
    rows = await database_instance.fetch_rows(query)

    if not rows or len(rows) == 0:
        return [{"msg": "No Such Country in Database"}]

    from app.composition.representation.parsers.music_parser import MusicParser

    indexes = []
    events = []

    possible_keys = ['A-', 'A', 'A#',
                     'B-', 'B', 'B#',
                     'C-', 'C', 'C#',
                     'D-', 'D', 'D#',
                     'E-', 'E', 'E#',
                     'F-', 'F', 'F#',
                     'G-', 'G', 'G#']
    for row in rows:
        if all:
            for key in possible_keys:
                path = os.sep.join(
                    [DATABASE_PATH, 'ViewpointsAll', row[1] + '-' + key])
                if os.path.isfile(path + '.pbz2'):
                    parser = MusicParser()
                    parser.from_pickle(path, folders=[])
                    keys = parser.get_part_events().keys()
                    if len(keys) == 1:
                        indexes.append(len(events))
                        events.extend(parser.get_part_events()[list(keys)[0]])
        else:
            path = os.sep.join([DATABASE_PATH, 'Viewpoints', row[1]])
            parser = MusicParser()
            parser.from_pickle(path, folders=[])
            keys = parser.get_part_events().keys()
            if len(keys) == 1:
                indexes.append(len(events))
                events.extend(parser.get_part_events()[list(keys)[0]])

    import app.composition as oracle_constr

    # Return from feature selection
    features, names, weights = oracle_constr.feature_selection(events)
    information = oracle_constr.feature_extraction(features, names, weights)

    print("Extracted Features")

    oracle_path = oracle_constr.create_model_oracle(information, indexes, path=os.sep.join(
        [DATABASE_PATH, 'Models', '']), country=country, all=False, verbose=True)

    print("Created Oracle")

    try:
        query = 'INSERT INTO gen_model (url) VALUES (?);'
        cursor = await database_instance.connection.cursor()
        await cursor.execute(query, (oracle_path,))
        await database_instance.connection.commit()

        model_id = cursor.lastrowid
        music = [(row[0], model_id) for row in rows]

        await cursor.close()

        query_2 = 'INSERT INTO model_music (music_id, model_id) VALUES (?, ?);'
        cursor = await database_instance.connection.cursor()
        await cursor.executemany(query_2, music)
        await database_instance.connection.commit()
        await cursor.close()
    except exc.IntegrityError:
        print('Unique Constraint')
        return [{"name": "main"}]

    return [{"msg": "Constructed Oracle"}]


