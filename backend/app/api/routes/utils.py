import os
import bz2
import pickle
import itertools

from app.core.config import DATABASE_PATH,CODE_SEP,SEPARATOR as SEP,MEI_NS,XML_NS

def retrieve_score(name):
    music_path = os.sep.join(
        [DATABASE_PATH[:-1], 'Scores', name])
    try:
        with bz2.BZ2File(music_path + '.pbz2', 'rb') as m21_handle:
            m21_score = pickle.load(m21_handle)
            try:
                m21_score = m21_score.expandRepeats()
            except:
                print('Repeats not expandable')
            m21_handle.close()
            return m21_score
    except:
        print("Can't load music21 score")
        return None


def combinations2(d, sum_to):
    def combinations_aux(d, current, sum_to):
        for j in range(len(d)):
            nex = current+[d[j]]
            if sum(nex) == sum_to:
                yield nex
            elif sum(nex) < sum_to:
                # d[j:] for elements >= d[j]
                yield from combinations_aux(d[j:], nex, sum_to)

    def permute_unique(iterable):
        # see https://stackoverflow.com/a/39014159/6914441
        perms = [[]]
        for i in iterable:
            perms = [perm[:j] + [i] + perm[j:]
                     for perm in perms
                     for j in itertools.takewhile(lambda j:j < 1 or perm[j-1] != i, range(len(perm) + 1))
                     ]
        return perms

    return (p for c in combinations_aux(sorted(set(d)), [], sum_to) for p in permute_unique(c))


"""
Determine whether an event is syncopated or not. More precisely, determine
whether the event is metrically stable, in the sense defined by Arthur Komar.
The process involves three functions:
First, assemble a representation of the local metric system in which the event
occurs. This map consists of a list of tuples, one for each accent point in
the metric system. Each tuple consists of the offset of the accent point in the
measure and the strength (weight) of the access point.
Second, using the local metric map, locate the onset of the event in the metric
map and calculate the duration between its onset and the onset of the next
stronger accent point. This elapsed duration is the maximal metrically
stable duration of any event iniated at that onset. And the next stronger
accent point is the point at which the event would become unstable (syncopated),
if it were to continue.
Third, calculate whether the event's duration does or does not exceed the
maximally stable duration. Return False for metrically unstable (syncopated)
events and True for stable events.
"""

def getMetricMap(event):
    """Generate a map of the local metric system for an event.
    Compile a list of tuples of measure offsets and accent weights.
    This can be sliced and the offsets used to calculate a stable duration.
    Example. The default map for a measure in 4/4 is:
    [(0.0, 1.0), (0.5, 0.125), (1.0, 0.25), (1.5, 0.125), (2.0, 0.5),
    (2.5, 0.125), (3.0, 0.25), (3.5, 0.125), (4.0, 1.0)]. In order to get more
    depth, the accent weights have to be extended.
    """
    # Get the local time signature.
    ts = event.getContextByClass('TimeSignature')
    # Arbitrarily extend the depth of the metric system.
    # (This should be replaced by a context-sentitive inference
    # of the local metric system (default depth=3).)
    ts._setDefaultAccentWeights(depth=4)
    # Compile a list of the local offsets for each accent point
    #   in the local metric system.
    accent_offsets = [accent.duration.quarterLength
                      for accent in ts.accentSequence.flat]
    # Now create the map of the local metric system.
    # Set an index to use for slicing the accent offset list.
    idx = 1
    # Initialize the metric map with the downbeat.
    metricMap = [(0.0, 1.0)]
    # Fill in the map.
    # Calculate the offset of each accent point by summing the meter
    #   terminals up to and including the accent point.
    while idx < len(accent_offsets):
        a_offset = sum(accent_offsets[0:idx])
        metricMap.append((a_offset,
                          ts.accentSequence.offsetToWeight(a_offset)))
        idx += 1
    # Finalize the metric map with the downbeat of the next bar.
    metricMap.append((ts.barDuration.quarterLength, 1.0))

    return metricMap


