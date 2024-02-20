from pydantic import BaseModel
from typing import Dict, List, Any

class PieceColSc(BaseModel):
    
    col_id: int = None
    title: List[str]
    rights: int
    extent: str
    subject: List[str]
    date: str
    language: str
    creator_role : List[Dict[str, str]] # Save it as a dictionary name, id of role
    contributor_role : List[Dict[str,str]] # Save it as a dictionary
    publisher : str # Save it as a dictionary
    source : str
    source_type : int
    description : str
    formatting : str
    relation : List[str]
    spatial : Dict [Any, Any] #Encoded as a dictionary with Century/Decade/Year
    rights_holder : str
    temporal : Dict[str,str] #Encoded as a dictionary with Country/State-Province/City-Location
    coverage : str
    review : bool
    code : str

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True