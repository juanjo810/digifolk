from app.core.config import DATABASE_PATH
from app.db.db_session import database_instance
from fastapi import APIRouter

router = APIRouter()

@router.post("/addDanceStep")
async def add_step(name='', tempo='All', description=''):
    """
    Add a Single Song to Database
    """

    query = 'INSERT OR REPLACE INTO dance_steps (name, tempo, description) VALUES (?, ?, ?)'

    cursor = await database_instance.connection.cursor()
    await cursor.execute(
        query,
        (name, tempo.capitalize(), description)
    )
    await database_instance.connection.commit()
    print(cursor.rowcount, "Record inserted successfully into DanceStep table")
    await cursor.close()

    return [{"msg": 'Record inserted successfully into DanceStep table'}]

@router.get("/getDanceSteps")
async def get_all_steps():
    rows = await database_instance.fetch_rows("""SELECT * FROM dance_steps;""", as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No dance steps in database"}]
    return rows

@router.delete("/removeDanceStep")
async def remove_step(name=None, id=None):

    query = f"""DELETE FROM dance_steps WHERE step_id = '{id}';"""
    if name:
        query = f"""DELETE FROM dance_steps WHERE name = '{name}';"""
    elif not id:
        return [{"msg": "No name or id of dance step to delete from database"}]

    _ = await database_instance.fetch_rows(query)
    return [{"msg": "Dance Step deleted from database"}]
