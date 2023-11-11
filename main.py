import math
import argparse
import binascii

input = input()
l = input.split()
bs = int(l[0])  # block size
l1ts = int(l[1])  # l1 total size
l1e = int(l[2])  # l1 number of lines in set
l2ts = int(l[3])
l2e = int(l[4])
rp = l[5]  # replacement policy
ip = l[6]  # policy
tf = l[7]  # trace file
rp1 = ''
ip1 = ''
l1s = 0  # l1 num of sets
l2s = 0  # l2 num of sets
l1dict = {}  # l1 counter for replacement policy used in evict and during lru
l2dict = {}
l1counter = {}
l1counter['Reads'] = 0
l1counter['ReadMiss'] = 0
l1counter['Write'] = 0
l1counter['WriteMiss'] = 0
l1counter['WriteBack'] = 0
l1counter['Inclusive'] = 0
l2counter = {}
l2counter['Reads'] = 0
l2counter['ReadMiss'] = 0
l2counter['Write'] = 0
l2counter['WriteMiss'] = 0
l2counter['WriteBack'] = 0
if rp == '0':
    rp1 = 'LRU'
    if ip == '0':
        ip1 = 'non-inclusive'
    elif ip == '1':
        ip1 = 'inclusive'
elif rp == '1':
    rp1 = 'FIFO'
    if ip == '0':
        ip1 = 'non-inclusive'
    elif ip == '1':
        ip1 = 'inclusive'
else:
    rp1 = 'optimal'
    if ip == '0':
        ip1 = 'non-inclusive'
    elif ip == '1':
        ip1 = 'inclusive'
if (bs != 0 and l1e != 0):
    l1s = int(l1ts / (l1e * bs))
    l1iv = int(math.log2(l1s))
    l1bv = int(math.log2(bs))
    l1tv = 32 - (l1iv + l1bv)
if (l2ts != 0 and l2e != 0):
    l2s = int(l2ts / (l2e * bs))
    l2iv = int(math.log2(l2s))
    l2bv = int(math.log2(bs))
    l2tv = 32 - (l2iv + l2bv)
l1cache = [[] for _ in range(l1s)]  # l1 main cache
l1main = [[] for _ in range(l1s)]
l2main = []
l2cache = []
if (l2s != 0):
    for i in range(l2s):
        l2cache.append([])
        l2main.append([])
l1dict['FIFO'] = {}
l1dict['LRU'] = {}
l1dict['Dirty'] = {}
l1dict['Optimal']={}
for i in range(0, l1s):
    l1dict['LRU'][i] = [0] * l1e
    l1dict['Dirty'][i] = ['r'] * l1e
    l1dict['FIFO'][i] = [0] * l1e
    l1dict['Optimal'][i]=[0]*l1e
l2dict['FIFO'] = {}
l2dict['LRU'] = {}
l2dict['Dirty'] = {}
if (l2s != 0):
    for i in range(0, l2s):
        l2dict['LRU'][i] = [0] * l2e
        l2dict['Dirty'][i] = ['r'] * l2e
        l2dict['FIFO'][i] = [0] * l2e

tlo=[]  # storing all tags in this list
tlodict={} # storing tag as key and index as value

if rp=='2':
    with open(tf) as f:
        for i in f:
            a1 = i.split()
            n1 = len(a1[1]) - 8
            if (n1 < 0):
                m = abs(n1) * '0'
                a1[1] = m + a1[1]
            res = bin(int(a1[1], 16))[2:].zfill(32)
            t = res[:l1tv]
            b= res[l1tv:l1iv + l1tv]
            r=t+b
            tlo.append(r)
        for i in range(0, len(tlo)):
            if tlo[i] in tlodict:
                tlodict[tlo[i]].append(i)
            else:
                tlodict[tlo[i]] = [i]

        for i in tlodict.keys():
            tlodict[i].append(100000000)
            tlodict[i]=tlodict[i][1:]

def readtracefile(input):

    with open(input) as f:
        for i in f:
            a1 = i.split()
            n1 = len(a1[1]) - 8
            if (n1 < 0):
                m = abs(n1) * '0'
                a1[1] = m + a1[1]
            res = bin(int(a1[1], 16))[2:].zfill(32)
            L1cachefun(res, a1[0])

