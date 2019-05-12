"""
spec for brainf*ck extention

additional register

* l :: load to register
* s :: save from register
* = :: cmpare
* a :: add
* m :: mult
* z :: mem[mp] = 0
"""

# ....program....instdata...regs...

code = [
"[",
	#isip
	"3>l3<",
	"<-[+7>-]+", #("to","decode"), 
	"2>s2<",
	">-[+7<-]+", #("tomark","prog"), 
	"4>l4<",
	"<-[+7>-]+", #("to","decode"), 
	"3>s3<",	
	">-[+7<-]+", #("tomark","prog"), 
	"5>l5<",
	"<-[+7>-]+", #("to","decode"), 
	"4>s4<",
	">",
	# fetch loop
	# operation (mult,cmp are same)
	"=[-", #0
		# mov only de iikannzi ni yaresou(mark naside)
		">>l<s", #opc
		"3>4>3>l3<4<1<s", #opr2
		"1>3>l3<2<s", #opr1
		"<<",#0
		"=[-", #add
			">>a<<"
		"]>-<",
		"=[-", #mul
			">>m<<"
		"]>-<",
		"=[-", #cmp
			">>=<<"
		"]>-<",
		"=[-", #inc
			">>,<<"
		"]>-<",
		"=[-", #outc
			">>.<<"
		"]>-<",
		">z>l5>s4<z<z<<",
	"]>-<",
	# jnz
	"=[-", #0
		"4>3>",#("to","mem[0]"),
		"l",
		"3<2<s" #opr1
		"[", #opr1
			#jmp directly at program.
			"2<-[+7<-]+",#("to","prog"), #isip
			">>>>l<<<s>>>>l<<<s", #buf2
			# mov forward
			"[-<", #buf1
				"[-l<->7>s<+>]",
			">]<", 
			#move backward
			"[-l<->7<s<+>]", #buf1
			"<", #isip
			"<-[+7>-]+", #("to","decode"),
		">>>z]<<"
	"]>-<",
	# mmovv
	# mem
		# ismem,cnt,mark,data
	"=[-", #0
		">>",  #("to","opr1@decode"),
		"l",
		">>", #("to","mem"), #ismem
		">s[-l4>s]>>l3<", #ismem
		"-[+4<-]+<<",#("to","opr1@decode"),
		"s",
		">", #("to","opr2@decode"),
		"l",
		">", #("to","mem"), #ismem
		">s[-l4>s]>>l3<", #ismem
		"-[+4<-]+<",#("to","opr2@decode"),
		"s",
		"<<+<", # reenter to mov
	"]>-<",
	# mov
	"=[-", #0
		">>",  #("to","opr1@decode"),
		"l",
		">>", #("to","mem"), #ismem
		">s[-l4>s]>+<<", #(mark) #ismem
		"-[+4<-]+<",#("to","opr2@decode"),
		"l",
		">", #("to","mem"),
		">s[-l4>s]>>l<<<", #ismem
		"-[+4<-]+", #("to","mem"),
		">>-[+4>-]>s<<<", #ismem
		"-[+4<-]+4<",#("to","decode"),
	"]>-<",
	# decode
		# 1,0,opc,opr1,opr2
	# program,
		# isdecode,isip,buf1,buf2,inst1,inst2,inst3
	"-[+7<-]+", #("tomark","prog"), 
	"-7>+", #isip
	"]"
]

code = "".join(code)

ts = ""
i = 0
while i < len(code):
	c = code[i]
	if c in '1234567890':
		ts += int(c) * code[i+1]
		i += 1
	else:
		ts += c
	i += 1

code = ts


def asm2imem(asm,imem):
	res = []
	opcs = [
		"add",
		"mul",
		"eq",
		"getc",
		"putc",
	]
	for d in asm:
		if d in opcs:
			res += [0,0,0,0] + [0,opcs.index(d),0]
		elif d[0]=='jnz':
			if d[1]>=0:
				res += [0,0,0,0] + [1,d[1],1]
			else:
				res += [0,0,0,0] + [1,-d[1],0]
		elif d[0]=='mmovv':
			res += [0,0,0,0] + [2,d[1],d[2]]
		elif d[0]=='mov':
			res += [0,0,0,0] + [3,d[1],d[2]]
		else:
			print("unknown op",d)
			exit(-1)
	
	#print(res)
	res[1] = 1
	res += [1,0,0,0,0]
	mr = []
	for d in imem:
		mr += [0,0,0,d]
	mr[0] = 1
	res += mr
	
	ts = "+" * 10 + "lz"
	print(res)
	for cd in res:
		dar = []
		d = cd
		while d > 0:
			dar.append(d % 10)
			d = d // 10
		if len(dar)<=1:
			ts += cd * '+' + ">"
		else:
			ts += ">s<"
			for x in dar[::-1]:
				ts += "m" + "+" * x
			ts += ">z" 
	
	ts += 'z' + '<'*len(res)
	ts += '>'
	return ts



""" 
needed VM instruction

* operations mem[0] = mem[0] op mem[1]
	* add
	* mult
	* cmp
	* inc
	* outc

* jnz ip +-= mem[0]
	* before
	* after

* mov mem[i] = mem[j]
* mmovv mem[mem[i]] = mem[mem[j]]
"""

"""
Additional memory access way at assembler

* mov(i,j)  mem[i]=mem[j];
* mov(i@k,j) mem[k+mem[i]] = mem[j];
* mov(i,j@k) mem[i] = mem[k+mem[j]];

"""


flag = "TSGCTF{vm_0n_vm_c4n_be_r3ver5able}"
N = len(flag)

