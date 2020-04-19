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
        img.fill(0)
        for i in range(min(128*128, len(gfxdata))):
            if i % 128 < 8 and i // 128 < 8:
                continue
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

        eol = b'\r\n' if cart.find(b'\r\n') >= 0 else b'\n'

        def split(header):
            gpos = cart.find(header)
            if gpos < 0:
                gpos = len(cart)
            gend = cart.find(b'_', gpos + 7)
            if gend < 0:
                gend = len(cart)
            data = ''.join(cart[gpos+7:gend].decode('ascii').split())
            return cart[:gpos], data, cart[gend:]

        def chunk(s, n):
            empty = b'0' * n
            while s[-n:] == empty:
                s = s[:-n] # Remove trailing empty lines
            return [s[i:i+n] for i in range(0, len(s), n)]

        l = T.tileLayerAt(m, 0)

        # Insert gfx data into cart
        prefix, data, suffix = split(b'__gfx__')

        # First 64 lines of gfx data are from the original cart; add padding
        # if not enough data in there
        newdata = data[:128*64]
        newdata += ''.join(['0' for x in range(128*64-len(newdata))])

        # The next 64 lines actually come from the last 32 lines of the map
        for n in range(128*32, 128*64):
            t = l.cellAt(n % 128, n // 128).tile()
            tid = t.id() if t else 0
            newdata += '{0:02x}'.format(tid)[::-1]

        # Convert chunked data to bytes
        newdata = eol.join([b'__gfx__'] + chunk(newdata.encode('ascii'), 128) + [b''])
        cart = prefix + newdata + suffix

        # Insert map data into cart
        prefix, _, suffix = split(b'__map__')

        newdata = ''
        for n in range(128*32):
            t = l.cellAt(n % 128, n // 128).tile()
            tid = t.id() if t else 0
            newdata += '{0:02x}'.format(tid)

        # Conert chunked data to bytes
        newdata = eol.join([b'__map__'] + chunk(newdata.encode('ascii'), 256) + [b''])
        cart = prefix + newdata + suffix

        with open(filename, 'wb') as f:
            f.write(cart)

        return True

