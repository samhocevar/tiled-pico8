
var PALETTE = [
    "#000000", // black
    "#1d2b53", // dark_blue
    "#7e2553", // dark_purple
    "#008751", // dark_green
    "#ab5236", // brown
    "#5f574f", // dark_gray
    "#c2c3c7", // light_gray
    "#fff1e8", // white
    "#ff004d", // red
    "#ffa300", // orange
    "#ffec27", // yellow
    "#00e436", // green
    "#29adff", // blue
    "#83769c", // indigo
    "#ff77a8", // pink
    "#ffccaa", // peach

    "#291814",
    "#111d35",
    "#422136",
    "#125359",
    "#742f29",
    "#49333b",
    "#a28879",
    "#f3ef7d",
    "#be1250",
    "#ff6c24",
    "#a8e72e",
    "#00b543",
    "#065ab5",
    "#754665",
    "#ff6e59",
    "#ff9d81",
]

function buffertohex(buf) {
    return Array.prototype.map.call(new Uint8Array(buf), e => tohex(e,2)).join('')
}

function tohex(x, ndigits) {
    return (x + (1 << (ndigits * 4))).toString(16).slice(-ndigits)
}

function fromhex(s) {
    return Number('0x'+s)
}

function extract(buf, header) {
    var start = -1
    var tmp = new Uint8Array(buf)
    while (start < buf.byteLength) {
        start = tmp.indexOf('_'.charCodeAt(0), start + 1)
        if (start < 0)
            return ''
        var s = buf.slice(start, start + header.length).toString()
        if (s == header)
            break
    }
    start += header.length
    let end = tmp.indexOf('_'.charCodeAt(0), start)
    let ret = buf.slice(start, end < 0 ? buf.byteLength : end)
    return ret.toString().replace(/\s/g, '')
}

function pico8_read(filename)
{
    let f = new BinaryFile(filename)
    let cart = f.readAll()
    f.close()

    if (cart.slice(0,16) != 'pico-8 cartridge')
        throw new TypeError('Not a PICO-8 cartridge!')

    // Create a map
    let tm = new TileMap()
    tm.setSize(128, 64)
    tm.setTileSize(8, 8)
    tm.orientation = TileMap.Orthogonal
    tm.backgroundColor = PALETTE[0]
    tm.setProperty('data', buffertohex(cart))

    // Create an image and a tileset for the palette
    let tsize = 12
    // TODO

    // Read gfx data into an image
    let gfx = extract(cart, '__gfx__')
    let img = new Image(128, 128, Image.Format_Indexed8)
    // FIXME: for some reason, #123abc will not work
    img.setColorTable(Array.prototype.map.call(PALETTE, e => e.replace('#', '0xff')))
    for (var i = 0; i < Math.min(128 * 128, gfx.length); ++i)
        img.setPixel(i % 128, Math.floor(i / 128), fromhex(gfx[i]))

    // Create a tileset from sprite image
    let t = new Tileset('PICO-8 Sprites')
    t.backgroundColor = PALETTE[3]
    t.loadFromImage(img)
    t.setTileSize(8, 8)
    tm.addTileset(t)

    // Read map data into a tile layer
    let map = extract(cart, '__map__')
    let tl = new TileLayer()
    tl.width = 128
    tl.height = 64
    let tle = tl.edit()
    for (var y = 0; y < 64; ++y)
    {
        for (var x = 0; x < 128; ++x)
        {
            let id = '0x'.concat(map.substring(y * 256 + x * 2, y * 256 + x * 2 + 2))
            tle.setTile(x, y, t.tile(id))
        }
    }
    tle.apply()
    tm.addLayer(tl)

    return tm
}

function pico8_write(map, filename)
{
}

const pico8_format = {
    name: "PICO-8 cart (*.p8)",
    extension: "p8",
    read: pico8_read,
    write: pico8_write,
}

// FIXME: update this when the new API lands in Tiled (https://github.com/bjorn/tiled/issues/2695)
var v = tiled.version.split('.').map((e,i) => e*100**(2-i)).reduce((a,b) => a+b)
if (v >= 10304) {
    tiled.registerMapFormat("PICO-8", pico8_format)
} else {
    console.warn(`Tiled version ${tiled.version} is too old for the PICO-8 plugin (1.3.4 required)`)
}

