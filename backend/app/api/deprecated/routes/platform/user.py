from xmlrpc.client import boolean
from app.core.config import TOKEN_URL
from app.db.db_session import database_instance
from app.db.security import manager, verify_password
from app.api.routes.admin.users import get_user, create_user
from fastapi import APIRouter, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/changeProfilePicture")
async def change_user_profile(request: Request):

    body = await request.json()

    query = '''UPDATE user SET character_selected = ?, adereco_selected = ? WHERE user_id = ?'''
    cursor = await database_instance.connection.cursor()
    await cursor.execute(
        query,
        (body['character_selected'], body['adereco_selected'], body['user_id'])
    )
    await database_instance.connection.commit()
    print(cursor.rowcount, "Records updated successfully into User table")
    await cursor.close()
    return  [{"msg": '{} Records updated successfully into User table'.format(cursor.rowcount)}]


@router.post("/getUsernames")
async def get_users():
    rows = await database_instance.fetch_rows("""SELECT username, email FROM user""")
    if not rows or len(rows) == 0:
        return {"msg": "No users in database"}
    return rows

@router.post("/getUser")
async def get_users(email: str = None, username: str = None, id: int = None, with_email: boolean = False):

    if email is not None:
        user = await get_user(email=email)
    elif username is not None:
        user = await get_user(username=username)
    elif id is not None:
        user = await get_user(id=id)
    else:
        return {'msg': 'No info provided to get User'}

    user = user[0]

    if 'msg' in user:
        to_return = user
    else:
        to_return = { 'id': user['user_id'], 'username': user['username'], 'is_admin': user['is_admin'], 'profile': {'character': user['character_selected'], 'adereco': user['adereco_selected']}}
        if with_email:
            to_return['email'] = user['email']

    return to_return

import re
def check(email):
    if(re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)):
        return True
    else:
        return False

@router.post(TOKEN_URL)
async def login(data: OAuth2PasswordRequestForm = Depends()):
    password = data.password

    if check(data.username):
        email = data.username
        user = await get_user(email=email)
    else:
        username = data.username
        user = await get_user(username=username)

    user = user[0]

    if 'msg' in user:
        return user

    if not verify_password(password, user['password']):
        return {'msg': f'Incorrect Password for user with email or username {data.username}', 'signed-in': False }

    access_token = manager.create_access_token(
        data=dict(sub=data.username)
    )
    return { 'id': user['user_id'], 'username': user['username'], 'profile': {'character': user['character_selected'], 'adereco': user['adereco_selected']}, 'access_token': access_token, 'token_type': 'Bearer', 'signed-in': True}

@router.post("/signin")
async def signin(request: Request):
    """
    Sign In Processing
    """
    body = await request.json()

    if 'username' in body:
        username = body['username']
    else:
        username = 'Anonymous User'

    res, msg = await create_user(username.capitalize(), body['email'], body['password'])
    if res:
        access_token = manager.create_access_token(
            data=dict(sub=body['email'])
        )
        return { 'id': msg, 'username': username, 'profile': {'character': 0, 'adereco': 0}, 'access_token': access_token, 'token_type': 'Bearer', 'signed-in': True}
    else:
        return { 'msg': msg, 'signed-in': False }

@router.post("/signin-test")
async def signin2(email, password, username=None):
    """
    Sign In Processing for Testing
    """
    if username is None:
        username = 'Anonymous User'

    res, msg = await create_user(username.capitalize(), email, password)
    if res:
        access_token = manager.create_access_token(
            data=dict(sub=email)
        )
        return { 'id': msg, 'username': username, 'profile': {'character': 0, 'adereco': 0}, 'access_token': access_token, 'token_type': 'Bearer', 'signed-in': True}
    else:
        return { 'msg': msg, 'signed-in': False }