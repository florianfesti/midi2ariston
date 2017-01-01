import midi
from instruments import Instrument
from midi import *

class Pling30(Instrument):

    tones = list(reversed(
        [C_0, D_0, G_0, A_0, B_0,
         C_1, D_1, E_1, F_1, Fs_1, G_1, Gs_1, A_1, As_1, B_1,
         C_2, Cs_2, D_2, Ds_2, E_2, F_2, Fs_2, G_2, Gs_2, A_2, As_2, B_2,
         C_3, D_3, E_3]))

    tones = [t + 36 for t in tones]
    track_positions = [1.23 + i * 5.08 for i in range(30)] # XXX 
    width = 160 # XXX

    def __init__(self):
        super(Pling30, self).__init__()
        self.tone2track = {t :  pos for t, pos in zip(self.tones, self.track_positions)}
        self.lead = 30
        self.trail = 10
        self.mm_per_second = 12.7
        self.hole_diameter = 2.5

    def renderSection(self, lines,  start, end, cards=None):
        mm_per_second = self.mm_per_second

        t_start = (start - self.lead) / mm_per_second
        t_end = (end - self.lead) / mm_per_second

        self.ctx.rectangle(0, 0, end-start, self.width)
        self.ctx.stroke()

        dt = 0.5*self.hole_diameter/mm_per_second

        for line in lines:
            for i, e in enumerate(line):
                if e.tick < t_start - dt:
                    continue
                elif e.tick > t_end + dt:
                    break
                if isinstance(e, midi.events.NoteOnEvent) and e.velocity > 0:
                    self.circle(mm_per_second*(e.tick-t_start),
                                self.tone2track[e.pitch], self.hole_diameter/2)

        if cards:
            d, x = self.ctx.get_dash()
            print(d)
            self.ctx.set_dash([0.5, 1.5])
            for i in range(int((end-start) // cards)):
                self.ctx.move_to((i+1) * cards, 0)
                self.ctx.line_to((i+1) * cards, self.width)
            self.ctx.stroke()
            self.ctx.set_dash(d)

    
    def render(self, tracks):
        self.open('pling30.svg')

        lines, unsupported = tracks.parse_tracks(self)
        last = self.getLast(lines)
        
        length = self.lead + self.mm_per_second*last.tick + self.trail

        l_length = 200
        self.moveTo(10, 20)

        if unsupported:
            self.ctx.show_text("Pitches ignored: " + ", ".join(sorted(unsupported)))
            self.moveTo(0, 20)

        for i in range(int(length // l_length) + 1):
            self.renderSection(lines, i * l_length, (i+1) * l_length, 100)
            self.moveTo(0, self.width + 5)

        self.close()
