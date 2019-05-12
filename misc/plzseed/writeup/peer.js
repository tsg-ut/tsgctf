const Client = require('bittorrent-tracker');
const Protocol = require('bittorrent-protocol')
const net = require('net')

const infoHash = Buffer.from('01234567890123456789');
const peerId = Buffer.from('01234567890123456780');

const socket = net.createConnection({
	port: 52679,
	host: '127.0.0.1',
	localAddress: '127.0.0.1',
	localPort: 10006,
});
const wire = new Protocol()

socket.pipe(wire).pipe(socket);

wire.handshake(infoHash, peerId);
wire.on('handshake', (dInfoHash, dPeerId) => {
	console.log({dInfoHash, dPeerId});
	wire.unchoke();
	wire.on('unchoke', () => {
		console.log('peer is no longer choking us: ' + wire.peerChoking)
		/*
		wire.request(0, 0, 100, (err, block) => {
			console.log({err, block});
		});
		*/
	});
});

