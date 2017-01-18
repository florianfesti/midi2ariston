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

import math

import midi
from instruments import PunchTapeOrgan

class Ariston(PunchTapeOrgan):
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

    def __init__(self, args, playtime=45., min_break=0.1):
        super(Ariston, self).__init__(args)
        self.playtime = playtime
        self.min_break = min_break
        self.tone2track = {t :  pos for t, pos in zip(self.tones, self.track_positions)}
        self.lead = self.trail = 0.0

    def drawHole(self, s_t, e_t, pitch, start_t=0):
        rad_per_second = -math.pi * 2 / self.playtime
        start_angle = 1*math.pi

        s_arc = s_t * rad_per_second + start_angle
        e_arc = e_t * rad_per_second + start_angle
        self.ctx.arc(200, 200, self.tone2track[pitch]-1.25, e_arc, s_arc)
        self.ctx.arc_negative(200, 200, self.tone2track[pitch]+1.25, s_arc, e_arc)
        self.ctx.close_path()
        self.ctx.stroke()

    def renderSectionBorders(self, start, end, cards=None):
        self.circle(200, 200, 166)
        self.circle(200, 200, 5)
        for x, y in ((-37, 0), (0, -37), (37, 0), (0, 37)):
            self.circle(200 + x, 200 + y, 3)
        
        #self.ctx.set_font_size(2)
        #
        #for pitch, position in self.tone2track.items():
        #    self.ctx.move_to(200-position-2, 200)
        #    self.ctx.show_text(midi.NOTE_VALUE_MAP_SHARP[pitch])
        #    self.ctx.stroke()

    def render(self, tracks):
        self.openCanvas()

        tracks.parse_tracks(self)

        self.renderSection(tracks, 0, self.playtime * self.mm_per_second)

        if tracks.unsupported:
            self.ctx.move_to(10, 480)
            self.ctx.show_text("Pitches ignored: " + ", ".join(sorted(tracks.unsupported)))
        self.closeCanvas()
    
