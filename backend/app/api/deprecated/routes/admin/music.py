import bz2
import glob
import os
import pickle

import app.api.routes.utils as utils

import app.composition.parsing as parse_mei
from app.composition.representation.parsers.music_parser import MusicParser
from app.composition.representation.parsers.segmentation import (
    apply_segmentation_info, segmentation)

from app.core.config import DATABASE_PATH
from app.db.db_session import database_instance

from fastapi import APIRouter
from sqlalchemy import exc
from starlette.status import HTTP_400_BAD_REQUEST

router = APIRouter()


def parse_complete_song(path, view=False):
    """
    Parse a Complete Song
    """
    # Parsing Metadata
    metadata = parse_mei.parseSongMetadata(path)

    if metadata['title'] == '' and metadata['alt_title'] != '':
        metadata['title'] = metadata['alt_title']

    # Parsing MusicXML and Lyrics
    metadata['xml'], has_lyrics, lyrics, m21_score = parse_mei.musicXMLFromMEI(
        path, metadata)
    if has_lyrics and not metadata['lyrics']:
        metadata['lyrics'] = lyrics

    # Parsing MIDI
    metadata['midi'] = parse_mei.midiFromMEI(metadata['name'], m21_score)

    # Save XML, MEI, M21_Score and MIDI to folders
    save_files(metadata, m21_score)
    mei_string = parse_mei.mei_to_string(metadata['mei'])
    metadata['mei'] = mei_string

    if view:
    # Parse Viewpoints
        viewpoints = MusicParser(
            filename=metadata['name'], score=m21_score, metadata=metadata)
        viewpoints.parse()
        viewpoints_path = os.sep.join(
            [DATABASE_PATH[:-1], 'Viewpoints', metadata['name']])
        viewpoints.to_pickle(filename=viewpoints_path, folders=[])
    return metadata


def save_files(metadata, m21_score):
    """
    Save Files to Folder
    """
    music_path = os.sep.join(
        [DATABASE_PATH[:-1], 'Scores', metadata['name']])

    try:
        with bz2.BZ2File(music_path + '.pbz2', 'wb') as m21_handle:
            pickle.dump(m21_score, m21_handle,
                        protocol=pickle.HIGHEST_PROTOCOL)
            m21_handle.close()
    except:
        print("Can't save music21 score")

    with open(music_path + '.mxl', 'w') as xml_handle:
        xml_handle.write(metadata['xml'])
        xml_handle.close()
    with open(music_path + '.mei', 'wb') as mei_handle:
        metadata['mei'].write(mei_handle)
        mei_handle.close()

    if metadata['midi'] != '':
        midi_path = os.sep.join(
            [DATABASE_PATH[:-1], 'MIDIs', metadata['name']])
        with open(midi_path + '.mid', 'wb') as mid_handle:
            mid_handle.write(metadata['midi'])
            mid_handle.close()


@router.post("/addSong")
async def add_single_song(path):
    """
    Add a Single Song to Database
    """
    if not os.path.exists(path) and not os.path.isfile(path):
        return [{"error": 'Song Specified does not exist!'}]
    elif path[-3:] != 'mei':
        return [{"error": 'Song Specified is not in MEI format!'}]

    metadata = parse_complete_song(path)

    keylist = list(metadata.keys())
    item = tuple(metadata.values())
    query = 'INSERT OR REPLACE INTO music (' + ','.join(['[' + i + ']' for i in keylist]) + \
        ') VALUES (' + ','.join(['?' for i in keylist]) + ')'

    cursor = await database_instance.connection.cursor()
    await cursor.execute(
        query,
        item
    )
    await database_instance.connection.commit()
    print(cursor.rowcount, "Record inserted successfully into Music table")
    await cursor.close()

    return [{"msg": 'Record inserted successfully into Music table'}]


