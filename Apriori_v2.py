# 最小支持度
Minsup = 0.25
# 最小置信度
Minconf = 0.5

# 根据前一项集创建aimN项集
def combineItems(preL, nowN, aimN):
    # 使用深拷贝防止原数据被修改
    tempL = preL.copy()
    # 至少合并aimN项，剔除非频繁项的超集
    if nowN == aimN:
        for i in tempL:
            # 利用集合去重，排序后转换为字符串 "BCAB->BCA->ABC"
            tempItem = "".join(sorted(set(i)))
            # 将长度为aimN的项记录到候选aimN项集
            if len(tempItem) == aimN:
                itemSetC[aimN][tempItem] = 0
        return
    nowL = []
    # 双重循环，对当前项集进行两两组合
    for i in range(len(tempL)-1):
        for j in range(i+1, len(tempL)):
            nowL.append(tempL[i] + tempL[j])
    # 将组合后的列表作为参数，进行进一步组合
    combineItems(nowL, nowN+1, aimN)

# 扫描数据集，过滤支持度
def scanD(k):
    # 计算最小支持数
    minsupNum = Minsup * tNum
    # 将候选k项集中每一项到数据集中统计支持数
    for i in itemSetC[k]:
        for T in dataSet:
            if set(i).issubset(set(T)):
                itemSetC[k][i] += 1
        # 每一项计算后，如果支持数大于等于最小支持数，写入频繁k项集
        if itemSetC[k][i] >= minsupNum:
            itemSetL[k][i] = itemSetC[k][i]
        # Apriori改进策略——事务压缩
        elif k == 1:
            for T in dataSet:
                if i in T:
                    T.remove(i)
        
# 读入数据集
"""
dataSet = [['A','B'],
            ['B','C','D'],
            ['A','B','D'],
            ['A','D'],
            ['A','B','C'],
            ['A','E'],
            ['A','B','C','E'],
            ['F']]
"""
dataSet = [['a','b','c','e'],
            ['c','d','e','h'],
            ['a','d','f','h'],
            ['a','h'],
            ['b','c','e'],
            ['a','b','f','h'],
            ['b','d','f','h'],
            ['c','f','g']]
#"""
# 总事务数
tNum = len(dataSet)
# 拍平数据集，创建项集合
items = list(set(sum(dataSet, [])))
items.sort()
# 项数
itemsN = len(items)
# 创建候选项集itemSetC、频繁项集itemSetL，其中一维下标i表示i项集
itemSetC = [{} for i in range(itemsN+1)]
itemSetL = [{} for i in range(itemsN+1)]

for k in range(1, itemsN+1):
    # 创建候选k项集
    if k == 1:
        itemSetC[1] = dict.fromkeys(items, 0)
    else:
        combineItems(list(itemSetL[k-1].keys()), 1, k)
    # 扫描事务映射到频繁k项集
    scanD(k)

# 合并频繁项集
itemSetF = {}
for i in range(1, itemsN+1):
    itemSetF.update(itemSetL[i])

# 生成规则
for i in itemSetF:
    # 记录该项长度
    k = len(i)
    # 跳过频繁1项集
    if k == 1:
        continue
    # 字符串处理，方便组合操作 "ABC->ABCAB"
    s = i + i[:k-1]
    # 计算支持度
    supRate = itemSetF[i] / tNum
    # 双重循环，提取频繁子集
    for j in range(k):
        for l in range(1, k):
            # 切片，排序，字符串处理 "BCA->B CA|BC A->B AC|BC A"
            x = "".join(sorted(list(s[j:j+l])))
            y = "".join(sorted(list(s[j+l:j+k])))
            # 计算置信度
            confRate = itemSetF[i]/itemSetF[x]
            # 显示置信度大于等于最小置信度的信息
            if confRate >= Minconf:
                print("{}=>{}[{}%,{}%]".format(x, y, round(supRate*100, 2), round(confRate*100, 2)))