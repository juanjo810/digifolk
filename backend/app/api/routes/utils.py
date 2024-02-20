import os
import bz2
import pickle
import itertools

from app.core.config import DATABASE_PATH

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
