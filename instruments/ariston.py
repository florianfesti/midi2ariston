import math

import midi
from instruments import Instrument
import sys
sys.path.append("/home/ffesti/CVS/python-midi/src/")
import events
import constants

class Ariston(Instrument):
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

    def __init__(self, playtime=45., min_break=0.05):
        super(Ariston, self).__init__()
        self.playtime = playtime
        self.min_break = min_break
        self.tone2track = {t :  pos for t, pos in zip(self.tones, self.track_positions)}

    def render(self, tracks):
        self.open("ariston.svg")

        self.circle(250, 250, 166)
        self.circle(250, 250, 5)
        for x, y in ((-37, 0), (0, -37), (37, 0), (0, 37)):
            self.circle(250 + x, 250 + y, 3)

        rad_per_second = -math.pi * 2 / self.playtime
        start_angle = 1*math.pi

        lines, unsupported = tracks.parse_tracks(self)

        for line in lines:
            for i, e in enumerate(line):
                if isinstance(e, events.NoteOnEvent) and e.velocity == 0 or isinstance(e, events.NoteOffEvent):
                    s = line[i-1]
                    # XXX check s
                    if len(line) > i+1:
                        # XXX check line[i+1]
                        e.tick = min(e.tick, line[i+1].tick-self.min_break)
                    if s.tick > e.tick: # needed?
                        print(s.tick, e.tick, s, e)
                    s_arc = s.tick * rad_per_second + start_angle
                    e_arc = e.tick * rad_per_second + start_angle
                    self.ctx.arc(250, 250, self.tone2track[s.pitch]-1.25, e_arc, s_arc)
                    self.ctx.arc_negative(250, 250, self.tone2track[s.pitch]+1.25, s_arc, e_arc)
                    self.ctx.close_path()
                    self.ctx.stroke()
        if unsupported:
            self.ctx.move_to(10, 480)
            self.ctx.show_text("Pitches ignored: " + " ".join(sorted(unsupported)))
        self.close()
    
