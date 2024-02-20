"""
Class to Extract MEI Information
"""

import verovio
from lxml import etree
import csv

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

def note_similarity_degree(note1, note2):
    """Check if two notes are similar"""
    sim = 0
    attrs = list(note1.attrib.keys())
    for attr in attrs:
        if note1.get(attr) == note2.get(attr):
            sim += 1
    return sim / len(attrs)



class MEIExtractor:
    def __init__(self):
        """
        GET NECESSARY INFORMATION
        """
        self.tk = verovio.toolkit()
        self.tk.setOptions({"xmlIdChecksum": False, "xmlIdSeed": 0})

    def extract_file(self, name, musicxml_path, old_mei_path=None, pandas_data=None, sources=None):
        self.tk.loadFile(musicxml_path)

        self.name = name
        self.date = name.split('-')[1]
        if 'X' not in self.date:
            self.date = int(self.date)

        if pandas_data is not None:
            self.pd_data = pandas_data.loc[pandas_data['name'] == name]
        if sources is not None:
            self.sources = sources

        try:
            if old_mei_path is not None:
                self.old_mei = etree.parse(old_mei_path)  # type: ignore
            else:
                self.old_mei = None
        except:
            print('Cannot parse old MEI')
            self.old_mei = None

        try:
            self.root = etree.fromstring(
                self.tk.getMEI().encode(), etree.XMLParser(remove_blank_text=True))
            print("MEI Parsed")
        except:
            print('Cannot parse new MEI')
        else:
            if self.old_mei is not None:
                self.process()

            tree = etree.ElementTree(self.root)
            #tree.write(f'iFolkCleaner/database_new/clean_meis/{self.name}.mei', pretty_print=True, xml_declaration=True, encoding="utf-8")

    def process(self):
        """
        Extract:

        1. File Description
        2. Encoding Description (Not necessary at the moment)
        3. Worklist
        """

        # File Description
        fileDesc = self.root.find('.//mei:fileDesc', NAME_SPACE)
        self.extract_title_statement(fileDesc)
        self.extract_publishing_statement(fileDesc)
        self.extract_source_description(fileDesc)

        # Worklist
        self.extract_worklist()

        try:
            self.extract_ambitus_information()
        except:
            print('Cannot extract ambitus information')

        try:
            self.extract_phrase_and_rythymn_pattern_information()
        except:
            print('Cannot extract phrase and rythymn pattern information')

        try:
            self.extract_all_cadences_information()
        except:
            print('Cannot extract cadences information')

    def extract_title_statement(self, fileDesc):
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
        titleTag.set("type", "main")

        titleTag.set(ID_SPACE, f"{self.name}")
        titleTag.text = self.extract_info_data('title')

        subtitleTag = etree.Element(
            f'{MEI_SPACE}title', type="subtitle")  # type: ignore
        subtitleTag.text = self.extract_info_data('alt_title')
        titleTag.addnext(subtitleTag)

        respStmt = titleStmt.find('.//mei:respStmt', NAME_SPACE)

        compilerTag = etree.SubElement(
            respStmt, f'{MEI_SPACE}persName', role="compiler")  # type: ignore
        compilerTag.text = self.extract_info_data('compiler')

        informantTag = etree.SubElement(
            respStmt, f'{MEI_SPACE}persName', role="informer")  # type: ignore
        informantTag.text = self.extract_info_data('informer')

        informantGeogName = etree.SubElement(
            informantTag, f'{MEI_SPACE}geogName')  # type: ignore
        informantGeogName.text = self.extract_info_data('informer_geogName')

        encoderTag = etree.SubElement(
            respStmt, f'{MEI_SPACE}persName', role="encoder")  # type: ignore
        encoderTag.text = self.extract_info_data('encoder')

        editorTag = etree.SubElement(
            respStmt, f'{MEI_SPACE}persName', role="editor")  # type: ignore
        editorTag.text = self.extract_info_data('editor')

    def extract_publishing_statement(self, fileDesc):
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
        publisherTag.text = 'co_POEM Reseach Project'

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

    def extract_source_description(self, fileDesc):
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
        source_title_info = self.extract_info_data('source_title')
        if source_title_info is not None:

            titleTag.text = source_title_info.title()

            self.sources = self.sources.loc[self.sources['title'] == titleTag.text]
            if self.sources.shape[0] > 1:
                self.sources = self.sources.loc[self.sources['date'] == self.date]

            subtitleTag = etree.SubElement(
                imprint, f'{MEI_SPACE}title', type='subordinate')  # type: ignore
            subtitleTag.text = self.extract_info_data('source_subtitle')

            respStmt = etree.SubElement(
                imprint, f'{MEI_SPACE}respStmt')  # type: ignore
            recopiladorTag = etree.SubElement(
                respStmt, f'{MEI_SPACE}persName', role="compiler")  # type: ignore
            recopiladorTag.text = self.extract_info_data('source_compiler')
            colaboradorTag = etree.SubElement(
                respStmt, f'{MEI_SPACE}persName', role="bibliography")  # type: ignore
            colaboradorTag.text = self.extract_info_data('source_bibliografia')
            introductionTag = etree.SubElement(
                respStmt, f'{MEI_SPACE}persName', role="introduction")  # type: ignore
            introductionTag.text = self.extract_info_data('source_introduction')
            editionTag = etree.SubElement(
                respStmt, f'{MEI_SPACE}persName', role="edition")  # type: ignore
            editionTag.text = self.extract_info_data('source_edition')

            publisherTag = etree.SubElement(
                imprint, f'{MEI_SPACE}publisher')  # type: ignore
            publisherTag.text = self.extract_info_data('source_publisher')

            pubPlaceTag = etree.SubElement(
                imprint, f'{MEI_SPACE}pubPlace')  # type: ignore
            pubPlaceTag.text = self.extract_info_data('source_publication_place')

            dateTag = etree.SubElement(
                imprint, f'{MEI_SPACE}date')  # type: ignore
            dateTag.text = self.extract_info_data('source_date')

            extentTag = etree.SubElement(
                imprint, f'{MEI_SPACE}extent', type="pages")  # type: ignore
            extentTag.text = self.extract_info_data('source_pages')

    def extract_worklist(self):
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

        meiHead = self.root.find('.//mei:meiHead', NAME_SPACE)
        work = etree.SubElement(
            etree.SubElement(
                meiHead, f'{MEI_SPACE}workList'), f'{MEI_SPACE}work')  # type: ignore
        print (work)

        titleTag = etree.SubElement(
            work, f'{MEI_SPACE}title', type="main")  # type: ignore
        titleTag.text = self.extract_info_data('title')
        print (titleTag)

        author = etree.SubElement(
            work, f'{MEI_SPACE}author', type="informant")  # type: ignore
        author.text = self.extract_info_data('author')

        incip = etree.SubElement(etree.SubElement(
            etree.SubElement(work, f'{MEI_SPACE}incip',
                             type="lyrics"),  # type: ignore
            f'{MEI_SPACE}incipText'),
            f'{MEI_SPACE}head')
        incip.text = self.extract_info_data('incip_lyrics')

        mode = self.extract_info_data('mode').lower() # type: ignore
        if mode == 'jonic':
            mode = 'ionian'
        elif mode == 'eolian':
            mode = 'aeolian'

        keyTag = etree.SubElement(
            work, f'{MEI_SPACE}key', mode=f"{mode}")  # type: ignore
        keyTag.text = self.extract_info_data('real_key')

        meterTag = etree.SubElement(work, f'{MEI_SPACE}meter')  # type: ignore
        meterTag.text = self.extract_info_data('meter')

        tempoTag = etree.SubElement(work, f'{MEI_SPACE}tempo')  # type: ignore
        tempoTag.text = self.extract_info_data('tempo')

        measuresTag = etree.SubElement(etree.SubElement(
            etree.SubElement(work, f'{MEI_SPACE}incip',
                             type="musical"),  # type: ignore
            f'{MEI_SPACE}score'),
            f'{MEI_SPACE}section')

        measures = self.root.xpath('.//mei:measure', namespaces=NAME_SPACE)
        n_add = 2
        if self.old_mei is not None:
            n_add = len(self.old_mei.xpath('.//mei:incip//mei:score//mei:measure', namespaces=NAME_SPACE))

        m_n_id = [(m.get('n'), m.get(
            '{http://www.w3.org/XML/1998/namespace}id')) for m in measures]
        _ = [etree.SubElement(
             measuresTag, f'{MEI_SPACE}measure', copyof=f"#{m[1]}") for m in m_n_id[:n_add]]  # type: ignore

        if self.old_mei is not None:
            work.append(self.old_mei.xpath('.//mei:langUsage', namespaces=NAME_SPACE)[0])

            notes_stmt = self.old_mei.xpath('.//mei:work//mei:notesStmt', namespaces=NAME_SPACE)[0]
            for c in list(notes_stmt):
                if c.text:
                    c.text = c.text.strip()
            work.append(notes_stmt)

        classificationTermList = etree.SubElement(etree.SubElement(work, f'{MEI_SPACE}classification'), f'{MEI_SPACE}termList') # type: ignore

        genreTag = etree.SubElement(classificationTermList, f'{MEI_SPACE}term', type='genre') # type: ignore
        genreTag.text = self.extract_info_data('genre')

        regionTag = etree.SubElement(classificationTermList, f'{MEI_SPACE}term', type='region') # type: ignore
        regionTag.text = self.extract_info_data('region')

        districtTag = etree.SubElement(classificationTermList, f'{MEI_SPACE}term', type='district') # type: ignore
        districtTag.text = self.extract_info_data('district')

        cityTag = etree.SubElement(classificationTermList, f'{MEI_SPACE}term', type='city') # type: ignore
        cityTag.text = self.extract_info_data('city')

    def extract_ambitus_information(self):
        """
        Convert Ambitus Information from Old MEIs
        """
        scoreDef = self.root.find('.//mei:score/mei:scoreDef', NAME_SPACE)

        ambitusTag = etree.SubElement(
            scoreDef, f"{MEI_SPACE}ambitus")  # type: ignore

        lowestNote = self.extract_info_data('ambitus_low')
        etree.SubElement(ambitusTag, f"{MEI_SPACE}ambNote", type="lowest",
                         oct=lowestNote[-1], pname=''.join(lowestNote[:-1]).lower())  # type: ignore

        highestNote = self.extract_info_data('ambitus_high')
        etree.SubElement(ambitusTag, f"{MEI_SPACE}ambNote", type="highest",
                         oct=highestNote[-1], pname=''.join(highestNote[:-1]).lower())  # type: ignore

    def extract_phrase_and_rythymn_pattern_information(self):
        """
        Convert Rhythm Pattern and Phrase Information from Old MEIs
        """
        score_section = self.root.find(
            './/mei:body//mei:score/mei:section', NAME_SPACE)

        if self.old_mei is not None:
            rhythm_pattern = self.old_mei.xpath(
                MEILINKS['rhythm_pattern'], namespaces=NAME_SPACE)
            score_section.insert(0, rhythm_pattern[0])

            phrase_info = self.old_mei.xpath(
                MEILINKS['phrases'], namespaces=NAME_SPACE)

            supplied_phrases = etree.Element(
                f"{MEI_SPACE}supplied", type="phrases", nsmap=NAME_SPACE)  # type: ignore

            last_phrase_num = 0
            if len(phrase_info) > 0:
                last_phrase_num = int(phrase_info[-1].get('n'))

            for phrase in phrase_info:
                start_id = self.get_new_phrase_note(phrase.get('startid'))
                end_id = self.get_new_phrase_note(phrase.get('endid'))

                etree.SubElement(
                    supplied_phrases,
                    f"{MEI_SPACE}phrase",
                    n=phrase.get('n'),
                    startid=start_id,
                    endid=end_id,
                    type=phrase.get('type'),
                    nsmap=NAME_SPACE)  # type: ignore

                has_repeat_in = self.check_phrase_repeats(start_id, end_id)
                if has_repeat_in is not None:

                    if has_repeat_in != (start_id, end_id):
                        last_phrase_num += 1
                        etree.SubElement(
                            supplied_phrases,
                            f"{MEI_SPACE}phrase",
                            n=str(last_phrase_num),
                            startid=has_repeat_in[0],
                            endid=has_repeat_in[1],
                            type=phrase.get('type'),
                            nsmap=NAME_SPACE) # type: ignore

            score_section.insert(1, supplied_phrases)

    def check_phrase_repeats(self, start_id, end_id):
        """Check if Phrase Repeats"""

        if start_id:
            start_note = self.root.xpath(
                        f".//mei:note[@xml:id='{start_id.replace('#', '')}']", namespaces=NAME_SPACE)

            if start_note and len(start_note) > 0:
                start_note_measure = list(start_note[0].iterancestors(f'{MEI_SPACE}measure', NAME_SPACE))[0]
                start_note_measure_number = start_note_measure.get('n')

                next_measure = self.root.xpath(f'.//mei:measure[@n=%s]' % str(int(start_note_measure_number) + 1), namespaces=NAME_SPACE)
                if len(next_measure) > 0:
                    next_measure = next_measure[0]
                else:
                    return None

                if next_measure.get('left') == 'rptstart':
                    # The measure is followed by a repeat start.
                    # We need to find the last measure of the repeated section
                    # and add a new phrase starting on the annacruxis there.
                    end_measure = self.root.xpath('.//mei:measure[@right="rptend" or @right="rptboth"]', namespaces=NAME_SPACE)[0]
                    end_measure_notes = end_measure.xpath('.//mei:note', namespaces=NAME_SPACE)

                    note_in_measure = list(reversed(list(start_note_measure.xpath('.//mei:note', namespaces=NAME_SPACE)))).index(start_note[0])
                    new_note = end_measure_notes[len(end_measure_notes)-1-note_in_measure]

                    new_phrase_start = f"#{new_note.get('{http://www.w3.org/XML/1998/namespace}id')}"

                    if end_id.replace("#", "") != end_measure_notes[len(end_measure_notes)-2-note_in_measure]:
                        # If the end of the phrase is not the note before the new start note, we don't need to do anything,
                        # ENDID is going to be the same for new phrase.
                        # Otherwise, we need to go to the next measure and find the note that is the same as the old end note.

                        new_phrase_end = end_id
                    else:
                        next_measure = self.root.xpath(f'.//mei:measure[@n=%s]' % str(int(end_measure.get('n')) + 1), namespaces=NAME_SPACE)
                        if len(next_measure) > 0:
                            next_measure = next_measure[0]
                        else:
                            return (new_phrase_start, '')

                        end_measure_notes = next_measure.xpath('.//mei:note', namespaces=NAME_SPACE)

                        notes_by_simil = [(note_similarity_degree(start_note[0], n), n.get('{http://www.w3.org/XML/1998/namespace}id')) for n in end_measure_notes]
                        sorted_notes_by_simil = sorted(notes_by_simil, key=lambda x: x[0])
                        filtered_notes_by_simil = list(filter(lambda x: x[0] == sorted_notes_by_simil[-1][0], sorted_notes_by_simil))

                        new_phrase_end = f"#{filtered_notes_by_simil[-1].get('{http://www.w3.org/XML/1998/namespace}id')}" # type: ignore

                    return (new_phrase_start, new_phrase_end)
                else:
                    new_phrase_start = start_id

                    end_note = self.root.xpath(
                        f".//mei:note[@xml:id='{end_id.replace('#', '')}']", namespaces=NAME_SPACE)

                    end_note_measure = list(end_note[0].iterancestors(f'{MEI_SPACE}measure', NAME_SPACE))[0]

                    if end_note_measure.get('right') in ['rptend', 'rptboth']:
                        # The measure is followed by a repeat end.
                        next_measure = self.root.xpath(f'.//mei:measure[@n=%s]' % str(int(end_note_measure.get('n')) + 1), namespaces=NAME_SPACE)
                        if len(next_measure) > 0:
                            next_measure = next_measure[0]
                        else:
                            return (new_phrase_start, '')

                        end_measure_notes = next_measure.xpath('.//mei:note', namespaces=NAME_SPACE)

                        if next_measure.get('n') == len(self.root.xpath('.//mei:measure', namespaces=NAME_SPACE)):
                            new_phrase_end = f"#{end_measure_notes[-1].get('{http://www.w3.org/XML/1998/namespace}id')}"
                        else:
                            notes_by_simil = [(note_similarity_degree(start_note[0], n), n.get('{http://www.w3.org/XML/1998/namespace}id')) for n in end_measure_notes]
                            sorted_notes_by_simil = sorted(notes_by_simil, key=lambda x: x[0])
                            filtered_notes_by_simil = list(filter(lambda x: x[0] == sorted_notes_by_simil[-1][0], sorted_notes_by_simil))
                            new_phrase_end = f"#{filtered_notes_by_simil[-1][1]}" # type: ignore
                        return (new_phrase_start, new_phrase_end)
                    else:
                        return None
        return None

    def extract_all_cadences_information(self):
        """
        """
        if self.old_mei is None:
            return

        cadence_tags = self.old_mei.xpath(".//mei:note[@type]", namespaces=NAME_SPACE)
        cadence_id_type = [(c.get('{http://www.w3.org/XML/1998/namespace}id'), c.get('type')) for c in cadence_tags]
        new_ids = [(self.get_new_phrase_note(c[0]),c[1]) for c in cadence_id_type]

        notes =  [(self.root.xpath(".//mei:note[@xml:id='%s']" % id[0].replace('#', ''), namespaces=NAME_SPACE), id[1]) for id in new_ids]
        for (n, ct) in notes:
            for n0 in n:
                n0.set('type', ct)

    def get_new_phrase_note(self, id):
        """
        GET ID OF NEW START NOTE
        """
        if self.old_mei is None:
            return ''

        exp_st = ".//mei:note[@xml:id='%s']" % id.replace('#', '')
        start_note = self.old_mei.xpath(exp_st, namespaces=NAME_SPACE)
        if len(start_note) > 0:
            start_note = start_note[0]
        else:
            return ''

        start_note_measure = list(start_note.iterancestors(
            f'{MEI_SPACE}measure', NAME_SPACE))[0].get('n')

        measure_notes = self.old_mei.xpath(
            './/mei:measure[@n=%s]//mei:note' % start_note_measure, namespaces=NAME_SPACE)
        note_in_measure = measure_notes.index(start_note)

        new_measure_notes = self.root.xpath(
            './/mei:measure[@n=%s]//mei:note' % start_note_measure, namespaces=NAME_SPACE)

        if len(new_measure_notes) > note_in_measure:
            return f"#{new_measure_notes[note_in_measure].get('{http://www.w3.org/XML/1998/namespace}id')}"
        elif len(new_measure_notes) > 0:
            return f"#{new_measure_notes[-1].get('{http://www.w3.org/XML/1998/namespace}id')}"

        return ''

    def extract_info_data(self, info_to_extract=None):
        """
        Try Extracting data from pandas columns
        """

        if 'source' in info_to_extract and info_to_extract != 'source_title':  # type: ignore
            data = str(self.sources[info_to_extract.replace(  # type: ignore
                'source_', '')].item())
            if data == 'nan':
                data = ''
        else:
            try:
                ite = info_to_extract
                if info_to_extract == 'tempo':
                    ite = 'tempo2'
                if info_to_extract == 'meter':
                    ite = 'meter2'

                data = str(self.pd_data[ite].item())
                if data is None:
                    elm = self.old_mei.xpath(MEILINKS[info_to_extract], namespaces=NAME_SPACE)
                    if len(elm) > 0:
                        data = '; '.join([e.text for e in elm if e.text is not None])
            except:
                data = self.extract_info_data_oldmei(info_to_extract)

            if data == 'nan':
                data = self.extract_info_data_oldmei(info_to_extract)

            # print(f'{info_to_extract} {data}')
        print(data)
        return data

    def extract_info_data_oldmei(self, info_to_extract):
        """
        Try to exctract the data from old mei
        """
        data = None

        if self.old_mei is not None and info_to_extract in MEILINKS:
            elm = self.old_mei.xpath(
                MEILINKS[info_to_extract], namespaces=NAME_SPACE)
            if len(elm) > 0:
                data = '; '.join([e.text for e in elm if e.text is not None])

        elif info_to_extract == 'source_date':
            data = self.pd_data['name'].item().split('-')[1]

        if data and (data == 'nan' or len(data) == 0 or data.isspace()):
            data = None

        return data

    def extract_info_both_sources(self, info_to_extract):

        if self.old_mei is None:
            elm = []
        else:
            elm = self.old_mei.xpath(
                    MEILINKS[info_to_extract], namespaces=NAME_SPACE)

        elm2 = self.pd_data[info_to_extract].to_list()

        if elm:
            elm.extend(elm2)
        else:
            elm = elm2

        clean_elm = []
        for cr in elm:
            if cr is not None:
                if isinstance(cr, str) or isinstance(cr, int) or isinstance(cr, float):
                    clean_elm.append(str(cr))
                else:
                    label = cr.get('label')
                    if label and any(c.isalpha() for c in label):
                        clean_elm.append(label)
                    txt = cr.text
                    if txt and any(c.isalpha() for c in txt):
                        clean_elm.append(txt)
        return clean_elm
    
    def get_phrases_in_mei(self, mei_tree):
        """Get Phrase Information from MEI File"""
        phrase_info = mei_tree.xpath(
                MEILINKS['phrases'], namespaces=NAME_SPACE)
        phrases = []
        for phrase in phrase_info:
            phrases.append((phrase.get('n'),phrase.get('startid'),phrase.get('endid'),phrase.get('type'))) # type: ignore
        return phrases

    def compare_phrases(self, old_mei, new_mei, name):
        print('NEW')
        self.view_phrases(new_mei, name=f'svgs/{name}_new.svg')
        print()
        print('OLD')
        self.view_phrases(old_mei, name=f'svgs/{name}_old.svg')

    def view_phrases(self, mei_file, name):
        self.tk.loadFile(mei_file)
        self.tk.setScale(20)

        phrases = self.get_phrases_in_mei(etree.parse(mei_file)) # type: ignore

        for page in range(self.tk.getPageCount()):

            svg = self.tk.renderToSVG(pageNo=page+1, xmlDeclaration=False)

            try:
                svg_tree = etree.fromstring(svg) # type: ignore
            except etree.XMLSyntaxError:
                print(f'Cannot parse SVG of music {name}')
                return

            for f in phrases:
                print(f)
                try:
                    svg_tree.xpath(f"//*[@id='{f[1].replace('#', '')}']")[0].set('fill', 'red')
                    svg_tree.xpath(f"//*[@id='{f[2].replace('#', '')}']")[0].set('fill', 'red')
                except:
                    print(f'Cannot find {f[1]} or {f[2]}')

            etree.ElementTree(svg_tree).write('_'.join([name.split('_')[0] + f'-page-{page+1}'] + name.split('_')[1:]), pretty_print=True,
                        xml_declaration=True, encoding="utf-8")

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
    mei_name="ES-1913-B-JSV-001"
    mei_path ="./"+mei_name+".mei"
    # score=parseEndings(mei_path)
    score = MEIExtractor()
    score.extract_file(mei_name,mei_path)
    score.process()
    filename = "class_attributes.csv"
    map_class_to_csv(score, filename)

