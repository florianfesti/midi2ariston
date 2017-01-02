import midi
from instruments import Pling
from midi import *

class Pling30(Pling):

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

