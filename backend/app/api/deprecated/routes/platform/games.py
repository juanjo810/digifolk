import ast
import itertools
import math
import os
import random
import sys
import traceback
from collections import OrderedDict

import app.composition.melodyGame as melodyGameMod
import app.composition.melodyGameAux as melodyGameModAux
import app.composition.newMelodyGame as newMelodyGameMod
import app.api.routes.utils as utils

import music21
from app.core.config import DATABASE_PATH
from app.db.db_session import database_instance
from fastapi import APIRouter, Request
from music21.midi import translate as midiTranslate

env = music21.environment.Environment()
# env['musicxmlPath'] = r'D:\MuseScorePortable\App\MuseScore\bin\MuseScore3.exe'
# env['musicxmlPath'] = r'/Applications/MuseScore 3.app/Contents/MacOS/mscore'

router = APIRouter()




def note_beat(n, bpms, mN=None):
    if mN:
        start = mN + (mN-1)*bpms
        if mN > 1:
            start -= (mN-1)
    else:
        start = n.measureNumber + (n.measureNumber-1)*bpms
        if n.measureNumber > 1:
            start -= (n.measureNumber-1)
    return start + math.floor(n.beat)-1


def curve_note(n, curve, bpms):
    beat = note_beat(n, bpms)
    if beat < len(curve):
        return (n.duration.ordinal, str(n.pitch), midiTranslate.durationToMidiTicks(n.duration), curve[beat - 1])
    else:
        return (n.duration.ordinal, str(n.pitch), midiTranslate.durationToMidiTicks(n.duration), curve[-1])


def extract_info(curve, score, bpms, ts):
    b_s_o = [(note_beat(n, bpms), curve_note(n, curve, bpms))
             for n in score.flat.notes]
    b_m_1 = [note_beat(n, bpms)
             for n in score.flat.notes if n.duration.quarterLength > ts]
    b_s_o2 = [(b[0]-1, b[1]) if b[0]-1 in b_m_1 else b for b in b_s_o]

    b_s = OrderedDict()
    _ = [b_s.setdefault(k, []).append(v) for k, v in b_s_o2]
    return b_s


def get_scores(curves, iscore, end_event, ts, key='C', mode='major', more_pitches=[]):
    """
    Get and Process Scores
    """
    bpms = ts.beatCount
    tbts = ts.beatDuration.quarterLength

    b_s = extract_info(curves['1'], iscore['alt_1'], bpms, tbts)
    b_s1 = extract_info(curves['1'], iscore['alt_2'], bpms, tbts)
    b_s2 = extract_info(curves['1'], iscore['alt_3'], bpms, tbts)

    different_rhythm_beats = []
    for k, v in b_s.items():
        if not k in b_s1 or b_s1[k] != v:
            different_rhythm_beats.append(k)

    score = {
        'number-beats': list(b_s.keys())[-1],
        'different_rhythm_beats': different_rhythm_beats,
        'alt_0': b_s,
        'alt_1': b_s1,
        'alt_2': b_s2,
        'whole_duration': midiTranslate.durationToMidiTicks(music21.duration.Duration('quarter')),
        'last_pitch': iscore['alt_1'].flat.notes[-1].pitch.ps,
        'end_event': end_event,
        'time_signature': ts.ratioString,
        'key': key,
        'mode': mode,
        'more_pitches': more_pitches
    }

    return score


def note_info(n):
    """
    """
    if n.isNote:
        return (str(n.duration.ordinal) + '.' * n.duration.dots, str(
            n.pitch), midiTranslate.durationToMidiTicks(n.duration), melodyGameModAux.level_of_pitch(n.pitch.ps))
    else:
        return (str(n.duration.ordinal) + '.' * n.duration.dots, 'R', midiTranslate.durationToMidiTicks(n.duration), 0)

def get_real_lyc(lyc):
    lycs = []
    for l in lyc:
        if l.syllabic == 'single':
            lycs.append(l.text)
        else:
            lycs.append(l.text)
            lycs.append('-')
    return lycs


def note_info_lyrics(n):
    """
    """
    if n.isNote:
        return (str(n.duration.ordinal) + '.' * n.duration.dots, str(
            n.pitch), midiTranslate.durationToMidiTicks(n.duration), melodyGameModAux.level_of_pitch(n.pitch.ps), get_real_lyc(n.lyrics))
    else:
        return (str(n.duration.ordinal) + '.' * n.duration.dots, 'R', midiTranslate.durationToMidiTicks(n.duration), 0, get_real_lyc(n.lyrics))


