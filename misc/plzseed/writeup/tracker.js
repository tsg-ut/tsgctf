const {Server} = require('./bittorrent-tracker');
const {torrentHash} = require('./parameter.js');

const server = new Server({
	udp: false,
	http: true,
	ws: false,
	stats: false,
	filter: (hash, params, callback) => {
		const torrent = server.torrents[hash];
		console.log({hash});
		if (hash !== torrentHash) {
			callback(new Error(`We want ${torrentHash}`));
			return;
		}
		callback(null);
	},
});

server.on('error', (error) => {
	console.log({error});
});

server.on('warning', (error) => {
	console.log({error});
});

server.listen(36262, '0.0.0.0', (event) => {
	console.log({event});
});
