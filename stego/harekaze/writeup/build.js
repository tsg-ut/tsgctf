const fs = require('fs');
const pngjs = require('png-js');
const editedJpegjs = require('./jpeg-js');

const width = 400;
const height = 50;

pngjs.decode('harekaze_in.png', (data) => {
	const jpeg = editedJpegjs.encode({width, height, data}, 85)
	fs.writeFileSync('harekaze.jpg', jpeg.data);
});

