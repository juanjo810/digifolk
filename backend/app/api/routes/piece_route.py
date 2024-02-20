from app.api.schemas.col_schema import PieceColSc
from app.models.items import ListItem
from fastapi import APIRouter, Request, Depends, UploadFile, File
from fastapi_sqlalchemy import db
from sqlalchemy import text, and_, or_
from fastapi.responses import Response, FileResponse
from app.models.piece import Piece
from app.models.collection import PieceCol
from app.api.schemas.piece_schema import PieceSc
from app.api.parsers.mtc_extractor import MTCExtractor
from typing import Dict
from app.api.routes.col_route import get_col
from app.core.config import CODE_SEP,SEPARATOR as SEP
import pandas as pd
import music21 as m21
import csv
from xml.etree import ElementTree as ET
from typing import Optional
from io import BytesIO
from app.api.routes.utils import piece_model_to_dict
import json
import base64


NAME_SPACE = {'mei': 'http://www.music-encoding.org/ns/mei'}


router = APIRouter()


## CREATE PIECE
@router.post("/createPiece")
#def create_piece(pc: PieceSc=Depends(), midi: Optional[UploadFile] = File(None)):
def create_piece(pc: PieceSc):

    
    #midi_data = pc.midi.read()
    
    db_music = Piece(publisher=pc.publisher, creator=pc.creator, title=pc.title, rights=pc.rights, date=pc.date,
    type_file=pc.type_file, contributor_role=pc.contributor_role,desc=pc.desc, rightsp=pc.rightsp,
    creatorp_role=pc.creatorp_role,contributorp_role=pc.contributorp_role, alt_title=pc.alt_title, datep=pc.datep, descp=pc.descp, type_piece=pc.type_piece, 
    formattingp=pc.formattingp,subject=pc.subject, language=pc.language, relationp=pc.relationp, hasVersion=pc.hasVersion, isVersionOf=pc.isVersionOf,
    coverage=pc.coverage,genre=pc.genre,meter=pc.meter,tempo=pc.tempo,real_key=pc.real_key,mode=pc.mode,instruments=pc.instruments,title_xml=pc.title_xml,
    xml=pc.xml, mei=pc.mei, midi=pc.midi, audio=pc.audio,video=pc.video,user_id=pc.user_id,review=pc.review,col_id=pc.col_id)
    try:
        db.session.add(db_music)
        db.session.commit()
        db.session.refresh(db_music)
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}  # Return an error message
    return db_music


#EDIT PIECE
@router.post("/editPiece")
def edit_piece(piece: PieceSc):
    
    ## We need the id to know identify the piece
    if (piece.music_id!=0):
        old_music=db.session.query(Piece).filter(Piece.music_id==piece.music_id).one()
    """if midi != None or midi != "":
        midi_data = midi.read()
        piece.midi=midi_data"""
    if old_music is not None:
        update_data = piece.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(old_music, key, value)

        # Commit the changes
        db.session.commit()
        db.session.refresh(old_music)
        return old_music
    return [{"msg": "Piece not found"}]

## REMOVE PIECE
@router.delete("/removePiece")
def delete_piece(id: str):
    if id != "":
        if db.session.query(Piece).filter(Piece.music_id == id).count() > 0:
            a=db.session.query(Piece).filter(Piece.music_id == id).delete()
            db.session.commit()
            return [{"msg": "Rm done"}]
    
    return [{"msg": "Piece not found"}]


# GET PIECES
@router.get("/getPiece")
#def get_piece(title: str = None, creator: Dict = None, id: int = None):
def get_piece(id: int):

    if id != None:
        pieces=db.session.query(Piece).filter(Piece.music_id==id).first()
    else:
        return {"msg": "Provide Title, Creator or id"}
    
    if pieces == None:
        return {"msg": "No piece with such data"}
   
    return pieces.__dict__


#GET LIST OF PIECES
@router.get("/getListOfPieces")
def get_list_music():
    ##Retrieve also songbooks
    #pieces=db.session.query(Piece,PieceCol).join(PieceCol).filter(Piece.col_id==PieceCol.col_id).all()
    pieces=db.session.query(Piece.music_id,Piece.title,Piece.review).all()
    return pieces