def extract_info_nocurve(notes, bpms, mN, beatDuration=1, ts='2/4', lyrics=False):
    """
    """
    if lyrics:
        b_s_o = [(note_beat(n, bpms, mN), note_info_lyrics(n)) for n in notes]
    else:
        b_s_o = [(note_beat(n, bpms, mN), note_info(n)) for n in notes]

    b_s = OrderedDict()
    _ = [b_s.setdefault(k, []).append(v) for k, v in b_s_o]

    for b in b_s:
        b_s[b] = {
            'dur': sum([n0[2] for n0 in b_s[b]]) / beatDuration,
            'ts': ts,
            'notes': b_s[b]
        }

    return b_s


def score_in_frontend_format(score, lyrics=False):
    if score:
        meas = score.parts[0].getElementsByClass('Measure')
        last_tm = meas[0].timeSignature

        if last_tm is None:
            last_tm = list(score.parts[0].recurse().getElementsByClass(music21.meter.TimeSignature))
            if len(last_tm) > 0:
                last_tm = last_tm[0]
            else:
                last_tm = music21.meter.TimeSignature('4/4')

        last_bc = last_tm.beatCount
        whole_notes = {}
        for i, m in enumerate(meas):
            if m.timeSignature:
                last_tm = m.timeSignature
            else:
                m.timeSignature = last_tm

            midi_bd = midiTranslate.durationToMidiTicks(last_tm.beatDuration)

            whole_notes = whole_notes | extract_info_nocurve(
                m.flat.notesAndRests, last_bc, i+1, midi_bd, last_tm.ratioString, lyrics)

        return whole_notes
    return {}


"""
GAMES
"""


@router.post("/createMusicTest1Phrase")
async def melody_game_test_1(request: Request):
    body = await request.json()

    curves = melodyGameModAux.curve_from_points(body['points'])
    time_signature = 'all'

    country = 'portuguese'
    if body['country'] == 'Italy':
        country = 'italian'
    elif body['country'] == 'Spain':
        country = 'spanish'

    oracle_path = os.sep.join(
        [DATABASE_PATH, 'Models', '{}_oracle.pbz2'.format(country)])

    iscore, end_event, ts, key, mode, more_pitches = newMelodyGameMod.query_points(
        oracle_path, time_signature, curves)
    iscore['alt_1'].show('t')

    # melodyGameModAux.show_phrase_alts('1', iscore)
    return get_scores(curves, iscore, end_event, ts, key, mode, more_pitches)


@router.post("/createMusicTest23Phrase")
async def melody_game_test_23(request: Request):
    body = await request.json()

    time_signature = body['time_signature']
    curves = melodyGameModAux.curve_from_points(body['points'])

    country = 'portuguese'
    if body['country'] == 'Italy':
        country = 'italian'
    elif body['country'] == 'Spain':
        country = 'spanish'

    oracle_path = os.sep.join(
        [DATABASE_PATH, 'Models', '{}_oracle.pbz2'.format(country)])

    end_point = body['end_event'] + 1
    last_pitch = body['last_pitch']
    key = body['key']
    mode = body['mode']
    more_pitches = body['more_pitches']

    try:
        iscore, end_event, ts = newMelodyGameMod.query_points_cont(
            oracle_path, time_signature, curves, end_point, last_pitch, body['phrase'], key, mode, more_pitches)
        # melodyGameModAux.show_phrase_alts(body['phrase'], iscore)
        return get_scores(curves, iscore, end_event, ts, key, mode, more_pitches)
    except Exception as e:
        tb = traceback.format_exc()
        print('ERROR at line {} - {}\n context: {}'.format(sys.exc_info()
              [-1].tb_lineno, str(e), str(tb)))
        return {}


