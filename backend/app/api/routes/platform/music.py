import glob
import os
from xml.etree import ElementTree as ET

from app.core.config import DATABASE_PATH
from app.db.db_session import database_instance
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy import exc
from starlette.status import HTTP_400_BAD_REQUEST

from app.models.country import Country


router = APIRouter()


@router.get("/music/{music_id}")
async def get_music(music_id):
    rows = await database_instance.fetch_rows("""SELECT * FROM music WHERE music_id = {};""".format(music_id))
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such id"}]
    return rows


@router.get("/musicByName/{music_name}")
async def get_music_by_name(music_name):
    rows = await database_instance.fetch_rows("""SELECT * FROM music WHERE name = '{}';""".format(music_name), as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such name tag"}]
    rows.sort(key=lambda x: x['title'])
    return rows


@router.get("/musicByCountry/{country}")
async def get_music_by_country(country):
    query = """SELECT music_id, title, midi FROM music WHERE country = '{}';""".format(country)
    if country == 'All':
        query = """SELECT music_id, title, midi FROM music;"""

    rows = await database_instance.fetch_rows(query, as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such name tag"}]
    rows.sort(key=lambda x: x['title'])
    return rows

@router.get("/musicByCountryWithRhythmLevels/{country}")
async def get_music_by_country(country):
    query = """SELECT music_id, title, midi, genre, rhythmic_level, meter_level FROM music WHERE country = '{}';""".format(country)
    if country == 'All':
        query = """SELECT music_id, title, midi, genre, rhythmic_level, meter_level FROM music;"""

    rows = await database_instance.fetch_rows(query, as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such name tag"}]
    rows.sort(key=lambda x: x['title'])
    return rows

@router.get("/musicByCountryForSing/{country}")
async def get_music_by_country(country):
    query = """SELECT music_id, title, midi, lyrics, has_music_lyrics, genre, melodic_level FROM music WHERE country = '{}' AND has_music_lyrics IS True;""".format(country)
    if country == 'All':
        query = """SELECT music_id, title, midi, lyrics, has_music_lyrics, genre, melodic_level FROM music WHERE has_music_lyrics IS True;"""

    rows = await database_instance.fetch_rows(query, as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such name tag"}]

    rows.sort(key=lambda x: x['title'])
    return rows