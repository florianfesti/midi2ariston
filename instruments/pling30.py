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

    def __init__(self):
        super(Pling30, self).__init__()
        self.tone2track = {t :  pos for t, pos in zip(self.tones, self.track_positions)}
    
    def render(self, tracks):
        self.open('pling30.svg')
        mm_per_second = 12.7
        hole_diameter = 2.5

        lines, unsupported = tracks.parse_tracks(self)

        posx = 20
        posy = 20
        
        for line in lines:
            for i, e in enumerate(line):
                if isinstance(e, midi.events.NoteOnEvent) and e.velocity > 0:
                    self.circle(posx+mm_per_second*e.tick,
                                posy + self.tone2track[e.pitch], hole_diameter/2)

        if unsupported:
            self.ctx.move_to(10, 480)
            self.ctx.show_text("Pitches ignored: " + " ".join(sorted(unsupported)))
        self.close()
        
