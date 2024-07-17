import base64
import datetime
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
from typing import Dict, List
from app.api.routes.col_route import get_col
from app.core.config import CODE_SEP,SEPARATOR as SEP
import pandas as pd
import music21 as m21
import csv
from xml.etree import ElementTree as ET
from typing import Optional
from io import BytesIO
from app.api.routes.utils import piece_model_to_dict, split_cell, get_cell
import subprocess
import os
import aiofiles



NAME_SPACE = {'mei': 'http://www.music-encoding.org/ns/mei'}


router = APIRouter()


def convert_xml_to_mei(xml: str):
    """
    This function converts an XML file to MEI format
    """
    # Convert the XML file to MEI
    xml_path = "./input.xml"
    mei_path = "./output.mei"
    xml_decoded = base64.b64decode(xml)
    
    # Write xml to file
    with open(xml_path, "wb") as file:
        file.write(xml_decoded)
    # with open(xml_path, "w") as file:
    #    file.write(xml)

    

    subprocess.run("verovio -t mei " + xml_path + " -o " + mei_path, shell=True)
    
    # Read the MEI file
    with open(mei_path, "r") as file:
        piece_mei = file.read()
        mei = base64.b64encode(piece_mei.encode("utf-8")).decode('utf-8')

    # Remove both files
    subprocess.run("rm " + xml_path, shell=True)
    subprocess.run("rm " + mei_path, shell=True)
    
    return mei