def asm_compile(asm,initarray={}):
	asm = filter(lambda x: x!='',map(lambda x: x.strip(),asm.split('\n')))
	def f(s):
		x = s.split('(')
		y = "(%s,)" % x[1].split(')')[0]
		return (x[0],eval(y))
	asm = map(f,asm)
	
	ts = []
	addrs = {}
	addrsum = 2
	def getaddr(x,isarr=False):
		nonlocal addrsum
		if not x in addrs:
			addrs[x] = addrsum
			if isarr:
				addrsum += N
			else:
				addrsum += 1
		return addrs[x]
	
	def constaddr(x):
		return getaddr(x)

	
	def rem_at(d,tmps):
		if len(d)>=2:
			i = getaddr(d[0])
			v = getaddr(d[1],True)
			tmp = getaddr(tmps)
			ts.append(("mov",0,i))
			ts.append(("mov",1,constaddr(v)))
			ts.append("add")
			ts.append(("mov",tmp,0))
			return tmp
		else:
			return constaddr(d[0])
	
	for d in asm:
		opc = d[0]
		opr = d[1]
		if opc == 'mov':
			#print(opc,d)
			ismmovv = '@' in ''.join(map(str,opr))
			#print(opc,opr,ismmovv)
			ti = 0
			def f(x):
				nonlocal ti
				if type(x) is str:
					if '@' in x:
						ti += 1
						return rem_at(x.split('@'),'tmp%d' % ti)
					else:
						res = getaddr(x)
				else:
					res = constaddr(x)
				if ismmovv:
					return constaddr(res)
				else:
					return res
			d = list(map(f,opr))
			if ismmovv:
				ts.append(("mmovv",d[0],d[1]))
			else:
				ts.append(("mov",d[0],d[1]))
		elif opc in ['add','mul','eq','getc','putc']:
			ts.append(("mov",0,getaddr(opr[0])))
			if opc in ['add','mul','eq']:
				ts.append(("mov",1,getaddr(opr[1])))
			ts.append(opc)
			ts.append(("mov",getaddr(opr[0]),0))
		elif opc == 'jnz':
			ts.append(("mov",0,getaddr(opr[0])))
			ts.append(("jnz",opr[1]))
		elif opc == 'label':
			ts.append((d[0],d[1][0]))
		elif opc == 'puts':
			for c in opr[0]:
				ts.append(("mov",0,constaddr(ord(c))))
				ts.append('putc')
		else:
			print('unknown',d)
			exit(-1)
	
	las = {}
	i = 0
	asm = []
	for d in ts:
		if d[0]=='label':
			las[d[1]] = i
		else:
			asm.append((i,d))
			i += 1
	
	def f(ids):
		i,d = ids
		if d[0]=='jnz':
			d = (d[0],las[d[1]]-i-1)
		
		return d
		
	asm = list(map(f,asm))
	#print(asm)
	#print(addrs)
	
	memdata = [0 for _ in range(addrsum)]
	for k,v in addrs.items():
		#print(k,k is int)
		if type(k) is int:
			memdata[v] = k
		elif k in initarray.keys():
			for i,d in enumerate(initarray[k]):
				memdata[v+i] = d
			
	#print(memdata)
	
	return asm,memdata

def genf():
	d = 4252634;
	def rand():
		nonlocal d
		d = d ^ (d << 13) 
		d &= ((1<<32)-1)
		d = d ^ (d >> 17)
		d &= ((1<<32)-1)
		d = d ^ (d << 5)
		d &= ((1<<32)-1)
		return d
	return rand

rand = genf()


das = [rand() % 65537 for _ in range(N)]
dbs = [rand() % 65537 for _ in range(N)]
ss = [0 for _ in range(N)]

for i,c in enumerate(flag):
	c = ord(c)
	for j in range(N):
		c *= das[i]
		c += dbs[i]
		ss[j] += c

ss = list(map(lambda x: x % 65537,ss))

#TSG{vm_0n_vm_c4n_be_r3ver5able}

asmdata,memdata = asm_compile('''
	mov("i",0),
	label("loop"),
		getc("c"),
		mov("j",0),
		label("innerloop"),
			mov("a","i@dat"),
			mul("c","a"),
			mov("a","i@dbt"),
			add("c","a"),
			mov("a","j@s"),
			add("a","c"),
			mov("j@s","a"),
			add("j",1),
			mov("a","j"),
			eq("a","n"),
			eq("a",0),
			jnz("a","innerloop"),
		add("i",1),
		mov("a","i"),
		eq("a","n"),
		eq("a",0),
		jnz("a","loop"),
	
	mov("ngn",0),
	mov("i",0),
	label("loop2"),
		mov("a","i@s"),
		mov("c","i@q"),
		eq("a","c"),
		eq("a",0),
		add("ngn","a"),

		add("i",1),
		mov("a","i"),
		eq("a","n"),
		eq("a",0),
		jnz("a","loop2"),
	
	
	jnz("ngn","failed"),
	puts("Correct!\\n"),
	jnz(1,"end"),
	label("failed"),
	puts("Wrong:cry:\\n"),
	label("end"),
	jnz(1,"end"),
''',{
	'n': [N],
	'dat': das,
	'dbt': dbs,
	'q': ss,
})

code = asm2imem(asmdata,memdata) + code
with open('code.h','w') as fp:
	fp.write('const char* code = "' + code + '";')

"""
# a,c,i,j,n

rep(i,n){
	c = getc();
	rep(j,n){
		c *= dat[i];
		c += dat[i];
		s[j] += c;
	}
}

int ngn = 0;
rep(j,n){
	if(s[j] != flag[j])ngn += 1;
}

if(ngn)puts("ng");
else puts("ok");
"""

