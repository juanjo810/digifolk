import os
from xml.etree import ElementTree as ET

from app.core.config import DATABASE_PATH
from app.db.db_session import database_instance
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy import exc
from starlette.status import HTTP_400_BAD_REQUEST

from app.composition.representation.parsers.music_parser import MusicParser
import app.composition as oracle_constr

router = APIRouter()

SELECT_FEATS = [
    #"basic.rest",
    #"basic.grace",
    "derived.seq_int",
    #"derived.beat_strength",
    "duration.length",
    "phrase.boundary",
    "metadata.genre"
]

@router.put("/createModel")
async def create_model(country='all'):
    """
    """
    query = 'SELECT music_id, name, phrases FROM music'
    if country != 'all':
        query = 'SELECT music_id, name, phrases FROM music WHERE country="{}";'.format(
            country)
    rows = await database_instance.fetch_rows(query)

    if not rows or len(rows) == 0:
        return [{"error": "No Music for the Country {} in the Database".format(country)}]

    indexes = []
    events = []

    for row in rows:
        if row[2] != '{}':
            path = os.sep.join([DATABASE_PATH, 'Viewpoints', row[1]])
            parser = MusicParser()
            parser.from_pickle(path, folders=[])
            keys = parser.get_part_events().keys()
            if len(keys) > 0:
                indexes.append(len(events))
                m_ev = parser.get_part_events()[list(keys)[0]]
                #m_nr_ev = [m for m in m_ev if m.not_rest_or_grace()]
                events.extend(m_ev)

    # Return from feature selection
    features, names, weights = oracle_constr.feature_selection(
        events, SELECT_FEATS)

    #weights['derived.beat_strength']['fixed'] = True
    information = oracle_constr.feature_extraction(features, names, weights)
    print("Extracted Features")

    oracle_path = oracle_constr.create_model_oracle(
        information, indexes,
        path=os.sep.join([DATABASE_PATH, 'Models', '']),
        country=country.capitalize(),
        verbose=True, plot=False,
        thresh_range=(0.05, 1.05, 0.05), ir_type='cum')

    return [{"msg": "Created Model for Country {} as {}".format(country, oracle_path)}]