@router.post("/getPieceFromFilters")
def get_pieces_filtered(pc: PieceSc):

# Define your JSON entity representing filters
    filters = dict(pc)

    # Create a list to hold individual filter conditions
    filter_conditions = []
    filter_values = []
    cuenta=0
    # Loop through the filters and build filter conditions dynamically
    for field, filter_value in filters.items():
        if filter_value:
            # Case-insensitive filter using ilike if it's a string
            if isinstance(filter_value, str) and filter_value != "":
                filter_condition = Piece.__table__.columns[field].ilike(f'%%{filter_value}%')
                filter_conditions.append(filter_condition)
                #filter_values.append(str(filter_value))
            else:
                if isinstance(filter_value, list) and any(item not in ("", {}) for item in filter_value):
                    # For non-string fields, use equality
                    
                    filter_condition = or_(*[Piece.__table__.columns[field] == [val] for val in filter_value])
                    filter_conditions.append(filter_condition)
                    #filter_values.append(str(filter_value))
                elif isinstance(filter_value, int) and filter_value >= 0:
                    filter_value=int(filter_value)
                    filter_condition = Piece.__table__.columns[field] == filter_value
                    filter_conditions.append(filter_condition)
                    #filter_values.append(str(filter_value))
                

    filter_condition = Piece.__table__.columns["review"] == True
    filter_conditions.append(filter_condition)              
    
    # Combine the filter conditions using 'and_' to create the final filter
    combined_filter = and_(*filter_conditions)
    #return str(filter_values)# Query the database using the combined filter
    results = db.session.query(Piece).filter(combined_filter).all()
    return results

@router.post("/uploadMidi")
def upload_midi(piece_id: int, file: UploadFile = File(...)):
    midi_data = file.file.read()
    #get piece from db
    piece=db.session.query(Piece).filter(Piece.music_id==piece_id).first()
    piece.midi=midi_data
    db.session.commit()
    db.session.refresh(piece)
    return {"msg": "Midi uploaded"}


