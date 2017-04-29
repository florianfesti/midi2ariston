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

import midi
from instruments import PunchTapeOrgan
from midi import *

class Organ20(PunchTapeOrgan):
    tones = list(reversed(
        [ F_3, Bb_3, C_4,
          D_4, Eb_4, E_4, F_4, G_4, A_4,
          Bb_4, C_5, D_5, Eb_5, E_5, F_5, G_5, A_5,
          Bb_5, C_6, D_6])) 

    track_positions = [10 + i * 3.65 for i in range(20)]

    def __init__(self, **kw):
        super(Organ20, self).__init__(**kw)

        self.mm_per_second = 70
        self.min_break = 0.02
        self.trackwidth = 3.0
        self.width = 110
