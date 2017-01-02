
try:
    import cairocffi    
    cairocffi.install_as_pycairo()
except ImportError:
    pass
import cairo
import math
import pkgutil

def getInstruments():
    instruments = {}
    for importer, modname, ispkg in pkgutil.iter_modules(__path__, 'instruments.'):
        module = __import__(modname, fromlist="dummy")
        for k, v in module.__dict__.items():
            if (type(v) is type and issubclass(v, Instrument) and
                v is not Instrument):
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
    
    def open(self, x=500, y=500):
        self.surface = cairo.SVGSurface(self.output, x, y)
        self.ctx = cairo.Context(self.surface)
        self.ctx.set_source_rgb(0.0, 0.0, 0.0)
        self.ctx.set_line_width(0.2)

    def close(self):
        self.ctx.stroke()
        self.surface.flush()
        self.surface.finish()

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
