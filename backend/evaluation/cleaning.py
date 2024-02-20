from app.composition.representation.conversor.score_conversor import parse_single_line
from app.composition.representation.parsers.music_parser import MusicParser


def open_mei_music_xml():
    import glob
    import os

    import music21

    music_folder = glob.glob(
        r"D:\Projects\COPOEM\coPoem\backend\db\files\Scores\ES-2012-CO-AN-003.mei")
    for music in music_folder:
        conv = music21.converter.subConverters.ConverterMEI()
        result = conv.parseFile(music)
        result.show('t')
        print(result.write(fmt='mxl', fp=os.path.splitext(music)[0]))


def move_music_database():
    import glob
    import os

    base_dir = r"D:\Projects\COPOEM\coPoem\Backend\db\files\ViewpointsAll\Portugal"
    # + glob.glob(base_dir + "\**\*.mxl", recursive=True)
    folder = glob.glob(base_dir + "\**\*.pbz2", recursive=True)

    for music in folder:
        id = music[music.rfind(os.sep) + 1: -4]
        ext = music[-4:]
        os.rename(
            music, r"D:\Projects\COPOEM\coPoem\Backend\db\files\ViewpointsAll" + os.sep + id + ext)


def search_note(id='d1e96', show=True):
    import glob
    import os

    if show:
        import music21
        env = music21.environment.Environment()
        env['musicxmlPath'] = r'D:\MuseScorePortable\App\MuseScore\bin\MuseScore3.exe'

    base_dir = r"D:\Projects\COPOEM\MEI Materials\ALL_MUSIC\Viewpoints"
    folder = glob.glob(base_dir + "\**\*.pbz2", recursive=True)

    for music in folder:
        name = str(music[music.rfind(os.sep) + 1: -5])

        parser = MusicParser()
        parser.from_pickle(music[:-5], folders=[])
        keys = parser.get_part_events().keys()
        events = parser.get_part_events()[list(keys)[0]]

        if any(ev.get_viewpoint('id') == id for ev in events):
            print(name)

            if show:
                new_score = parse_single_line(events,
                                            end_position_last_phrase=None,
                                            show_segmentation=True, contour=True)
                new_score.makeAccidentals(inPlace=True, overrideStatus=True)
                new_score.insert(0.0, music21.clef.TrebleClef())
                new_score.show()
                input()


def create_midis():
    import glob
    import os
    import music21

    base_dir = r"D:\Projects\COPOEM\MEI Materials\db phrases only\Scores"
    folder = glob.glob(base_dir + "\**\*.mxl", recursive=True)

    for music in folder:
        name = str(music[music.rfind(os.sep) + 1: -4])
        score = music21.converter.parse(music)
        try:
            midi_folder = music[:music.rfind(
                os.sep) + 1].replace('Scores', 'MIDIs')
            os.makedirs(midi_folder, exist_ok=True)

            midi_path = midi_folder
            if not os.path.exists(midi_path + name + '.mid'):
                _ = score.write('midi', fp=midi_path + name + '.mid')
                print('Converted: ' + str(name))
        except:
            print('No Audio: ' + str(name))


