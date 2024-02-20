from collections import Counter
import statistics

import music21

import app.api.routes.utils as utils

from app.db.db_session import database_instance
from fastapi import APIRouter

router = APIRouter()

def sync_level(sync_count):
    if sync_count == 0:
        return 1
    if sync_count < 4:
        return 2
    return 3

def duration_level(duration_hist):
    level_1_ints = [0.5, 1.0, 0.25, 4.0, 2.0]
    if all(k in level_1_ints for k in duration_hist.keys()):
        return 1
    level_2_ints = [0.0, 1.5, 3.0, 3.5, 0.75]
    if all(k in level_2_ints + level_1_ints for k in duration_hist.keys()):
        return 2
    return 3

def interval_level(interval_hist):
    level_1_ints = ['A1', 'm2', 'M2', 'm3', 'M3', 'P4']
    if all(k in level_1_ints for k in interval_hist.keys()):
        return 1
    level_2_ints = ['A2', 'P5', 'm6', 'M6', 'm7', 'M7', 'P8']
    if all(k in level_2_ints + level_1_ints for k in interval_hist.keys()):
        return 2
    return 3

def meter_level(meter):
    if meter.lower() == 'binary':
        return 1
    if meter.lower().replace(' ', '').replace('\n', '') == 'ternary':
        return 2
    return 3

def range_level(range):
    interval = music21.interval.Interval(range)
    if interval.semitones <= 7:
        return 1
    if interval.semitones <= 12:
        return 2
    return 3

def analysis_of_song(row):

    score = utils.retrieve_score(row['name'])

    # ambitus
    _, _, range = range_info(score, row)

    # intervals
    i = music21.analysis.discrete.MelodicIntervalDiversity()

    if score:

        levels = {
            'duration': duration_level(music21.analysis.elements.attributeCount(score.flat.notesAndRests, 'quarterLength')),
            'metrical_stability': sync_level(has_syncopation(score)),
            'meter': meter_level(row['meter']),
            'ambitus': range_level(range),
            'interval': interval_level(i.countMelodicIntervals(score)),
        }
        media_rhyt = round((1/3) * levels['metrical_stability'] + (1/3) * levels['meter'] + (1/3) * levels['duration'])
        media_mel = round(0.50 * levels['interval'] + 0.50 * levels['ambitus'])

        # EXP 1
        levels['rhythmic'] = media_rhyt
        levels['melodic'] = media_mel

    else:

        levels = {
            'duration': 3,
            'metrical_stability': 3,
            'meter': 3,
            'ambitus': 3,
            'interval': 3,
            'rhythmic': 3,
            'melodic': 3
        }

    # EXP 2
    #levels['rhythmic'] = 3 if max([levels['metrical_stability'], levels['meter'], levels['duration']]) == 3 else media_rhyt
    #levels['melodic'] = 3 if max([levels['interval'], levels['ambitus']]) == 3 else media_mel

    # EXP 3
    # Max
    #levels['rhythmic'] = max([levels['metrical_stability'], levels['meter'], levels['duration']])
    #levels['melodic'] = max([levels['interval'], levels['ambitus']])

    # EXP 4
    # Most Common
    #levels['rhythmic'] = statistics.mode([levels['metrical_stability'], levels['meter'], levels['duration']])
    #levels['melodic'] = statistics.mode([levels['interval'], levels['ambitus']])

    return levels

