from fastapi import APIRouter, Request, Depends, File, UploadFile
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
from app.api.routes.utils import is_empty


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
    if id is not "":
        collection = db.session.query(PieceCol).filter(PieceCol.col_id == id).first()
         ## Retrieve pieces with col.id and remove them
        db.session.query(Piece).filter(Piece.col_id==collection.col_id).delete()
        db.session.delete(collection)
        #pieces.delete()
        #n.delete()
        db.session.commit()
        return [{"msg": "Rm done"}]
    else:
        return [{"msg": "Collection not found"}]


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
    excel_file= file.file.read()
    #excel_file="Metadatadummy.xlsx"
    sheet_name="Collections"
    df = pd.read_excel(excel_file, sheet_name=sheet_name,skiprows=[0,1,3,4,5],index_col=None,dtype=str)
    """df = df.drop([0,1,3,4,5])
    df_header=df.iloc[0].values
    df.columns=df_header"""

    df_c = df.iloc[:, :]
    
    #duplicated_columns = df_c.columns[df_c.columns.duplicated()]
    col_list=list()
    #return json.dumps(str(df_c.dtypes))#to_json(orient='records')
    ##CHECK if collection exists:
    for index, row in df_c.iterrows():
        columns = df.columns.tolist()

        # Convert the column names to JSON
      
       
        # Supposing we are working with numbers directly

        if is_empty(row["ContributorC"]):
            cont = row["ContributorC"].split(SEP)
        else:
            cont = []
        if is_empty(row["RoleCC"]):
            roles = row["RoleCC"].split(SEP)
        else:
            roles = []
        cont_role=list()
        for ci,ri in zip(cont,roles):
            cont_role.append(dict(name=ci,role=ri.split(CODE_SEP)[0]))
        
        if is_empty(row["CreatorC"]):
            creators= row["CreatorC"].split(SEP)
        else:
            creators=[]
        if is_empty(row["RoleC"]):
            roles=row["RoleC"].split(SEP)
        else:
            roles=[]
        c_role=list()
        for ci,ri in zip(creators,roles):
            c_role.append(dict(name=ci,role=ri.split(CODE_SEP)[0]))
        
        if is_empty(row["TemporalC"]):
            tl=row["TemporalC"].split(SEP)
            temp=dict(century=tl[0],decade=tl[1],year=tl[2])
        else:
            temp=dict(century="",decade="",year="")

        if is_empty(row["SpatialC"]):
            tl=row["SpatialC"].split(SEP)
            spat=dict(country=tl[0],state=tl[1],location=tl[2])
        else:
            spat=dict(country="",state="",location="")
        
        col=PieceColSc(title=row["SourceTitle"].split(SEP), rights=row["RightsC"].split(CODE_SEP)[0], extent=row["Extent"],
                    date=row["DateC"], subject=row["SubjectC"].split(SEP),language=row["LanguageC"],
                    contributor_role=cont_role, creator_role=c_role, publisher=row["PublisherC"],source=row["Source"], description=row["DescriptionC"],
                    source_type=row["TypeC"].split(CODE_SEP)[0], formatting=row["FormatC"], relation=row["RelationC"].split(SEP),
                    spatial=spat, temporal=temp, rights_holder=row["RightsHolder"],coverage=row["CoverageC"],code=row["CodeC"],review=True)
        
        db_col  = PieceCol(title=col.title, rights=col.rights, extent=col.extent, subject=col.subject, date=col.date, language=col.language, creator_role=col.creator_role,
            contributor_role=col.contributor_role, publisher=col.publisher, source=col.source, source_type=col.source_type, description=col.description,
            formatting=col.formatting, relation=col.relation, spatial=col.spatial,temporal=col.temporal,rights_holder=col.rights_holder,coverage=col.coverage,review=col.review,code=col.code)
        
        db.session.add(db_col)
    db.session.commit()

    
    return {"msg": "Collections added"}
