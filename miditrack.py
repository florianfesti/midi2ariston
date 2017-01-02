
import sys
import math

import midi
from midi import events
from midi import constants

class MidiTrack:

    def __init__(self, filename):
        m = midi.FileReader()
        self.tracks = m.read(open(filename, 'rb'))
        #print(self.tracks)
        if self.tracks.format == 2:
            raise ValueError("Midi format 2 is not supported")

    def parse_tracks(self, instrument):
        unsupported = set()
        start = {}
        s_per_quarter = 500000 / 1E6
        s_per_tick = s_per_quarter / self.tracks.resolution

        lines = [[] for i in range(len(instrument.tones))]

        for track in self.tracks:
            t = 0.0
            for e in track:
                t += s_per_tick * e.tick
                e.tick = t
                if isinstance(e, events.NoteOnEvent) or isinstance(e, events.NoteOffEvent):
                    if e.pitch not in instrument.tone2track:
                        unsupported.add(constants.NOTE_VALUE_MAP_SHARP[e.pitch])
                        continue
                    lines[instrument.tone2number[e.pitch]].append(e)
                elif isinstance(e, events.SetTempoEvent):
                    s_per_tick = e.mpqn * 1E-6 / self.tracks.resolution

        for line in lines:
            line.sort(key=lambda x: x.tick)

        self.lines = lines
        self.unsupported = unsupported

    def getLastTime(self):
        last = None
        for line in self.lines:
            for i, e in enumerate(line):
                if not last or last.tick < e.tick:
                    last = e
        return last.tick