@router.delete("/removeSong")
async def remove_single_song(id=None, name=None):

    query = None
    if name:
        query = 'DELETE FROM music WHERE name = "{}"'.format(str(name))
    elif id:
        query = 'DELETE FROM music WHERE music_id = "{}"'.format(str(id))

    if query:
        cursor = await database_instance.connection.cursor()
        await cursor.execute(query)
        await database_instance.connection.commit()
        print(cursor.rowcount, "Record(s) deleted successfully from Music table")
        await cursor.close()
        return [{"msg": '{} Record(s) deleted successfully from Music table'.format(cursor.rowcount)}]

    return [{"error": 'No specified ID or Name!'}]


@router.delete("/removeAllSongs")
async def remove_all_songs():
    """
    Delete All Songs from Database
    """
    cursor = await database_instance.connection.cursor()
    await cursor.execute('DELETE FROM music;')
    await database_instance.connection.commit()
    print(cursor.rowcount, "Record(s) deleted successfully from Music table")
    await cursor.close()
    return [{"msg": '{} Record(s) deleted successfully from Music table'.format(cursor.rowcount)}]


@router.post("/populateMusic")
async def populate_database_of_music(local_path=''):
    """
    Add whole folder of songs in MEI format to database
    """
    local_path = os.sep.join([local_path, '**', '*.mei'])
    if local_path == '':
        local_path = os.sep.join([DATABASE_PATH, 'Scores', '**', '*.mei'])

    pieces = glob.glob(local_path, recursive=True)

    if len(pieces) == 0:
        return [{"error": 'No Songs in Specified Folder!'}]

    all_information = [{}]

    pieces.sort()
    for piece in pieces:
        try:
            metadata = parse_complete_song(piece, view=True)
            all_information[0][metadata['name']] = metadata
        except Exception as exc:
            print(f'COUNDNT GET {piece}: {exc}')

    first_item_key = list(all_information[0].keys())[0]
    keylist = list(all_information[0][first_item_key].keys())
    items = list(tuple(x.values()) for x in list(all_information[0].values()))

    query = 'INSERT OR REPLACE INTO music (' + ','.join(['[' + i + ']' for i in keylist]) + \
        ') VALUES (' + ','.join(['?' for i in keylist]) + ')'

    cursor = await database_instance.connection.cursor()
    await cursor.executemany(
        query,
        items
    )
    await database_instance.connection.commit()
    print(cursor.rowcount, "Records inserted successfully into Music table")
    await cursor.close()

    return [{"msg": '{} Records inserted successfully into Music table'.format(cursor.rowcount)}]


@router.put("/updateName")
async def update_portuguese_names():
    rows = await database_instance.fetch_rows("""SELECT music_id, name FROM music WHERE country="Portugal";""")
    if not rows or len(rows) == 0:
        return [{"error": "No Portuguese music"}]

    items = []
    for row in sorted(rows):
        items.append((row[1].replace('PO', 'PT'), row[0]))

    query = '''UPDATE music SET name = ? WHERE music_id = ?'''
    cursor = await database_instance.connection.cursor()
    await cursor.executemany(
        query,
        items
    )
    await database_instance.connection.commit()
    print(cursor.rowcount, "Records updated successfully into Music table")
    await cursor.close()

    return [{"msg": '{} Records updated successfully into Music table'.format(cursor.rowcount)}]