@router.post("/createMusicTest1Phrase-OUTGAME")
async def melody_game_test_1(points, bcountry):

    curves = melodyGameModAux.curve_from_points(ast.literal_eval(points))

    country = 'portuguese'
    if bcountry == 'Italy':
        country = 'italian'
    elif bcountry == 'Spain':
        country = 'spanish'

    oracle_path = os.sep.join(
        [DATABASE_PATH, 'Models', '{}_oracle.pbz2'.format(country)])

    iscore, end_event, ts, key, mode, more_pitches = newMelodyGameMod.query_points(
        oracle_path, 'all', curves)
    # melodyGameModAux.show_phrase_alts('1', iscore)

    return get_scores(curves, iscore, end_event, ts, key, mode, more_pitches)


@router.post("/createMusic23Phrase-OUTGAME")
async def melody_game_test_23_2(timesig, points, bcountry, endpoint, lastpitch, phrase='2', key='C', mode='major', more_pitches=[]):

    curves = melodyGameModAux.curve_from_points(ast.literal_eval(points))

    country = 'portuguese'
    if bcountry == 'Italy':
        country = 'italian'
    elif bcountry == 'Spain':
        country = 'spanish'

    oracle_path = os.sep.join(
        [DATABASE_PATH, 'Models', '{}_oracle.pbz2'.format(country)])

    try:
        iscore, end_event, ts = newMelodyGameMod.query_points_cont(
            oracle_path, timesig, curves, int(endpoint)+1, int(lastpitch), phrase, key, mode, more_pitches)
        # melodyGameModAux.show_phrase_alts(phrase, iscore)
        return get_scores(curves, iscore, end_event, ts, key, mode, more_pitches)
    except Exception as e:
        tb = traceback.format_exc()
        print('ERROR at line {} - {}\n context: {}'.format(sys.exc_info()
              [-1].tb_lineno, str(e), str(tb)))
        return {}


# Rhythm Game


def transform_rhythm_pattern(ptn):
    """DEF"""
    ret_ptn = []

    for el in ptn.split(' '):
        el_nd = el.replace('.', '')

        t1 = 6
        if el_nd == '1':
            t1 = 4
        elif el_nd == '2':
            t1 = 5
        elif el_nd == '4':
            t1 = 6
        elif el_nd == '8':
            t1 = 7
        elif el_nd == '16':
            t1 = 8
        elif el_nd == '32':
            t1 = 9
        ret_ptn.append(str(t1) + ''.join(c for c in el if c not in el_nd))

    return ' '.join(ret_ptn)


def get_possible_rhythms(notes):
    beat_rythms = {}
    for ts in set([beat['ts'] for beat in notes.values()]):
        beat_rythms[ts] = {}
        beats_ts = [(beat['dur'], beat['notes'])
                    for beat in notes.values() if beat['ts'] == ts]
        b_s = OrderedDict()
        _ = [b_s.setdefault(round(k, 2), []).append(
            ' '.join([str(i[0]) for i in v])) for k, v in beats_ts]
        for b, it in b_s.items():
            b_s[b] = list(set(it))

        beat_rythms[ts] = OrderedDict(sorted(b_s.items()))
    return beat_rythms


def extend_possible_rhythms(beat_rhythms):
    for ts in beat_rhythms:
        alts = beat_rhythms[ts]
        for dur in alts:
            res = utils.combinations2(list(alts.keys()), dur)
            for comb in res:
                if len(comb) > 1:
                    a = [alts[c] for c in comb]
                    aposs = list(itertools.product(*a))
                    poss = list(set([' '.join(item) for sublist in [
                                list(itertools.permutations(ap)) for ap in aposs] for item in sublist]))
                    _ = [alts[dur].append(p)
                         for p in poss if p not in alts[dur]]

            m21_dur = music21.duration.Duration(quarterLength=dur)
            str_m21_dur = str(m21_dur.ordinal) + '.' * m21_dur.dots
            if str_m21_dur not in alts[dur]:
                alts[dur].append(str_m21_dur)