def L1cachefun(binadd, bit1):
    l1tb = binadd[:l1tv]
    l1ib = binadd[l1tv:l1iv + l1tv]
    l1bb = binadd[l1iv + l1tv:]
    if len(l1ib)==0:
        l1sn = 0
    else:
        l1sn = int(l1ib, 2)
    # target=l1cache[l1sn]

    if (bit1 == 'r'):

        l1counter['Reads'] = l1counter['Reads'] + 1
        if l1tb in l1cache[l1sn]:

            n = l1cache[l1sn].index(l1tb)
            m = sorted(l1dict['LRU'][l1sn])[::-1][0] + 1
            l1dict['LRU'][l1sn][n] = m
            if rp=='2':
                l1dict['Optimal'][l1sn][n]=tlodict[l1tb+l1ib][0]
                tlodict[l1tb+l1ib] = tlodict[l1tb+l1ib][1:]

            return 0
        elif l1tb not in l1cache[l1sn]:

            l1counter['ReadMiss'] = l1counter['ReadMiss'] + 1
            if (len(l1cache[l1sn]) < l1e):

                l1cache[l1sn].append(l1tb)
                l1main[l1sn].append(binadd)
                n = l1cache[l1sn].index(l1tb)
                m = sorted(l1dict['LRU'][l1sn])[::-1][0] + 1
                m1 = sorted(l1dict['FIFO'][l1sn])[::-1][0] + 1
                l1dict['LRU'][l1sn][n] = m
                l1dict['FIFO'][l1sn][n] = m1
                if rp=='2':
                    l1dict['Optimal'][l1sn][n] = tlodict[l1tb+l1ib][0]
                    tlodict[l1tb+l1ib] = tlodict[l1tb+l1ib][1:]
                if (l2s != 0):
                    L2cachefun(binadd, 'r')

                return 1
            elif len(l1cache[l1sn]) == l1e:

                if (rp == '0'):
                    m = sorted(l1dict['LRU'][l1sn])
                    n = l1dict['LRU'][l1sn].index(m[0])
                    vt = l1main[l1sn][n]
                    l1cache[l1sn][n] = l1tb
                    l1main[l1sn][n] = binadd
                    if (l1dict['Dirty'][l1sn][n] == 'D'):
                        l1counter['WriteBack'] = l1counter['WriteBack'] + 1
                        if (l2s != 0):
                            L2cachefun(vt, 'w')
                    if (l2s != 0):
                        L2cachefun(binadd, 'r')
                    l1dict['LRU'][l1sn][n] = m[-1] + 1
                    l1dict['Dirty'][l1sn][n] = 'r'
                    return 1

                elif (rp == '1'):
                    m = sorted(l1dict['FIFO'][l1sn])
                    n = l1dict['FIFO'][l1sn].index(m[0])
                    vt = l1main[l1sn][n]
                    l1cache[l1sn][n] = l1tb
                    l1main[l1sn][n] = binadd
                    if (l1dict['Dirty'][l1sn][n] == 'D'):
                        l1counter['WriteBack'] = l1counter['WriteBack'] + 1
                        if (l2s != 0):
                            L2cachefun(vt, 'w')
                    if (l2s != 0):
                        L2cachefun(binadd, 'r')
                    l1dict['FIFO'][l1sn][n] = m[-1] + 1
                    l1dict['Dirty'][l1sn][n] = 'r'
                    return 1
                else:
                    m=sorted(l1dict['Optimal'][l1sn])[::-1][0]
                    n=l1dict['Optimal'][l1sn].index(m)
                    vt = l1main[l1sn][n]
                    l1cache[l1sn][n] = l1tb
                    l1main[l1sn][n] = binadd
                    if (l1dict['Dirty'][l1sn][n] == 'D'):
                        l1counter['WriteBack'] = l1counter['WriteBack'] + 1
                        if (l2s != 0):
                            L2cachefun(vt, 'w')
                    if (l2s != 0):
                        L2cachefun(binadd, 'r')
                    l1dict['Optimal'][l1sn][n] = tlodict[l1tb+l1ib][0]
                    tlodict[l1tb+l1ib] = tlodict[l1tb+l1ib][1:]
                    l1dict['Dirty'][l1sn][n] = 'r'
                    return 1
    else:
        l1counter['Write'] = l1counter['Write'] + 1

        if l1tb in l1cache[l1sn]:

            n = l1cache[l1sn].index(l1tb)
            m = sorted(l1dict['LRU'][l1sn])[::-1][0] + 1
            l1dict['LRU'][l1sn][n] = m
            l1dict['Dirty'][l1sn][n] = 'D'
            if rp=='2':
                l1dict['Optimal'][l1sn][n] = tlodict[l1tb+l1ib][0]
                tlodict[l1tb+l1ib] = tlodict[l1tb+l1ib][1:]

            return 0
        elif l1tb not in l1cache[l1sn]:

            l1counter['WriteMiss'] = l1counter['WriteMiss'] + 1
            if (len(l1cache[l1sn]) < l1e):
                if (l2s != 0):
                    L2cachefun(binadd, 'r')
                l1cache[l1sn].append(l1tb)
                l1main[l1sn].append(binadd)
                n = l1cache[l1sn].index(l1tb)
                m = sorted(l1dict['LRU'][l1sn])[::-1][0] + 1
                m1 = sorted(l1dict['FIFO'][l1sn])[::-1][0] + 1
                l1dict['LRU'][l1sn][n] = m
                l1dict['FIFO'][l1sn][n] = m1
                if rp=='2':
                    l1dict['Optimal'][l1sn][n] = tlodict[l1tb+l1ib][0]
                    tlodict[l1tb+l1ib] = tlodict[l1tb+l1ib][1:]
                l1dict['Dirty'][l1sn][n] = 'D'
                return 0
            elif len(l1cache[l1sn]) == l1e:
                if (rp == '0'):
                    m = sorted(l1dict['LRU'][l1sn])
                    n = l1dict['LRU'][l1sn].index(m[0])
                    vt = l1main[l1sn][n]
                    l1cache[l1sn][n] = l1tb
                    l1main[l1sn][n] = binadd
                    if (l1dict['Dirty'][l1sn][n] == 'D'):
                        l1counter['WriteBack'] = l1counter['WriteBack'] + 1
                        if (l2s != 0):
                            L2cachefun(vt, 'w')
                    if (l2s != 0):
                        L2cachefun(binadd, 'r')
                    l1dict['LRU'][l1sn][n] = m[-1] + 1
                    l1dict['Dirty'][l1sn][n] = 'D'
                    return 0
                elif (rp == '1'):
                    m = sorted(l1dict['FIFO'][l1sn])
                    n = l1dict['FIFO'][l1sn].index(m[0])
                    vt = l1main[l1sn][n]
                    l1cache[l1sn][n] = l1tb
                    l1main[l1sn][n] = binadd
                    if (l1dict['Dirty'][l1sn][n] == 'D'):
                        l1counter['WriteBack'] = l1counter['WriteBack'] + 1
                        if (l2s != 0):
                            L2cachefun(vt, 'w')
                    if (l2s != 0):
                        L2cachefun(binadd, 'r')
                    l1dict['FIFO'][l1sn][n] = m[-1] + 1
                    l1dict['Dirty'][l1sn][n] = 'D'
                    return 1
                else:
                    m = sorted(l1dict['Optimal'][l1sn])[::-1][0]
                    n = l1dict['Optimal'][l1sn].index(m)
                    vt = l1main[l1sn][n]
                    l1cache[l1sn][n] = l1tb
                    l1main[l1sn][n] = binadd
                    if (l1dict['Dirty'][l1sn][n] == 'D'):
                        l1counter['WriteBack'] = l1counter['WriteBack'] + 1
                        if (l2s != 0):
                            L2cachefun(vt, 'w')
                    if (l2s != 0):
                        L2cachefun(binadd, 'r')
                    l1dict['Optimal'][l1sn][n] = tlodict[l1tb+l1ib][0]
                    tlodict[l1tb+l1ib] = tlodict[l1tb+l1ib][1:]
                    l1dict['Dirty'][l1sn][n] = 'D'
                    return 1



