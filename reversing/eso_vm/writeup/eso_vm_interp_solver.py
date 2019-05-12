from data import prog

mem = [0 for _ in range(10000)]

def corresp_parenthes(s):
        stk = []
        res = [-1 for _ in range(len(s))]
        for i,c in enumerate(s):
                if c == '[':
                        stk.append(i)
                elif c==']':
                        bi = stk.pop()
                        res[bi] = i
                        res[i] = bi
        return res
0
prog_parenthes = corresp_parenthes(prog)
MOD = 65537

def add(a,b):
        if type(a) is str or type(b) is str:
                return '+(%s,%s)' % (str(a),str(b))
        return (a+b+MOD)%MOD

def mult(a,b):
        if type(a) is str or type(b) is str:
                return '*(%s,%s)' % (str(a),str(b))
        return (a*b+MOD)%MOD

def eq(a,b,isbranch=False):
        global eq_cnt
        if type(a) is str or type(b) is str:
                if isbranch:
                        print('check?',a,b)
                        return int(input('> '))
                else:
                        return '=(%s,%s)' % (str(a),str(b))
        if a == b:
                return 1
        else:
                return 0

inputs = ['c%d' % i for i in range(100)][::-1]
inp = 0
ip,mp,reg = 0,0,0

import sys

for t in range(10 ** 10):
        if t % (10 ** 6) == 0:
                #print(mem)
                sys.stderr.write("%d\n" % t)
        c = prog[ip]
        if c == '+':
                mem[mp] = add(mem[mp],1)
        elif c == '-':
                mem[mp] = add(mem[mp],-1)
        elif c == '>':
                mp += 1
        elif c == '<':
                mp -= 1
        elif c == 'l':
                reg = mem[mp]
        elif c == 's':
                mem[mp] = reg
        elif c == 'a':
                mem[mp] = add(mem[mp],mem[mp+1])
        elif c == 'm':
                mem[mp] = mult(mem[mp],mem[mp+1])
        elif c == '=':
                mem[mp] = eq(mem[mp],mem[mp+1])
        elif c == 'z':
                mem[mp] = 0
        elif c == '[':
                if eq(mem[mp],0,True):
                        ip = prog_parenthes[ip]
        elif c == ']':
                if eq(mem[mp],0,True):
                        pass
                else:
                        ip = prog_parenthes[ip]
        elif c == ',':
                mem[mp] = inputs.pop()
        elif c == '.':
                if type(mem[mp]) is str:
                        sys.stdout.write(mem[mp])
                else:
                        sys.stdout.write(chr(mem[mp]))
                sys.stdout.flush()
        else:
                print('unknown character',c)
                exit(0)
        ip += 1