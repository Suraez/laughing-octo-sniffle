'use strict'

const Mustache = require('mustache');
const fs = require('fs');
const path = require('path');

const filename = "template.html";
const filePath = path.join(__dirname, filename);

function random(b, e) {
    return Math.round(Math.random() * (e - b) + b);
}

module.exports = async function(event, context = null) {
    let username = "hanfeiyu";
    let size = 1000;

    let random_numbers = new Array(size);
    for (let i = 0; i < size; ++i) {
        random_numbers[i] = random(0, 100);
    }

    let input = {
        cur_time: new Date().toLocaleString(),
        username: username,
        random_numbers: random_numbers
    };

    return new Promise((resolve, reject) => {
        fs.readFile(filePath, "utf-8", (err, data) => {
            if (err) {
                reject(err);
            } else {
                const rendered = Mustache.render(data, input);
                resolve({
                    statusCode: 200,
                    headers: { "Content-Type": "text/html" },
                    body: rendered
                });
            }
        });
    });
}
