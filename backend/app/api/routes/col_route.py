from fastapi import APIRouter, HTTPException, Request, Depends, File, UploadFile
from fastapi_sqlalchemy import db
from sqlalchemy import text, and_, or_
from app.models.piece import Piece
from app.api.schemas.piece_schema import PieceSc
from app.models.collection import PieceCol
from app.api.schemas.col_schema import PieceColSc
from typing import Dict
from sqlalchemy import text
from app.core.config import CODE_SEP,SEPARATOR as SEP
import pandas as pd
from app.api.routes.utils import extract_excel_collection_fields, is_empty


router = APIRouter()


## CREATE COLLECTION
@router.post("/createCol")
def create_col(col: PieceColSc):
    """
    Create piece process
    """
    ## IMPORTANT! A way to detect same collection???? #############
  
    db_col = PieceCol(title=col.title, rights=col.rights, extent=col.extent, subject=col.subject, date=col.date, language=col.language, creator_role=col.creator_role,
    contributor_role=col.contributor_role, publisher=col.publisher, source=col.source, source_type=col.source_type, description=col.description,
    formatting=col.formatting, relation=col.relation, spatial=col.spatial,temporal=col.temporal,rights_holder=col.rights_holder,coverage=col.coverage,review=col.review)
    
 
    db.session.add(db_col)
    db.session.commit()
    return db_col
    

#EDIT COLLECTION
@router.post("/editCol")
def edit_col(col: PieceColSc):
    
    ## We need the id to know identify the piece
    if (col.col_id!=""):
        old_music=db.session.query(PieceCol).filter(PieceCol.col_id==col.col_id).first()
    
    if old_music is not None:
        update_data = col.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(old_music, key, value)
        # Commit the changes
        db.session.commit()

        return old_music
    return [{"msg": "Collection not found"}]

## REMOVE COLLECTION
@router.delete("/removeCol")
def delete_col(id: str):
    if not id:
        raise HTTPException(status_code=400, detail="Collection ID is required")

    # Usa la sesión de db de fastapi_sqlalchemy para buscar la colección
    collection = db.session.query(PieceCol).filter(PieceCol.col_id == id).first()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    # Elimina las piezas asociadas
    db.session.query(Piece).filter(Piece.col_id == collection.col_id).delete()

    # Elimina la colección
    db.session.delete(collection)

    # Confirma los cambios
    db.session.commit()

    return {"msg": "Collection and pieces removed successfully"}


# GET COLLECTIONS
@router.get("/getCol")
def get_col(title: str = None, creator: Dict = None, id: int = None):

    if title is not None:
        pieces=db.session.query(PieceCol).filter(text(":value = ANY (piece_col.title)")).params(value=title).all()
        #pieces=db.session.query(PieceCol).filter(PieceCol.title==title).all()
    elif creator is not None:
        pieces=db.session.query(PieceCol).filter(PieceCol.creator_role["name"]==creator).all()
    elif id is not None:
        pieces=db.session.query(PieceCol).filter(PieceCol.col_id==id).all()
    else:
        return [{"msg": "Provide Title, Creator or id"}]
    
    if len(pieces)==0:
        return None
    return pieces


#GET LIST OF COLLECTIONS
@router.get("/getListOfCols")
def get_list_col():
    ##Retrieve also songbooks
    cols=db.session.query(PieceCol.col_id,PieceCol.title,PieceCol.review,PieceCol.code).all()
    return cols

@router.post("/getPieceFromFilters")
def get_pieces_filtered(col: PieceColSc):

# Define your JSON entity representing filters
    filters = dict(col)

    # Create a list to hold individual filter conditions
    filter_conditions = []
    filter_values = []
    cuenta=0
    # Loop through the filters and build filter conditions dynamically
    for field, filter_value in filters.items():
        if filter_value:
            # Case-insensitive filter using ilike if it's a string
            if isinstance(filter_value, str) and filter_value != "":
                filter_condition = PieceCol.__table__.columns[field].ilike(f'%%{filter_value}%')
                filter_conditions.append(filter_condition)
                #filter_values.append(str(filter_value))
            else:
                if isinstance(filter_value, list) and any(item not in ("", {}) for item in filter_value):
                    # For non-string fields, use equality
                    
                    filter_condition = or_(*[PieceCol.__table__.columns[field] == [val] for val in filter_value])
                    filter_conditions.append(filter_condition)
                    #filter_values.append(str(filter_value))
                elif isinstance(filter_value, int) and filter_value >= 0:
                    filter_value=int(filter_value)
                    filter_condition = PieceCol.__table__.columns[field] == filter_value
                    filter_conditions.append(filter_condition)
                    #filter_values.append(str(filter_value))
                
    filter_condition = PieceCol.__table__.columns["review"] == True
    filter_conditions.append(filter_condition) 
                    
    
    # Combine the filter conditions using 'and_' to create the final filter
    combined_filter = and_(*filter_conditions)
    #return str(filter_values)# Query the database using the combined filter
    results = db.session.query(PieceCol).filter(combined_filter).all()
    return results

#GET PIECES FROM COLLECTION
@router.get("/getPiecesFromCol")
def get_pieces_from_col(id:str):
    list_p= db.session.query(Piece.music_id,Piece.title).filter(Piece.col_id==id).all()
    return list_p
    

#MAP FROM EXCEL FILE
@router.post("/ExcelToCol")
def col_excel_to_sqlalchemy(file: UploadFile = File(...)):
    #excel_file= file.file.read()
    excel_file="Metadata template - IE_1797_BT_EB.xlsx"
    sheet_name="Collections"
    df = pd.read_excel(excel_file, sheet_name=sheet_name,skiprows=[0,1,3,4,5],index_col=None,dtype=str)
    """df = df.drop([0,1,3,4,5])
    df_header=df.iloc[0].values
    df.columns=df_header"""

    df_c = df.iloc[:, :]

    ##CHECK if collection exists:
    for index, row in df_c.iterrows():
        row = df_c.iloc[index]
        collection_fields = extract_excel_collection_fields(row)

        # We create the PieceColSc from the dictionary returned by extract_excel_fields
        col = PieceColSc(**collection_fields)
        
        # We create the PieceCol object from the PieceColSc object
        db_col  = PieceCol(title=col.title, rights=col.rights, extent=col.extent, subject=col.subject, date=col.date, language=col.language, creator_role=col.creator_role,
            contributor_role=col.contributor_role, publisher=col.publisher, source=col.source, source_type=col.source_type, description=col.description,
            formatting=col.formatting, relation=col.relation, spatial=col.spatial,temporal=col.temporal,rights_holder=col.rights_holder,coverage=col.coverage,review=col.review,code=col.code)
        
        print(col)

        db.session.add(db_col)
    db.session.commit()

    
    return {"msg": "Collections added"}
