const xorshift = (x) => {
	x ^= (x << 13) & 0xffffffff;
	x ^= (x >> 17) & 0xffffffff;
	x ^= (x << 5) & 0xffffffff;
	return x;
};

const get = (x) => xorshift(xorshift(xorshift(x))) & 0xff;

console.log(xorshift(0));
console.log(xorshift(1));
console.log(xorshift(2));
console.log(xorshift(1000));