def L2cachefun(binadd2, bit2):
    l2tb = binadd2[:l2tv]
    l2ib = binadd2[l2tv:l2iv + l2tv]
    l2bb = binadd2[l2iv + l2tv:]
    l2sn = int(l2ib, 2)

    if (bit2 == 'r'):
        l2counter['Reads'] = l2counter['Reads'] + 1
        if l2tb in l2cache[l2sn]:
            n = l2cache[l2sn].index(l2tb)
            m = sorted(l2dict['LRU'][l2sn])[::-1][0] + 1
            l2dict['LRU'][l2sn][n] = m
            return 0
        elif l2tb not in l2cache[l2sn]:
            l2counter['ReadMiss'] = l2counter['ReadMiss'] + 1
            if (len(l2cache[l2sn]) < l2e):
                l2cache[l2sn].append(l2tb)
                l2main[l2sn].append(binadd2)
                n = l2cache[l2sn].index(l2tb)
                m = sorted(l2dict['LRU'][l2sn])[::-1][0] + 1
                m1 = sorted(l2dict['FIFO'][l2sn])[::-1][0] + 1
                l2dict['LRU'][l2sn][n] = m
                l2dict['FIFO'][l2sn][n] = m1
                return 1
            elif len(l2cache[l2sn]) == l2e:
                if (rp == '0'):
                    m = sorted(l2dict['LRU'][l2sn])
                    n = l2dict['LRU'][l2sn].index(m[0])
                    if ip == '1':
                        vt = l2main[l2sn][n]
                        L1cacheinc(vt)
                    if (l2dict['Dirty'][l2sn][n] == 'D'):
                        l2counter['WriteBack'] = l2counter['WriteBack'] + 1
                    l2cache[l2sn][n] = l2tb
                    l2main[l2sn][n] = binadd2
                    l2dict['LRU'][l2sn][n] = m[-1] + 1
                    l2dict['Dirty'][l2sn][n] = 'r'
                    return 1

                elif (rp == '1'):
                    m = sorted(l2dict['FIFO'][l2sn])
                    n = l2dict['FIFO'][l2sn].index(m[0])
                    if ip == '1':
                        vt = l2main[l2sn][n]
                        L1cacheinc(vt)
                    if (l2dict['Dirty'][l2sn][n] == 'D'):
                        l2counter['WriteBack'] = l2counter['WriteBack'] + 1

                    l2cache[l2sn][n] = l2tb
                    l2main[l2sn][n] = binadd2
                    l2dict['FIFO'][l2sn][n] = m[-1] + 1
                    l2dict['Dirty'][l2sn][n] = 'r'
                    return 1
    else:
        l2counter['Write'] = l2counter['Write'] + 1
        if l2tb in l2cache[l2sn]:
            n = l2cache[l2sn].index(l2tb)
            m = sorted(l2dict['LRU'][l2sn])[::-1][0] + 1
            l2dict['LRU'][l2sn][n] = m
            l2dict['Dirty'][l2sn][n] = 'D'
            return 0
        elif l2tb not in l2cache[l2sn]:
            l2counter['WriteMiss'] = l2counter['WriteMiss'] + 1
            if (len(l2cache[l2sn]) < l2e):
                l2cache[l2sn].append(l2tb)
                l2main.append(binadd2)
                n = l2cache[l2sn].index(l2tb)
                m = sorted(l2dict['LRU'][l2sn])[::-1][0] + 1
                m1 = sorted(l2dict['FIFO'][l2sn])[::-1][0] + 1
                l2dict['LRU'][l2sn][n] = m
                l2dict['FIFO'][l2sn][n] = m1
                l2dict['Dirty'][l2sn][n] = 'D'
                return 0
            elif len(l2cache[l2sn]) == l2e:
                if (rp == '0'):
                    m = sorted(l2dict['LRU'][l2sn])
                    n = l2dict['LRU'][l2sn].index(m[0])
                    if ip == '1':
                        vt = l2main[l2sn][n]
                        L1cacheinc(vt)
                    if (l2dict['Dirty'][l2sn][n] == 'D'):
                        l2counter['WriteBack'] = l2counter['WriteBack'] + 1

                    l2cache[l2sn][n] = l2tb
                    l2main[l2sn][n] = binadd2
                    l2dict['LRU'][l2sn][n] = m[-1] + 1
                    l2dict['Dirty'][l2sn][n] = 'D'
                    return 0
                elif (rp == '1'):
                    m = sorted(l2dict['FIFO'][l2sn])
                    n = l2dict['FIFO'][l2sn].index(m[0])
                    if ip == '1':
                        vt = l2main[l2sn][n]
                        L1cacheinc(vt)
                    if (l2dict['Dirty'][l2sn][n] == 'D'):
                        l2counter['WriteBack'] = l2counter['WriteBack'] + 1
                    l2cache[l2sn][n] = l2tb
                    l2main[l2sn][n] = binadd2
                    l2dict['FIFO'][l2sn][n] = m[-1] + 1
                    l2dict['Dirty'][l2sn][n] = 'D'
                    return 1


