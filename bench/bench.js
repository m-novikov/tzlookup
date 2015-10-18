const Benchmark = require('benchmark').Benchmark;

const tzcoords = require('coordinate-tz');
const tzwhere  = require('tzwhere');
const tzLookup = require('tz-lookup');

const tzlookup = require('../').tzNameAt;

const suite = new Benchmark.Suite;

tzwhere.init();

[
    ['coordinate-tz', tzcoords.calculate],
    ['tzwhere', tzwhere.tzInfo],
    ['tz-lookup', tzLookup],
    ['tzlookup', tzlookup]
].forEach(function (item) {
    var name = item[0];
    var fn   = item[1];

    suite
        .add(name, function() {
            fn( 40.7092,  -74.0151 );
            fn( 42.3668,  -71.0546 );
            fn( 41.8976,  -87.6205 );
            fn( 47.6897, -122.4023 );
            fn( 42.7235,  -73.6931 );
            fn( 42.5807,  -83.0223 );
            fn( 36.8381,  -84.8500 );
            fn( 40.1674,  -85.3583 );
            fn( 37.9643,  -86.7453 );
            fn( 38.6043,  -90.2417 );
            fn( 41.1591, -104.8261 );
            fn( 35.1991, -111.6348 );
            fn( 43.1432, -115.6750 );
            fn( 47.5886, -122.3382 );
            fn( 58.3168, -134.4397 );
            fn( 21.4381, -158.0493 );
            fn( 42.7000,  -80.0000 );
            fn( 51.0036, -114.0161 );
            fn(-16.4965,  -68.1702 );
            fn(-31.9369,  115.8453 );
            fn( 42.0000,  -87.5000 );
        });
});

suite
    .on('cycle', function(event) {
        console.log(String(event.target));
    })
    .on('complete', function() {
        console.log('Fastest is ' + this.filter('fastest').pluck('name'));
    })
    .run();