## CREATE PIECE
@router.post("/createPiece")
#def create_piece(pc: PieceSc=Depends(), midi: Optional[UploadFile] = File(None)):
def create_piece(pc: PieceSc):

    
    #midi_data = pc.midi.read()

    if pc.xml != "" and pc.mei == "":
        pc.mei = convert_xml_to_mei(pc.xml)
    
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
        if piece.xml != old_music.xml:
            piece.mei = convert_xml_to_mei(piece.xml)
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
            db.session.query(Piece).filter(Piece.music_id == id).delete()
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
def excel_controller(file: UploadFile = File(...), mei: List[UploadFile] = None , xml: List[UploadFile] = None, user_id: int = None):
    # Read the Excel File
    excel_file= file.file.read()
    # excel_file="prueba.xlsx"

    # Read the Collections from the file
    sheet_name="Collections"
    df = pd.read_excel(excel_file, sheet_name=sheet_name,skiprows=[0,1,3,4,5],index_col=None,dtype=str)
    df_c = df.iloc[:, :]  # Columns A to AJ
    
    col_list=list()
    new_col_list=dict()

    ##CHECK if collection exists:
    for index, row in df_c.iterrows():
        print(row)
        columns = df.columns.tolist()
        # Convert the column names to JSON
        cont = split_cell(row["ContributorC"], SEP)
        roles = split_cell(row["RoleCC"], SEP)
        cont_role=list()
        for ci,ri in zip(cont,roles):
            cont_role.append(dict(name=ci,role=split_cell(ri, CODE_SEP)[0]))
        
        creators= split_cell(row["CreatorC"], SEP)
        roles=split_cell(row["RoleC"], SEP)
        c_role=list()
        for ci,ri in zip(creators,roles):
            c_role.append(dict(name=ci,role=split_cell(ri, CODE_SEP)[0]))

        tl=split_cell(row["TemporalC"], SEP)
        temp=dict(century=tl[0],decade=tl[1],year=tl[2])

        tl=split_cell(row["SpatialC"], SEP)
        spat=dict(country=tl[0],state=tl[1],location=tl[2])

        col = PieceColSc(title=split_cell(row["SourceTitle"],SEP), rights=split_cell(row["RightsC"], CODE_SEP)[0], extent=get_cell(row["Extent"]),
                    date=get_cell(row["DateC"]), subject=split_cell(row["SubjectC"], SEP),language=get_cell(row["LanguageC"]),
                    contributor_role=cont_role, creator_role=c_role, publisher=get_cell(row["PublisherC"]),source=row["Source"], description=row["DescriptionC"],
                    source_type=split_cell(row["TypeC"], CODE_SEP)[0], formatting=get_cell(row["FormatC"]), relation=split_cell(row["RelationC"], SEP),
                    spatial=spat, temporal=temp, rights_holder=get_cell(row["RightsHolder"]),coverage=get_cell(row["CoverageC"]),code=get_cell(row["CodeC"]),review=True)
        item = PieceCol(title=col.title, rights=col.rights, extent=col.extent, subject=col.subject, date=col.date, language=col.language, creator_role=col.creator_role,
            contributor_role=col.contributor_role, publisher=col.publisher, source=col.source, source_type=col.source_type, description=col.description,
            formatting=col.formatting, relation=col.relation, spatial=col.spatial,temporal=col.temporal,rights_holder=col.rights_holder,coverage=col.coverage,review=col.review,code=col.code)
        col_list.append(item)
        print(item.code)
        
        db.session.add(item)
      
        db.session.commit()

        new_col_list[item.code]=item.col_id

    # Extract pieces from the file

    sheet_name="Pieces"
    df = pd.read_excel(excel_file, sheet_name=sheet_name,skiprows=[0,1,3,4],index_col=None,dtype=str)
    
    df_p = df.iloc[:, :]  # Columns A to AJ

    lpieces=list()
    for index, row in df_p.iterrows():
        
        row=df_p.iloc[index]
        print(row)
        cont=split_cell(row["Contributor"], SEP)
        roles=split_cell(row["Role"], SEP)
        cont_role=list()
        for ci,ri in zip(cont,roles):
            cont_role.append(dict(name=ci,role=split_cell(ri, CODE_SEP)[0]))

        cont = split_cell(row["ContributorP"], SEP)
        roles = split_cell(row["RoleCP"], SEP)
        gend = split_cell(row["GenderCP"], SEP)
        cont2_role=list()
        for ci,ri,ge in zip(cont,roles,gend):
            ri=split_cell(ri, CODE_SEP)[0]
            cont2_role.append(dict(name=ci,role=int(ri),gender=ge))
        

        creators= split_cell(row["CreatorP"], SEP)
        roles=split_cell(row["RoleP"], SEP)
        gend = split_cell(row["GenderP"], SEP)
        c_role=list()
        for ci,ri,ge in zip(creators,roles,gend):
            ri=split_cell(ri, CODE_SEP)[0]
            c_role.append(dict(name=ci,role=int(ri),gender=ge))

        tl = split_cell(row["Temporal"], SEP)
        temp=dict(century=tl[0],decade=tl[1],year=tl[2])

        tl = split_cell(row["Spatial"], SEP)
        spat=dict(country=tl[0],state=tl[1],location=tl[2])

        colect_id=new_col_list[row["Col_id"]]

        title_xml = row["Identifier"]

        # Assign the mei and xml files to the piece if the filename matches with title_xml
        piece_mei = ""
        piece_xml = ""
        if mei is not None:
            for m in mei:
                file_name = m.filename.split(".")[0]    
                if title_xml == file_name:
                    piece_mei = m.file.read()
                    piece_mei = base64.b64encode(piece_mei).decode('utf-8')
                    break
        if xml is not None:
            for x in xml:
                file_name = x.filename.split(".")[0]
                if title_xml == file_name:
                    piece_xml = x.file.read()
                    piece_xml = base64.b64encode(piece_xml).decode('utf-8')
                    break
        
        
        pc = PieceSc(publisher=get_cell(row["Publisher"]),contributor_role=cont_role,creator=get_cell(row["Creator"]),title=split_cell(row["Title"], SEP),rights=split_cell(row["Rights"], CODE_SEP)[0],
                     date=get_cell(row["Date"]),type_file=split_cell(row["Type"], CODE_SEP)[0], desc=get_cell(row["Description"]),rightsp=split_cell(row["RightsP"], CODE_SEP)[0],contributorp_role=cont2_role, 
                     creatorp_role=c_role,alt_title=get_cell(row["AlternativeTitle"]), datep=get_cell(row["DateP"]),descp=get_cell(row["DescriptionP"]),type_piece=split_cell(row["TypeP"], CODE_SEP)[0],
                     formattingp=get_cell(row["FormatP"]),hasVersion=split_cell(row["HasVersion"],SEP),subject=split_cell(row["Subject"], SEP),language=get_cell(row["Language"]), spatial=spat, temporal=temp,
                     isVersionOf=split_cell(row["IsVersionOf"], SEP),coverage=get_cell(row["Coverage"]), relationp=split_cell(row["Relation"], SEP), real_key=get_cell(row["Key"]), mode=get_cell(row["Mode"]),
                     meter=get_cell(row["Metre"]), tempo=get_cell(row["Tempo"]), genre=split_cell(row["Genre"], SEP),instruments=split_cell(row["Instrument"], SEP),xml=piece_xml,mei=piece_mei,midi="",audio="",
                     video="",user_id=user_id,col_id=colect_id,review=True,title_xml=get_cell(row["Identifier"]))
        
        
        item = Piece(publisher=pc.publisher, creator=pc.creator, title=pc.title, rights=pc.rights, date=pc.date,
            type_file=pc.type_file, contributor_role=pc.contributor_role,desc=pc.desc, rightsp=pc.rightsp,
            creatorp_role=pc.creatorp_role,contributorp_role=pc.contributorp_role, alt_title=pc.alt_title, datep=pc.datep, descp=pc.descp, type_piece=pc.type_piece, 
            formattingp=pc.formattingp,subject=pc.subject, language=pc.language, relationp=pc.relationp, hasVersion=pc.hasVersion, isVersionOf=pc.isVersionOf,
            coverage=pc.coverage,genre=pc.genre,meter=pc.meter,tempo=pc.tempo,real_key=pc.real_key,mode=pc.mode,instruments=pc.instruments, temporal=pc.temporal,spatial=pc.spatial,
            xml=pc.xml, mei=pc.mei, midi=pc.midi, audio=pc.audio,video=pc.video,user_id=pc.user_id,col_id=pc.col_id,review=pc.review,title_xml=pc.title_xml)#,col_id=pc.col_id)
 
            
        lpieces.append(item)
        db.session.add(item)
    
    db.session.commit()
    print(lpieces)
    
    return {"msg": "Information uploaded"}


