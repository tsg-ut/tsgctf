const express = require('express');
const session = require('express-session');
const {random} = require('lodash');

const initSession = (req) => {
	if (typeof req.session.dollar !== 'number') {
		req.session.dollar = 0;
	}
	if (typeof req.session.shots !== 'number') {
		req.session.shots = 0;
	}
	if (typeof req.session.combo !== 'number') {
		req.session.combo = 0;
	}
	if (!Array.isArray(req.session.cache)) {
		req.session.cache = [];
	}
	if (req.session.cache.length === 0) {
		while (req.session.cache.length < 240) {
			const randomTexts = random(0, 6 ** 16 - 1).toString(6).padStart(16, '0');
			const randomNumbers = randomTexts.split('').map((char) => parseInt(char));
			req.session.cache.push(...randomNumbers);
		}
	}
}

const app = express();

app.use(express.static('public'));

app.use(session({
	secret: Math.random().toString(),
	resave: false,
	saveUninitialized: false,
}));

app.post('/shot', (req, res) => {
	initSession(req);
	if (req.session.cache[0] === 0) {
		req.session.cache.shift();
		req.session.dollar = 0;
		req.session.shots = 0;
		req.session.combo = 0;
		return res.send('bang!');
	}
	req.session.cache[0]--;
	req.session.shots++;
	req.session.combo++;
	req.session.dollar += req.session.shots * req.session.combo * 10;
	if (req.session.dollar >= 1000000) {
		return res.send(process.env.FLAG);
	}
	return res.send(req.session.dollar.toString());
});

app.post('/roll', (req, res) => {
	initSession(req);
	req.session.cache.shift();
	req.session.combo = 0;
	return res.send('rattle');
});

app.listen(10030, () => console.log('Launched'));