def L1cacheinc(binadd3):
    l1tb = binadd3[:l1tv]
    l1ib = binadd3[l1tv:l1iv + l1tv]
    l1bb = binadd3[l1iv + l1tv:]
    l1sn = int(l1ib, 2)

    if l1tb in l1cache[l1sn]:
        n = l1cache[l1sn].index(l1tb)
        l1cache[l1sn].remove(l1tb)
        l1main[l1sn].remove(binadd3)
        if l1dict['Dirty'][l1sn][n] == 'D':
            l1counter['Inclusive'] = l1counter['Inclusive'] + 1

            l1dict['Dirty'][l1sn] = l1dict['Dirty'][l1sn][:n] + l1dict['Dirty'][l1sn][n + 1:] + ['r']

            if rp == '0':

                l1dict['LRU'][l1sn] = l1dict['LRU'][l1sn][:n] + l1dict['LRU'][l1sn][n + 1:] + [0]

            elif rp == '1':
                l1dict['FIFO'][l1sn] = l1dict['FIFO'][l1sn][:n] + l1dict['FIFO'][l1sn][n + 1:] + [0]

        else:

            if rp == '0':
                l1dict['LRU'][l1sn] = l1dict['LRU'][l1sn][:n] + l1dict['LRU'][l1sn][n + 1:] + [0]
            elif rp == '1':
                l1dict['FIFO'][l1sn] = l1dict['FIFO'][l1sn][:n] + l1dict['FIFO'][l1sn][n + 1:] + [0]

