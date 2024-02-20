#!/usr/bin/env python3.7
"""
This script presents the class Parser that tries different approaches to segment a melodic line
"""

import bz2
import json
import os
import pickle
from xml.etree import ElementTree as ET

import music21

import app.composition.representation.parsers.utils as utils
import app.composition.representation.utils.printing as printing
import app.composition.representation.utils.voice as voice_utils
from app.composition.representation.events.linear_event import PartEvent
from app.composition.representation.events.interpart_event import InterPartEvent
from app.composition.representation.parsers.line_parser import LineParser
from app.composition.representation.parsers.interpart_parser import InterPartParser

FOLDER_DEFAULT = ['data', 'myexamples']
LINEAR_INSTRUMENTS = ['WoodwindInstrument', 'BrassInstrument']


class MusicParser:
    """
    A class used to parse a musical file.

    Attributes
    ----------
    """

    def __init__(self, filename=None, score=None, metadata=None, mei_filename=None, folders=None):

        if folders is None:
            folders = FOLDER_DEFAULT

        self.name = filename
        self.music = None
        self.music_parts = []
        self.first_part = None

        self.analysis = {}

        self.music_events = {
            'part_events': {},
            'interpart_events': []
        }

        self.exception = False

        if score:
            try:
                self.music = score.expandRepeats()
                self.analysis = {
                    'key': {
                        'key_mode': metadata['real_key'],
                        'mode': metadata['mode'],
                    },
                    'meter': metadata['meter'],
                    'tempo': metadata['tempo'],
                    'classes': {'genre': metadata['genre']},
                }
            except music21.repeat.ExpanderException as exception:
                self.exception = exception
            if not self.exception:
                self.clean_hidden_music()
        elif filename is not None:
            try:
                self.music = music21.converter.parse(
                    filename, format=filename[-3:])

                if mei_filename and filename[-3:] != 'mei':
                    self.get_MEI_info(mei_filename)
                elif filename[-3:] == 'mei':
                    self.clean_endings(filename)
                    self.get_MEI_info(filename)

                self.music = self.music.expandRepeats()

            except music21.musicxml.xmlToM21.MusicXMLImportException as exception:
                self.exception = exception

            if not self.exception:
                self.clean_hidden_music()

    def clean_endings(self, filename):
        """
        CLEAN ENDINGS IF MEI FILE
        """
        ns = {'mei': 'http://www.music-encoding.org/ns/mei'}
        endings = ET.parse(filename).getroot().findall(".//mei:ending", ns)
        measures_beg = ET.parse(filename).getroot().findall(
            ".//mei:measure", ns)
        first_measure = int([meas.get('n')
                             for meas in measures_beg if meas.get('n')][0])

        for end in endings:
            measures = [el for el in end.iter() if el.tag ==
                        '{}measure'.format('{' + ns['mei'] + '}')]
            first_number = 0
            for i, measure in enumerate(measures):
                number = int(measure.get('n'))
                if first_measure == 0:
                    number += 1
                if i == 0:
                    first_number = number

                meas = music21.mei.base.measureFromElement(
                    measure, backupNum=number, expectedNs=['1'])

                if number <= self.music.parts[0].measure(-1).number:
                    last_measure = self.music.parts[0].measure(number - 1)
                    offset = last_measure.offset + last_measure.barDuration.quarterLength
                    self.music.parts[0].insertAndShift(offset, meas['1'])
                else:
                    self.music.parts[0].append(meas['1'])

            music21.repeat.insertRepeatEnding(
                self.music, first_number, first_number + len(measures), endingNumber=int(end.get('n')), inPlace=True)

    def get_MEI_info(self, filename):
        """
        Get Important Information from MEI File
        """
        ns = {'mei': 'http://www.music-encoding.org/ns/mei'}
        root = ET.parse(filename).getroot()

        title = ET.parse(
            filename).getroot().findall(".//mei:title", ns)[0].text
        composer = ET.parse(
            filename).getroot().findall(".//mei:author", ns)[0].text
        if not composer:
            composer = 'Anonymous'

        subtitle = filename[filename.rfind(os.sep) + 1: -4]

        self.music.metadata = music21.metadata.Metadata(
            title=title, composer=composer, subtitle=subtitle)

        keys = root.findall('.//mei:key', ns)
        mode = keys[0].attrib['mode']
        k_mode = keys[0].text

        meters = root.findall('.//mei:meter', ns)
        meter = meters[0].text

        tempos = root.findall('.//mei:tempo', ns)
        tempo = tempos[0].text

        classes = {}
        class_ = root.findall('.//mei:classification', ns)
        class_terms = class_[0].findall('mei:termList/mei:term', ns)
        for term in class_terms:
            classes[term.attrib['type']] = term.text

        self.analysis = {
            'key': {
                'key_mode': k_mode,
                'mode': mode
            },
            'meter': meter,
            'tempo': tempo,
            'classes': classes
        }

    def parse(self, parts=True, interpart=True, number_parts=None, verbose=True):
        """
        Parse music
        """
        if self.exception:
            return

        if parts:
            self.music.makeVoices(inPlace=True)
            self.music.flattenUnnecessaryVoices(inPlace=True)
            if self.music.hasVoices():
                self.music = self.music.voicesToParts(separateById=True)

            self.music_parts = self.music.parts
            if number_parts is None or number_parts > len(self.music_parts):
                number_parts = len(self.music_parts)

            for i in range(number_parts):
                part = self.music_parts[i]

                instrument = utils.instrument_for_voices(
                    part.getInstrument().instrumentName)
                is_linear_instrument = any(val in instrument.classes for
                                           val in LINEAR_INSTRUMENTS)

                if (is_linear_instrument and
                        (len(part.recurse(classFilter='Chord')) > 0 or part.hasVoices())):
                    self.process_voiced_part_linear_instruments(
                        part, i, instrument)
                elif not part.isSequence() or part.hasVoices():
                    self.process_voiced_part(part, i, instrument)
                else:
                    _, name = self.name_of_part(instrument)
                    self.music_events['part_events'][name] = self.parse_sequence_part(
                        part, name=name, first=(False, True)[i == 0], verbose=verbose)

        if interpart and (len(self.music.parts) > 1 or
                          len(self.music.getOverlaps()) > 0 or
                          len(self.music.recurse(classFilter='Chord')) > 0):
            print('Processing InterPart Events')
            self.music_events['interpart_events'] = InterPartParser(
                self.music).parse_music()
            print('End of Processing {} InterPart Events'.format(
                len(self.music_events['interpart_events'])))

    def parse_sequence_part(self, part, name=None, first=False, verbose=True):
        """
        Parse sequence
        """
        if name is None:
            name = part.partName

        if verbose:
            print('Processing part {}'.format(name))

        parser = LineParser(part, self.music.metadata, self.analysis)
        parsed = parser.parse_line()

        first_metro_marks = list(
            self.music.parts[0].flat.metronomeMarkBoundaries())
        if not first and first_metro_marks != list(part.flat.metronomeMarkBoundaries()):
            parser.metronome_marks_parsing(first_metro_marks, parsed)

        if verbose:
            print('End of Processing part {}'.format(name))

        return parsed

    def process_voiced_part_linear_instruments(self, part, i, real_in):
        """
        Process a part that has overlappings
        """
        max_voice_count = voice_utils.get_number_voices(part)

        if isinstance(part, music21.stream.Part):
            part = music21.stream.Stream(part)

        for measure in list(part.recurse(classFilter='Measure')):
            measure.flattenUnnecessaryVoices(inPlace=True)
            if measure.hasVoices():
                voice_utils.process_voiced_measure(measure, max_voice_count)
            else:
                voice_utils.make_voices(measure, in_place=True,
                                        number_voices=max_voice_count)

        new_parts = part.voicesToParts()
        if hasattr(new_parts, 'parts'):
            for j, voice in enumerate(new_parts.parts):
                voice.insert(0, real_in)
                index, name = self.name_of_part(real_in, j)
                self.music_events['part_events'][index] = self.parse_sequence_part(
                    voice, name=name, first=(False, True)[i == 0])
        else:
            new_parts.insert(0, real_in)
            index, name = self.name_of_part(real_in)
            self.music_events['part_events'][index] = self.parse_sequence_part(
                new_parts, name=name, first=(False, True)[i == 0])

    def process_voiced_part(self, part, i, real_in):
        """
        Process a part that has voices: divide voices in new parts
        """
        part.recurse().flattenUnnecessaryVoices(inPlace=True, force=True)

        new_parts = part
        if len(part.recurse(classFilter='Voice')) > 0:
            try:
                new_parts = part.voicesToParts(separateById=True)
            except Exception:
                new_parts = part.voicesToParts(separateById=False)

        if hasattr(new_parts, 'parts'):
            for j, voice in enumerate(new_parts.parts):
                voice.insert(0, real_in)
                index, name = self.name_of_part(real_in, j)
                self.music_events['part_events'][index] = self.parse_sequence_part(
                    voice, name=name, first=(False, True)[i == 0])
        else:
            new_parts.insert(0, real_in)
            index, name = self.name_of_part(real_in)
            self.music_events['part_events'][index] = self.parse_sequence_part(
                new_parts, name=name, first=(False, True)[i == 0])

    def name_of_part(self, real_in, j=None):
        """
        Return Index and Name of a part
        """
        if j is not None:
            index = str(real_in) + '.' + str(j)
            name = str(real_in) + ', voice ' + str(j)

            counter = [1 for key in self.music_events['part_events'].keys()
                       if str(real_in) in key and str(j) in key]

            if len(counter) > 0:
                index = str(real_in) + '_' + \
                    str(len(counter) + 1) + '.' + str(j)
                name = str(real_in) + '_' + str(len(counter) + 1) + \
                    ', voice ' + str(j)
        else:
            index = str(real_in)
            name = str(real_in)
            counter_0 = [key for key in self.music_events['part_events'].keys()
                         if str(real_in) in key]
            counter = set([key.split('.')[0] for key in counter_0])
            if len(counter) > 0:
                index = str(real_in) + '_' + str(len(counter) + 1)
                name = str(real_in) + '_' + str(len(counter) + 1)

        return index, name

    def clean_hidden_music(self):
        """
        Clean Hidden Elements From Score
        """
        for _elm in self.music.recurse():
            if '_style' in _elm.__dict__ and not isinstance(_elm.style, str) and _elm.style.hideObjectOnPrint:
                self.music.remove(_elm, recurse=True)

    def show_events(self, events='all parts', part_number=0,
                    parts=None, viewpoints='all', offset=False):
        """
        Show sequence of events
        """
        if viewpoints == 'all':
            self.show_all_viewpoints(events, parts, part_number)
        else:
            _ = [self.show_single_viewpoints(
                viewpoint, events, part_number, parts, offset) for viewpoint in viewpoints]

    def show_all_viewpoints(self, events='all parts', parts=None, part_number=0):
        """
        Show all viewpoints
        """
        if events == 'one part':
            _ = [print(str(ev) + '\n')
                 for ev in self.music_events['part_events'][part_number]]
        elif events == 'some parts' and parts is not None:
            for part in parts:
                print('Part ' + str(part))
                _ = [print(str(ev) + '\n')
                     for ev in self.music_events['part_events'][part]]
                print('')
            print('')
        if events in ('all parts', 'all'):
            for part, part_events in self.music_events['part_events'].items():
                print('Part ' + str(part))
                _ = [print(str(ev) + '\n') for ev in part_events]
                print('')
            print('')
        if events in ('inter-part', 'all'):
            print('InterPart Events ')
            _ = [print(str(ev) + '\n')
                 for ev in self.music_events['interpart_events']]

    def show_single_viewpoints(self, viewpoint, events='all parts',
                               part_number=0, parts=None, offset=False):
        """
        Shows only a viewpoint sequence
        """
        if events == 'one part':
            printing.show_part_viewpoint(
                viewpoint, self.music_events['part_events'][part_number], offset)
        elif events == 'some parts':
            for part in parts:
                print('Part ' + str(part))
                printing.show_part_viewpoint(
                    viewpoint, self.music_events['part_events'][part], offset)
                print('')
            print('')
        if events in ('all parts', 'all'):
            _ = [printing.show_part_viewpoint(viewpoint, part, offset)
                 for key, part in self.music_events['part_events'].items()]
        if events in ('inter-part', 'all'):
            printing.show_part_viewpoint(
                viewpoint, self.music_events['interpart_events'], offset)

    def get_part_events(self):
        """
        Returns the parts events
        """
        if 'part_events' in self.music_events:
            return self.music_events['part_events']
        return None

    def get_interpart_events(self):
        """
        Returns the interpart events
        """
        if 'interpart_events' in self.music_events:
            return self.music_events['interpart_events']
        return None

    def to_json(self, filename, folders=None, indent=2, verbose=False):
        """
        Parses Music To json object
        """
        if folders is None:
            folders = FOLDER_DEFAULT

        file_path = os.sep.join(folders + [filename])
        if os.path.realpath('.').find('code') != -1:
            file_path.replace('code', '')
            file_path = os.sep.join(['..', file_path])

        to_dump = {
            'part_events': {},
            'interpart_events': [
                event.to_feature_dict() for event in self.music_events['interpart_events']]
        }

        for key, part in self.music_events['part_events'].items():
            to_dump['part_events'][key] = [event.to_feature_dict()
                                           for event in part]

        with open(file_path + '.json', 'w') as handle:
            json.dump(to_dump, handle, indent=indent)
            handle.close()

        if verbose:
            print('Dumped to json')

    def from_json(self, filename, folders=None, verbose=False):
        """
        Parses Music from json object
        """
        if folders is None:
            folders = FOLDER_DEFAULT

        file_path = os.sep.join(folders + [filename])
        if os.path.realpath('.').find('code') != -1:
            file_path.replace('code', '')
            file_path = os.sep.join(['..', file_path])

        with open(file_path + '.json', 'rb') as handle:
            to_load = json.load(handle)
            print(to_load['interpart_events'])
            self.music_events['interpart_events'] = [
                InterPartEvent(from_dict=event) for event in to_load['interpart_events']]
            for key, part in to_load['part_events'].items():
                self.music_events['part_events'][int(key)] = [
                    PartEvent(from_dict=event) for event in part]
            handle.close()

        if verbose:
            print('Loaded from json')

    def to_pickle(self, filename, folders=None, verbose=False):
        """
        Parses Music To cpickle object
        """
        if folders is None:
            folders = FOLDER_DEFAULT

        file_path = os.sep.join(folders + [filename])

        # .pbz2 is even better for compression than pickle
        with bz2.BZ2File(file_path + '.pbz2', 'wb') as handle:
            pickle.dump(self.music_events, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)
            handle.close()

        if verbose:
            print('Dumped to pickle')

    def from_pickle(self, filename, folders=None, verbose=False):
        """
        Parses Music To cpickle object
        """
        if folders is None:
            folders = FOLDER_DEFAULT

        file_path = os.sep.join(folders + [filename])

        with bz2.BZ2File(file_path + '.pbz2', 'rb') as handle:
            self.name = filename
            self.music_events = pickle.load(handle)
            handle.close()

        if verbose:
            print('Loaded from pickle')
