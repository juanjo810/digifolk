import base64
import datetime
from app.api.schemas.col_schema import PieceColSc
from fastapi import APIRouter, Body, UploadFile, File
from fastapi_sqlalchemy import db
from sqlalchemy import and_, or_
from fastapi.responses import FileResponse
from app.models.piece import Piece
from app.models.collection import PieceCol
from app.api.schemas.piece_schema import PieceSc
from typing import List
import pandas as pd
import music21 as m21
import xml.etree.ElementTree as ET
from app.api.routes.utils import extract_excel_piece_fields, extract_excel_collection_fields, extract_mei_piece_fields
import subprocess
import os



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
        if piece.xml != old_music.xml and piece.xml != "":
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
    EXCEL CONTROLLER
    Function to import data from an excel file to the database.
    The Excel file contains the metadata of the pieces and the collections that belongs to.
    1.- The function reads the Excel file
    2.- The function reads the collections from the file
    3.- The function imports the collections to the database
    4.- The function reads the pieces from the file
    5.- The function imports the pieces to the database
"""
@router.post("/ExcelController")
def excel_controller(file: UploadFile = File(...), mei: List[UploadFile] = None , xml: List[UploadFile] = None, user_id: int = None):
    # Read the Excel File
    # excel_file = file.file.read()
    excel_file="Metadata template - IE_1797_BT_EB.xlsx"

    # Read the Collections from the file
    sheet_name="Collections"
    df = pd.read_excel(excel_file, sheet_name=sheet_name,skiprows=[0,1,3,4,5],index_col=None,dtype=str)
    df_c = df.iloc[:, :]  # Columns A to AJ
    
    new_col_list=dict()

    ##CHECK if collection exists:
    for index, row in df_c.iterrows():
        collection_fields = extract_excel_collection_fields(row)
       
        # We create the PieceColSc from the dictionary returned by extract_excel_fields
        col = PieceColSc(**collection_fields)
        
        # We create the PieceCol object from the PieceColSc object
        item = PieceCol(title=col.title, rights=col.rights, extent=col.extent, subject=col.subject, date=col.date, language=col.language, creator_role=col.creator_role,
            contributor_role=col.contributor_role, publisher=col.publisher, source=col.source, source_type=col.source_type, description=col.description,
            formatting=col.formatting, relation=col.relation, spatial=col.spatial,temporal=col.temporal,rights_holder=col.rights_holder,coverage=col.coverage,review=col.review,code=col.code)
         
        db.session.add(item)
        db.session.commit()
        new_col_list[item.code] = item.col_id
        print(new_col_list)

    # Extract pieces from the file
    sheet_name="Pieces"
    df = pd.read_excel(excel_file, sheet_name=sheet_name,skiprows=[0,1,3,4],index_col=None,dtype=str)
    df_p = df.iloc[:, :]  # Columns A to AJ

    for index, row in df_p.iterrows():
        
        row=df_p.iloc[index]
        fields = extract_excel_piece_fields(row)

        # Assign the mei and xml files to the piece if the filename matches with title_xml
        piece_mei = ""
        piece_xml = ""
        if mei is not None:
            for m in mei:
                file_name = m.filename.split(".")[0]    
                if fields["title_xml"] == file_name:
                    piece_mei = m.file.read()
                    piece_mei = base64.b64encode(piece_mei).decode('utf-8')
                    break
        if xml is not None:
            for x in xml:
                file_name = x.filename.split(".")[0]
                if fields["title_xml"] == file_name:
                    piece_xml = x.file.read()
                    piece_xml = base64.b64encode(piece_xml).decode('utf-8')
                    break
        
        
        # We create the PieceSC from the dictionary returned by extract_excel_fields, and we add the user_id, xml, mei and midi
        # Also, we edit the col_id to match the one in the database
        fields["user_id"] = user_id
        fields["xml"] = piece_xml   
        fields["mei"] = piece_mei
        fields["midi"] = ""
        fields["col_id"] = new_col_list[str(fields["col_id"])]
        pc = PieceSc(**fields)   
        print(pc)     
        
        item = Piece(publisher=pc.publisher, creator=pc.creator, title=pc.title, rights=pc.rights, date=pc.date,
            type_file=pc.type_file, contributor_role=pc.contributor_role,desc=pc.desc, rightsp=pc.rightsp,
            creatorp_role=pc.creatorp_role,contributorp_role=pc.contributorp_role, alt_title=pc.alt_title, datep=pc.datep, descp=pc.descp, type_piece=pc.type_piece, 
            formattingp=pc.formattingp,subject=pc.subject, language=pc.language, relationp=pc.relationp, hasVersion=pc.hasVersion, isVersionOf=pc.isVersionOf,
            coverage=pc.coverage,genre=pc.genre,meter=pc.meter,tempo=pc.tempo,real_key=pc.real_key,mode=pc.mode,instruments=pc.instruments, temporal=pc.temporal,spatial=pc.spatial,
            xml=pc.xml, mei=pc.mei, midi=pc.midi, audio=pc.audio,video=pc.video,user_id=pc.user_id,col_id=pc.col_id,review=pc.review,title_xml=pc.title_xml)
 
        db.session.add(item)
    
    db.session.commit()
    
    return {"msg": "Information uploaded"}


@router.post("/ExcelToPiece")
def piece_excel_to_sqlalchemy(file: UploadFile = File(...), user_id: int=None, xml: str="", mei: str="", midi: str="", col_id_list: list=None, excel_file: bytes=None):
    # We read the Excel file
    # excel_file= file.file.read()
    excel_file="Metadata template - IE_1797_BT_EB.xlsx"
    sheet_name="Pieces"
    df = pd.read_excel(excel_file, sheet_name=sheet_name,skiprows=[0,1,3,4,5],index_col=None,dtype=str)
    df_p = df.iloc[:, :]  # Columns A to AJ

    # Extract pieces from the file:
    for index, row in df_p.iterrows():
            
        # Extract the metadata fields from the Excel file
        fields = extract_excel_piece_fields(row)

        # We create the PieceSC from the dictionary returned by extract_excel_fields, and we add the user_id, xml, mei and midi
        fields["user_id"] = user_id
        fields["xml"] = xml
        fields["mei"] = mei
        fields["midi"] = midi
        pc = PieceSc(**fields)
        
        # We create the Piece object from the PieceSC object    
        item = Piece(publisher=pc.publisher, creator=pc.creator, title=pc.title, rights=pc.rights, date=pc.date,
            type_file=pc.type_file, contributor_role=pc.contributor_role,desc=pc.desc, rightsp=pc.rightsp,
            creatorp_role=pc.creatorp_role,contributorp_role=pc.contributorp_role, alt_title=pc.alt_title, datep=pc.datep, descp=pc.descp, type_piece=pc.type_piece, 
            formattingp=pc.formattingp,subject=pc.subject, language=pc.language, relationp=pc.relationp, hasVersion=pc.hasVersion, isVersionOf=pc.isVersionOf,
            coverage=pc.coverage,genre=pc.genre,meter=pc.meter,tempo=pc.tempo,real_key=pc.real_key,mode=pc.mode,instruments=pc.instruments, temporal=pc.temporal,spatial=pc.spatial,
            xml=pc.xml, mei=pc.mei, midi=pc.midi, audio=pc.audio,video=pc.video,user_id=pc.user_id,col_id=pc.col_id,review=pc.review,title_xml=pc.title_xml)#,col_id=pc.col_id)
 
        db.session.add(item)

        print(pc)
    
    db.session.commit()
        
    return {"msg": "Pieces added"}

@router.post("/piecesToCsv")
def piece_to_csv(piece_id: int=None):

    #get piece from db
    if piece_id is None:
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
def parse_mei_to_metadata(user_id: int, mei: UploadFile = File(...)):
    # Write the MEI file to disk
    mei_path = "./input.mei"
    # mei_path = "./ES-1913-B-JSV-001.mei"

    data = mei.file.read()
    data_encoded = base64.b64encode(data).decode('utf-8')
    with open(mei_path, "wb") as file:
        file.write(data)

    tree = ET.parse(mei_path)
    root = tree.getroot()
    
    # Extract the metadata fields from the MEI file
    metadata = extract_mei_piece_fields(root, mei.filename)
    # metadata = extract_mei_piece_fields(root, "ES-1913-B-JSV-001.mei")

    # We define the current date in format Day of Month Year
    current_date = datetime.datetime.now().strftime("%d %B %Y")
    # We add the user_id, date and mei to the metadata dictionary
    metadata.update({
        "date": current_date,
        "mei": data_encoded,
        "user_id": user_id,
    })

    # We create the PieceSC from the dictionary returned by extract_mei_piece_fields
    pc = PieceSc(**metadata)
    print(pc)

    # We create the Piece object from the PieceSC object
    db_music = Piece(publisher=pc.publisher, creator=pc.creator, title=pc.title, rights=pc.rights, date=pc.date,
            type_file=pc.type_file, contributor_role=pc.contributor_role,desc=pc.desc, rightsp=pc.rightsp,
            creatorp_role=pc.creatorp_role,contributorp_role=pc.contributorp_role, alt_title=pc.alt_title, datep=pc.datep, descp=pc.descp, type_piece=pc.type_piece, 
            formattingp=pc.formattingp,subject=pc.subject, language=pc.language, relationp=pc.relationp, hasVersion=pc.hasVersion, isVersionOf=pc.isVersionOf,
            coverage=pc.coverage,genre=pc.genre,meter=pc.meter,tempo=pc.tempo,real_key=pc.real_key,mode=pc.mode,instruments=pc.instruments, temporal=pc.temporal,spatial=pc.spatial,
            xml=pc.xml, mei=pc.mei, midi=pc.midi, audio=pc.audio,video=pc.video,user_id=pc.user_id,col_id=pc.col_id,review=pc.review,title_xml=pc.title_xml)

    db.session.add(db_music)
    
    db.session.commit()

    return db_music

@router.post("/XMLToCsv")
def parse_xml_to_metadata(user_id: int, xml: UploadFile = File(...)):
    
    # We read the XML file and convert it to MEI
    xml_data = xml.file.read()
    xml_data = base64.b64encode(xml_data).decode('utf-8')
    data_encoded = convert_xml_to_mei(xml_data)

    # Write the new MEI file to disk
    mei_path = "./input.mei"
    mei_data = base64.b64decode(data_encoded)
    with open(mei_path, "wb") as file:
        file.write(mei_data)
    
    # mei_path = "./PRUEBA_XML.mei"

    tree = ET.parse(mei_path)
    root = tree.getroot()
    
    # Extract the metadata fields from the MEI file
    metadata = extract_mei_piece_fields(root, xml.filename)
    # metadata = extract_mei_piece_fields(root, "PRUEBA-2025-XML.mei")

    # We define the current date in format Day of Month Year
    current_date = datetime.datetime.now().strftime("%d %B %Y")
    # We add the user_id, date and mei to the metadata dictionary
    metadata.update({
        "date": current_date,
        "mei": data_encoded,
        "user_id": user_id,
    })

    # We create the PieceSC from the dictionary returned by extract_mei_piece_fields
    pc = PieceSc(**metadata)

    # We create the Piece object from the PieceSC object    
    db_music = Piece(publisher=pc.publisher, creator=pc.creator, title=pc.title, rights=pc.rights, date=pc.date,
            type_file=pc.type_file, contributor_role=pc.contributor_role,desc=pc.desc, rightsp=pc.rightsp,
            creatorp_role=pc.creatorp_role,contributorp_role=pc.contributorp_role, alt_title=pc.alt_title, datep=pc.datep, descp=pc.descp, type_piece=pc.type_piece,
            formattingp=pc.formattingp,subject=pc.subject, language=pc.language, relationp=pc.relationp, hasVersion=pc.hasVersion, isVersionOf=pc.isVersionOf,
            coverage=pc.coverage,genre=pc.genre,meter=pc.meter,tempo=pc.tempo,real_key=pc.real_key,mode=pc.mode,instruments=pc.instruments, temporal=pc.temporal,spatial=pc.spatial,
            xml=pc.xml, mei=pc.mei, midi=pc.midi, audio=pc.audio,video=pc.video,user_id=pc.user_id,col_id=pc.col_id,review=pc.review,title_xml=pc.title_xml)
    
    db.session.add(db_music)
    
    db.session.commit()

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
