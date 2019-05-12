use num::traits::pow;
use ramp::Int;
use fnv::FnvHashMap;

#[derive(Clone, Debug)]
struct Point {
	x: Int,
	y: Int,
}

fn bn(n: u32) -> Int {
	Int::from(n)
}

fn inv(a: Int, p: &Int) -> Int {
	a.pow_mod(&(p - 2), &p)
}

fn add(a_in: &Option<Point>, b_in: &Option<Point>, p: &Int) -> Option<Point> {
	if a_in.is_none() {
		return b_in.clone();
	}
	if b_in.is_none() {
		return a_in.clone();
	}
	let a = a_in.clone().unwrap();
	let b = b_in.clone().unwrap();
	if &a.x == &b.x && &a.y == &b.y {
		let l: Int = ((3 * &a.x.pow(2)) * inv(&a.y * 2, p)) % p;
		let x: Int = (l.pow(2) + (p - &a.x) * 2) % p;
		return Some(Point { x: &x % p, y: (&l * (&a.x + (p - &x)) + (p - &a.y)) % p })
	}
	if &a.x == &b.x {
		return None;
	}
	{
		let l = ((&b.y + (p - &a.y)) * inv(&b.x + (p - &a.x), p)) % p;
		let x = (l.pow(2) + (p - &a.x) + (p - &b.x)) % p;
		return Some(Point { x: &x % p, y: (&l * (&a.x + (p - &x)) + (p - &a.y)) % p })
	}
}

fn mul(a_in: &Option<Point>, n_in: &Int, p: &Int) -> Option<Point> {
	let mut k = None;
	let mut a = a_in.clone();
	let mut n = n_in.clone();
	while n != 0 {
		if n.clone() % 2 == 1 {
			k = add(&k, &a, &p);
		}
		a = add(&a, &a, &p);
		n = n / 2;
	}
	k
}

fn main() {
	// let mut map = FnvHashMap::default();
	let p = (bn(1) << 256) - (bn(1) << 32) - bn(91931);
	for i in 0..100000 {
		inv(bn(i), &p);
	}
	/*
	let g = Some(Point {
		x: Int::from_str_radix("79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798", 16).unwrap(),
		y: Int::from_str_radix("0a398300b51ebda42267d6d7ec3a70ddb60fa1665092e499da77bbc6bbe43714", 16).unwrap(),
	});
	let o = mul(&g, &bn(100000348), &p).unwrap();
	let mut gj: Option<Point> = None;
	for j in 0..10000 {
		match gj.clone() {
			None => {},
			Some(n) => {
				map.insert(n.x.to_str_radix(16, false), j);
			},
		}
		gj = add(&gj, &g, &p);
		if j % 1000 == 0 {
			println!("{:?}", j);
		}
	}
	println!("{:?}", o.x.to_str_radix(16, false));
	println!("{:?}", o.y.to_str_radix(16, false));
	*/
}
