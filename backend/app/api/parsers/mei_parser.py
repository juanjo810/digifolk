"""
Class to Extract MEI Information
"""

import verovio
import os
import music21 as m21
import converter21 as c21
from lxml import etree
import csv
import xml.etree.ElementTree as ET
import subprocess
# from app.models.piece import Piece

NAME_SPACE = {'mei': 'http://www.music-encoding.org/ns/mei'}
MEI_SPACE = '{' + NAME_SPACE['mei'] + '}'
ID_SPACE = '{http://www.w3.org/XML/1998/namespace}id'

MEILINKS = {
    'title': ".//mei:title[@type='main']",
    'subtitle': ".//mei:title[@type='subtitle']",

    'alt_title': ".//mei:incip[@type='lyrics']//mei:head",
    'author': ".//mei:author",

    'compiler': ".//mei:titleStmt//mei:persName[@role='compiler' or @role='recopilador']",
    'informer': './/mei:titleStmt//mei:persName[contains(@role, "informant")]',
    'informer_geogName': './/mei:titleStmt//mei:persName[contains(@role, "informant")]//mei:geogName',
    'encoder': ".//mei:titleStmt//mei:persName[@role='encoder']",
    'editor': ".//mei:titleStmt//mei:persName[@role='editor']",

    'source_title': ".//mei:sourceDesc//mei:title[not(@type='subordinate') and not(@type='desc')]",
    'source_subtitle': ".//mei:sourceDesc/mei:title[@type='subordinate' or @type='desc']",

    'source_compiler': ".//mei:source//mei:persName[@role='compiler' or @role='recopilador' or @role='a cura di']",
    'source_informer': ".//mei:source//mei:persName[@role='colaborador' or @role='informante' or @role='informant']",
    'source_bibliografia': ".//mei:source//mei:persName[contains(@role, 'bibliografía') or contains(@role, 'bibliográfia')]",
    'source_introduction': ".//mei:source//mei:persName[contains(@role, 'introducción') or @role='preámbulo' or @role='presentación, comentarios e índices' or @role='presentazione' or contains(@role, 'prólogo')]",
    'source_edition': ".//mei:source//mei:persName[contains(@role, 'edición') or @role='disegni' or contains(@role, 'catalogación')]",

    'date': ".//mei:biblStruct//mei:date",

    'genre': ".//mei:term[@type='genre']",
    'meter': ".//mei:meter",
    'tempo': ".//mei:tempo",
    'real_key': ".//mei:key",
    'mode': ".//mei:key",
    'time_signature': ".//mei:scoreDef",

    'city': ".//mei:term[@type='localidad' or @type='città' or @type='provincia']",
    'region': ".//mei:term[@type='distrito' or @type='comunidad' or @type='regione']",

    'incip_lyrics': ".//mei:workList//mei:incip[@type='lyrics']//mei:head",

    'ambitus_low': ".//mei:ambNote[@type='lowest']",
    'ambitus_high': ".//mei:ambNote[@type='highest']",

    'rhythm_pattern': ".//mei:supplied[@type='rythymn pattern']",
    'phrases': ".//mei:phrase",

    'lyrics': ".//mei:workList//mei:annot",
}



