# Copyright (C) 2016-2017 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