@router.get("/rhythmGame")
async def rhythm_game(music_id):
    rows = await database_instance.fetch_rows("""SELECT name, rhythm_pattern, time_signature FROM music WHERE music_id = {};""".format(music_id), as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such id"}]

    original_music = utils.retrieve_score(rows[0]['name'])
    #original_music.show('t')
    notes = score_in_frontend_format(original_music)
    if len(list(notes)) < 0:
        return [{"msg": "ERROR"}]


    if -1 in notes:
        notes[0] = notes[-1]
        del notes[-1]
    elif -2 in notes:
        notes[0] = notes[-2]
        del notes[-2]

    notes = OrderedDict(sorted(notes.items()))

    beat_rhythms = get_possible_rhythms(notes)
    extend_possible_rhythms(beat_rhythms)


    key_last_note = list(notes.keys())[-1]
    last_element = list(filter(lambda x: len(
        x) == 1 or ('.' in x and (len(
            x) == 2 or len(
            x) == 3)), beat_rhythms[notes[key_last_note]['ts']][round(notes[key_last_note]['dur'],2)]))

    proposals = {}
    for i in range(3):
        proposals[f'alt_{i}'] = [random.choice(
            beat_rhythms[v['ts']][round(v['dur'],2)]) for v in notes.values()]
        if len(last_element) > 0:
            proposals[f'alt_{i}'][-1] = last_element[0]

    score = {
        'original': dict(notes),
        'whole_duration':  midiTranslate.durationToMidiTicks(
            music21.duration.Duration('quarter')),
        'alternatives': beat_rhythms,
        'proposals': proposals
    }
    return score


@router.get("/singGame")
async def sing_game(music_id):
    rows = await database_instance.fetch_rows("""SELECT name, time_signature FROM music WHERE music_id = {};""".format(music_id), as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such id"}]

    original_music = utils.retrieve_score(rows[0]['name'])
    notes = score_in_frontend_format(original_music, lyrics=True)
    if -1 in notes.keys():
        notes[0] = notes[-1]
        del notes[-1]
    elif -2 in notes.keys():
        notes[0] = notes[-2]
        del notes[-2]

    quarter = midiTranslate.durationToMidiTicks(
        music21.duration.Duration('quarter'))

    score = {
        'music': dict(OrderedDict(sorted(notes.items()))),
        'whole_duration': quarter
    }
    return score


@router.get("/danceGame")
async def dance_game(music_id):
    rows = await database_instance.fetch_rows("""SELECT name, time_signature, meter FROM music WHERE music_id = {};""".format(music_id), as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such id"}]

    original_music = utils.retrieve_score(rows[0]['name'])
    notes = score_in_frontend_format(original_music)
    if -1 in notes:
        notes[0] = notes[-1]
        del notes[-1]
    elif -2 in notes:
        notes[0] = notes[-2]
        del notes[-2]

    quarter = midiTranslate.durationToMidiTicks(
        music21.duration.Duration('quarter'))

    meter = rows[0]['meter'].capitalize()
    if meter == ['Polyrhythmic', 'Irregular', 'Free']:
        meter = 'Poly'
    elif meter not in ['Binary', 'Ternary']:
        meter = 'All'

    possible_steps = await database_instance.fetch_rows(f"""SELECT step_id, name, description FROM dance_steps WHERE tempo IN ('{meter}', 'All');""", as_dict=True)
    ordered_beats = dict(OrderedDict(sorted(notes.items())))

    m = 4
    if meter == 'Ternary':
        m = 3

    proposed = []
    for i, b in enumerate(ordered_beats):
        if (int(b)-1) % m == 0 or (i > 0 and list(ordered_beats.keys())[i-1] < b-1 and (int(b)-1) % m == 1):
            if len(proposed) > 0:
                iLastEl = possible_steps.index(proposed[-1])
                choosable = possible_steps[:iLastEl] + \
                    possible_steps[iLastEl+1:]
            else:
                choosable = possible_steps

            proposed.append(random.choice(choosable))
        else:
            proposed.append(proposed[-1])
        """
        if (int(b)-1) % m == 0 or (i > 0 and list(ordered_beats.keys())[i-1] < b-1 and (int(b)-1) % m == 1):
            if len(proposed) > 0:
                if proposed[-1]['step']['name'] != 'Clap' and len(proposed[-1]['beats']) < int(ordered_beats[b]['ts'][0]):
                    choosable = [proposed[-1]['step']]
                else:
                    iLastEl = possible_steps.index(proposed[-1]['step'])
                    choosable = possible_steps[:iLastEl] + \
                        possible_steps[iLastEl+1:]
            else:
                choosable = possible_steps

            proposed.append({
                'step': random.choice(choosable),
                'beats': [int(b)]
            })
        else:
            proposed[-1]['beats'].append(int(b))
        """

    score = {
        'music': ordered_beats,
        'whole_duration': quarter,
        'proposed_dance': proposed,
        'all_possible_steps': possible_steps
    }
    return score
