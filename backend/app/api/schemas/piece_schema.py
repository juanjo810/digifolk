from pydantic import BaseModel, Json
from typing import Dict, List, Any

class PieceSc(BaseModel):    
    #Uploader Metadata
    music_id : int = None
    publisher : str
    creator : str
    title : List[str]
    rights : int
    date : str
    type_file : int
    #formatting : str
    contributor_role : List[Dict[Any,Any]] # Save it as a dictionary creator+role
    desc : str
    
    # Piece Metadata
	
    rightsp : int #
    contributorp_role : List[Dict[Any,Any]] # save at as a dictionary contributor+role #
    creatorp_role : List[Dict[Any,Any]] # save at as a dictionary contributor+role+gender #
    alt_title : str
    datep : str #
    descp : str #
    type_piece : int #
    formattingp : str #
    subject : List[str] #
    language : str #
    relationp : List[str] #
    hasVersion : List[str]  #
    isVersionOf	: List[str] #
    coverage : str
    temporal : Dict [Any, Any] #Encoded as a dictionary with Century/Decade/Year
    spatial : Dict[str,str] #Encoded as a dictionary with Country/State-Province/City-Location
    
    
    # Music Analysis
    genre : List[str]  #
    meter : str #
    tempo : str #
    real_key : str #
    mode : str #
    instruments : List[str] #

    xml : str
    mei : str
    midi : bytes = None
    audio : str
    video : str
    user_id :int
    col_id : int = None
    review : bool
    title_xml : str
    
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True