def phrases_for_xml():
    import glob
    import os
    from itertools import accumulate
    from operator import add
    from xml.etree import ElementTree as ET

    import app.composition.representation.utils.printing as printUtils
    from app.composition.representation.parsers.music_parser import MusicParser

    base_dir = r"D:\Projects\COPOEM\MEI Materials\db phrases only\Scores"
    folder = glob.glob(base_dir + "\**\*.mei", recursive=True)

    for music in folder:
        id = music[music.rfind(os.sep) + 1: -4]
        print(id)
        print()

        ns = {'mei': 'http://www.music-encoding.org/ns/mei'}
        id_space = '{http://www.w3.org/XML/1998/namespace}id'

        notes = [elem for elem in ET.parse(music).getroot().iter() if elem.tag in (
            "{}note".format("{" + ns['mei'] + "}"), "{}rest".format("{" + ns['mei'] + "}"))]
        note_ids = [note.get(id_space) for note in notes]
        note_names = [note.get('pname') + str(note.get('oct')) if note.get('pname') else 'Rest'
                      for note in notes]

        indexes = [i for i, n in enumerate(note_ids) if n]
        note_ids = list(map(lambda i: note_ids[i], indexes))
        print(note_ids)
        note_names = list(map(lambda i: note_names[i], indexes))

        cadence_notes = [(note.get(id_space), note.get('type'))
                         for note in notes if note.get('type') != None]

        parser = MusicParser(music[:-4] + '.mxl', music, folders=[])
        parser.parse()

        if len(parser.get_part_events().keys()) > 1:
            continue

        key = list(parser.get_part_events().keys())[0]
        events = parser.get_part_events()[key]

        print(printUtils.show_sequence_of_viewpoint_without_offset(
            events, 'pitch.dnote'))
        print(len(events))

        double_note_events = [len(ev.get_viewpoint('pitch.chordPitches')) if len(
            ev.get_viewpoint('pitch.chordPitches')) > 1 else 1 for ev in events]
        acc_dne = list(accumulate(double_note_events, func=add))
        print(acc_dne)
        print(len(note_ids))

        phrases = ET.parse(music).getroot().findall(".//mei:phrase", ns)
        for phrase in phrases:
            print(phrase.get('n'))
            print(phrase.get('startid'))
            print(phrase.get('endid'))
            print(phrase.get('type'))

            print()

            start_i = note_ids.index(phrase.get('startid')[1:])
            start_n = note_names[start_i]
            print(start_i)

            end_i = note_ids.index(phrase.get('endid')[1:])
            end_n = note_names[end_i]
            print(end_i)

            print()

            view_start = 'Rest'
            if any(x > 1 for x in double_note_events):
                start_i = acc_dne.index(start_i + 1)
                end_i = acc_dne.index(end_i + 1)

            print(start_i)
            print(end_i)

            print()

            if start_i < len(events) and events[start_i].get_viewpoint('pitch.dnote'):
                if double_note_events[start_i] > 1:
                    highest_note = events[start_i].get_viewpoint(
                        'pitch.chordPitches')[-1]
                    view_start = highest_note.replace('#', '').replace('-', '')
                else:
                    view_start = str(events[start_i].get_viewpoint(
                        'pitch.dnote')) + str(events[start_i].get_viewpoint('pitch.octave'))

            view_end = 'Rest'
            if end_i < len(events) and events[end_i].get_viewpoint('pitch.dnote'):
                if double_note_events[end_i] > 1:
                    highest_note = events[end_i].get_viewpoint(
                        'pitch.chordPitches')[-1]
                    view_end = highest_note.replace('#', '').replace('-', '')
                else:
                    view_end = str(events[end_i].get_viewpoint(
                        'pitch.dnote')) + str(events[end_i].get_viewpoint('pitch.octave'))

            print('ST: ' + start_n + ' and ' + view_start)
            print('END: ' + end_n + ' and ' + view_end)

            if (start_n.upper() == view_start.upper()) and (end_n.upper() == view_end.upper()):

                events[start_i].add_viewpoint('phrase.boundary', 1)
                events[start_i].add_viewpoint(
                    'phrase.length', end_i - start_i + 1)
                events[start_i].add_viewpoint(
                    'phrase.type', phrase.get('type'))

                for event in events[start_i + 1:end_i]:
                    event.add_viewpoint('phrase.boundary', 0)
                    event.add_viewpoint('phrase.length', end_i - start_i + 1)
                    event.add_viewpoint('phrase.type', phrase.get('type'))

                events[end_i].add_viewpoint('phrase.boundary', -1)
                events[end_i].add_viewpoint(
                    'phrase.length', end_i - start_i + 1)
                events[end_i].add_viewpoint('phrase.type', phrase.get('type'))
                cad = [cn[1] for cn in cadence_notes if cn[0] == phrase.get('endid')[
                    1:]]
                if len(cad):
                    events[end_i].add_viewpoint('phrase.cadence', cad[0])

        print(printUtils.show_sequence_of_viewpoint_without_offset(
            events, 'phrase.boundary'))
        parser.to_pickle(
            music[:-4].replace('Scores', 'Viewpoints'), folders=[])

        print('-------\n')
        # input()


def remove_staff_2():
    import glob
    import os

    from lxml import etree

    base_dir = r"D:\Projects\COPOEM\MEI Materials\ALL_MUSIC\Scores"
    folder = glob.glob(base_dir + "\**\*.mei", recursive=True)

    for music in folder[0:1]:
        ns = {'mei': 'http://www.music-encoding.org/ns/mei'}

        tree = etree.parse(music)
        root = tree.getroot()

        staffs = root.findall('.//mei:staff', ns)
        staffs = [tag for tag in staffs if tag.get('n') != "1"]

        for tag in staffs:
            print(tag)
            parent = tag.getparent()
            parent.remove(tag)

        layers = root.findall('.//mei:layer', ns)
        layers = [tag for tag in layers if tag.get('n') != "1"]

        for tag in layers:
            print(tag)
            parent = tag.getparent()
            parent.remove(tag)

        tree.write(music)


