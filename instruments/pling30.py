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
        [53, 55, 60, 62, 64, 65, 67, 69, 70,
         71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85,
         86, 87, 88, 89, 91, 93]))

    track_positions = [6 + i * (58. / 29) for i in range(30)]
    width = 70

    def __init__(self, args):
        super(Pling30, self).__init__(args)
        self.tone2track = {t :  pos for t, pos in zip(self.tones, self.track_positions)}
        self.length = args.width
        self.card_length = args.cardlength
        self.lead = 30
        self.trail = 10
        self.mm_per_second = 16.
        self.min_distance = 7.
        self.hole_diameter = 1.75
