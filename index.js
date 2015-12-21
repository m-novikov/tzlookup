const readFile = require('fs').readFileSync;
const names = require('./data/names.json');
const coordsBuffer = readFile(__dirname + '/data/array');

function makeCoordsArray(buffer) {
    var arrBuffer = new ArrayBuffer(buffer.length);
    var view = new Uint8Array(arrBuffer);

    var buflen = buffer.length;

    for (var i = 0; i < buflen; ++i) {
        view[i] = buffer[i];
    }

    return new Uint16Array(arrBuffer);
}

const coordsArray = makeCoordsArray(coordsBuffer);
const floor = Math.floor;

function tzNameAt(lat, lon) {
    if (typeof lat !== 'number' || typeof lon !== 'number') {
        throw new TypeError('Coordinates is not a number');
    }

    if (!(lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180)) {
        throw new RangeError('Coordinates is out of range');
    }

    // Grid which stores tz data represented as array 1801 x 3601
    // First dimension is latitude it varies from 90 to -90 step is -0.1
    // Second dimension is longitude it varies from 180 to -180 step is -0.1
    // Computing index of flat array using following formula
    // 3601 * (900 - floor(lat * 10 + 0.5)) + (1800 - floor(lon * 10 + 0.5) - 1
    // Simplified of which version is below
    var coordIndex = 3242700 - 3601 * floor(lat * 10 + 0.5) - floor(lon * 10 + 0.5);

    var nameIndex = coordsArray[coordIndex];

    return names[nameIndex];
}

exports.tzNameAt = tzNameAt;
exports.tzNames  = names;
