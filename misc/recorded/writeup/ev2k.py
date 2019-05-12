import data

def rmemp(v):
	return list(filter(lambda x: x!='',v))
def f(s):
	s = s[len('#define '):]
	s = s.split('\t')
	s = rmemp(s)
	#print(s)
	#print(s[0],s[1])
	s[0] = s[0][s[0].index('_'):]
	if not ('_' in s[0] and s[1].isdigit()):
		return ('_','Error')
	return (int(s[1]),s[0])

keys = dict(map(f,rmemp(data.keys.split('\n'))))

def b2i(s):
	res = 0
	for c in s[::-1]:
		res = res * 256 + c
	return res

ds = open('input','rb').read()
ts = []

ev_size = 12

nt = -1

ts = ""
for i in range(len(ds)//ev_size):
	d = ds[i*ev_size:i*ev_size+ev_size]
	#print(d)
	
	t = b2i(d[0:4])
	if t != 0:
		nt = t
	d = d[4:]
	ty = b2i(d[0:2])	
	co = b2i(d[2:4])
	va = b2i(d[4:8])

	if ty == 1:
		if co in keys.keys():
			co = keys[co]
		else:
			co = "Unknown"
		s = "KEY %s %d : %d" % (co,va,nt)
		co = co[1:]
		if co == 'ENTER':
			ts += ('        time %d' % nt)
			co = '\n'
		elif co == 'SPACE':
			co = ' '
		elif co == 'SLASH':
			co = '/'
		elif co == 'TAB':
			co = '/t'
		elif co == 'MINUS':
			co = '-'
		elif co == 'DOT':
			co = '.'
		elif co == 'APOSTROPHE':
			co = ':'
		elif co == 'LEFTSHIFT':
			co = ''
		else:
			co = co.lower()
		
		if va == 1:
			ts += co
	else:
		s = "%d %d %d : %d" % (ty,co,va,t)
		#print(s)
		continue
	
	#ts.append(s)
	#print(s)

print(ts)
exit(0)

ses = {}
for kv in ts:
	print(kv['code'],kv['value'])
	for k,v in kv.items():
		if not k in ses.keys():
			ses[k] = set([])
		#print(k,v)
		ses[k].add(v)

#print(ses)
