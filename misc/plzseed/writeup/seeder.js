const Client = require('bittorrent-tracker');
const Protocol = require('bittorrent-protocol')
const net = require('net')
const Bitfield = require('bitfield');
const fs = require('fs');

const {getBytes} = require('./utils.js');
const hashes = require('./hashes.json');
const {torrentHash, pieceSize, fileSize} = require('./parameter.js');

const port = 10001;
const infoHash = Buffer.from(torrentHash, 'hex');
const peerId = Buffer.from('-ZZ0000-89a123456789');

const client = new Client({
	infoHash,
	peerId,
	announce: [
		'http://node-tracker:36262/announce',
	],
	port,
})

client.on('error', function (err) {
	console.log(err.message)
})

client.on('warning', function (err) {
	console.log(err.message)
})

client.on('update', function (data) {
	console.log('announce:', {complete: data.complete, incomplete: data.incomplete});
});

const peers = new Set();
const set = new Set();

client.on('peer', function (addr) {
	// console.log('found a peer: ' + addr)
	if (peers.has(addr)) {
		return;
	}
	const remotePort = parseInt(addr.split(':')[1]);
	if (remotePort === port) {
		return;
	}
	peers.add(addr);
	const socket = net.createConnection({
		port: remotePort,
		host: '127.0.0.1',
	});
	const wire = new Protocol()

	socket.on('error', (error) => {
		// console.error(error);
		peers.delete(addr);
	});
	socket.pipe(wire).pipe(socket);
	// wire.on('data', (d) => console.log(`[${addr}]`, '<--', d))
	// socket.on('data', (d) => console.log(`[${addr}]`, '-->', d))
	socket.on('end', () => {
		console.log('end', addr);
		peers.delete(addr);
	});

	wire.handshake(infoHash, peerId);
	wire.on('handshake', (dInfoHash, dPeerId) => {
		// console.log('hankshake', {dInfoHash, dPeerId});
		if (dInfoHash !== torrentHash) {
			return;
		}
		wire.unchoke();
		const field = new Bitfield(hashes.pieceCount);
		for (const i of Array(hashes.pieceCount).fill().keys()) {
			field.set(i);
		}
		wire.bitfield(field.buffer);
		wire.on('request', (pieceIndex, offset, length, callback) => {
			if (length > 512 * 1024) {
				return callback(new Error('Request length is too large'));
			}
			if (offset + length > pieceSize) {
				return callback(new Error('Requested resource exceeds the piece size boundary'));
			}
			if (pieceIndex * pieceSize + offset + length > hashes.fileSize) {
				return callback(new Error('Requested resource exceeds the file size boundary'));
			}
			if (!set.has(pieceIndex)) {
				set.add(pieceIndex);
				// console.log({pieceIndex, offset, length, callback});
			}
			const bytes = getBytes(pieceIndex * pieceSize + offset, length);
			callback(null, bytes);
		});
	});

	wire.on('choke', () => console.log('choke', addr))
	wire.on('unchoke', () => console.log('unchoke', addr))
	wire.on('interested', () => console.log('interested', addr))
	wire.on('uninterested', () => console.log('uninterested', addr))
	wire.on('bitfield', () => console.log('bitfield', addr))
	wire.on('have', () => console.log('have', addr))
});

client.update();
client.complete()

setInterval(() => {
	console.log('Updating peers...');
	client.update();
	client.complete()
}, 10000);

net.createServer((socket) => {
	const wire = new Protocol()
	const addr = socket.address();

	socket.on('error', (error) => {
		console.error(error);
	})

	socket.pipe(wire).pipe(socket)
	// wire.on('data', (d) => console.log(`[${addr.address}]`, '<--', d))
	// socket.on('data', (d) => console.log(`[${addr.address}]`, '-->', d))
	socket.on('end', () => {
		console.log('end', addr.address);
		peers.delete(addr.address);
	});

	wire.handshake(infoHash, peerId);
	wire.on('handshake', (dInfoHash, dPeerId) => {
		console.log('hankshake', {dInfoHash, dPeerId});
		if (dInfoHash !== torrentHash) {
			return;
		}
		wire.unchoke();
		const field = new Bitfield(hashes.pieceCount);
		for (const i of Array(hashes.pieceCount).fill().keys()) {
			field.set(i);
		}
		wire.bitfield(field.buffer);
		wire.on('request', (pieceIndex, offset, length, callback) => {
			if (length > 512 * 1024) {
				return callback(new Error('Request length is too large'));
			}
			if (offset + length > pieceSize) {
				return callback(new Error('Requested resource exceeds the piece size boundary'));
			}
			if (pieceIndex * pieceSize + offset + length > hashes.fileSize) {
				return callback(new Error('Requested resource exceeds the file size boundary'));
			}
			if (!set.has(pieceIndex)) {
				set.add(pieceIndex);
				// console.log({pieceIndex, offset, length, callback});
			}
			const bytes = getBytes(pieceIndex * pieceSize + offset, length);
			callback(null, bytes);
		});
	});

	wire.on('choke', () => console.log('choke', addr.address))
	wire.on('unchoke', () => console.log('unchoke', addr.address))
	wire.on('interested', () => console.log('interested', addr.address))
	wire.on('uninterested', () => console.log('uninterested', addr.address))
	wire.on('bitfield', () => console.log('bitfield', addr.address))
	wire.on('have', () => console.log('have', addr.address))
}).listen(port);
