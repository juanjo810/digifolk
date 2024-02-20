from pydantic import BaseModel
from typing import List

class UserSc(BaseModel):    
    first_name: str
    last_name: str = None
    email: str
    username : str
    is_admin : bool
    institution : str
    user_id : int = None

    class Config:
        orm_mode = True


class UserCreateSc(UserSc):
    password : str
    class Config:
        orm_mode = True

class UserList(BaseModel):
    users: List[UserSc]


class PasswordChange(BaseModel):
    old_password: str
    new_password: str
    user_id: int
