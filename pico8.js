
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
    return Array.prototype.map.call(new Uint8Array(buf), e => tohex(e,2)).join('');
}

function tohex(x, ndigits) {
    return (x + (1 << (ndigits * 4))).toString(16).slice(-ndigits);
}

function pico8_read(filename)
{
    let f = new BinaryFile(filename);
    let cart = f.readAll();
    f.close();

    // TODO: extract func

    if (cart.slice(0,16) != 'pico-8 cartridge')
        throw new TypeError('Not a PICO-8 cartridge!');

    // Create a map
    let m = new TileMap();
    m.setSize(128, 64);
    m.setTileSize(8, 8);
    m.orientation = TileMap.Orthogonal;
    m.backgroundColor = PALETTE[0];
    m.setProperty('data', buffertohex(cart));

    // Create an image and a tileset for the palette
    let tsize = 12;
    // TODO: see API in https://github.com/bjorn/tiled/pull/2787/commits/79e8e26608704649dd1cec303acbf526d65d4282
    let img = new Image(128, 128, Format_Indexed8);

/*
    let s = new TileSet();

    let tm = new TileMap();
    tm.setSize(128, 64);
    tm.setTileSize(8, 8);

    let tl = new TileLayer();
    tl.resize(128, 64);
    let tle = tl.edit();
    for (let y = 0; ; ++y)
    {
        let data = lines[gfx + 1 + y];
        if (data.length != 256)
            break;
        for (let x = 0; x < 128; ++x)
        {
            let id = '0x'.concat(data.substring(x * 2, x * 2 + 2));
            //tle.setTile(x, y, new Tile // FIXME
        }
    }
    tle.apply();
*/

    return m;
}

function pico8_write(map, filename)
{
}

const pico8_format = {
    name: "PICO-8 cart (*.p8)",
    extension: "p8",
    read: pico8_read,
    write: pico8_write,
};

var v = tiled.version.split('.').map((e,i) => e*100**(2-i)).reduce((a,b) => a+b);
if (v >= 10304) {
    tiled.registerMapFormat("PICO-8", pico8_format);
} else {
    console.warn(`Tiled version ${tiled.version} is too old for the PICO-8 plugin (1.3.4 required)`);
}