def print1():
    readtracefile(tf)
    print("===== Simulator configuration =====")
    print("BLOCKSIZE:             "+l[0])
    print("L1_SIZE:               "+l[1])
    print("L1_ASSOC:              "+l[2])
    print("L2_SIZE:               "+l[3])
    print("L2_ASSOC:              "+l[4])
    print("REPLACEMENT POLICY:    "+rp1)
    print("INCLUSION PROPERTY:    "+ip1)
    print("trace_file:            "+l[7])
    print("===== L1 contents =====")
    print(l1cache)
    for i in range(0,len(l1cache)):
        p="Set     "+str(i)+":"
        s="      "
        s1=s[(len(str(i))-1):]
        p=p+s1
        q=''
        for j in range(0,len(l1cache[i])):

            x=l1cache[i][j]

            q=q+hex(int(x,2))[2:]
            if l1dict['Dirty'][i][j]=="D":
                q=q+" D  "
            else:
                q=q+"    "
        p=p+q
        print(p)
    if l2s!=0:
        print("===== L2 contents =====")
        for i in range(0, len(l2cache)):
            p = "Set     " + str(i) + ":"
            s = "      "
            s1 = s[(len(str(i)) - 1):]
            p = p + s1
            q = ''
            for j in range(0, l2e):
                x=l2cache[i][j]
                q=q+hex(int(x, 2))[2:]
                if l2dict['Dirty'][i][j] == "D":
                    q=q+" D   "
                else:
                    q=q+"     "
            p=p+q
            print(p)
    print("===== Simulation results (raw) =====")
    l1mr=(l1counter['ReadMiss']+l1counter['WriteMiss'])/(l1counter['Reads']+l1counter['Write'])

    tmt=0
    print("a. number of L1 reads:        "+str(l1counter['Reads']))
    print("b. number of L1 read misses:  "+str(l1counter['ReadMiss']))
    print("c. number of L1 writes:       "+str(l1counter['Write']))
    print("d. number of L1 write misses: "+str(l1counter['WriteMiss']))
    print("e. L1 miss rate:              "+"{:.6f}".format(l1mr))
    print("f. number of L1 writebacks:   "+str(l1counter['WriteBack']))
    #print(l1counter['Inclusive'])
    print("g. number of L2 reads:        "+str(l2counter['Reads']))
    print("h. number of L2 read misses:  "+str(l2counter['ReadMiss']))
    print("i. number of L2 writes:       "+str(l2counter['Write']))
    print("j. number of L2 write misses: "+str(l2counter['WriteMiss']))

    if l2s!=0:
        l2mr = (l2counter['ReadMiss']) / (l2counter['Reads'])
        print("k. L2 miss rate:              " + "{:.6f}".format(l2mr))
        print("l. number of L2 writebacks:   " + str(l2counter['WriteBack']))
        if ip=='0':
            tmt=l2counter['ReadMiss']+l2counter['WriteMiss']+l2counter['WriteBack']
        elif ip=='1':
            tmt=l2counter['ReadMiss']+l2counter['WriteMiss']+l2counter['WriteBack']+l1counter['Inclusive']
    else:
        l2mr=0
        print("k. L2 miss rate:              " + str(l2mr))
        print("l. number of L2 writebacks:   " + str(l2counter['WriteBack']))
        tmt=l1counter['ReadMiss']+l1counter['WriteMiss']+l1counter['WriteBack']
    print("m. total memory traffic:      "+str(tmt))


print1()









