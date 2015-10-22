# tzlookup [![NPM version](https://badge.fury.io/js/tzlookup.svg)](http://badge.fury.io/js/tzlookup) [![Build Status](https://travis-ci.org/m-novikov/tzlookup.svg)](https://travis-ci.org/m-novikov/tzlookup)

NodeJS Module for timezone lookup by geo location

## Install

```bash
npm install tzlookup --save
```

## Usage

```js
const tz = require('tzlookup').tzNameAt;

console.log(tz(40.7092, -74.0151));
// => America/New_York
```

Also you can get all timezone names

```js
var tzNames = require('tzlookup').tzNames;

console.log(tzNames.filter(function (name) { return /Europe/.test(name) }));
// => [ 'Europe/Amsterdam',
//      'Europe/Andorra',
//      'Europe/Athens',
//      'Europe/Belgrade',
//      ...
```

## API

### tzNameAt(lat, lon)

#### lat

_Required_  
Type: `Number`

Latitude – number between -90 and +90.

#### lon

_Required_  
Type: `Number`

Longitude – number between -180 and +180.

Function with two arguments – latitude and longitude. Throws `TypeError` if arguments is not a `Number` and `RangeError` if at least one of them is out of range.

### tzNames

Returns the list of all known names of the timezones.

## Lisense

MIT © [Maxim Novikov](https://github.com/m-novikov)