@router.post("/ExcelToPiece")
def piece_excel_to_sqlalchemy(file: UploadFile = File(...), user_id: int=None, xml: str=None, mei: str=None, midi: bytes=None, col_id_list: list=None, excel_file: bytes=None):
    if(excel_file==None):
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

        cont=split_cell(row["Contributor"], SEP)
        roles=split_cell(row["Role"], SEP)
        cont_role=list()
        for ci,ri in zip(cont,roles):
            cont_role.append(dict(name=ci,role=split_cell(ri, CODE_SEP)[0]))

        cont = split_cell(row["ContributorP"], SEP)
        roles = split_cell(row["RoleCP"], SEP)
        gend = split_cell(row["GenderCP"], SEP)
        cont2_role=list()
        for ci,ri,ge in zip(cont,roles,gend):
            ri=split_cell(ri, CODE_SEP)[0]
            cont2_role.append(dict(name=ci,role=int(ri),gender=ge))
        

        creators= split_cell(row["CreatorP"], SEP)
        roles=split_cell(row["RoleP"], SEP)
        gend = split_cell(row["GenderP"], SEP)
        c_role=list()
        for ci,ri,ge in zip(creators,roles,gend):
            ri=split_cell(ri, CODE_SEP)[0]
            c_role.append(dict(name=ci,role=int(ri),gender=ge))

        tl = split_cell(row["Temporal"], SEP)
        temp=dict(century=tl[0],decade=tl[1],year=tl[2])

        tl = split_cell(row["Spatial"], SEP)
        spat=dict(country=tl[0],state=tl[1],location=tl[2])

        #get col_id from Collection where code=row["col_id"] with sqlalchemy query
        # colect_id=db.session.query(PieceCol.col_id).filter(PieceCol.code==row["Col_id"]).first()
        #return col_list
        colect_id=int(row["Col_id"])
        # colect_id=db.session.query(PieceCol.col_id).filter(PieceCol.code==row["Col_id"]).first()

        pc = PieceSc(publisher=get_cell(row["Publisher"]),contributor_role=cont_role,creator=get_cell(row["Creator"]),title=split_cell(row["Title"], SEP),rights=split_cell(row["Rights"], CODE_SEP)[0],
                     date=get_cell(row["Date"]),type_file=split_cell(row["Type"], CODE_SEP)[0], desc=get_cell(row["Description"]),rightsp=split_cell(row["RightsP"], CODE_SEP)[0],contributorp_role=cont2_role, 
                     creatorp_role=c_role,alt_title=get_cell(row["AlternativeTitle"]), datep=get_cell(row["DateP"]),descp=get_cell(row["DescriptionP"]),type_piece=split_cell(row["TypeP"], CODE_SEP)[0],
                     formattingp=get_cell(row["FormatP"]),hasVersion=split_cell(row["HasVersion"],SEP),subject=split_cell(row["Subject"], SEP),language=get_cell(row["Language"]), spatial=spat, temporal=temp,
                     isVersionOf=split_cell(row["IsVersionOf"], SEP),coverage=get_cell(row["Coverage"]), relationp=split_cell(row["Relation"], SEP), real_key=get_cell(row["Key"]), mode=get_cell(row["Mode"]),
                     meter=get_cell(row["Metre"]), tempo=get_cell(row["Tempo"]), genre=split_cell(row["Genre"], SEP),instruments=split_cell(row["Instrument"], SEP),xml=xml,mei=mei,midi=midi,audio="",
                     video="",user_id=user_id,col_id=colect_id,review=True,title_xml=get_cell(row["Identifier"]))
        
        
        item = Piece(publisher=pc.publisher, creator=pc.creator, title=pc.title, rights=pc.rights, date=pc.date,
            type_file=pc.type_file, contributor_role=pc.contributor_role,desc=pc.desc, rightsp=pc.rightsp,
            creatorp_role=pc.creatorp_role,contributorp_role=pc.contributorp_role, alt_title=pc.alt_title, datep=pc.datep, descp=pc.descp, type_piece=pc.type_piece, 
            formattingp=pc.formattingp,subject=pc.subject, language=pc.language, relationp=pc.relationp, hasVersion=pc.hasVersion, isVersionOf=pc.isVersionOf,
            coverage=pc.coverage,genre=pc.genre,meter=pc.meter,tempo=pc.tempo,real_key=pc.real_key,mode=pc.mode,instruments=pc.instruments, temporal=pc.temporal,spatial=pc.spatial,
            xml=pc.xml, mei=pc.mei, midi=pc.midi, audio=pc.audio,video=pc.video,user_id=pc.user_id,col_id=pc.col_id,review=pc.review,title_xml=pc.title_xml)#,col_id=pc.col_id)
 
            
        lpieces.append(item)
        db.session.add(item)
    
    db.session.commit()
    print(lpieces)
        
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
def parse_mei_to_metadata(mei: str):
    mei_path="IT-1952-RO-CO-047.mei"
    # score=parseEndings(mei_path)
    #score = MTCExtractor(mei_path,ET.parse(mei_path))
    # Parse the XML file
    import xml.etree.ElementTree as ET



    tree = ET.parse(mei_path)
    root = tree.getroot()
    
    # Define the namespace
    MEI_NS = '{http://www.music-encoding.org/ns/mei}'
    XML_NS = '{http://www.w3.org/XML/1998/namespace}'
    # Start exploring from the root element
    # score.explore_xml_element(root)
    
    
    # Load the MEI file
    # Find the metadata elements
    titles = root.findall(f'.//{MEI_NS}fileDesc/{MEI_NS}titleStmt/{MEI_NS}title')
    for title in titles:
        title_type = title.get('type')
        if title_type == 'main':
            title_main = title.text if title.text else "Unknown"
            id = title.get(f'{XML_NS}id')
            print(id)
        elif title_type == 'subtitle':
            title_subtitle = title.text if title.text else "Unknown"
    # Extract contributors
    contributors = []

    # Find all respStmt elements
    respStmt_elements = root.findall(f'.//{MEI_NS}fileDesc/{MEI_NS}titleStmt/{MEI_NS}respStmt')

    # Iterate over respStmt elements
    for respStmt in respStmt_elements:
        # Find all persName elements within respStmt
        persName_elements = respStmt.findall(f'.//{MEI_NS}persName')
        # Iterate over persName elements
        for persName in persName_elements:
            name = persName.text if persName.text else "Unknown"
            role = persName.get('role') if persName.get('role') else "Unknown"
            gender = persName.get('gender') if persName.get('gender') else "Unknown"
            contributors.append({"name": name, "role": role, "gender": gender})
    
    publisher = root.find(f'.//{MEI_NS}fileDesc/{MEI_NS}pubStmt/{MEI_NS}publisher').text
    creation_date = root.find(f'.//{MEI_NS}fileDesc/{MEI_NS}pubStmt/{MEI_NS}date').text
    # source_title = root.find(f'.//{MEI_NS}fileDesc/{MEI_NS}sourceDesc/{MEI_NS}source/{MEI_NS}biblStruct/{MEI_NS}monogr/{MEI_NS}imprint/{MEI_NS}title').text
    author = root.find(f'.//{MEI_NS}workList/{MEI_NS}work/{MEI_NS}author').text if root.find(f'.//{MEI_NS}workList/{MEI_NS}work/{MEI_NS}author') is not None else "Unknown"
    key = root.find(f'.//{MEI_NS}workList/{MEI_NS}work/{MEI_NS}key')
    mode = key.get('mode')
    key = key.text
    meter = root.find(f'.//{MEI_NS}workList/{MEI_NS}work/{MEI_NS}meter').text
    tempo = root.find(f'.//{MEI_NS}workList/{MEI_NS}work/{MEI_NS}tempo').text
    terms_elements = root.findall(f'.//{MEI_NS}workList/{MEI_NS}work/{MEI_NS}classification/{MEI_NS}termList/{MEI_NS}term')
    terms = {}   
    for term in terms_elements:
        term_type = term.get('type')
        term_value = term.text if term.text is not None else "Unknown"
        terms[term_type] = term_value
    tempo = root.find(f'.//{MEI_NS}workList/{MEI_NS}work/{MEI_NS}tempo').text


    # Print metadata
    # print("ID:", id)
    # print("Main Title:", title_main)
    # print("Subtitle:", title_subtitle)
    # print("Contributors:", contributors)
    # print("Creation Date:", creation_date)
    # print("Publisher:", publisher)
    # print("Availability:", availability)
    # print("Source Title:", source_title)
    # print("Source Publisher:", source_publisher)
    # print("Source Publication Place:", source_pubPlace)
    # print("Source Date:", source_date)
    # print("Author:", author)
    # print("Key:", key)
    # print("Mode:", mode)
    # print("Meter:", meter)
    # print("Tempo:", tempo)
    # print("Terms:", terms)

    # Create a dictionary to store the metadata
    # Current date in format Day of Month Year
    current_date = datetime.datetime.now().strftime("%d %B %Y")
    year_str = id.split("-")[1]
    # Obtener el siglo
    century = str(int(year_str[:2]) + 1)
    # Obtener la década
    decade = f"{year_str[2]}0s"
    # Obtener el año
    year = year_str
    metadata = {
        "publisher": publisher,
        "creator": author,
        "title": [title_main, title_subtitle],
        "rights": 0,
        "date": current_date,
        "type_file": "Unknown",
        "contributor_role": contributors,
        "desc": "",
        "rightsp": 0,
        "contributorp_role": [],
        "creatorp_role": [],
        "alt_title": "Unknown",
        "datep": creation_date,
        "descp": "",
        "type_piece": 0,
        "formattingp": "MEI",
        "subject": [],
        "language": id.split("-")[0],
        "relationp": [],
        "hasVersion": [],
        "isVersionOf": [],
        "coverage": "Unknown",
        "temporal": {"century": f"{century}th", "decade": decade, "year": year},
        "spatial": {"country": "Italy", "state": terms["region"], "location": terms["district"] + ", " + terms["city"]},
        "genre": terms["genre"],
        "meter": meter,
        "tempo": tempo,
        "real_key": key,
        "mode": mode,
        "instruments": [],
        "title_xml": id,
        "xml": "",
        "mei": mei,
        "midi": "",
        "audio": "",
        "video": "",
        "review": True,
        "user_id": 0,
        "col_id": 0
    }
    print(metadata)
    db_music = Piece(publisher=metadata["publisher"], creator=metadata["creator"], title=metadata["title"], rights=metadata["rights"], date=metadata["date"],
    type_file=metadata["type_file"], contributor_role=metadata["contributor_role"],desc=metadata["desc"], rightsp=metadata["rightsp"],
    creatorp_role=metadata["creatorp_role"],contributorp_role=metadata["contributorp_role"], alt_title=metadata["alt_title"], datep=metadata["datep"], descp=metadata["descp"], type_piece=metadata["type_piece"],
    formattingp=metadata["formattingp"],subject=metadata["subject"], language=metadata["language"], relationp=metadata["relationp"], hasVersion=metadata["hasVersion"], isVersionOf=metadata["isVersionOf"],
    coverage=metadata["coverage"],genre=metadata["genre"],meter=metadata["meter"],tempo=metadata["tempo"],real_key=metadata["real_key"],mode=metadata["mode"],instruments=metadata["instruments"],title_xml=metadata["title_xml"],
    xml=metadata["xml"], mei=metadata["mei"], midi=metadata["midi"], audio=metadata["audio"],video=metadata["video"],user_id=metadata["user_id"],review=metadata["review"],col_id=metadata["col_id"])
    try:
        db.session.add(db_music)
        db.session.commit()
        db.session.refresh(db_music)
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}  # Return an error message
    return db_music

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

    


