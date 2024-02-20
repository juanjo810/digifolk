# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 15:45:52 2023

@author: Nádia Carvalho
"""

from collections import defaultdict
import copy

import converter21 as c21
import music21 as m21
import verovio
from xml.etree import ElementTree as ET
#import ms3





class MTCExtractor():
    """
    Show Structure 
    """
    

    

    



    def __init__(self, path, mei_tree, musical_metadata=None):
        """
        Parse MEI file and extract features
        """
        self.tk = verovio.toolkit()
        self.tk.setOptions({"xmlIdChecksum": False, "xmlIdSeed": 0})
        self.tk.loadFile(path)
        # self.tk.renderToSVGFile('data/temp.svg')

        # m21.environment.Environment('converter21.mei.base')['warnings'] = 0 # type: ignore
        converter = c21.MEIConverter()
        self.music_stream = converter.parseFile(path, verbose=False)

        try:
            self.music_stream = self.music_stream.expandRepeats()
        except:
            for repeat_bracket in self.music_stream.recurse().getElementsByClass('RepeatBracket'):
                spanner_measures = repeat_bracket.getSpannedElements()

                if len(spanner_measures) > 0:
                    number_to_get = spanner_measures[0].number
                    ending = mei_tree.find(f'.//mei:measure[@n="{number_to_get}"]...', namespaces={
                                           'mei': 'http://www.music-encoding.org/ns/mei'})
                    if ending is not None:
                        ending_markings = [
                            int(i) for i in ending.attrib['n'].split(', ')]
                        if len(ending_markings) == 1:
                            repeat_bracket.number = ending_markings[0]
                        elif list(range(ending_markings[0], ending_markings[-1])) == ending_markings:
                            repeat_bracket.number = f'{ending_markings[0]}-{ending_markings[-1]}'
                        else:
                            repeat_bracket.number = ', '.join(
                                [str(i) for i in ending_markings])

                        if isinstance(spanner_measures[-1].rightBarline, m21.bar.Repeat) and len(ending_markings) > 1:
                            spanner_measures[-1].rightBarline.times = len(
                                ending_markings)

            try:
                self.music_stream = self.music_stream.expandRepeats()
            except:
                print('Error expanding repeats in: ' + path)
                return None

        self.metadata = {}
        if musical_metadata:
            self.metadata = musical_metadata

    def process_stream(self):
        """
        Process Music21 stream to extract JSON data
        """
        chords = self.music_stream.recurse().getElementsByClass(m21.chord.Chord)  # type: ignore
        if len(chords) > 0:
            voices_to_create = max(len(chord.pitches) for chord in chords)
            for measure in self.music_stream.recurse().getElementsByClass(m21.stream.Measure): # type: ignore
                if len(measure.voices) != voices_to_create:
                    new_voice = copy.deepcopy(measure.voices[-1])
                    new_voice.id = len(measure.voices) + 1
                    measure.insert(0, new_voice) # type: ignore
                for voice in measure.voices:
                    for chord in voice.recurse().getElementsByClass(m21.chord.Chord): # type: ignore
                        if len(chord.pitches) > 1:
                            p = chord.pitches[int(voice.id)-1]
                            new_chord = m21.note.Note(p, duration=chord.duration) # type: ignore
                            voice.replace(chord, new_chord) # type: ignore

        self.music_stream = self.music_stream.voicesToParts(separateById=True)
        return [self.process_inside_stream(part) for part in self.music_stream.parts]


    def has_lyrics(self):
        """
        Check if stream has lyrics
        """
        text = m21.text.assembleLyrics(self.music_stream)
        return 'Vocal' if text is not None else 'Instrumental'
    
    # method to parse a music21 object to MIDI
    def m21_to_midi(self,output_file):
        # output_file: file path and filename

        # Generate the MIDI file
        self.music_stream.write('midi', fp=output_file)
    
    def m21_to_xml(self,output_file):
        # Convert the stream to MusicXML string representation
        musicxml_string = m21.musicxml.m21ToString.fromMusic21Object(self.music_stream)

        # Write the MusicXML string to a file
        with open("output_music.xml", "w") as xml_file:
            xml_file.write(musicxml_string)
    
    def muses_to_midi(input_file, output_file):
        ms = MuseScore()
        ms.convert(input_file, output_file, format="midi")



if __name__ == "__main__":
    mei_path="ES-1913-B-JSV-001.mei"
    # score=parseEndings(mei_path)
    score = MTCExtractor(mei_path,ET.parse(mei_path))
    # Parse the XML file
    tree = ET.parse(mei_path)
    root = tree.getroot()

    # Start exploring from the root element
    score.explore_xml_element(root)


    # Define the target element tag and the new attribute to add
    target_element_tag = 'title'
    new_attribute = ('type', 'main')
    text='TITULO PROBANDO'

    # Start the search and modify process from the root element
    tree_modified=score.search_and_modify(root, text, target_element_tag, new_attribute)
    if tree_modified==None:
        # add the new element as a child of a parent element called meiStmt
        parent_element_tag = 'meiStmt'
        parent_element = tree.find(parent_element_tag)
        new_element = ET.SubElement(parent_element, target_element_tag)
        new_element.set(new_attribute[0], new_attribute[1])
        new_element.text = text


    # Save the modified XML to a new file
    #tree.write('modified_xml_file.xml')
    
    #mscore = ms3.Score("ES-1913-B-JSV-001.mscz")
    #score.music_stream.write('musicxml', fp="ES-1913.xml")
