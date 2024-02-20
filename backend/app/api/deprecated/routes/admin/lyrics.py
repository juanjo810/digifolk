import os
import bz2
import pickle
import json
import pandas as pd
import re
from xml.etree import ElementTree as ET

from app.core.config import DATABASE_PATH
from app.db.db_session import database_instance
from fastapi import APIRouter

router = APIRouter()


def retrieve_score(name):
    music_path = os.sep.join(
        [DATABASE_PATH[:-1], 'Scores', name])
    try:
        with bz2.BZ2File(music_path + '.pbz2', 'rb') as m21_handle:
            m21_score = pickle.load(m21_handle)
            # protocol=pickle.HIGHEST_PROTOCOL)
            m21_handle.close()
            return m21_score
    except:
        print("Can't load music21 score")
        return None


def save_score(name, m21_score):
    music_path = os.sep.join(
        [DATABASE_PATH[:-1], 'Scores', name])
    try:
        with bz2.BZ2File(music_path + '.pbz2', 'wb') as m21_handle:
            pickle.dump(m21_score, m21_handle,
                        protocol=pickle.HIGHEST_PROTOCOL)
            m21_handle.close()
    except:
        print("Can't save music21 score")


def retrieve_mei(name):
    music_path = os.sep.join(
        [DATABASE_PATH[:-1], 'Scores', name])
    try:
        return ET.parse(music_path + '.mei')
    except:
        print("Can't load MEI score")
        return None


NAME_SPACE = {'mei': 'http://www.music-encoding.org/ns/mei'}


def extract_complete_lyrics(mei_score):
    """
    """
    a_lyrics = mei_score.getroot().findall(
        ".//mei:notesStmt//mei:annot", NAME_SPACE)

    try:
        return ' '.join(re.split(r'[^a-zA-Z0-9_À-ÿ\']+', a_lyrics[1].text))
    except:
        pass

    b_lyrics = mei_score.getroot().findall(
        ".//mei:incip[@type='lyrics']//mei:incipText//mei:head", NAME_SPACE)
    if len(b_lyrics) > 0 and b_lyrics[0].text:
        return ' '.join(re.split(r'[^a-zA-Z0-9_À-ÿ\']+', b_lyrics[0].text))

    return ''


@router.get("/getExcelLyricsState")
async def get_excel_lyrics():
    rows = await database_instance.fetch_rows("""SELECT name, country FROM music;""")
    if not rows or len(rows) == 0:
        return [{"error": "No music"}]

    info = {}

    for row in sorted(rows):
        name = row[0]
        info[name] = {}

        m21_score = retrieve_score(name)
        mei_score = retrieve_mei(name)

        if mei_score:
            lycs = extract_complete_lyrics(mei_score)
            info[name]['has_annotated_lyrics'] = lycs != ''
            info[name]['annotated_lyrics'] = lycs

        if m21_score:
            n_lyrics = [n.lyric for n in m21_score.flat.notesAndRests]
            info[name]['has_music_lyrics'] = any(n != None for n in n_lyrics)
            if info[name]['has_music_lyrics']:
                info[name]['music_lyrics'] = ' '.join(
                    re.split(r'[^a-zA-Z0-9_À-ÿ\']+', ' '.join([nl for nl in n_lyrics if nl])))

    df = pd.DataFrame(info)
    df.to_csv(
        r'/Users/nadiacarvalho/Documents/Projects/COPOEM/MEI MATERIALS/lyrics.csv', index=True)

    return info


@router.get("/createMusicLyrics")
async def create_music_lyrics():
    """"""
    rows = await database_instance.fetch_rows("""SELECT name, country FROM music;""")
    if not rows or len(rows) == 0:
        return [{"error": "No music"}]

    import pyphen
    dic_pt = pyphen.Pyphen(lang='pt_PT')
    dic_es = pyphen.Pyphen(lang='es')
    dic_it = pyphen.Pyphen(lang='it_IT')

    from syllabipy.sonoripy import SonoriPy

    syls = {}

    for row in sorted(rows):
        name = row[0]

        mei_score = retrieve_mei(name)
        if mei_score:
            lycs = extract_complete_lyrics(mei_score)

            if lycs != '':
                spl_lycs = lycs.split(' ')

                if row[1] == 'Portugal':
                    syl = ' '.join([dic_pt.inserted(ly) for ly in spl_lycs])
                elif row[1] == 'Spain':
                    syl = ' '.join([dic_es.inserted(ly) for ly in spl_lycs])
                else:
                    syl = ' '.join([dic_it.inserted(ly) for ly in spl_lycs])

                syls[name] = {
                    'original': lycs,
                    'sylabic_1': syl,
                    'sylabic_2': ' '.join(['-'.join(SonoriPy(ly)) for ly in spl_lycs])
                }

        if name in syls:
            m21_score = retrieve_score(name)
            if m21_score:
                n_lyrics = [n.lyric for n in m21_score.flat.notesAndRests]
                if any(n != None for n in n_lyrics):
                    syls[name]['music'] = ' '.join(
                        re.split(r'[^a-zA-Z0-9_À-ÿ\']+', ' '.join([nl for nl in n_lyrics if nl])))

    with open('/Users/nadiacarvalho/Documents/Projects/COPOEM/MEI MATERIALS/lyrics_syl_2.json', 'w') as fp:
        json.dump(syls, fp, indent=4)
        fp.close()

    return syls


