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


        lt = len(self.tracks)

        trackpos = [0] * lt
        trackticks = [0.0] * lt
        tracktimes = [0.0] * lt
        tracklengths = [len(t) for t in self.tracks]

        while True:
            nexttrack = None
            e = None
            # find next event
            for i in range(lt):
                if (trackpos[i] < tracklengths[i] and
                    (e is None or
                     trackticks[i] + self.tracks[i][trackpos[i]].tick <
                     trackticks[nexttrack] + e.tick)):
                    nexttrack = i
                    e = self.tracks[i][trackpos[i]]
            if nexttrack is None:
                # No events left
                break

            # update before tempo changes
            tracktimes[nexttrack] += s_per_tick * e.tick

            if (isinstance(e, events.NoteOnEvent) or
                isinstance(e, events.NoteOffEvent)):
                if e.pitch not in instrument.tone2track:
                    unsupported.add(constants.NOTE_VALUE_MAP_SHARP[e.pitch])
                else:
                    lines[instrument.tone2number[e.pitch]].append(e)
            elif isinstance(e, events.SetTempoEvent):
                # advance all other tracks to this point in time
                # using the old tempo
                tick = trackticks[nexttrack] + e.tick
                for i in range(2):
                    if (i == nexttrack or
                        not (trackpos[i] < tracklengths[i])):
                        continue
                    tracktimes[i] += s_per_tick * (tick - trackticks[i])
                    self.tracks[i][trackpos[i]].tick -= (tick - trackticks[i])
                    trackticks[i] = tick
                s_per_tick = e.mpqn * 1E-6 / self.tracks.resolution

            trackticks[nexttrack] += e.tick
            trackpos[nexttrack] += 1
            e.tick = tracktimes[nexttrack]

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
