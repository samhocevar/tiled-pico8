"""
PICO-8 cart support for Tiled
2020, <sam@hocevar.net>
"""
import tiled as T
import pickle, base64

PALETTE = [
    (0x00, 0x00, 0x00), # black
    (0x1d, 0x2b, 0x53), # dark_blue
    (0x7e, 0x25, 0x53), # dark_purple
    (0x00, 0x87, 0x51), # dark_green
    (0xab, 0x52, 0x36), # brown
    (0x5f, 0x57, 0x4f), # dark_gray
    (0xc2, 0xc3, 0xc7), # light_gray
    (0xff, 0xf1, 0xe8), # white
    (0xff, 0x00, 0x4d), # red
    (0xff, 0xa3, 0x00), # orange
    (0xff, 0xec, 0x27), # yellow
    (0x00, 0xe4, 0x36), # green
    (0x29, 0xad, 0xff), # blue
    (0x83, 0x76, 0x9c), # indigo
    (0xff, 0x77, 0xa8), # pink
    (0xff, 0xcc, 0xaa), # peach
]

class PICO8(T.Plugin):
    @classmethod
    def nameFilter(self):
        return "PICO-8 cart (*.p8)"

    @classmethod
    def shortName(self):
        return "pico8"

    @classmethod
    def supportsFile(self, f):
        return open(f, 'rb').read(16) == b'pico-8 cartridge'

    @classmethod
    def read(self, filename):
        lines = []
        gpos, mpos = -1, -1
        with open(filename, 'rb') as f:
            for l in f.readlines():
                lines.append(l)
                l = l.strip()
                if l == b'__gfx__':
                    gpos = len(lines)
                elif l == b'__map__':
                    mpos = len(lines)

        # Create a map
        m = T.Tiled.Map(T.Tiled.Map.Orthogonal, 128, 64, 8, 8)
        m.setBackgroundColor(T.qt.QColor(96,96,96))
        m.setProperty('data', base64.b64encode(pickle.dumps(lines)))

        # Read gfx data into a tileset
        pal = [T.qt.QColor(*rgb).rgb() for rgb in PALETTE]
        img = T.qt.QImage(128, 128, T.qt.QImage.Format_Indexed8)
        img.setColorTable(pal)
        for y in range(128):
            data = lines[gpos + y].strip()
            if len(data) != 128:
                break
            data = data.decode('ascii')
            for x in range(128):
                img.setPixel(x, y, int(data[x], 16))

        t = T.Tiled.Tileset.create('Sprites', 8,8, 0, 0)
        t.data().loadFromImage(img, 'embedded')
        m.addTileset(t)

        # Read map data into a layer
        l = T.Tiled.TileLayer('Map', 0, 0, 128, 64)
        for y in range(64):
            data = lines[mpos + y].strip()
            if len(data) != 256:
                break
            data = data.decode('ascii')
            for x in range(128):
                n = int(data[x*2:x*2+2], 16)
                if n > 0:
                    ti = t.data().tileAt(n)
                    l.setCell(x, y, T.Tiled.Cell(ti))

        m.addLayer(l)

        return m

    @classmethod
    def write(self, m, filename):

        lines = pickle.loads(base64.b64decode(m.propertyAsString('data')))

        with open(filename, 'wb') as f:
            # FIXME: not implemented yet
            for l in lines:
                f.write(l)
#
        return True

