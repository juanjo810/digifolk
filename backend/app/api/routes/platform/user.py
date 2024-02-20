from xmlrpc.client import boolean
from app.core.config import TOKEN_URL
from app.db.db_session import database_instance
from app.db.security import manager, verify_password
from fastapi import APIRouter, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

