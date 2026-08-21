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
from instruments import PunchTapeOrgan, restore

class MrChristmas(PunchTapeOrgan):
    track_positions = list([(48.1 + i*(162.2-48.1)/19)/2 for i in range(20)])

    tones = list([midi.NOTE_NAME_MAP_SHARP[p] for p in [
        'C_4',
        'D_4',
        'E_4',
        'F_4',
        'G_4',
        'A_4',
        'B_4',
        'C_5',
        'D_5',
        'E_5',
        'F_5',
        'G_5',
        'A_5',
        'B_5',
        'C_6',
        'D_6',
        'E_6',
        'F_6',
        'G_6',
        'A_6']])

    def __init__(self, playtime=30., min_break=0.1, **kw):
        super().__init__(**kw)
        self.playtime = playtime
        self.min_break = min_break
        self.tone2track = {t :  pos for t, pos in zip(self.tones, self.track_positions)}
        self.lead = self.trail = 0.0

    @restore
    def drawHole(self, s_t, e_t, pitch, start_t=0):
        rad_per_second = -math.pi * 2 / self.playtime
        start_angle = 1*math.pi + start_t * rad_per_second

        s_arc = s_t * rad_per_second + start_angle
        s_ang = math.degrees(s_arc)
        r = self.tone2track[pitch]
        self.moveTo(0, 0, s_ang)
        self.circle(r, 0, d=2.9)

    def renderSectionBorders(self, start, end, cards=None):
        self.moveTo(100, 100) 
        self.circle(0, 0, d=178)
        self.circle(0, 0, d=0.2*25.4)
        for i in range(143):
            with self.saved_context():
                self.moveTo(0, 0, i*360/143.)
                self.moveTo((174.5 - 5) / 2, 0)
                self.polyline(2.5, 90, 2.3, 90, 2.5, 90, 2.3, 90)

    def render(self, tracks):
        self.openCanvas()

        tracks.parse_tracks(self)

        with self.saved_context():
            self.renderSection(tracks, 0, self.playtime * self.mm_per_second)

        if tracks.unsupported:
            self.ctx.move_to(10, 220)
            self.ctx.show_text("Pitches ignored: " + ", ".join(sorted(tracks.unsupported)))
        self.closeCanvas()