@router.put("/getLyricsForSong")
async def get_lyrics_for_song(id, name=None):
    rows = await database_instance.fetch_rows(f"""SELECT name, title, country, lyrics FROM music WHERE music_id = {id};""", as_dict=True)
    if not rows or len(rows) == 0:
        return [{"error": "No music"}]

    import music21

    row = rows[0]
    music_path = os.sep.join([DATABASE_PATH[:-1], 'Scores', row['name']])
    score = music21.converter.parse(music_path + '.mei')
    score.show()
    #print(mei_score)

    return rows

@router.put("/updateLyrics")
async def update_lyrics():
    """"""

    lycs = {}

    with open('/Users/nadiacarvalho/Documents/Projects/COPOEM/MEI MATERIALS/lyrics_syl_new.json', 'r') as fp:
        lycs = json.load(fp)
        fp.close()

    items = []

    for name, info in lycs.items():
        lyc = ''
        if 'music' in info:
            lyc = info['music'].replace('- ', '')

            m21_lycs = info['music'].split(' ')
            m21_score = retrieve_score(name)
            if m21_score:
                #m21_score.show()
                notes = list(m21_score.recurse().notes)
                print(notes)
                for i, n in enumerate(notes):
                    if i < len(m21_lycs) and n.lyric != m21_lycs[i]:
                        n.lyric = m21_lycs[i]
                save_score(name, m21_score)

                # m21_2_score = retrieve_score(name)
                # m21_2_score.metadata.title += ' - NEW'
                # m21_2_score.show()

            info['processed'] = True

        """
        stop = input()
        if stop == 'stop':
            with open('/Users/nadiacarvalho/Documents/Projects/COPOEM/MEI MATERIALS/lyrics_syl_2.json', 'w') as fp:
                json.dump(lycs, fp, indent=4)
                fp.close()
            return [{'msg': 'Stop Update'}]
        """

        items.append({'has_lyrics': lyc != '', 'lyrics': lyc, 'name': name})

        """
        q = input()
        if q == 'q':
            break
        """

    query = '''UPDATE music SET has_music_lyrics = :has_lyrics, lyrics = :lyrics WHERE name = :name'''
    cursor = await database_instance.connection.cursor()
    await cursor.executemany(
        query,
        items
    )
    await database_instance.connection.commit()
    print(cursor.rowcount, "Records updated successfully into Music table")
    await cursor.close()

    return [{"msg": '{} Records updated successfully into Music table'.format(cursor.rowcount)}]

@router.put("/correctAllSongs")
async def correct_all_songs():
    rows = await database_instance.fetch_rows("""SELECT name, country FROM music;""")

    info = []

    for row in sorted(rows):
        name = row[0]
        info.append({ 'name': name })

        m21_score = retrieve_score(name)
        mei_score = retrieve_mei(name)

        if mei_score:
            lycs = extract_complete_lyrics(mei_score)
            if not 'Another' in lycs:
                info[-1]['has_annotated_lyrics'] = lycs != ''
                info[-1]['annotated_lyrics'] = lycs

        if m21_score:
            n_lyrics = [n.lyric for n in m21_score.recurse().notes]
            info[-1]['has_music_lyrics'] = any(n != None for n in n_lyrics)
            if info[-1]['has_music_lyrics']:
                info[-1]['music_lyrics'] = ' '.join(
                    re.split(r'[^a-zA-Z0-9_À-ÿ\']+', ' '.join([nl for nl in n_lyrics if nl])))


    query = '''UPDATE music SET has_music_lyrics = :has_music_lyrics WHERE name = :name'''
    cursor = await database_instance.connection.cursor()
    await cursor.executemany(
        query,
        info
    )
    await database_instance.connection.commit()
    print(cursor.rowcount, "Records updated successfully into Music table")
    await cursor.close()

    return [{"msg": '{} Records updated successfully into Music table'.format(cursor.rowcount)}]


@router.put("/correctItalianSongs")
async def correct_italian_songs():
    with open('/Users/nadiacarvalho/Documents/Projects/COPOEM/MEI MATERIALS/lyrics_syl_new.json', 'r') as fp:
        lycs = json.load(fp)
        fp.close()

    items = []

    for name, info in lycs.items():
        if name[:2] == 'IT' and 'Another' in info['original']:
            items.append({'has_lyrics': False, 'name': name})

    query = '''UPDATE music SET has_music_lyrics = :has_lyrics WHERE name = :name'''
    cursor = await database_instance.connection.cursor()
    await cursor.executemany(
        query,
        items
    )
    await database_instance.connection.commit()
    print(cursor.rowcount, "Records updated successfully into Music table")
    await cursor.close()

    return [{"msg": '{} Records updated successfully into Music table'.format(cursor.rowcount)}]
