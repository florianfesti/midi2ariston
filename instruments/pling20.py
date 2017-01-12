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
from instruments import Pling
from midi import *

class Pling30(Pling):

    tones = list(reversed(
        [ C_4, D_4, E_4, F_4, G_4, A_4, B_4,
          C_5, D_5, E_5, F_5, G_5, A_5, B_5,
          C_6, D_6, E_6, F_6, G_6, A_6 ] ))
    track_positions = [6 + i * (58. / 19) for i in range(30)]
    width = 70

    def __init__(self, args):
        super(Pling30, self).__init__(args)
        self.mm_per_second = 16.
        self.min_distance = 7.
        self.hole_diameter = 1.75
