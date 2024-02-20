from pydantic import BaseModel
from typing import Dict, List, Any

class ListItemSc(BaseModel):
    id : int 
    type_item : int
    name : str
    class Config:
        orm_mode = True