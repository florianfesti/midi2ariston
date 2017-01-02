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
    track_positions = [10 + i * 4.0 for i in range(30)] # XXX
    width = 20 + 29 * 4.0 # XXX

    def __init__(self, args):
        super(Pling30, self).__init__(args)
        self.tone2track = {t :  pos for t, pos in zip(self.tones, self.track_positions)}
        self.length = args.width
        self.card_length = args.cardlength
        self.lead = 30
        self.trail = 10
        self.mm_per_second = 12.7
        self.hole_diameter = 3.5

    def renderSection(self, tracks,  start, end, cards=None):
        mm_per_second = self.mm_per_second

        t_start = (start - self.lead) / mm_per_second
        t_end = (end - self.lead) / mm_per_second

        self.ctx.rectangle(0, 0, end-start, self.width)
        self.ctx.stroke()

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

        if cards:
            d, x = self.ctx.get_dash()
            self.ctx.set_dash([0.5, 1.5])
            for i in range(int((end-start) // cards)-1):
                self.ctx.move_to((i+1) * cards, 0)
                self.ctx.line_to((i+1) * cards, self.width)
            self.ctx.stroke()
            self.ctx.set_dash(d)

    
    def render(self, tracks):

        tracks.parse_tracks(self)
        last = tracks.getLastTime()
        
        length = self.lead + self.mm_per_second*last + self.trail

        if self.card_length:
            l_length = (self.length // self.card_length) * self.card_length
        else:
            l_length = self.length

        lines = int(length // l_length + 1)

        self.open(l_length + 100, lines * (self.width + 20) + 100)

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

        self.close()