@router.put("/updateGeography")
async def update_geography():
    rows = await database_instance.fetch_rows("""SELECT music_id, name, city, district, region FROM music;""", as_dict=True)
    if not rows or len(rows) == 0:
        return [{"error": "No music"}]

    import pandas as pd
    import numpy as np

    updated = pd.read_csv('geography.csv', index_col=0)
    esquema = pd.read_csv('esquema-comunidades.csv')


    for row in sorted(rows, key=lambda t: t['music_id']):
        print(row['name'])

        """
        mei_score = utils.retrieve_mei(row['name'])

        city = get_possible_local(mei_score, [".//mei:term[@type='localidad']", ".//mei:term[@type='citt&#224;']"])
        district = get_possible_local(mei_score, [".//mei:term[@type='provincia']", ".//mei:term[@type='distrito']"])
        region = get_possible_local(mei_score, [".//mei:term[@type='comunidad']", ".//mei:term[@type='regione']"])

        letters_comunidad = row['name'].split('-')[-3],
        letters_provincia = row['name'].split('-')[-2],
        """

        updated_values = updated.loc[updated['music_id'] == row['music_id']]
        new_name = updated_values["name"].values[0]

        if row["name"] != new_name:
            try:
                os.rename(f'{DATABASE_PATH[:-1]}/MIDIs/{row["name"]}.mid', f'{DATABASE_PATH[:-1]}/MIDIs/{new_name}.mid')
                os.rename(f'{DATABASE_PATH[:-1]}/Scores/{row["name"]}.mei', f'{DATABASE_PATH[:-1]}/Scores/{new_name}.mei')
                os.rename(f'{DATABASE_PATH[:-1]}/Scores/{row["name"]}.mxl', f'{DATABASE_PATH[:-1]}/Scores/{new_name}.mxl')
                os.rename(f'{DATABASE_PATH[:-1]}/Scores/{row["name"]}.pbz2', f'{DATABASE_PATH[:-1]}/Scores/{new_name}.pbz2')
                os.rename(f'{DATABASE_PATH[:-1]}/Viewpoints/{row["name"]}.pbz2', f'{DATABASE_PATH[:-1]}/Viewpoints/{new_name}.pbz2')
            except:
                print(f'No file named {DATABASE_PATH[:-1]}/MIDIs/{row["name"]}.mid')

        try:
            query = '''UPDATE music SET name = :name, city = :city, district = :district, region = :region WHERE music_id = :music_id'''
            cursor = await database_instance.connection.cursor()
            await cursor.execute(
                query,
                {
                    'music_id': row['music_id'],
                    'name': new_name,
                    'city': updated_values['city'].values[0],
                    'district': updated_values['district'].values[0],
                    'region': updated_values['region'].values[0],
                }
            )
            await database_instance.connection.commit()
            print(cursor.rowcount, "Records updated successfully into Music table")
            await cursor.close()
        except Exception as e:
            print(e)

    return rows

@router.put("/updateGenres")
async def update_genres():
    rows = await database_instance.fetch_rows(f"""SELECT music_id, genre FROM music;""", as_dict=True)
    if not rows or len(rows) == 0:
        return [{"error": "No music"}]

    NEW_GENRES = {
        'Canción De Cuna': 'Lullaby',
        'Canción Cuna': 'Lullaby',
        'Cuna': 'Lullaby',
        'Lullaby': 'Lullaby',
        'Ninna Nanna': 'Lullaby',
        'Canción Infantil, Juego De Palmas': 'Children song',
        'Canción Infantil': 'Children song',
        'Canción Infatil': 'Children song',
        'Corro': 'Children song',
        'Canción De Corro': 'Children song',
        'De Corro': 'Children song',
        'Canción De Columpio': 'Children song',
        'De Columpio': 'Children song',
        'Canción De Rueda': 'Children song',
        'De Rueda': 'Children song',
        'Canción De Comba': 'Children song',
        'De Comba': 'Children song',
        'Canción De Procesión': 'Children song',
        'Filastrocca': 'Children song',
        'De Baile': 'Dance song',
        'Canción De Baile': 'Dance song',
        'Danza': 'Dance song',
    }

    for row in rows:
        row['new_genre'] = NEW_GENRES[row['genre'].title()]

    query = '''UPDATE music SET genre = :new_genre WHERE music_id = :music_id'''
    cursor = await database_instance.connection.cursor()
    await cursor.executemany(
        query,
        rows
    )
    await database_instance.connection.commit()
    print(cursor.rowcount, "Records updated successfully into Music table")
    await cursor.close()

    return rows

