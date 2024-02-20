from fastapi import APIRouter, Depends, HTTPException
from fastapi_sqlalchemy import db
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import User
from app.api.schemas.user_schema import *
from app.db.security import hash_password, manager, verify_password
from app.core.config import TOKEN_URL, DIGIFOLK_EMAIL_PASSWORD

import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def check(email):
    if(re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)):
        return True
    else:
        return False

router = APIRouter()

## CREATE USER
@router.post("/createUser")
def create_user(user: UserCreateSc):
    """
    Create user process
    """
    hashed_password = hash_password(user.password)
    num_users=1
    num_users=db.session.query(User).filter(User.email==user.email).count()
    num_names=db.session.query(User).filter(User.username==user.username).count()
    if num_users==0 and num_names==0:
        db_user = User(
            first_name=user.first_name, last_name=user.last_name, email=user.email, username=user.username, 
            password=hashed_password, is_admin=user.is_admin, institution=user.institution
        )
        db.session.add(db_user)
        db.session.commit()
        #detect if the commit was successful
        db.session.refresh(db_user)
        if db_user is not None:
            #send an email to the user
            send_email(user.email)
        return db_user
    else:
        if num_names !=0:
            return [{"msg": "Username already registered"}]
        else:
            return [{"msg": "Email already registered"}]


#EDIT USER
@router.post("/editUser")
def edit_user(user: UserSc):
    
    ## CHECK IF EMAIL IS ALREADY REGISTERED!!!
    old_user=db.session.query(User).filter(User.user_id==user.user_id).one()
    if old_user is not None:
        update_data = user.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(old_user, key, value)

        # Commit the changes
        db.session.commit()
        db.session.refresh(old_user)
        return UserSc(**old_user.__dict__)
    else:
        return [{"msg": "User not found"}]
    


    if old_item:
        # Update the data using Pydantic
        update_data = item.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(old_item, key, value)

        # Commit the changes
        db.session.commit()
        #db.session.refresh(old_item)
        return old_item

    return [{"msg": "Collection not found"}]
    
#CHANGE PASSWORD
@router.post("/editPassword")
def edit_password(pd: PasswordChange):
    user=db.session.query(User).filter(User.user_id==pd.user_id).one()
    if user is not None:
        if verify_password(pd.old_password, user.password):
            hashed_password = hash_password(pd.new_password)
            user.password=hashed_password
            db.session.commit()
            return [{"msg": "OK"}]
        else:
            return [{"msg": "Incorrect password"}]
    else:
        return [{"msg": "User not found"}]

## REMOVE USER
@router.delete("/removeUser")
def delete_user(email: str=None, username:str=None, id:int=None):
    if email is not None:
        a=db.session.query(User).filter(User.username == username).delete()
        db.session.commit()
        return [{"msg": "Rm done"}]
    elif username is not None:
        db.session.query(User).filter(User.email == email).delete()
        db.session.commit()
        return [{"msg": "Rm done"}]
    elif id is not None:
        db.session.query(User).filter(User.user_id == id).delete()
        db.session.commit()
        return [{"msg": "Rm done"}]
    else:
        return [{"msg": "Provide Id, E-Mail or Username"}]
    

# GET USER

#@router.get("/getUser")
@manager.user_loader()
def get_user(username: str = None, email: str = None, id: int = None):

    if email is not None:
        users=db.session.query(User).filter(User.email==email).first()
    elif username is not None:
        users=db.session.query(User).filter(User.username==username).first()
    elif id is not None:
        users=db.session.query(User).filter(User.user_id==id).first()
    else:
        return [{"msg": "Provide E-Mail or Username"}]
    
    if users == None:
        return [{"msg": "No user with such username/email"}]
    return users

#GET LIST OF USERS
@router.get("/getListOfUsers")
def get_list_users():
    users=db.session.query(User).all()
    user_list = UserList(users=[UserSc(**user.__dict__) for user in users])
    return user_list


# PROCESS LOGIN
@router.post(TOKEN_URL)
async def login(data: OAuth2PasswordRequestForm = Depends()):
    password = data.password

    if check(data.username):
        email = data.username
        user = get_user(email=email)
    else:
        username = data.username
        user = get_user(username=username)

    if not verify_password(password, user.password):
        return {'msg': f'Incorrect Password for user with email or username {data.username}', 'signed-in': False }

    access_token = manager.create_access_token(
        data=dict(sub=data.username)
    )
    return UserSc(**user.__dict__),access_token

# a method to log out user with fastapi-jwt-auth
"""@router.get('/logout')
def logout():
    
    return {'msg': 'Logged out successfully'}

"""


@router.get('/getAuth')
def protected_route(user=Depends(manager)):
     # 'manager' is your instance of LoginManager
    """
    Refresh an expired access token using a valid refresh token.
    """
    # You should handle your token validation logic here. This is just a basic example.
    # Check if the user is logged in and the refresh token is valid
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Decode and verify the refresh token

    # Generate a new access token
    """access_token_expires = timedelta(minutes=manager.token_expire_minutes)
    access_token_data = {
        "sub": str(user["id"]),
        "exp": datetime.utcnow() + access_token_expires,
    }
    access_token = jwt.encode(access_token_data, manager.secret_key, algorithm=manager.algorithm)
    """
    #manager.get_current_user(user.get("access_token"))
    access_token = manager.create_access_token(
        data=dict(sub=user.username)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# method to send an email to a given email address
@router.post('/sendEmail')
def send_email(receiver_email:str):

    # Email configuration
    sender_email = "noreply@digifolk.usal.es"  # A generic "noreply" address
    #receiver_email = "recipient@digifolk.usal.es"  # Recipient's email address
    subject = "User Registration"
    message_body = "This is a message to confirm your registration as user in our platform digifolk.usal.es."

    # Create a MIME message
    msg = MIMEText(message_body)
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject


    # SMTP server settings for Gmail (you might need to change these for other providers)
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    smtp_username = "eadigifolk@gmail.com"
    smtp_password = DIGIFOLK_EMAIL_PASSWORD

    
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp_server:
       smtp_server.login(smtp_username, smtp_password)
       smtp_server.sendmail(sender_email, receiver_email, msg.as_string())
    return("Message sent!")

@router.get('/logOut')
def protected_route_logOut(user=Depends(manager)):
     # 'manager' is your instance of LoginManager
    """
    Log out a user.
    """
    # You should handle your token validation logic here. This is just a basic example.
    # Check if the user is logged in and the refresh token is valid
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Decode and verify the refresh token

    # Generate a new access token
    """access_token_expires = timedelta(minutes=manager.token_expire_minutes)
    access_token_data = {
        "sub": str(user["id"]),
        "exp": datetime.utcnow() + access_token_expires,
    }
    access_token = jwt.encode(access_token_data, manager.secret_key, algorithm=manager.algorithm)
    """
    #manager.get_current_user(user.get("access_token"))
    manager.create_access_token(
        data=dict(sub=user.username)
    )
    return("Log out successful!")
    