def getMaximumSpanFromMetricPosition(event):
    # Get the local time signature.
    ts = event.getContextByClass('TimeSignature')
    # Get the beat strength of the event.
    event_bs = event.beatStrength
    # Get the local offset of the event in the local measure.
    event_metricOffset = ts.getMeasureOffsetOrMeterModulusOffset(event)
    # Get the index of the event's onset in the local metric system.
    event_metricIndex = ts.accentSequence.offsetToIndex(event_metricOffset)
    # Generate a map of the local metric system: tuples of offsets and weights.
    local_metricMap = getMetricMap(event)
    # Get just that part of the map that starts with the onset of the event.
    metricMapSlice = local_metricMap[event_metricIndex:len(local_metricMap)]
    # Calculate the maximum metrically stable span by looking forward:
    # (a) find the local offset of the next stronger metric timepoint
    max_span_end = 0
    for w in metricMapSlice:
        if w[1] > event_bs:
            max_span_end = w[0]
            break
    # (b) calculate the duration between event onset and that
    #   of the next stronger timepoint.
    return max_span_end - event_metricOffset


def isMetricallyStable(event):
    # This function only evaluates notes that do not begin on downbeats.
    event_bs = event.beatStrength
    max_span = getMaximumSpanFromMetricPosition(event)
    if event_bs < 1.0 and event.duration.quarterLength > max_span:
        return False
    else:
        return True


from xml.etree import ElementTree as ET

def retrieve_mei(name):
    music_path = os.sep.join(
        [DATABASE_PATH[:-1], 'Scores', name])
    try:
        return ET.parse(music_path + '.mei')
    except:
        print("Can't load MEI score")
        return None


def piece_model_to_dict(model_instance):
    # Initialize an empty dictionary to store the data
    data_dict = {}

    # Iterate through the columns and attributes of the model
    for column in model_instance. __table__.columns:
        column_name = column.name
        column_value = getattr(model_instance, column_name, None)
        data_dict[column_name] = column_value

    return data_dict

""""
Function to check if an Excel cell contains any value
"""
def is_empty(cell):
    if type(cell) is float or cell is None or cell == "":
        return False
    return True

"""
Function to split a cell into a list of elements
"""
def split_cell(cell, separator):
    if is_empty(cell):
        return  cell.split(separator)
    return []

"""
Function to get and clean a cell
"""
def get_cell(cell):
    if is_empty(cell):
        return cell.strip()
    return ""

def extract_excel_piece_fields(row):
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
    piece_dict = {
        "col_id": int(row["Col_id"]),
        "publisher": get_cell(row["Publisher"]),
        "contributor_role": cont_role,
        "creator": get_cell(row["Creator"]),
        "title": split_cell(row["Title"], SEP),
        "rights": split_cell(row["Rights"], CODE_SEP)[0],
        "date": get_cell(row["Date"]),
        "type_file": split_cell(row["Type"], CODE_SEP)[0],
        "desc": get_cell(row["Description"]),
        "rightsp": split_cell(row["RightsP"], CODE_SEP)[0],
        "contributorp_role": cont2_role,
        "creatorp_role": c_role,
        "alt_title": get_cell(row["AlternativeTitle"]),
        "datep": get_cell(row["DateP"]),
        "descp": get_cell(row["DescriptionP"]),
        "type_piece": split_cell(row["TypeP"], CODE_SEP)[0],
        "formattingp": get_cell(row["FormatP"]),
        "hasVersion": split_cell(row["HasVersion"], SEP),
        "subject": split_cell(row["Subject"], SEP),
        "language": get_cell(row["Language"]),
        "spatial": spat,
        "temporal": temp,
        "isVersionOf": split_cell(row["IsVersionOf"], SEP),
        "coverage": get_cell(row["Coverage"]),
        "relationp": split_cell(row["Relation"], SEP),
        "real_key": get_cell(row["Key"]),
        "mode": get_cell(row["Mode"]),
        "meter": get_cell(row["Metre"]),
        "tempo": get_cell(row["Tempo"]),
        "genre": split_cell(row["Genre"], SEP),
        "instruments": split_cell(row["Instrument"], SEP),
        "audio": "",
        "video": "",
        "review": True,
        "title_xml": get_cell(row["Identifier"])
    }

    # We create a PieceSc from the dictionary

    return piece_dict

