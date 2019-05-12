const hashes = require('./hashes.json');
const assert = require('assert');
const fs = require('fs');
const path = require('path');

const starter = Buffer.from(hashes.starter, 'hex');
const terminator = Buffer.from(hashes.terminator, 'hex');
const terminatorOffset = hashes.fileSize - terminator.length;
const chunks = hashes.chunks.map((chunk) => Buffer.from(chunk, 'hex'));

const getByte = (x) => {
	x = (48271 * (x % 0xe9cc19e1)) % 0x7fffffff;
	x = (x << 13) ^ x;
	x = (x >> 17) ^ x;
	x = (x << 5) ^ x;
	return x & 0xff;
};

const flagBuffer = fs.readFileSync(path.join(__dirname, 'flag.rar'));

module.exports.getBytes = (offset, size) => {
	assert(1 <= size && size <= 512 * 1024);
	const buffer = Buffer.alloc(size);
	for (const i of buffer.keys()) {
		buffer[i] = getByte(offset + i);
	}
	if (offset < starter.length) {
		starter.copy(buffer, 0, offset);
	}
	for (const [index, chunkOffset] of hashes.offsets.entries()) {
		const chunk = chunks[index];
		if (offset < chunkOffset + chunk.length && chunkOffset < offset + size) {
			chunk.copy(buffer, Math.max(0, chunkOffset - offset), Math.max(0, offset - chunkOffset));
		}
	}
	if (hashes.flagOffset < offset + size) {
		flagBuffer.copy(buffer, Math.max(0, hashes.flagOffset - offset), Math.max(0, offset - hashes.flagOffset));
	}
	if (terminatorOffset < offset + size) {
		terminator.copy(buffer, Math.max(0, terminatorOffset - offset), Math.max(0, offset - terminatorOffset));
	}
	return buffer;
};
