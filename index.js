const fs = require('fs');
const names = require('./data/names.json');
const buf = fs.readFileSync('./data/array');

function toArrayBuffer(buffer) {
    var arrBuffer = new ArrayBuffer(buffer.length);
    var view = new Uint8Array(arrBuffer);
    for (var i = 0; i < buffer.length; ++i) {
        view[i] = buffer[i];
    }
    return new Uint16Array(arrBuffer);
}

// const arrBuffer = toArrayBuffer(buf);
const arr = toArrayBuffer(buf);
// const arr = new Uint16Array(arrBuffer);

function tzNameAt(lat, lon) {
    if (lat <= -90 || lat > 90 || lon <= -180 || lon > 180) {
        throw new RangeError('Invalid coordinates');
    }

    var index = 3241800 - 3600 * Math.floor(lat * 10 + 0.5) - Math.floor(lon * 10 + 0.5);
    var nameIndex = arr[index]

    return names[nameIndex];
}

exports.tzNameAt = tzNameAt;
exports.tzNames  = names;
