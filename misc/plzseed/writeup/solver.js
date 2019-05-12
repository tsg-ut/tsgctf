const Client = require('bittorrent-tracker');
const Protocol = require('bittorrent-protocol')
const net = require('net')
const fs = require('fs');
const {promisify} = require('util');

const pieceSize = 16777216;

const infoHash = Buffer.from('6ed7e46a243c10f612bfcdfddc9ce7d45dca6122', 'hex');
const peerId = Buffer.from('-ZZ0000-89a123456789');

const client = new Client({
	infoHash,
	peerId,
	announce: [
		'http://34.85.75.40:36262/announce',
	],
	port: 38951,
});

client.on('peer', function (addr) {
	console.log('found a peer: ' + addr)
	const [host, port] = addr.split(':');
	const socket = net.createConnection({
		port: parseInt(port),
		host,
	});
	const wire = new Protocol()

	socket.pipe(wire).pipe(socket);

	wire.handshake(infoHash, peerId);
	wire.on('handshake', (dInfoHash, dPeerId) => {
		wire.unchoke();
	});

	const get = (offset, length) => {
		return new Promise((resolve, reject) => {
			const pieceIndex = Math.floor(offset / pieceSize);
			const pieceOffset = offset % pieceSize;
			wire.request(pieceIndex, pieceOffset, Math.min(length, pieceSize - pieceOffset), (error, block) => {
				if (error) {
					reject(error);
					return;
				}
				if (length <= pieceSize - pieceOffset) {
					resolve(block);
					return;
				}
				wire.request(pieceIndex + 1, 0, length - (pieceSize - pieceOffset), (error, block2) => {
					if (error) {
						reject(error);
						return;
					}
					resolve(Buffer.concat([block, block2]));
				});
			});
		});
	}

	wire.on('bitfield', async () => {
		let offset = 0;

		// Read RAR format details here: https://www.forensicswiki.org/wiki/RAR
		const rarMarker = await get(offset, 7);
		offset += 7;
		const rarHeader = await get(offset, 13);
		const headerSize = rarHeader.readUInt16LE(5);
		offset += headerSize;
		while (1) {
			const chunkHeader = await get(offset, 100);
			const chunkFlags = chunkHeader.readUInt16LE(3);
			const chunkHeaderSize = chunkHeader.readUInt16LE(5);
			const chunkPackSize = chunkHeader.readUInt32LE(7);
			const nameSize = chunkHeader.readUInt16LE(26);

			if (!(chunkFlags & 0x100)) {
				const chunkHighPackSize = chunkHeader.readUInt32LE(32);
				const fileName = chunkHeader.slice(32, 32 + nameSize).toString();
				console.log({chunkHeader, chunkFlags, chunkHeaderSize, chunkPackSize, fileName, offset});

				if (fileName === 'flag.jpg') {
					const content = await get(offset, chunkHeaderSize + chunkPackSize);
					console.log({content});
					await promisify(fs.writeFile)('flag_out.rar', Buffer.concat([rarMarker, rarHeader, content]));
					console.log('flag_out.rar was extracted.');
					process.exit();
				}

				offset += chunkHeaderSize;
				offset += chunkPackSize;
			} else {
				const chunkHighPackSize = chunkHeader.readUInt32LE(32);
				const fileName = chunkHeader.slice(40, 40 + nameSize).toString();
				console.log({chunkHeader, chunkFlags, chunkHeaderSize, chunkPackSize, fileName, chunkHighPackSize, offset});

				offset += chunkHeaderSize;
				offset += chunkPackSize + chunkHighPackSize * 2 ** 32;
			}
		}
	});
});

client.update();