@router.put("/musicDifficultyLevel")
async def music_level(music_id):
    rows = await database_instance.fetch_rows("""SELECT * FROM music WHERE music_id = {};""".format(music_id), as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such id"}]

    levels = analysis_of_song(rows[0])

    values = list(levels.values())
    values.append(music_id)
    item = tuple(values)

    query = '''UPDATE music SET {} WHERE music_id = ?'''.format(
        ', '.join(f'{l}_level = ?' for l in list(levels.keys()))
    )
    cursor = await database_instance.connection.cursor()
    await cursor.execute(
        query,
        item
    )
    await database_instance.connection.commit()
    print(cursor.rowcount, "Record updated successfully into Music table")
    await cursor.close()

    return [{"msg": f'Record updated successfully into Music table with level values: {levels}'}]


@router.put("/musicDifficultyLevelAll")
async def music_level_all():
    rows = await database_instance.fetch_rows("""SELECT * FROM music;""", as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such id"}]

    keys_levels = []
    items = []
    for row in rows:
        levels = analysis_of_song(row)
        values = list(levels.values())
        values.append(row['music_id'])
        items.append(tuple(values))
        keys_levels = levels.keys()

    query = '''UPDATE music SET {} WHERE music_id = ?'''.format(
        ', '.join(f'{l}_level = ?' for l in list(keys_levels))
    )
    cursor = await database_instance.connection.cursor()
    await cursor.executemany(
        query,
        items
    )
    await database_instance.connection.commit()
    print(cursor.rowcount, "Records updated successfully into Music table")
    await cursor.close()

    return [{"msg": '{} Records updated successfully into Music table'.format(cursor.rowcount)}]

def put_in_dict(dict_levels, key, row):
        if key in dict_levels:
            dict_levels[key].append(row[key])
        else:
            dict_levels[key] = [row[key]]



@router.get("/getAnalX")
async def music_stats_anal(type='histo'):
    rows = await database_instance.fetch_rows("""SELECT name, real_key, mode FROM music;""", as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such id"}]

    if type == 'histo':
        list_key_mode = []
        for row in rows:
            list_key_mode.append(f"{row['real_key']} {row['mode']}")

        key_mode_counts = Counter(list_key_mode)

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(18, 6))
        plt.bar(key_mode_counts.keys(), key_mode_counts.values())

        ax.legend(fontsize = 8)
        plt.xticks(rotation=85)

        fig.savefig('analysis.png', bbox_inches='tight')

        #plt.show()
    else:
        with open('analysis.txt', 'a') as file_handler:
            for row in rows:
                try:
                    score = utils.retrieve_score(row['name'])
                    hist = music21.analysis.pitchAnalysis.pitchAttributeCount(score, 'pitchClass')
                    hist_2 = [str(hist[x]) if x in hist else '0' for x in range(12)]
                    file_handler.write(f"{row['name']} {row['real_key']} {row['mode']} {','.join(hist_2)}\n")
                except Exception as e:
                    print(f"Can't read {row['name']}: {e}")

@router.get("/getStatistics")
async def music_level_stats():
    rows = await database_instance.fetch_rows("""SELECT * FROM music;""", as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such id"}]

    levels = {}
    pt_levels = {}
    es_levels = {}
    it_levels = {}

    level_keys = ['melodic_level'] #[k for k in rows[0].keys() if 'level' in k]

    for row in rows:

        for key in level_keys:
            put_in_dict(levels, key, row)

            if row['country'] == 'Portugal':
                put_in_dict(pt_levels, key, row)
            elif row['country'] == 'Spain':
                put_in_dict(es_levels, key, row)
            else:
                put_in_dict(it_levels, key, row)


    to_return = {}

    for key, item in levels.items():
        to_return[key] = {}
        to_return[key]['GEN'] = dict(sorted(Counter(item).items(), key=lambda pair: pair[1], reverse=True))
        to_return[key]['PT'] = dict(sorted(Counter(pt_levels[key]).items(), key=lambda pair: pair[1], reverse=True))
        to_return[key]['ES'] = dict(sorted(Counter(es_levels[key]).items(), key=lambda pair: pair[1], reverse=True))
        to_return[key]['IT'] = dict(sorted(Counter(it_levels[key]).items(), key=lambda pair: pair[1], reverse=True))

    return to_return

@router.get("/getStatisticsForLevels")
async def database_statistics():
    rows = await database_instance.fetch_rows("""SELECT * FROM music;""", as_dict=True)
    if not rows or len(rows) == 0:
        return [{"msg": "No music with such id"}]

    intervals_histogram = {}
    duration_histogram = {}
    media_duration_histogram = {}

    ranges = []
    p_mins = []
    p_maxs = []

    meters = []
    time_signatures = []

    number_syncopas = []

    for row in rows:
        print(row['name'])
        score = utils.retrieve_score(row['name'])

        try:
            _ = score.flat.notes

            intervalar_info(intervals_histogram, score)
            durations_info(duration_histogram, media_duration_histogram, score)

            number_syncopas.append(has_syncopation(score))
            meters.append(row['meter'])
            time_signatures.append(row['time_signature'])

            p_min, p_max, range = range_info(score, row)
            p_mins.append(p_min)
            p_maxs.append(p_max)
            ranges.append(range)

        except Exception as e:
            print(f"ERROR: {e}")

    media_duration_histogram_2 = {m: len(v)/len(rows) for m, v in media_duration_histogram.items() }

    stats = [{
        'durations': dict(sorted(duration_histogram.items(), key=lambda pair: pair[1], reverse=True)),
        'media_durations': dict(sorted(media_duration_histogram_2.items(), key=lambda pair: pair[1], reverse=True)),

        'syncopas': dict(sorted(Counter(number_syncopas).items(), key=lambda pair: pair[1], reverse=True)),
        'meters': dict(sorted(Counter(meters).items(), key=lambda pair: pair[1], reverse=True)),
        'time_signatures': dict(sorted(Counter(time_signatures).items(), key=lambda pair: pair[1], reverse=True)),

        'intervals': dict(sorted(intervals_histogram.items(), key=lambda pair: pair[1], reverse=True)),
        'range': dict(sorted(Counter(ranges).items(), key=lambda pair: pair[1], reverse=True)),
        'p_mins': dict(sorted(Counter(p_mins).items(), key=lambda pair: pair[1], reverse=True)),
        'p_maxs': dict(sorted(Counter(p_maxs).items(), key=lambda pair: pair[1], reverse=True)),
    }]

    return stats

def intervalar_info(intervals_histogram, score):
    i = music21.analysis.discrete.MelodicIntervalDiversity()
    hist = i.countMelodicIntervals(score)

    for val, item in hist.items():
        if val in intervals_histogram:
            intervals_histogram[val] += item[1]
        else:
            intervals_histogram[val] = item[1]

def has_syncopation(score):

    sync_count = 0

    try:
        last_time_signature = score.parts[0].measure(1).timeSignature
        for measure in score.parts[0].getElementsByClass('Measure'):
            ts = last_time_signature
            if measure.timeSignature:
                ts = measure.timeSignature
                last_time_signature = measure.timeSignature

            if ts and ts.denominator == 4:
                sync_count += [utils.isMetricallyStable(note) for note in measure.flat.notes].count(False)
    except Exception as e:
        print(e)

    return sync_count

def durations_info(duration_histogram, media_duration_histogram, score):
    hist = music21.analysis.elements.attributeCount(score.flat.notesAndRests, 'quarterLength')
    for val, item in dict(hist).items():

        if str(val) in duration_histogram:
            duration_histogram[str(val)] += item
        else:
            duration_histogram[str(val)] = item

        if str(val) in media_duration_histogram:
            media_duration_histogram[str(val)].append(item)
        else:
            media_duration_histogram[str(val)] = [item]

def range_info(score, row):

    try:
        a = music21.analysis.discrete.Ambitus()
        pitchMin, pitchMax = a.getPitchSpan(score.flat.notes)
        range = music21.interval.Interval(pitchMin, pitchMax)
    except:
        pitchMin = music21.pitch.Pitch(row['ambitus_low'])
        pitchMax = music21.pitch.Pitch(row['ambitus_high'])
        range = music21.interval.Interval(pitchMin, pitchMax)

    return pitchMin.ps, pitchMax.ps, range.name