""" 
#MAP FROM EXCEL FILE
@router.post("/PieceFromExcel")
def piece_excel_to_sqlalchemy(file: UploadFile = File(...), user_id: int=None, xml: str=None, mei: str=None, midi: bytes=None):
    excel_file= file.file.read()
    #excel_file="Metadatadummy.xlsx"
    sheet_name="Pieces"
    df = pd.read_excel(excel_file, sheet_name=sheet_name,skiprows=[0,1,3,4,5],index_col=None,dtype=str)
    df = df.drop([0,1,3,4,5])
    df_header=df.iloc[0].values
    df.columns=df_header

    df_p = df.iloc[:, :]  # Columns A to AJ
    #df_c = df.iloc[:, 36:]
    
    #duplicated_columns = df_c.columns[df_c.columns.duplicated()]
    lpieces=list()
    #return json.dumps(str(df_c.dtypes))#to_json(orient='records')
    ##CHECK if collection exists:
    for index, row in df_p.iterrows():
            
     
        row=df_p.iloc[index]

        cont= row["Contributor"].split(SEP)
        roles=row["Role"].split(SEP)
        cont_role=list()
        for ci,ri in zip(cont,roles):
            ri=ri.split(CODE_SEP)[0]
            cont_role.append(dict(name=ci,role=int(ri)))

        cont= row["ContributorP"].split(SEP)
        roles=row["RoleCP"].split(SEP)
        gend=row["GenderCP"].split(SEP)
        cont2_role=list()
        for ci,ri in zip(cont,roles):
            ri=ri.split(CODE_SEP)[0]
            cont2_role.append(dict(name=ci,role=int(ri),gender=gend))
        
        creators= row["CreatorP"].split(SEP)
        roles=row["RoleP"].split(SEP)
        gend=row["GenderP"].split(SEP)
        c_role=list()
        for ci,ri in zip(creators,roles):
            ri=ri.split(CODE_SEP)[0]
            c_role.append(dict(name=ci,role=int(ri),gender=gend))

        tl=row["Temporal"].split(SEP)
        temp=dict(century=tl[0],decade=tl[1],year=tl[2])

        tl=row["Spatial"].split(SEP)
        spat=dict(country=tl[0],state=tl[1],location=tl[2])
        #return col_list
"""
"""
    EXCEL CONTROLLER
    Function to import data from an excel file to the database.
    The Excel file contains the metadata of the pieces and the collections that belongs to.
    1.- The function reads the file
    2.- The function reads the collections from the file
    3.- The function imports the collections to the database
    4.- The function reads the pieces from the file
    5.- The function imports the pieces to the database
"""
@router.post("/ExcelController")
def excel_controller(file: UploadFile = File(...), user_id: int=None,):
    # Read the Excel File
    excel_file= file.file.read()
    #excel_file="Metadatadummy.xlsx"

    # Read the Collections from the file
    sheet_name="Collections"
    df = pd.read_excel(excel_file, sheet_name=sheet_name,skiprows=[0,1,3,4,5],index_col=None,dtype=str)
    df_c = df.iloc[:, :]  # Columns A to AJ
    #duplicated_columns = df_c.columns[df_c.columns.duplicated()]
    col_list=list()
    new_col_list=list()
    #return json.dumps(str(df_c.dtypes))#to_json(orient='records')
    ##CHECK if collection exists:
    for index, row in df_c.iterrows():
        columns = df.columns.tolist()
        # Convert the column names to JSON
        cont=row["ContributorC"].split(SEP)
        roles=row["RoleCC"].split(SEP)
        cont_role=list()
        for ci,ri in zip(cont,roles):
            cont_role.append(dict(name=ci,role=ri.split(CODE_SEP)[0]))
        
        creators= row["CreatorC"].split(SEP)
        roles=row["RoleC"].split(SEP)
        c_role=list()
        for ci,ri in zip(creators,roles):
            c_role.append(dict(name=ci,role=ri.split(CODE_SEP)[0]))
        
        tl=row["TemporalC"].split(SEP)
        temp=dict(century=tl[0],decade=tl[1],year=tl[2])

        tl=row["SpatialC"].split(SEP)
        spatial=dict(country=tl[0],state=tl[1],location=tl[2])
        #return col_list
        pc = PieceColSc(code=row["CodeC"],title=row["TitleC"],rights=row["RightsC"].split(CODE_SEP)[0],date=row["DateC"],type_file=row["TypeC"].split(CODE_SEP)[0], contributor_role=cont_role, creator=c_role, temporal=temporal, spatial=spatial, description=row["DescriptionC"], rights=row["RightsC"].split(CODE_SEP)[0], user_id=user_id,review=True)
        item = PieceCol(code=pc.code,title=pc.title,rights=pc.rights,date=pc.date,type_file=pc.type_file,contributor_role=pc.contributor_role,creator=pc.creator,temporal=pc.temporal,spatial=pc.spatial,description=pc.description,rights=pc.rights,user_id=pc.user_id,review=pc.review)
        col_list.append(item)
        new_col_list.append(pc.code)
        db.session.add(item)
    db.session.commit()
    #return col_list
    # Read the Pieces from the file
    sheet_name="Pieces"
    df = pd.read_excel(excel_file, sheet_name=sheet_name,skiprows=[0,1,3,4,5],index_col=None,dtype=str)
    df_p = df.iloc[:, :]  # Columns A to AJ
    #df_c = df.iloc[:, 36:]
    
    #duplicated_columns = df_c.columns[df_c.columns.duplicated()]
    lpieces=list()
    #return json.dumps(str(df_c.dtypes))#to_json(orient='records')
    ##CHECK if collection exists:
    piece_excel_to_sqlalchemy(df_p, user_id, col_list)
    