def join_abcs_one_file():
    import glob
    base_dir = r"D:\Projects\COPOEM\MEI Materials\db phrases only\ABCS"
    folder = glob.glob(base_dir + "\**\*.abc", recursive=True)

    new_abc = []
    for music in folder:
        f = open(music, "r")

        abc_str = f.read()
        music_abc = abc_str.split('\n')
        filter = [music_abc[2], music_abc[5][:music_abc[5].index('%')]]
        m_p = [i for i, m in enumerate(music_abc) if "%%MIDI program" in m]
        real_notes = music_abc[m_p[-1] + 1:]
        filter.append(''.join([n.replace(" \\", " ") for n in real_notes]))

        new_abc.append('\n'.join(filter))

    new_file = r"D:\Projects\COPOEM\FolkRNN\folk-rnn\data\ifolk-data"
    f = open(new_file, "w")
    f.write('\n\n'.join(new_abc))


def open_abc_database_as_mxl():
    import glob
    import music21

    env = music21.environment.Environment()
    env['musicxmlPath'] = r'D:\MuseScorePortable\App\MuseScore\bin\MuseScore3.exe'

    base_dir = r"D:\Projects\COPOEM\FolkRNN\folk-rnn\samples"
    #base_dir = r"D:\Projects\COPOEM\Mei Materials\db phrases only\ABCS"
    folder = glob.glob(base_dir + "\**\*.abc", recursive=True)

    for music in folder:
        print(music)
        stream = music21.converter.parse(music, format='abc')
        stream.show()


def open_mei():
    import os
    import glob
    import music21
    from xml.etree import ElementTree as ET
    import app.composition.representation.utils.printing as printUtils

    ns = {'mei': 'http://www.music-encoding.org/ns/mei',
          'id': '{http://www.w3.org/XML/1998/namespace}id'}

    env = music21.environment.Environment()
    env['musicxmlPath'] = r'D:\MuseScorePortable\App\MuseScore\bin\MuseScore3.exe'

    folder = glob.glob(
        r"D:\Projects\COPOEM\MEI Materials\ALL_MUSIC\Scores" + "\**\*.mei", recursive=True)
    for music in folder[74 + 27:]:
        id = music[music.rfind(os.sep) + 1: -4]
        print(id)

        parser = MusicParser(filename=music, folders=[])
        parser.parse()

        key = list(parser.get_part_events().keys())[0]
        events = parser.get_part_events()[key]

        phrases = ET.parse(music).getroot().findall(".//mei:phrase", ns)
        for phrase in phrases:
            start_ev_index = [i for i, ev in enumerate(
                events) if '#' + ev.get_viewpoint('id') == phrase.get('startid')]
            end_ev_index = [i for i, ev in enumerate(
                events) if '#' + ev.get_viewpoint('id') == phrase.get('endid')]

            for i, ind in enumerate(start_ev_index):
                last_ind = len(events) - 1
                if i < len(end_ev_index):
                    last_ind = end_ev_index[i]

                events[ind].add_viewpoint('phrase.boundary', 1)
                events[last_ind].add_viewpoint('phrase.boundary', -1)
                for ev in events[ind:last_ind + 1]:
                    ev.add_viewpoint('phrase.length', last_ind - ind + 1)
                    ev.add_viewpoint('phrase.type', phrase.get('type'))

        notes = [elem for elem in ET.parse(music).getroot().iter() if elem.tag in (
            "{}note".format("{" + ns['mei'] + "}"), "{}rest".format("{" + ns['mei'] + "}"))]
        cadence_notes = [(note.get(ns['id']), note.get('type'))
                         for note in notes if note.get('type') != None]

        for (key, type) in cadence_notes:
            cadence_ev = [ev for ev in events if ev.get_viewpoint('id') == key]
            for ev in cadence_ev:
                ev.add_viewpoint('phrase.cadence', type)

        print(printUtils.show_sequence_of_viewpoint_without_offset(
            events, 'phrase.boundary'))
        print()

        parser.to_pickle(
            music[:-4].replace('Scores', 'Viewpoints'), folders=[])
