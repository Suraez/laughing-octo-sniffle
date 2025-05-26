'use strict'

const path = require('path');
const filename = "data.json";
const filePath = path.join(__dirname, filename);

// find the index in 'array' where the value 'v' is stored
const binarySearch = function (array, v) {
  let lo = -1, hi = array.length;
  const vlen = v.length;
  let mi = -1;
  let miv = null;
  let finished = false;

  while (1 + lo !== hi) {
    mi = lo + ((hi - lo) >> 1);
    miv = array[mi].substr(0, vlen);
    if (miv == v) {
      break;
    } else if (miv > v) {
      hi = mi;
    } else {
      lo = mi;
    }
  }

  if (mi > 0) {
    do {
      if (array[mi - 1] < miv) {
        finished = true;
      } else {
        mi--;
      }
    } while (mi > 0 && !finished);
  }

  return mi;
};

// formulate response object that OpenFaaS expects
const response = function(retval) {
  return {
    headers: {
      'Content-Type': 'application/json'
    },
    statusCode: 200,
    body: Buffer.from(JSON.stringify(retval)).toString('base64')
  };
};

// filter unwanted characters from strings
const filterStr = function(str) {
  return str.toLowerCase().replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, "").trim();
};

// main OpenFaaS entry
module.exports = function(event, context = null) {
  let term = "ikun";

  // load the autocomplete data
  const arr = require(filePath);
  const MAX_RESULTS = 20;

  term = filterStr(term);
  const ind = binarySearch(arr, term);

  let retval = [];

  if (ind > -1) {
    for (let i = ind; i < arr.length; i++) {
      if (!arr[i].startsWith(term)) break;

      const j = arr[i].indexOf('*');
      retval.push(arr[i].substr(j + 1));

      if (retval.length === MAX_RESULTS) break;
    }
  }

  return response(retval);
};