@router.post("/ExcelToPiece")
def piece_excel_to_sqlalchemy(file: UploadFile = File(...), user_id: int=None, xml: str=None, mei: str=None, midi: bytes=None, col_id_list: list=None):
    excel_file= file.file.read()
    #excel_file="Metadatadummy.xlsx"
    sheet_name="Pieces"
    df = pd.read_excel(excel_file, sheet_name=sheet_name,skiprows=[0,1,3,4,5],index_col=None,dtype=str)
    """df = df.drop([0,1,3,4,5])
    df_header=df.iloc[0].values
    df.columns=df_header"""

    df_p = df.iloc[:, :]  # Columns A to AJ
    #df_c = df.iloc[:, 36:]
    
    #duplicated_columns = df_c.columns[df_c.columns.duplicated()]
    lpieces=list()
    #return json.dumps(str(df_c.dtypes))#to_json(orient='records')
    ##CHECK if collection exists:
    for index, row in df_p.iterrows():
            
     
        row=df_p.iloc[index]

        cont= row["Contributor"].split(SEP)
        roles=row["Role"].split(SEP)
        cont_role=list()
        for ci,ri in zip(cont,roles):
            ri=ri.split(CODE_SEP)[0]
            cont_role.append(dict(name=ci,role=int(ri)))

        cont= row["ContributorP"].split(SEP)
        roles=row["RoleCP"].split(SEP)
        gend=row["GenderCP"].split(SEP)
        cont2_role=list()
        for ci,ri in zip(cont,roles):
            ri=ri.split(CODE_SEP)[0]
            cont2_role.append(dict(name=ci,role=int(ri),gender=gend))
        
        creators= row["CreatorP"].split(SEP)
        roles=row["RoleP"].split(SEP)
        gend=row["GenderP"].split(SEP)
        c_role=list()
        for ci,ri in zip(creators,roles):
            ri=ri.split(CODE_SEP)[0]
            c_role.append(dict(name=ci,role=int(ri),gender=gend))

        tl=row["Temporal"].split(SEP)
        temp=dict(century=tl[0],decade=tl[1],year=tl[2])

        tl=row["Spatial"].split(SEP)
        spat=dict(country=tl[0],state=tl[1],location=tl[2])

        #get col_id from Collection where code=row["col_id"] with sqlalchemy query
        colect_id=db.session.query(PieceCol.col_id).filter(PieceCol.code==row["Col_id"]).first()
        #return col_list
        if col_id_list:
            colect_id=col_id_list[int(row["Col_id"])]
        else:
            colect_id=db.session.query(PieceCol.col_id).filter(PieceCol.code==row["Col_id"]).first()

        pc = PieceSc(publisher=row["Publisher"],contributor_role=cont_role,creator=row["Creator"],title=row["Title"].split(SEP),rights=row["Rights"].split(CODE_SEP)[0],
                     date=row["Date"],type_file=row["Type"].split(CODE_SEP)[0], desc=row["Description"],rightsp=row["RightsP"].split(CODE_SEP)[0],contributorp_role=cont2_role, 
                     creatorp_role=c_role,alt_title=row["AlternativeTitle"], datep=row["DateP"],descp=row["DescriptionP"],type_piece=row["TypeP"].split(CODE_SEP)[0],
                     formattingp=row["FormatP"],hasVersion=row["HasVersion"].split(SEP),subject=row["Subject"].split(SEP),language=row["Language"], spatial=spat, temporal=temp,
                     isVersionOf=row["IsVersionOf"].split(SEP),coverage=row["Coverage"], relationp=row["Relation"].split(SEP), real_key=row["Key"], mode=row["Mode"],
                     meter=row["Metre"], tempo=row["Tempo"], genre=row["Genre"].split(SEP),instruments=row["Instrument"].split(SEP),xml=xml,mei=mei,midi=midi,audio=row["Audio"],
                     video=row["Video"],user_id=user_id,col_id=colect_id,review=True,title_xml=row["Identifier"])
        
        
        item = Piece(publisher=pc.publisher, creator=pc.creator, title=pc.title, rights=pc.rights, date=pc.date,
            type_file=pc.type_file, contributor_role=pc.contributor_role,desc=pc.desc, rightsp=pc.rightsp,
            creatorp_role=pc.creatorp_role,contributorp_role=pc.contributorp_role, alt_title=pc.alt_title, datep=pc.datep, descp=pc.descp, type_piece=pc.type_piece, 
            formattingp=pc.formattingp,subject=pc.subject, language=pc.language, relationp=pc.relationp, hasVersion=pc.hasVersion, isVersionOf=pc.isVersionOf,
            coverage=pc.coverage,genre=pc.genre,meter=pc.meter,tempo=pc.tempo,real_key=pc.real_key,mode=pc.mode,instruments=pc.instruments, temporal=pc.temporal,spatial=pc.spatial,
            xml=pc.xml, mei=pc.mei, midi=pc.midi, audio=pc.audio,video=pc.video,user_id=pc.user_id,col_id=pc.col_id,review=pc.review,title_xml=pc.title_xml)#,col_id=pc.col_id)
 
            
        lpieces.append(item)
        db.session.add(item)
    
    db.session.commit()
        
    return {"msg": "Pieces added"}