def extract_excel_collection_fields(row):
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

    collection_dict = {
        "title": split_cell(row["SourceTitle"], SEP),
        "rights": split_cell(row["RightsC"], CODE_SEP)[0],
        "extent": get_cell(row["Extent"]),
        "date": get_cell(row["DateC"]),
        "subject": split_cell(row["SubjectC"], SEP),
        "language": get_cell(row["LanguageC"]),
        "contributor_role": cont_role,
        "creator_role": c_role,
        "publisher": get_cell(row["PublisherC"]),
        "source": get_cell(row["Source"]),
        "description": get_cell(row["DescriptionC"]),
        "source_type": split_cell(row["TypeC"], CODE_SEP)[0],
        "formatting": get_cell(row["FormatC"]),
        "relation": split_cell(row["RelationC"], SEP),
        "spatial": spat,
        "temporal": temp,
        "rights_holder": get_cell(row["RightsHolder"]),
        "coverage": get_cell(row["CoverageC"]),
        "code": get_cell(row["CodeC"]),
        "review": True
    }

    return collection_dict

def extract_mei_piece_fields(root, mei_name):
    # FIND THE METADATA ELEMENTS
    # Extract the ID from the MEI name
    id = mei_name.split(".")[0]

    # Extract the titles
    titles = root.findall(f'.//{MEI_NS}fileDesc/{MEI_NS}titleStmt/{MEI_NS}title')
    titles_found = []
    for title in titles:
        title_type = title.get('type')
        if title_type == 'subtitle':
            title_subtitle = title.text if title.text else "Unknown"
            titles_found.append(title_subtitle)
        else:
            title_main = title.text if title.text else "Unknown"
            titles_found.append(title_main)
    
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
    
    publisher = root.find(f'.//{MEI_NS}fileDesc/{MEI_NS}pubStmt/{MEI_NS}publisher')
    publisher = publisher.text if publisher is not None else "Unknown"

    creation_date = root.find(f'.//{MEI_NS}fileDesc/{MEI_NS}pubStmt/{MEI_NS}date')
    creation_date = creation_date.text if creation_date is not None else "Unknown"

    author = root.find(f'.//{MEI_NS}workList/{MEI_NS}work/{MEI_NS}author')
    author = author.text if author is not None else "Unknown"
    
    key = root.find(f'.//{MEI_NS}workList/{MEI_NS}work/{MEI_NS}key')
    mode = key.get('mode') if key is not None else "Unknown"
    key = key.text if key is not None else "Unknown"

    meter = root.find(f'.//{MEI_NS}workList/{MEI_NS}work/{MEI_NS}meter')
    meter = meter.text if meter is not None else "Unknown"

    tempo = root.find(f'.//{MEI_NS}workList/{MEI_NS}work/{MEI_NS}tempo')
    tempo = tempo.text if tempo is not None else "Unknown"

    terms_elements = root.findall(f'.//{MEI_NS}workList/{MEI_NS}work/{MEI_NS}classification/{MEI_NS}termList/{MEI_NS}term')
    terms = {}   
    for term in terms_elements:
        if term is not None:
            term_type = term.get('type')
            term_value = term.text
            terms[term_type] = term_value


    genre = []
    if "genre" in terms:
        genre.append(terms["genre"])
    spatial = { 
        "country": "Unknown",
        "state": terms["region"] if "region" in terms else "Unknown",
        "location": terms["district"] or terms["city"] if "district" in terms or "city" in terms else "Unknown"
    }
    
    tempo = root.find(f'.//{MEI_NS}workList/{MEI_NS}work/{MEI_NS}tempo')
    tempo = tempo.text if tempo is not None else "Unknown"
    
    # Extract the year from the ID checking if the ID is in the format "IT-YYYY-XXXX"
    year_str = id.split("-")[1]
    # Obtain the century
    century = str(int(year_str[:2]) + 1)
    century = f"{century}th"
    # Obtain the decade
    decade = f"{year_str[2]}0s"
    # Obtain the year
    year = year_str
    
    # Create the metadata dictionary
    metadata = {
        "publisher": publisher,
        "creator": author,
        "title": titles_found,
        "rights": 0,
        "type_file": 0,
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
        "temporal": {"century": century, "decade": decade, "year": year},
        "spatial": spatial,
        "genre": genre,
        "meter": meter,
        "tempo": tempo,
        "real_key": key,
        "mode": mode,
        "instruments": [],
        "title_xml": id,
        "xml": "",
        "midi": "",
        "audio": "",
        "video": "",
        "review": True,
        # "col_id": 0 # Revisar este valor para que coincida con algo de la tabla col
    }

    return metadata

