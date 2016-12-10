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

    def __init__(self):
        pass


    def open(self, filename):
        self.surface = cairo.SVGSurface(filename, 500, 500)
        self.ctx = cairo.Context(self.surface)
        self.ctx.set_source_rgb(0.0, 0.0, 0.0)

    def close(self):
        self.ctx.stroke()
        self.surface.flush()
        self.surface.finish()
                
    def render(self, track):
        last = track[-2].tick
        start = None
        self.open("ariston.svg")
        for e in track:
            if isinstance(e, events.NoteOnEvent):
                if e.velocity == 0 and start:
                    print(constants.NOTE_VALUE_MAP_SHARP[start.pitch], start.tick, e.tick)
                    self.ctx.arc(250, 250, start.pitch * 2, 2*math.pi*start.tick/last, 2*math.pi*e.tick/last)
                    self.ctx.stroke()
                    start = None
                else:
                    start = e

        self.close()

def main():
    m = FileReader()
    tracks = m.read(open(sys.argv[1], 'rb'))
    tracks.make_ticks_abs()
    a = Ariston()
    a.render(tracks[0])
    #for e in tracks[0]:
    #    if isinstance(e, events.NoteOnEvent):
    #        print(constants.NOTE_VALUE_MAP_SHARP[e.pitch], e.velocity)
    

main()
