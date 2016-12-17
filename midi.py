#!/usr/bin/python

import sys
import math

sys.path.append("/home/ffesti/CVS/python-midi/src/")
from fileio import FileReader
import events
import constants

try:
    import cairocffi    
    cairocffi.install_as_pycairo()
except ImportError:
    pass
import cairo
    
class Ariston:

    track_positions = [
        70.7,
        74.4,
        78.1,
        81.8,
        85.5,
        89.2,
        92.9,
        96.6,
        100.3,
        104.0,
        107.7,
        111.4,
        115.1,
        118.8,
        122.5,
        126.2,
        129.9,
        133.6,
        137.3,
        141.0,
        144.7,
        148.4,
        152.1,
        155.8]

    tones = [
        45,
        47,
        50,
        52,
        57,
        59,
        61,
        62,
        64,
        66,
        68,
        69,
        71,
        73,
        74,
        75,
        76,
        78,
        79,
        80,
        81,
        83,
        85,
        86]

    tone2number = {t : i for i, t in enumerate(tones)}
    tone2track = {t :  pos for t, pos in zip(tones, track_positions)}

    def __init__(self):
        self.unsupported = set()

    def open(self, filename):
        self.surface = cairo.SVGSurface(filename, 500, 500)
        self.ctx = cairo.Context(self.surface)
        self.ctx.set_source_rgb(0.0, 0.0, 0.0)
        self.ctx.set_line_width(0.2)

    def close(self):
        self.ctx.stroke()
        self.surface.flush()
        self.surface.finish()

    def circle(self, x, y, r):
        self.ctx.arc(x, y, r, 0, 2*math.pi)
        self.ctx.stroke()

    def parseTracks(self, tracks):
        start = {}
        s_per_quarter = 500000 / 1E6
        s_per_tick = s_per_quarter / tracks.resolution

        lines = [[] for i in range(len(self.tones))]

        for track in tracks:
            t = 0.0
            for e in track:
                t += s_per_tick * e.tick
                e.tick = t
                if isinstance(e, events.NoteOnEvent) or isinstance(e, events.NoteOffEvent):
                    if e.pitch not in self.tone2track:
                        name = constants.NOTE_VALUE_MAP_SHARP[e.pitch]
                        if name not in self.unsupported:
                            self.unsupported.add(name)
                            print("Not supported pitch: %s" % name)
                        continue
                    lines[self.tone2number[e.pitch]].append(e)
                elif isinstance(e, events.SetTempoEvent):
                    s_per_tick = e.mpqn * 1E-6 / tracks.resolution

        for line in lines:
            line.sort(key=lambda x: x.tick)
                
        return lines

    def render(self, tracks):
        self.open("ariston.svg")

        self.circle(250, 250, 166)
        self.circle(250, 250, 5)
        for x, y in ((-37, 0), (0, -37), (37, 0), (0, 37)):
            self.circle(250 + x, 250 + y, 3)

        rad_per_second = math.pi * 2 / 45.0 # 45 seconds playtime
        min_break = 0.1 # minimal break between notes of te same pitch

        lines = self.parseTracks(tracks)

        for line in lines:
            for i, e in enumerate(line):
                if isinstance(e, events.NoteOnEvent) and e.velocity == 0 or isinstance(e, events.NoteOffEvent):
                    s = line[i-1]
                    # XXX check s
                    if len(line) > i+1:
                        # XXX check line[i+1]
                        e.tick = min(e.tick, line[i+1].tick-min_break)
                    if s.tick > e.tick: # needed?
                        print(s.tick, e.tick, s, e)
                    self.ctx.arc(250, 250, self.tone2track[s.pitch]-1.25, s.tick * rad_per_second, e.tick * rad_per_second)
                    self.ctx.arc_negative(250, 250, self.tone2track[s.pitch]+1.25, e.tick * rad_per_second, s.tick * rad_per_second)
                    self.ctx.close_path()
                    self.ctx.stroke()
        self.close()

def main():
    m = FileReader()
    tracks = m.read(open(sys.argv[1], 'rb'))
    #print(tracks)
    if tracks.format == 2:
        print("Midi format 2 is not supported")
        return
    a = Ariston()
    a.render(tracks)

main()
