
try:
    import cairocffi    
    cairocffi.install_as_pycairo()
except ImportError:
    pass
import cairo
import math

class Instrument(object):

    tones = []
    
    def __init__(self):
        self.tone2number = {t : i for i, t in enumerate(self.tones)}
    
    def open(self, filename):
        self.surface = cairo.SVGSurface(filename, 500, 500)
        self.ctx = cairo.Context(self.surface)
        self.ctx.set_source_rgb(0.0, 0.0, 0.0)
        self.ctx.set_line_width(0.2)

    def close(self):
        self.ctx.stroke()
        self.surface.flush()
        self.surface.finish()

    def circle(self, x, y, r):
        self.ctx.arc(x, y, r, 0, 2*math.pi)
        self.ctx.stroke()