@router.put("/updateNamesError")
async def update_name_with_error(name, new_name):
    rows = await database_instance.fetch_rows(f"""SELECT * FROM music WHERE name = '{name}';""", as_dict=True)
    if not rows or len(rows) == 0:
        return [{"error": "No music"}]

    try:
        query = '''UPDATE music SET name = :name WHERE music_id = :music_id'''
        cursor = await database_instance.connection.cursor()
        await cursor.execute(
            query,
            {
                'music_id': rows[0]['music_id'],
                'name': new_name,
            }
        )
        await database_instance.connection.commit()
        print(cursor.rowcount, "Records updated successfully into Music table")
        await cursor.close()
    except Exception:
        cursor = await database_instance.connection.cursor()
        await cursor.execute(f"""DELETE FROM music WHERE name = '{name}';""")
        await database_instance.connection.commit()
        print(cursor.rowcount, "Old Record deleted successfully from Music table")
        await cursor.close()

    return rows

def get_possible_local(mei_score, ALTER):
    for alter in ALTER:
        info = mei_score.getroot().findall(alter, {'mei': 'http://www.music-encoding.org/ns/mei'})
        if len(info) > 0 and info[0].get('label') is not None:
            return info[0].get('label')
        elif len(info) > 0 and info[0].text is not None:
            return info[0].text
    return None

@router.put("/updateViewpoints")
async def update_viewpoints(mode='Phrases'):
    rows = await database_instance.fetch_rows("""SELECT music_id, name FROM music;""")
    if not rows or len(rows) == 0:
        return [{"error": "No music"}]

    for row in sorted(rows):
        print('Song : {}'.format(row[1]))
        viewpoints_path = os.sep.join([DATABASE_PATH, 'Viewpoints', row[1]])

        if not os.path.isfile(viewpoints_path + '.pbz2'):
            print('NO FILE')
            continue

        parser = MusicParser()
        parser.from_pickle(viewpoints_path, folders=[])
        if mode == 'Phrases':
            phrases = await database_instance.fetch_rows("""SELECT phrases FROM music WHERE music_id = "{}";""".format(row[0]))
            if not phrases or not phrases[0]:
                print("No phrase information for this music")
            parse_mei.phrases_to_viewpoints(parser, phrases)
        elif mode == 'Segmentation':
            for _, events in parser.get_part_events().items():
                segmentation(events)
                apply_segmentation_info(events)
        elif mode == 'name':
            for _, events in parser.get_part_events().items():
                for _, event in enumerate(events):
                    event.add_viewpoint("song", row[1])
        parser.to_pickle(viewpoints_path, folders=[])
    return rows

@router.put("/viewViewpoints")
async def view_viewpoints(music_id):
    rows = await database_instance.fetch_rows("""SELECT * FROM music WHERE music_id = {};""".format(music_id), as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such id"}]

    viewpoints_path = os.sep.join([DATABASE_PATH, 'Viewpoints', rows[0]['name']])
    parser = MusicParser()
    parser.from_pickle(viewpoints_path, folders=[])

    parser.show_all_viewpoints()

    return rows

@router.put("/getALLJSONs")
async def view_viewpoints_as_jsons():
    rows = await database_instance.fetch_rows("""SELECT name FROM music;""", as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such id"}]

    for row in sorted(rows, key=lambda x: x['name']):
        viewpoints_path = os.sep.join([DATABASE_PATH, 'Viewpoints', row['name']])
        json_path = os.sep.join([DATABASE_PATH, 'JSONs', row['name']])

        parser = MusicParser()
        parser.from_pickle(viewpoints_path, folders=[])
        parser.to_json(json_path, folders=[])

    return rows

@router.put("/getALLMIDIs")
async def view_music_as_midi():
    rows = await database_instance.fetch_rows("""SELECT name FROM music;""", as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such id"}]

    for row in sorted(rows, key=lambda x: x['name']):
        midi_path = os.sep.join([DATABASE_PATH, 'MIDIs-2', row['name']])

        try:
            score = utils.retrieve_score(row['name'])
            if score is not None:
                score.write('midi', fp=midi_path + '.mid')
        except:
            print(f"Can't load music21 score for {row['name']}")

    return rows
