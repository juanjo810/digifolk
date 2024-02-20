from fastapi import APIRouter, Body, Depends, HTTPException, Request
from starlette.status import HTTP_400_BAD_REQUEST

from app.db.db_session import database_instance
from app.core.config import DATABASE_PATH
from sqlalchemy import exc

import os
from xml.etree import ElementTree as ET

router = APIRouter()


@router.get("/getModels")
async def get_all_models():
    rows = await database_instance.fetch_rows("""SELECT * FROM gen_model;""")
    print(rows, flush=True)
    return [{"msg": "Oracle Retrieved"}]


@router.delete("/removeModels")
async def remove_models():
    rows = await database_instance.fetch_rows("""DELETE FROM gen_model;""")
    print(rows, flush=True)
    return [{"msg": "Removed Oracle"}]