class MEIExtractor:

    def __init__(self, ):
        """
        GET NECESSARY INFORMATION
        """
        self.tk = verovio.toolkit()
        self.tk.setOptions({"xmlIdChecksum": False, "xmlIdSeed": 0})

    def xml_to_mei(self, xml_path, mei_path):
        
        # Load MusicXML data
        # xml_data = m21.converter.parse(xml_path)

        # I need to execute a command in the shell : musicxml2hum output.musicxml -o output.hum
        # I need to execute the command in the shell: hum2mxml output.hum -o output.musicxml
        subprocess.run("verovio -t xml " + xml_path + " -o output.mei", shell=True)
        print(mei)

    def explore_xml_element(self,element, level=0):
        # Print the element's tag and attributes
        print("  " * level + f"Element: {element.tag}, Attributes: {element.attrib}")

        # Print the element's text if it exists
        if element.text:
            print("  " * (level + 1) + f"Text: {element.text}")

        # Recursively explore child elements
        for child in element:
            self.explore_xml_element(child, level + 1)


    # Define a recursive function to search for and modify XML elements
    def search_and_modify(tree, target_tag, text, new_attribute):
        # get the element of the tree with the target tag
        target_element = tree.find(target_tag)

        if target_element is not None:
        
            #add a new attribute to the element if it does not exist
            if new_attribute[0] not in target_element.attrib:
                target_element.set(new_attribute[0], new_attribute[1])
                #now modify the text of the elemnt
                target_element.text = text
                #if the attribute already exists, modify the text of the element
            elif target_element.attrib[new_attribute[0]] == new_attribute[1]:
                #now modify the text of the elemnt
                target_element.text = text
            #return the modified tree
            return tree
        else:
            print(f"Target element '{target_tag}' not found!")
            return None
    

    def print_xml_tree(element, level=0):
        # Print the current element with appropriate indentation
        print('  ' * level + element.tag)

        # Print attributes of the current element
        for key, value in element.attrib.items():
            print('  ' * (level + 1) + f'@{key}: {value}')

        # Recursively print child elements
        for child in element:
            print_xml_tree(child, level + 1)


    def mei_info_to_database(self):
        """
        Extract:

        1. File Description
        2. Encoding Description (Not necessary at the moment)
        3. Worklist
        """
        piece= Piece()
        # File Description
        fileDesc = self.root.find('.//mei:fileDesc', NAME_SPACE)
        piece=self.extract_title_statement(fileDesc,piece)

        # Worklist
        piece=self.extract_worklist(piece)
        return piece

       
    def extract_title_statement(self, fileDesc,piece):
        """
        1. TitleStmt
        1.1. Title
        1.2. Subtitle
        1.3. Identifier
        1.4. Responsibility statement
            1.4.1. Compiler
            1.4.2. Informant
            1.4.3. Geographic Name
            1.4.4. Encoder
            1.4.5. Editor
        """
        titleStmt = fileDesc.find('.//mei:titleStmt', NAME_SPACE)
        if titleStmt is None:
            titleStmt = etree.Element(f'{MEI_SPACE}titleStmt')  # type: ignore
            fileDesc.append(titleStmt)

        titleTag = titleStmt.find('.//mei:title', NAME_SPACE)
        if titleTag.attrib['type'] == 'main':
                #now extract the text of the elemnt
                piece.title.append(titleTag.text)
                

        subtitleTag = etree.Element(
            f'{MEI_SPACE}title', type="subtitle")  # type: ignore
        piece.title.append(subtitleTag.text)

        respStmt = titleStmt.find('.//mei:respStmt', NAME_SPACE)

        compilerTag = etree.SubElement(
            respStmt, f'{MEI_SPACE}persName', role="compiler")  # type: ignore
        dict_temp={"name":compilerTag.text, "role":"compiler"}
        piece.creatorp_role=dict_temp
        informantTag = etree.SubElement(
            respStmt, f'{MEI_SPACE}persName', role="informer")  # type: ignore
        informantTag.text = self.extract_info_data('informer')

        informantGeogName = etree.SubElement(
            informantTag, f'{MEI_SPACE}geogName')  # type: ignore
        informantGeogName.text = self.extract_info_data('informer_geogName')

        encoderTag = etree.SubElement(
            respStmt, f'{MEI_SPACE}persName', role="encoder")  # type: ignore
        piece.creator=encoderTag.text

        editorTag = etree.SubElement(
            respStmt, f'{MEI_SPACE}persName', role="editor")  # type: ignore
        editorTag.text = self.extract_info_data('editor')

        dateTag = etree.SubElement(classificationTermList, f'{MEI_SPACE}term', type='date') # type: ignore
        piece.datep=dateTag

        return piece


    def extract_worklist(self,piece):
        """
        1. Title
        2. Author (informant)
        3. Incipit (lyrics)
        4. Key, mode
        5. Meter
        6. Tempo
        7. Incipit (musical) (First measures of the song)
        8. Language
        9. Notes Statement (additional information)
        10. Classification:
            10.1. Genre
            10.2. Location (Province/State)
        """

        incip = etree.SubElement(etree.SubElement(
            etree.SubElement(work, f'{MEI_SPACE}incip',
                             type="lyrics"),  # type: ignore
            f'{MEI_SPACE}incipText'),
            f'{MEI_SPACE}head')
        piece.alt_title=incip.text

        keyTag = etree.SubElement(
            work, f'{MEI_SPACE}key', mode=f"{mode}")  # type: ignore
        piece.real_key=keyTag.text

        meterTag = etree.SubElement(work, f'{MEI_SPACE}meter')  # type: ignore
        piece.meter=meterTag.text

        tempoTag = etree.SubElement(work, f'{MEI_SPACE}tempo')  # type: ignore
        piece.tempo=tempoTag.text

        genreTag = etree.SubElement(classificationTermList, f'{MEI_SPACE}term', type='genre') # type: ignore
        piece.genre=genreTag.text

        classificationTermList = etree.SubElement(etree.SubElement(work, f'{MEI_SPACE}classification'), f'{MEI_SPACE}termList') # type: ignore

        regionTag = etree.SubElement(classificationTermList, f'{MEI_SPACE}term', type='region') # type: ignore
        districtTag = etree.SubElement(classificationTermList, f'{MEI_SPACE}term', type='district') # type: ignore
        cityTag = etree.SubElement(classificationTermList, f'{MEI_SPACE}term', type='city') # type: ignore

        dict_temp={"country":regionTag.text,"location":districtTag.text+"-"+cityTag.text}
        piece.spatial=dict_temp

        return piece

    def database_to_mei_info(self,piece,col):
        """
        Extract:

        1. File Description
        2. Encoding Description (Not necessary at the moment)
        3. Worklist
        """

        # File Description
        fileDesc = self.root.find('.//mei:fileDesc', NAME_SPACE)
        self.set_title_statement(fileDesc,piece)
        self.set_publishing_statement(fileDesc,col)
        self.set_source_description(fileDesc,piece)
        
        return fileDesc

    def set_title_statement(self, fileDesc):
        """
        1. TitleStmt
        1.1. Title
        1.2. Subtitle
        1.3. Identifier
        1.4. Responsibility statement
            1.4.1. Compiler
            1.4.2. Informant
            1.4.3. Geographic Name
            1.4.4. Encoder
            1.4.5. Editor
        1.5. Date
        """
        titleStmt = fileDesc.find('.//mei:titleStmt', NAME_SPACE)
        if titleStmt is None:
            titleStmt = etree.Element(f'{MEI_SPACE}titleStmt')  # type: ignore
            fileDesc.append(titleStmt)

        titleTag = titleStmt.find('.//mei:title', NAME_SPACE)
        titleTag.set("type", "main")

        titleTag.set(ID_SPACE, f"{self.name}")
        titleTag.text = piece.title  ## REVISAR

        respStmt = titleStmt.find('.//mei:respStmt', NAME_SPACE)

        compilerTag = etree.SubElement(
            respStmt, f'{MEI_SPACE}persName', role="compiler")  # type: ignore
        #i have a list of dictionaries with fields "name", "role", "gender". I need to get the name of the element with role="compiler"
        for entry in piece.creatorp_role:
            if entry["role"] == "compiler":
                compilerTag.text = entry["name"]
            
        informantTag = etree.SubElement(
            respStmt, f'{MEI_SPACE}persName', role="informer")  # type: ignore
        
        for entry in piece.creatorp_role:
            if entry["role"] == "performer" or entry["role"] == "singer":
                informantTag.text = entry["name"]

        editorTag = etree.SubElement(
            respStmt, f'{MEI_SPACE}persName', role="editor")  # type: ignore
        editorTag.text = self.extract_info_data('editor')

        for entry in piece.contributorp_role:
            if entry["role"] == "editor":
                editorTag.text = entry["name"]
        
        dateTag = etree.SubElement(
            respStmt, f'{MEI_SPACE}date')

        date=piece.date
        if date["year"] !="":
            dateTag.text=date["year"]
        elif date["decade"] !="":
            dateTag.text=date["decade"]
        elif date["century"] !="":
            dateTag.text=date["century"]

        


    def set_publishing_statement(self, fileDesc):
        """
        2. PubStmt
            2.1. Publisher
            2.2. Date
            2.3. Availability
        """
        pubStmt = fileDesc.find('.//mei:pubStmt', NAME_SPACE)

        # remove automatic date of verovio
        pubStmt.remove(pubStmt.getchildren()[0])

        publisherTag = etree.SubElement(
            pubStmt, f'{MEI_SPACE}publisher')  # type: ignore
        publisherTag.text = 'DIGIFOLK Reseach Project'

        dateTag = etree.SubElement(pubStmt, f'{MEI_SPACE}date')  # type: ignore
        dateTag.text = '2023'

        availabilityTag = etree.SubElement(
            pubStmt, f'{MEI_SPACE}availability')  # type: ignore
        availabilityTag.text = """To the best of our knowledge,
                the full compositions on this site are in the public domain,
                the excerpts are in the public domain or are allowable under fair-use,
                and the few compositions that are still under copyright are used by permission.
                These scores, are provided for educational use only and are not to be used commercially.
            """

    def set_source_description(self, fileDesc, col, piece):
        """
        3. SourceDesc
            3.1. Source
                3.1.1. BiblStruct (Structured bibliographic citation)
                    3.1.1.1. title
                    3.1.1.2. subtitle
                    3.1.1.3. responsability
                    3.1.1.4. publisher
                    3.1.1.5. publication place
                    3.1.1.6. date
                    3.1.1.7. number of pages
        """
        sourceDesc = etree.SubElement(
            fileDesc, f'{MEI_SPACE}sourceDesc')  # type: ignore

        imprint = etree.SubElement(etree.SubElement(etree.SubElement(etree.SubElement(
            sourceDesc, f'{MEI_SPACE}source', {ID_SPACE: 'to_add'}), f'{MEI_SPACE}biblStruct'), f'{MEI_SPACE}monogr'), f'{MEI_SPACE}imprint')  # type: ignore

        titleTag = etree.SubElement(
            imprint, f'{MEI_SPACE}title')  # type: ignore
        titleTag.text = col.title

        self.sources = self.sources.loc[self.sources['title'] == titleTag.text]

        respStmt = etree.SubElement(
            imprint, f'{MEI_SPACE}respStmt')  # type: ignore
        recopiladorTag = etree.SubElement(
            respStmt, f'{MEI_SPACE}persName', role="compiler")  # type: ignore
        for entry in col.creator_role:
            if entry["role"] == "writer":
                recopiladorTag.text = entry["name"]

        editionTag = etree.SubElement(
            respStmt, f'{MEI_SPACE}persName', role="editor")  # type: ignore
        for entry in col.contributor_role:
            if entry["role"] == "editor":
                compilerTag.text = entry["name"]

        publisherTag = etree.SubElement(
            imprint, f'{MEI_SPACE}publisher')  # type: ignore
        publisherTag.text = col.publisher

        pubPlaceTag = etree.SubElement(
            imprint, f'{MEI_SPACE}pubPlace')  # type: ignore
        pubPlaceTag.text = col.spatial["country"]

        dateTag = etree.SubElement(
            imprint, f'{MEI_SPACE}date')  # type: ignore
        dateTag.text = col.temporal["year"]


    def set_worklist(self):
        """
        1. Title
        2. Author (informant)
        3. Incipit (lyrics)
        4. Key, mode
        5. Meter
        6. Tempo
        7. Incipit (musical) (First measures of the song)
        8. Language
        9. Notes Statement (additional information)
        10. Classification:
            10.1. Genre
            10.2. Location (Province/State)
        """

        keyTag = etree.SubElement(
            work, f'{MEI_SPACE}key', mode=f"{mode}")  # type: ignore
        keyTag.text = piece.real_key+" "+piece.mode

        meterTag = etree.SubElement(work, f'{MEI_SPACE}meter')  # type: ignore
        meterTag.text = piece.meter

        tempoTag = etree.SubElement(work, f'{MEI_SPACE}tempo')  # type: ignore
        tempoTag.text = piece.tempo


        classificationTermList = etree.SubElement(etree.SubElement(work, f'{MEI_SPACE}classification'), f'{MEI_SPACE}termList') # type: ignore

        genreTag = etree.SubElement(classificationTermList, f'{MEI_SPACE}term', type='genre') # type: ignore
        genreTag.text = " | ".join(array_of_strings)

        regionTag = etree.SubElement(classificationTermList, f'{MEI_SPACE}term', type='region') # type: ignore
        regionTag.text = col.spatial["country"]

        districtTag = etree.SubElement(classificationTermList, f'{MEI_SPACE}term', type='district') # type: ignore
        districtTag.text = col.spatial["province"]

        cityTag = etree.SubElement(classificationTermList, f'{MEI_SPACE}term', type='city') # type: ignore
        cityTag.text = col.spatial["city"]




# Function to map class attributes to a CSV file
def map_class_to_csv(objects, filename):
    # Get the class attribute names
    attributes = list(vars(objects[0]).keys())

    # Write data to CSV file
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=attributes)
        writer.writeheader()
        for obj in objects:
            writer.writerow(vars(obj))

# Example usage
if __name__ == "__main__":
    mei_path = "./ES-1913-B-JSV-001.mei"
    mei_name="ES-1913-B-JSV-001"
    xml_path ="./ES-1913.xml"
    # score=parseEndings(mei_path)
    score = MEIExtractor()
    mei_file=score.xml_to_mei(xml_path,"./probando.mei")
     # Load the XML file
    tree = ET.parse(mei_path)
    root = tree.getroot()
    # Print the tree structure starting from the root element
    score.print_xml_tree(root)

    #Operations: FROM MEI --> DATABASE
    piece=score.mei_info_to_database()
    dict_temp={"year":mei_name.split("-")[1]}
    piece.temporal=dict_temp


    #Operations: FROM DATABASE --> MEI