@router.post("/piecesToCsv")
def piece_to_csv(piece_id: int=None):

    #get piece from db
    if piece_id== None:
        piece=db.session.query(Piece).all()
        update_data = [item.__dict__ for item in piece]
        #return json.dumps(pd.DataFrame([update_data]).columns.to_list())
        df = pd.DataFrame.from_records(update_data,columns=Piece.__table__.columns.keys())
    else:
        piece=db.session.query(Piece).filter(Piece.music_id==piece_id).first()
        if piece ==None:
            return {"msg": "Piece not found"}
        update_data = piece.__dict__ 
        df = pd.DataFrame([update_data],columns=Piece.__table__.columns.keys())
    
    # Specify the file path where you want to save the CSV file
    file_path = 'my_data.csv'

    # Save the DataFrame to a CSV file
    df.to_csv(file_path, index=False)

    return FileResponse(file_path, headers={"Content-Disposition": "attachment; filename=my_data.csv"})


@router.post("/MeiToCsv")
def parse_mei_to_metadata():
    mei_path="ES-1913-B-JSV-001.mei"
    # score=parseEndings(mei_path)
    score = MTCExtractor(mei_path,ET.parse(mei_path))
    # Parse the XML file
    tree = ET.parse(mei_path)
    root = tree.getroot()

    # Start exploring from the root element
    score.explore_xml_element(root)

    score.m21_to_midi("ES-1913.mid")
    # score = m21.converter.parse("prob.mei", format='mei', forceSource=True)
    # Load the MEI file into a music21 stream
    
    
    metadata = {}

    return score
    try:
        # Extract metadata from the music21 stream
        if 'composer' in score.metadata:
            metadata['composer'] = score.metadata.composer
        if 'title' in score.metadata:
            metadata['title'] = score.metadata.title
        if 'date' in score.metadata:
            metadata['date'] = score.metadata.date

        # You can add more fields here based on the metadata available in your MEI files
        csv_path="probandocsv.csv"
        save_metadata_to_csv(metadata, csv_path)

        mf = score.to_midi()

        # Save the MIDI file
        mf.open("./output.mid", 'wb')
        mf.write()
        mf.close()
    except Exception as e:
        print ("ups")
        

    

    except IOError as e:
        print("Error saving metadata to CSV:", e)

def parseEndings(song):
    """
    Parse the Ending Tag of MEI that was giving errors
    """
    ending_streams = {}

    mei_file = ET.parse(song)
    score_def = mei_file.getroot().findall('.//mei:scoreDef', NAME_SPACE)

    string_scoredef = ET.tostring(score_def[0], encoding="unicode")
    string_begin = """
                    <mei meiversion="4.0.0" xmlns="http://www.music-encoding.org/ns/mei" xmlns:xlink="http://www.w3.org/1999/xlink">
                        <music>
                            <score>
                    """
    string_end = """</score></music></mei>"""

    endings = mei_file.getroot().findall('.//mei:ending', NAME_SPACE)

    for end in endings:
        string_child = "<section>"
        for child in end:
            string_child += ET.tostring(child, encoding="unicode")
        string_child += "</section>"

        mei_string = string_begin + string_scoredef + string_child + string_end
        file = open("prob.mei", "w")
        a = file.write(mei_string)
        file.close()
        score = m21.converter.parse(
            mei_string, format='mei', forceSource=True)
        ending_streams[end[0].get('n')] = (score, end.get('n'))
    return ending_streams

    

