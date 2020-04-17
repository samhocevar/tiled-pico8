"""
PICO-8 cart support for Tiled
2020, <sam@hocevar.net>
"""
import tiled as T
import base64

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
        with open(filename, 'rb') as f:
            cart = f.read()

        def extract(header):
            pos = cart.find(header)
            if pos < 0:
                return ''
            pos += len(header)
            data = cart[pos:cart.find(b'_',pos)]
            return ''.join(data.decode('ascii').split())

        # Create a map
        m = T.Tiled.Map(T.Tiled.Map.Orthogonal, 128, 64, 8, 8)
        m.setBackgroundColor(T.qt.QColor(*PALETTE[0]))
        m.setProperty('data', base64.b64encode(cart))

        # Read gfx data into an image
        gfxdata = extract(b'__gfx__')
        pal = [T.qt.QColor(*rgb).rgb() for rgb in PALETTE]
        img = T.qt.QImage(128, 128, T.qt.QImage.Format_Indexed8)
        img.setColorTable(pal)
        for i in range(min(128*128, len(gfxdata))):
            img.setPixel(i % 128, i // 128, int(gfxdata[i], 16))

        # Create fileset from the image
        t = T.Tiled.Tileset.create('PICO-8 Sprites', 8,8, 0, 0)
        t.data().loadFromImage(img, '')
        m.addTileset(t)

        # Read map data into a layer
        mapdata = extract(b'__map__')
        l = T.Tiled.TileLayer('PICO-8 Map', 0, 0, 128, 64)
        for i in range(min(128*64, len(mapdata) // 2)):
            n = int(mapdata[i*2:i*2+2], 16)
            if n > 0:
                ti = t.data().tileAt(n)
                l.setCell(i % 128, i // 128, T.Tiled.Cell(ti))

        # 2nd half of gfx data can overlap 2nd half of map
        for i in range(128*64, min(128*128, len(gfxdata)), 2):
            n = int(gfxdata[i:i+2][::-1], 16)
            if n > 0:
                ti = t.data().tileAt(n)
                l.setCell(i // 2 % 128, i // 256, T.Tiled.Cell(ti))

        m.addLayer(l)

        return m

    @classmethod
    def write(self, m, filename):

        try:
            cart = base64.b64decode(m.propertyAsString('data'))
        except:
            raise Exception('This map was not loaded from a PICO-8 cart.')

        # FIXME: implement actual save
        with open(filename, 'wb') as f:
            f.write(cart)

        return True

