const fs = require('fs');
const {promisify} = require('util');
const bencode = require('bencode');

const {trackerAddr, pieceSize} = require('./parameter.js');

(async () => {
	const hashesData = await promisify(fs.readFile)('hashes.txt');
	const entries = hashesData.toString().split(/\r?\n/).filter((line) => line).map((line) => line.split(': '));
	const map = new Map(entries);
	const pieces = [];
	const chunks = [];
	const offsets = [];
	for (const [indexString, pieceHash] of entries.filter(([key]) => key.startsWith('piece_hash'))) {
		const index = parseInt(indexString.match(/\d+/)[0]);
		pieces[index] = pieceHash;
	}
	for (const [indexString, chunk] of entries.filter(([key]) => key.startsWith('chunk'))) {
		const index = parseInt(indexString.match(/\d+/)[0]);
		chunks[index] = chunk;
	}
	for (const [indexString, offset] of entries.filter(([key]) => key.startsWith('offset'))) {
		const index = parseInt(indexString.match(/\d+/)[0]);
		offsets[index] = parseInt(offset);
	}
	const torrent = bencode.encode({
		announce: `http://${trackerAddr}/announce`,
		'announce-list': [[`http://${trackerAddr}/announce`]],
		comment: 'This torrent is a part of the challenge on TSGCTF. Don\'t use it for other purposes.',
		'created by': 'hakatashi',
		'creation date': 1556939538,
		encoding: 'UTF-8',
		info: {
			length: parseInt(map.get('file_size')),
			name: 'plzseed.rar',
			'piece length': pieceSize,
			pieces: Buffer.from(pieces.join(''), 'hex'),
			private: 1
		},
		'url-list': [],
	});
	await promisify(fs.writeFile)('plzseed.torrent', torrent);
	await promisify(fs.writeFile)('hashes.json', JSON.stringify({
		chunks,
		offsets,
		starter: map.get('starter'),
		terminator: map.get('terminator'),
		fileSize: parseInt(map.get('file_size')),
		flagOffset: parseInt(map.get('flag_offset')),
		pieceCount: pieces.length,
	}));
})();
