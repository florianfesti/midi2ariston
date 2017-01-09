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

try:
    import cairocffi    
    cairocffi.install_as_pycairo()
except ImportError:
    pass
import cairo
import math
import pkgutil
import midi
import svgutil

def getInstruments():
    instruments = {}
    for importer, modname, ispkg in pkgutil.iter_modules(__path__, 'instruments.'):
        module = __import__(modname, fromlist="dummy")
        for k, v in module.__dict__.items():
            if (type(v) is type and issubclass(v, Instrument) and
                v.__module__ is not Instrument.__module__):
                instruments[k] = v
    return instruments

class Instrument(object):

    tones = []
    
    def __init__(self, args):
        self.tone2number = {t : i for i, t in enumerate(self.tones)}
        self.args = args
        self.output = args.output
        if not self.output:
            if args.input.endswith('.midi'):
                self.output = args.input[:-5] + '.svg'
            elif args.input.endswith('.mid'):
                self.output = args.input[:-4] + '.svg'
            else:
                self.output = args.input + '.svg'
    
    def openCanvas(self):
        self.surface = cairo.SVGSurface(self.output, 10000, 10000)
        self.ctx = cairo.Context(self.surface)
        self.ctx.set_source_rgb(0.0, 0.0, 0.0)
        self.ctx.set_line_width(0.2)

    def closeCanvas(self):
        self.ctx.stroke()
        self.surface.flush()
        self.surface.finish()

        svg = svgutil.SVGFile(self.output)
        svg.getEnvelope()
        svg.rewriteViewPort()

    def moveTo(self, x, y=0.0, degrees=0):
        """
        Move coordinate system to given point
        :param y:  (Default value = 0.0)
        :param degrees:  (Default value = 0)
        """
        self.ctx.move_to(0, 0)
        self.ctx.translate(x, y)
        self.ctx.rotate(degrees * math.pi / 180.0)
        self.ctx.move_to(0, 0)

    def circle(self, x, y, r):
        self.ctx.arc(x, y, r, 0, 2*math.pi)
        self.ctx.stroke()

class PunchCardInstrument(Instrument):

    track_positions = []

    def __init__(self, args):
        super(PunchCardInstrument, self).__init__(args)
        self.tone2track = {t :  pos for t, pos in zip(self.tones, self.track_positions)}
        self.length = args.width
        self.card_length = args.cardlength

        self.lead = 30
        self.trail = 30

        self.mm_per_second = 16.
        self.width = 70

    def render(self, tracks):

        tracks.parse_tracks(self)
        last = tracks.getLastTime()

        length = self.lead + self.mm_per_second*last + self.trail

        if self.card_length:
            l_length = (self.length // self.card_length) * self.card_length
        else:
            l_length = self.length

        lines = int(length // l_length + 1)

        self.openCanvas()

        self.moveTo(10, 20)

        if tracks.unsupported:
            self.ctx.show_text("Pitches ignored: " + ", ".join(sorted(tracks.unsupported)))
            self.moveTo(0, 20)

        for i in range(lines):
            end = (i+1) * l_length
            if i == lines-1:
                end = length
                if self.card_length:
                    end = self.card_length * (length // self.card_length + 1)
            self.renderSection(tracks, i * l_length, end, self.card_length)
            self.moveTo(0, self.width + 5)

        self.closeCanvas()

    def renderSectionBorders(self, start, end, cards=None):
        mm_per_second = self.mm_per_second

        self.ctx.rectangle(0, 0, end-start, self.width)
        self.ctx.stroke()

        if cards:
            d, x = self.ctx.get_dash()
            self.ctx.set_dash([0.5, 1.5])
            for i in range(int((end-start) // cards)-1):
                self.ctx.move_to((i+1) * cards, 0)
                self.ctx.line_to((i+1) * cards, self.width)
            self.ctx.stroke()
            self.ctx.set_dash(d)

class Pling(PunchCardInstrument):

    def __init__(self, args):
        super(Pling, self).__init__(args)

        self.hole_diameter = 1.75
        self.min_distance = 7.

    def renderSection(self, tracks,  start, end, cards=None):
        mm_per_second = self.mm_per_second

        t_start = (start - self.lead) / mm_per_second
        t_end = (end - self.lead) / mm_per_second

        self.renderSectionBorders(start, end, cards)

        dt = 0.5*self.hole_diameter/mm_per_second

        for line in tracks.lines:
            for i, e in enumerate(line):
                if e.tick < t_start - dt:
                    continue
                elif e.tick > t_end + dt:
                    break
                if isinstance(e, midi.events.NoteOnEvent) and e.velocity > 0:
                    self.circle(mm_per_second*(e.tick-t_start),
                                self.tone2track[e.pitch], self.hole_diameter/2)


class PunchTapeOrgan(PunchCardInstrument):

    def __init__(self, args):
        super(PunchTapeOrgan, self).__init__(args)

        self.min_break = 2.1
        self.trackwidth = 3.2

    def renderSection(self, tracks,  start, end, cards=None):
        mm_per_second = self.mm_per_second

        t_start = (start - self.lead) / mm_per_second
        t_end = (end - self.lead) / mm_per_second

        self.renderSectionBorders(start, end, cards)

        for line in tracks.lines:
            for i, e in enumerate(line):
                s = line[i-1]
                if i>1 and e.tick < s.tick:
                    print(s.tick, e.tick, s, e)

        for line in tracks.lines:
            for i, e in enumerate(line):
                if (isinstance(e, midi.events.NoteOnEvent) and e.velocity == 0
                    or isinstance(e, midi.events.NoteOffEvent)):
                    s = line[i-1]
                    if e.tick < t_start:
                        continue
                    elif s.tick > t_end:
                        break

                    # XXX check s
                    if len(line) > i+1:
                        # XXX check line[i+1]
                        e.tick = min(e.tick, line[i+1].tick-self.min_break/mm_per_second)
                    if s.tick > e.tick: # needed?
                        print(s.tick, e.tick, s, e)
                    s_x = (s.tick-t_start) * mm_per_second
                    e_x = (e.tick-t_start) * mm_per_second
                    w = 0.5 * self.trackwidth
                    self.ctx.rectangle(s_x, self.tone2track[s.pitch] - w,
                                       e_x-s_x, self.trackwidth)
                    self.ctx.stroke()
