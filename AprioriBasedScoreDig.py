# 最小支持度
Minsup = 0.5
# 最小置信度
Minconf = 0.5

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

df = pd.read_csv("成绩表.csv")
df = df[:-1]
df = df.replace(to_replace=u'\u3000',value=0)
df[['学号','成绩']] = df[['学号','成绩']].astype(int)
df = df[(df['考核方式']=='考试') & (df['选课属性']=='必修')]

stuNum = df['学号'].unique()
courseNum = df['课程号'].unique()

stuCourse = pd.DataFrame([],index=stuNum,columns=courseNum)
for i in stuNum:
    for j in courseNum:
        stuCourse[j][i] = df[(df['学号']==i) & (df['课程号']==j)]['成绩'].max()

for i in courseNum:
    if stuCourse[i].count() < Minsup*len(stuCourse):
        stuCourse.drop([i],axis=1,inplace=True)
stuCourse.fillna(0,inplace=True)

clusList = []
for index,row in stuCourse.iteritems():
    X = np.array(stuCourse[index])
    X = X.reshape(-1,1)
    estimator = KMeans(n_clusters=3)
    estimator.fit(X)
    clusList.append(estimator.labels_)

Res = {}
for i in range(len(stuCourse.iloc[0])):
    aMax = 0
    aMin = 100
    bMax = 0
    bMin = 100
    cMax = 0
    cMin = 100
    for j in range(len(stuCourse)):
        flag = clusList[i][j]
        if flag == 0:
            if stuCourse.iloc[j,i] > aMax:
                aMax = stuCourse.iloc[j,i]
            if stuCourse.iloc[j,i] < aMin:
                aMin = stuCourse.iloc[j,i]
        if flag == 1:
            if stuCourse.iloc[j,i] > bMax:
                bMax = stuCourse.iloc[j,i]
            if stuCourse.iloc[j,i] < bMin:
                bMin = stuCourse.iloc[j,i]
        if flag == 2:
            if stuCourse.iloc[j,i] > cMax:
                cMax = stuCourse.iloc[j,i]
            if stuCourse.iloc[j,i] < cMin:
                cMin = stuCourse.iloc[j,i]
    Res[courseNum[i]]=[df[df['课程号']==courseNum[i]]['课程名'].unique()[0],{'A':[aMin,aMax],'B':[bMin,bMax],'C':[cMin,cMax]}]

stuGrade = stuCourse.copy()
gradeList = []
i = 0
for index,row in stuGrade.iteritems():
    temp = []
    for j in range(len(clusList[i])):
        if clusList[i][j] == 0:
            temp.append(index + '_A')
        if clusList[i][j] == 1:
            temp.append(index + '_B')
        if clusList[i][j] == 2:
            temp.append(index + '_C')
    stuGrade[index] = temp
    i+=1

dataSet = []
for i in range(len(stuGrade)):
    dataSet.append(list(stuGrade.iloc[i]))

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

Result = L[1].copy()
k = 2
while len(L[k-1]) > 1:
    C.append(apriori_gen(L[k-1],k))
    L.append(scanD(C[k]))
    Result.update(L[k])
    k += 1

print("----------哪些课程成绩之间具有较强的关联性？----------")
for i in Result:
    word = ""
    for j in list(i):
        courseID,courseGrade = j.split('_')
        word += "《{}》考{}-{}分 ".format(Res[courseID][0],Res[courseID][1][courseGrade][0],Res[courseID][1][courseGrade][1])
    word += "的支持度是{}%".format(round(Result[i]/tNum*100,2))
    print(word)

print("----------课程A成绩为优时，课程B成绩也为优的可信程度为多大？----------")
for i in L[2]:
    a = list(i)[0]
    b = list(i)[1]
    aName,aGrade = a.split('_')
    bName,bGrade = b.split('_')
    aMaxScore = Res[aName][1][aGrade][1]
    bMaxScore = Res[bName][1][bGrade][1]
    if aMaxScore>=90 and bMaxScore>=90:
        AtoBconfRate = L[2][i]/L[1][frozenset([b])]
        BtoAconfRate = L[2][i]/L[1][frozenset([a])]
        if AtoBconfRate >= Minconf:
            print("《{}》 => 《{}》,可信度:{}%".format(Res[aName][0],Res[bName][0],round(AtoBconfRate*100,2)))
        if BtoAconfRate >= Minconf:
            print("《{}》 => 《{}》,可信度:{}%".format(Res[bName][0],Res[aName][0],round(BtoAconfRate*100,2)))
