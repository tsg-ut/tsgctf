const fs = require('fs');
const pngjs = require('png-js');
const jpegjs = require('jpeg-js');
const editedJpegjs = require('./jpeg-js');

const width = 400;
const height = 50;

fs.readFile('harekaze.jpg', (error, jpegData) => {
	const data = editedJpegjs.decode(jpegData);
	const jpeg = jpegjs.encode({width, height, data: data.data}, 100);
	fs.writeFileSync('harekaze_solve.jpg', jpeg.data);
});
