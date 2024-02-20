import json
import os
import base64

from app.api.routes.admin.users import create_user, get_user
from app.core.config import DATABASE_PATH, TOKEN_URL
from app.db.db_session import database_instance
from app.db.security import hash_password, manager, verify_password
from fastapi import APIRouter, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm

from .games import dance_game, rhythm_game, sing_game

router = APIRouter()


def save_melody_game(info, user_id):
    json_info = json.dumps(
        {'finished_song': info['finished_song'], 'saved_options': info['saved_options']})
    query = '''INSERT INTO game_save (user_id, game_type, game_info) VALUES (?, ?, ?)'''
    return query, (user_id, "Melody", json_info)


def save_rhythm_game(info, music_id, user_id):
    json_info = json.dumps({'displayPhrases': info['game_info']})
    query = '''INSERT INTO game_save (music_id, user_id, game_type, game_info) VALUES (?, ?, ?, ?)'''
    return query, (music_id, user_id, "Rhythm", json_info)


def save_dance_game(info, music_id, user_id):
    json_info = json.dumps({'chosen_steps': info['chosen_steps']})
    query = '''INSERT INTO game_save (music_id, user_id, game_type, game_info) VALUES (?, ?, ?, ?)'''
    return query, (music_id, user_id, 'Dance', json_info)


@router.post("/saveGame")
async def save_a_game(request: Request):
    body = await request.json()

    if body['game'] == 'Melody':
        query, item = save_melody_game(body, body['user_id'])
    elif body['game'] == 'Rhythm':
        query, item = save_rhythm_game(body, body['music_id'], body['user_id'])
    elif body['game'] == 'Dance':
        query, item = save_dance_game(body, body['music_id'], body['user_id'])
    else:
        return {'msg': f"Saving for Game Mode *{body['game']}* not implemented!"}

    cursor = await database_instance.connection.cursor()
    cursor = await cursor.execute(query, item)
    await database_instance.connection.commit()
    print(cursor.rowcount,
          f"Record inserted successfully into {body['game'].capitalize()}GameSave table")
    await cursor.close()
    return {'msg': "Saved!"}


@router.post("/saveSingGame")
async def save_sing_game(user_id: int, music_id: int, velocity: float, audio_file: UploadFile = File(...)):

    query = '''INSERT INTO game_save (user_id, music_id, game_type, game_info) VALUES (?, ?, ?, ?)'''
    item = (user_id, music_id, 'Sing', json.dumps({'velocity': velocity}))

    path = os.sep.join(
        [DATABASE_PATH, 'RecordingsSingGame', f'user_{user_id}'])
    os.makedirs(path, exist_ok=True)

    cursor = await database_instance.connection.cursor()
    cursor = await cursor.execute(query, item)
    await database_instance.connection.commit()
    print(cursor.rowcount,
          f"Record inserted successfully into SingcGameSave table")
    await cursor.close()

    game_id = int(cursor.lastrowid)
    with open(os.sep.join([path, f'game_{game_id}.mp3']), "wb+") as file_object:
        file_object.write(audio_file.file.read())
        file_object.close()

    return {'msg': "Saved!"}


@router.get("/getGamesUser")
async def get_games_user(user_id, game=None, grouped_by_type=True):

    query = f"""SELECT game_save.*, b.title
                FROM game_save
                INNER JOIN music AS b ON game_save.music_id = b.music_id AND game_save.game_type != 'Melody'
                WHERE user_id = {user_id}

                UNION ALL

                SELECT game_save.*, '' AS title
                FROM game_save
                WHERE user_id = {user_id} AND game_save.game_type = 'Melody'
                """
    if game is not None:
        if game.capitalize() == 'Melody':
            query = f"""SELECT game_save.*, '' AS title
                        FROM game_save
                        WHERE user_id = {user_id} and game_type = '{game.capitalize()}'"""
        else:
            query = f"""SELECT game_save.*, b.title
                        FROM game_save
                        INNER JOIN music AS b ON game_save.music_id = b.music_id
                        WHERE user_id = {user_id} and game_type = '{game.capitalize()}'"""

    rows = await database_instance.fetch_rows(query, as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No games saved for this user"}]

    if grouped_by_type:
        grouped_rows = {}
        for row in rows:
            type = row['game_type'].lower()
            if type not in grouped_rows:
                grouped_rows[type] = []
            grouped_rows[type].append(row)
        for type, rows in grouped_rows.items():
            rows.sort(key=lambda x: (x['updated_at'] is not None,
                                     x['updated_at'], x['created_at']), reverse=True)
        rows = grouped_rows
    else:
        rows.sort(key=lambda x: (x['updated_at'] is not None,
                                 x['updated_at'], x['created_at']), reverse=True)
    return rows


@router.delete("/deleteGame")
async def delete_game(game_id):
    query = f'''DELETE FROM game_save WHERE game_id = {game_id}'''
    _ = await database_instance.fetch_rows(query)
    return [{"msg": f"Game {game_id} deleted from database"}]


@router.get("/getSavedGame")
async def get_game(game_id):

    query = f"""SELECT *
                FROM game_save
                WHERE game_id = {game_id}"""
    rows = await database_instance.fetch_rows(query, as_dict=True)

    if not rows or len(rows) == 0:
        return [{"msg": f"No saved game with id {game_id}"}]

    if 'game_info' not in rows[0]:
        return [{"msg": f"Game {game_id} has no information to retrieve"}]

    if rows[0]['game_type'] == 'Melody':
        rows[0]['game_info'] = json.loads(rows[0]['game_info'])
    elif rows[0]['game_type'] == 'Rhythm':
        rows[0]['game_info'] = json.loads(rows[0]['game_info'])
        rhythm_info = await rhythm_game(rows[0]['music_id'])
        rows[0]['game_info']['phrases'] = rhythm_info
    elif rows[0]['game_type'] == 'Dance':
        steps = json.loads(rows[0]['game_info'])
        dance_info = await dance_game(rows[0]['music_id'])
        dance_info['proposed_dance'] = steps['chosen_steps']
        rows[0]['game_info'] = dance_info
    elif rows[0]['game_type'] == 'Sing':
        velocity = json.loads(rows[0]['game_info'])
        sing_info = await sing_game(rows[0]['music_id'])

        path = os.sep.join(
            [DATABASE_PATH, 'RecordingsSingGame', f'user_{rows[0]["user_id"]}'])
        recording = None
        with open(os.sep.join([path, f'game_{game_id}.mp3']), "rb+") as file_object:
            recording = file_object.read()
            file_object.close()

        rows[0]['game_info'] = {
            'original': sing_info,
            'velocity': velocity['velocity'],
            'recorded': base64.b64encode(recording)
        }
    else:
        return [{"msg": f"Game {game_id} has a not implemented Game Type of {rows[0]['game_type']}"}]

    return rows
