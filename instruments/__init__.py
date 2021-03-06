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
    
    def __init__(self, filename="", output=None, **kw):
        self.tone2number = {t : i for i, t in enumerate(self.tones)}
        self.output = output
        self.filename = filename
        if not self.output:
            if filename.endswith('.midi'):
                self.output = filename[:-5] + '.svg'
            elif filename.endswith('.mid'):
                self.output = filename[:-4] + '.svg'
            else:
                self.output = filename + '.svg'
        self.unplayable = 0
    
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
        self.ctx.stroke()
        self.ctx.set_source_rgb(0.0, 0.0, 1.0)
        self.ctx.arc(x, y, r, 0, 2*math.pi)
        self.ctx.stroke()
        self.ctx.set_source_rgb(0.0, 0.0, 0.0)

class PunchCardInstrument(Instrument):

    track_positions = []

    def __init__(self, length=800, card_length=0, **kw):
        super(PunchCardInstrument, self).__init__(**kw)
        self.tone2track = {t :  pos for t, pos in zip(self.tones, self.track_positions)}
        self.length = length
        self.card_length = card_length

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

        self.moveTo(10, 10)

        for i in range(lines):
            end = (i+1) * l_length
            if i == lines-1:
                end = length
                if self.card_length:
                    end = self.card_length * (length // self.card_length + 1)
            self.renderSection(tracks, i * l_length, end, self.card_length)
            self.moveTo(0, self.width + 5)

        err = ""
        if self.unplayable:
            err += "%i unplayable notes. " % self.unplayable
        if tracks.unsupported:
            err += "Pitches ignored: " + ", ".join(sorted(tracks.unsupported))
        if err:
            self.ctx.move_to(10, 20)
            self.ctx.show_text(err)
            self.moveTo(0, 20)
            self.circle(0, 0, 0.1)

        self.closeCanvas()

    def renderSectionBorders(self, start, end, cards=None):
        mm_per_second = self.mm_per_second

        self.ctx.rectangle(0, 0, end-start, self.width)
        self.ctx.stroke()

        if cards:
            d, x = self.ctx.get_dash()
            #self.ctx.set_dash([0.5, 1.5])
            for i in range(int((end-start) // cards)-1):
                self.ctx.move_to((i+1) * cards, 0)
                self.ctx.line_to((i+1) * cards, self.width)
            self.ctx.stroke()
            self.ctx.set_dash(d)

class Pling(PunchCardInstrument):

    def __init__(self, **kw):
        super(Pling, self).__init__(**kw)

        self.hole_diameter = 1.75
        self.min_distance = 7.

    def renderSection(self, tracks,  start, end, cards=None):
        mm_per_second = self.mm_per_second

        t_start = (start - self.lead) / mm_per_second
        t_end = (end - self.lead) / mm_per_second

        self.renderSectionBorders(start, end, cards)

        dt = 0.5*self.hole_diameter/mm_per_second

        for line in tracks.lines:
            last = None
            for i, e in enumerate(line):
                if e.tick < t_start - dt:
                    if (isinstance(e, midi.events.NoteOnEvent) and
                        e.velocity > 0):
                        last = e
                    continue
                elif e.tick > t_end + dt:
                    break
                if isinstance(e, midi.events.NoteOnEvent) and e.velocity > 0:
                    if last and abs(e.tick - last.tick) < 0.0001:
                        # ignore tones with the same starting time
                        continue
                    if last and (e.tick - last.tick) * mm_per_second < self.min_distance:
                        self.circle(mm_per_second*(e.tick-t_start),
                                    self.tone2track[e.pitch], self.hole_diameter/5)
                        self.unplayable += 1
                        continue
                    self.circle(mm_per_second*(e.tick-t_start),
                                self.tone2track[e.pitch], self.hole_diameter/2)
                    last = e

class PunchTapeOrgan(PunchCardInstrument):

    def __init__(self, **kw):
        super(PunchTapeOrgan, self).__init__(**kw)

        self.min_break = 2.1
        self.trackwidth = 3.2

    def drawHole(self, s_t, e_t, pitch, section_t=0.0):
        mm_per_second = self.mm_per_second
        s_x = max((s_t-section_t), 0) * mm_per_second
        e_x = (e_t-section_t) * mm_per_second
        w = 0.5 * self.trackwidth
        self.ctx.rectangle(s_x, self.tone2track[pitch] - w,
                           e_x-s_x, self.trackwidth)
        self.ctx.stroke()

    def getEnd(self, e, i, line):
        for j in range(i+1, len(line)):
            s = line[j]
            if isinstance(s, midi.events.NoteOnEvent) and s.velocity > 0:
                return min(e.tick, s.tick-self.min_break)
        return e.tick

    def renderSection(self, tracks,  start, end, cards=None):
        mm_per_second = self.mm_per_second

        t_start = (start - self.lead) / mm_per_second
        t_end = (end - self.lead) / mm_per_second

        self.renderSectionBorders(start, end, cards)

        for line in tracks.lines:
            start = None
            started = 0
            for i, e in enumerate(line):
                if isinstance(e, midi.events.NoteOnEvent) and e.velocity > 0:
                    if not started:
                        # mark start of note
                        start = e
                        started += 1
                    else:
                        # if enough space
                        end_t = e.tick - self.min_break
                        if end_t > start.tick and end_t > t_start:
                            # draw already started note
                            # until this new one starts
                            self.drawHole(start.tick, min(end_t, t_end), start.pitch, t_start)
                            started += 1
                            start = e
                        else:
                            # note enough space: add to earlier
                            started += 1
                if isinstance(e, midi.events.NoteOnEvent) and e.velocity == 0 or isinstance(e, midi.events.NoteOffEvent):
                    started -= 1
                    if not started: # end of last note
                        end_t = min(self.getEnd(e, i, line), t_end)
                        if end_t > t_start:
                            self.drawHole(start.tick, end_t, start.pitch, t_start)
                        start = None
                    else: # ignore ends while the same tone continues
                        pass
                if start and start.tick > t_end:
                    break
