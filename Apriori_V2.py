# 最小支持度
Minsup = 0.25
# 最小置信度
Minconf = 0.5

dataSet = [['a','b','c','e'],
            ['c','d','e','h'],
            ['a','d','f','h'],
            ['a','h'],
            ['b','c','e'],
            ['a','b','f','h'],
            ['b','d','f','h'],
            ['c','f','g']]


tNum = len(dataSet)
Minsupnum = Minsup * tNum

def CreatC1():
    C1 = []
    for T in dataSet:
        for i in T:
            if [i] not in C1:
                C1.append([i])
    C1.sort()
    return list(map(frozenset,C1))

def scanD(Ck):
    ssCnt = {}
    for T in dataSet:
        for i in Ck:
            if i.issubset(T):
                if i not in ssCnt:
                    ssCnt[i] = 1
                else:
                    ssCnt[i] += 1
    Lk = {k:v for k,v in ssCnt.items() if v>=Minsupnum}
    return Lk

def has_infrequent_subset(temp,Lk):
    for i in range(len(temp)):
        sonSet = temp.difference(set([list(temp)[i]]))
        if sonSet not in Lk:
            return False
    return True

def apriori_gen(Lk,k):
    Ck = []
    for i in Lk:
        for j in Lk:
            if i != j:
                La = list(i)
                Lb = list(j)
                La.sort()
                Lb.sort()
                if La[:k-2] == Lb[:k-2]:
                    temp = i|j
                    if temp not in Ck and has_infrequent_subset(temp,Lk):
                        Ck.append(temp)
    return Ck

C = [[]]
L = [[]]
C.append(CreatC1())
L.append(scanD(C[1]))

k = 2
while len(L[k-1]) > 1:
    C.append(apriori_gen(L[k-1],k))
    L.append(scanD(C[k]))
    k += 1

for i in L:
    print(i)
    print("----------------------------------------------------------")

