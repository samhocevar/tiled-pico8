//
//  PICO-8 cart support for Tiled
//
//  Copyright © 2020—2021 Sam Hocevar <sam@hocevar.net>
//
//  This program is free software. It comes without any warranty, to
//  the extent permitted by applicable law. You can redistribute it
//  and/or modify it under the terms of the Do What the Fuck You Want
//  to Public License, Version 2, as published by the WTFPL Task Force.
//  See http://www.wtfpl.net/ for more details.
//

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

function reverse(str) {
    return str.split('').reverse().join('')
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
    //tm.setProperty('Show Sprite 0', false)
    tm.setProperty('Internal Data', Qt.btoa(cart))

    // Create an image and a tileset for the palette
    let tsize = 12
    // TODO

    // Read gfx data into an image
    let gfx = extract(cart, '__gfx__')
    let img = new Image(128, 128, Image.Format_Indexed8)
    img.setColorTable(PALETTE)
    for (let i = 0; i < Math.min(128 * 128, gfx.length); ++i)
        img.setPixel(i % 128, Math.floor(i / 128), fromhex(gfx[i]))

    // Create a tileset from sprite image
    let t = new Tileset('PICO-8 Sprites')
    t.backgroundColor = PALETTE[3]
    t.setTileSize(8, 8)
    t.loadFromImage(img)
    tm.addTileset(t)

    // Read map data into a tile layer
    let map = extract(cart, '__map__')
    let tl = new TileLayer()
    tl.width = 128
    tl.height = 64
    let tle = tl.edit()
    function set_tile(x, y, s) {
        let id = '0x'.concat(s)
        if (id > 0)
            tle.setTile(x, y, t.tile(id))
    }
    for (let i = 0; i < Math.min(64 * 128, Math.floor(map.length / 2)); ++i)
        set_tile(i % 128, Math.floor(i / 128), map.substring(i * 2, i * 2 + 2))
    // The second part of the sprite data also contains map data
    for (let i = 128 * 64; i < Math.min(128 * 128, gfx.length); i += 2)
        set_tile(Math.floor(i / 2) % 128, Math.floor(i / 256), reverse(gfx.substring(i, i + 2)))
    tle.apply()
    tm.addLayer(tl)

    return tm
}

function pico8_write(map, filename)
{
    // console.log(map.property("data"))
    return "unimplemented"
}

const pico8_format = {
    name: "PICO-8 cart (*.p8)",
    extension: "p8",
    read: pico8_read,
    write: pico8_write,
}

var v = tiled.version.split('.').map((e,i) => e*100**(2-i)).reduce((a,b) => a+b)
if (v >= 10500) {
    tiled.registerMapFormat("PICO-8", pico8_format)
} else {
    console.warn(`Tiled version ${tiled.version} is too old for the PICO-8 plugin (1.5.0 required)`)
}
