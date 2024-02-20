from sqlite3 import IntegrityError
from app.db.db_session import database_instance
from app.db.security import hash_password, manager
from fastapi import APIRouter

router = APIRouter()


@router.delete("/removeUser")
@manager.user_loader()
async def delete_user(email: str):
    _ = await database_instance.fetch_rows(f"""DELETE FROM user WHERE email = "{email}";""", as_dict=True)
    return [{"msg": f"User with email {email} deleted from database"}]

@manager.user_loader()
async def get_user(username: str = None, email: str = None, id: int = None):

    if email is not None:
        query = f"""SELECT * FROM user WHERE email = "{email}";"""
    elif username is not None:
        query = f"""SELECT * FROM user WHERE username = "{username}";"""
    elif id is not None:
        query = f"""SELECT * FROM user WHERE user_id = {id};"""
    else:
        return [{"msg": "Provide E-Mail or Username"}]

    rows = await database_instance.fetch_rows(query, as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No user with such username/email"}]
    return rows

async def create_user(username, email, password):
    """
    Sign In Processing
    """
    hashed_password = hash_password(password)

    query = 'INSERT INTO user (username, email, password, is_admin) VALUES (?, ?, ?, ?)'

    try:
        cursor = await database_instance.connection.cursor()
        await cursor.execute(
            query,
            (username, email, hashed_password, False)
        )
        await database_instance.connection.commit()
        print(cursor.rowcount, "Record inserted successfully into User table")
        await cursor.close()
        return True, cursor.lastrowid
    except IntegrityError:
        return False, f'email address "{email}" already exists in database'
