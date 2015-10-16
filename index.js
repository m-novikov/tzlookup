const fs = require('fs');
const names = require(__dirname + '/data/names.json');
const buf = fs.readFileSync(__dirname + '/data/array');

function  toArrayBuffer(buffer) {
    var ab = new ArrayBuffer(buffer.length);
    var view = new Uint8Array(ab);
    for (var i = 0; i < buffer.length; ++i) {
        view[i] = buffer[i];
    }
    return ab;
}

const arrBuffer = toArrayBuffer(buf);
const arr = new Uint16Array(arrBuffer);

module.exports.tzNameAt = function (lat, lon) {
    if (!(lat > -90.0 && lat <= +90.0 && lon > -180.0 && lon <= +180.0)) {
        throw new RangeError("Invalid coordinates");
    }
    var idx = arr[3241800 - 3600 * Math.floor(lat * 10 + 0.5) - Math.floor(lon * 10 + 0.5)];
    return names[idx];
}
