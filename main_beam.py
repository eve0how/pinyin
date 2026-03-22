import sys
import math
import json
import os
import subprocess
import time


if not os.path.exists('./data/unigram.json') or not os.path.exists('./data/bigram.json'):
    sys.stderr.write("正在生成统计数据...\n")
    sys.stderr.write("(语料库较大,需要一定时间,请耐心等待qaq)\n")

    subprocess.run(["python", "src/statistic.py"])
    sys.stderr.write("生成完成！\n")

pinyin_dict = {} # 拼音——汉字


with open('./data/拼音汉字表.txt', 'r', encoding = 'gbk', errors = 'ignore') as file:
    for line in file:
        data = line.strip().split() 
        if len(data) >= 2:
            pinyin_dict[data[0]] = data[1:] # 存储拼音和对应的汉字列表

char2pinyin = {} # 汉字——拼音
for pinyin, chars in pinyin_dict.items():
    for char in chars:
        if char not in char2pinyin:
            char2pinyin[char] = set()
        char2pinyin[char].add(pinyin) # 存储汉字和对应的拼音集合

with open('./data/unigram.json', 'r', encoding = 'utf-8') as file:
    unigrams = json.load(file) # 一元词和出现次数
total_count = sum(unigrams.values()) # 一元词的总出现次数

with open('./data/bigram.json', 'r', encoding = 'utf-8') as file:
    bigrams = json.load(file) # 二元词和出现次数


lamb = 0.99 # 平滑参数， 0.99表示更依赖二元词，0.01表示更依赖一元词

start_time = time.perf_counter()

for line in sys.stdin: # 输入
    shuru = line.strip().split() # 切分
    if not shuru: # 没有输入
        continue
    ans = []

    first_ans = pinyin_dict.get(shuru[0], []) # 第一个拼音对应的汉字列表
    first_dict = {} # 第一个位置的汉字和对应的代价

    for character in first_ans: # 取汉字
        count = unigrams.get(character, -1) # 得到汉字的出现次数

        k = len(char2pinyin.get(character, [shuru[0]])) # 得到汉字对应的拼音数量
        p_duoyin = 1.0 / k

        if count != -1: # 计算代价
            cost = -math.log(count / total_count) - math.log(p_duoyin)
        else:
            cost = -math.log(0.5 / total_count) - math.log(p_duoyin) # 如果汉字没有出现过，使用一个较小的概率
        
        first_dict[character] = (cost, None) # 存储代价和前一个汉字（第一个位置没有前一个汉字，所以为None）

    ans.append(first_dict) # 将第一个位置的汉字和代价存储到ans中

    for i in range(1, len(shuru)): # 从第二个位置开始处理
        pre_pinyin = shuru[i-1]
        now_pinyin = shuru[i]

        now_ans = pinyin_dict.get(shuru[i], []) # 当前拼音对应的汉字列表
        now_dict = {}

        for character in now_ans:
            min_cost = float('inf')
            choose_pre = None # 记录最后选择的上一个字

            now_count = unigrams.get(character, -1) # 得到当前字的出现次数
            if now_count != -1:
                p1 = now_count / total_count 
            else:
                p1 = 0.5 / total_count

            for pre_character in ans[i-1]: # 遍历前一个位置的汉字
                pre_cost = ans[i-1][pre_character][0] # 前一个字的代价
                pre_count = unigrams.get(pre_character, -1) # 前一个字的出现次数

                if pre_character in bigrams and character in bigrams[pre_character]:
                    word_count = bigrams[pre_character][character]
                else:
                    word_count = -1
            
                p2 = 0.0
                if word_count != -1 and pre_count != -1 and pre_count != 0: # 计算词语代价
                    p2 = word_count / pre_count
                
                p = lamb * p2 + (1 - lamb) * p1

                k = len(char2pinyin.get(character, [now_pinyin])) # 得到当前字对应的拼音数量
                p_duoyin = 1.0 / k

                add_cost = -math.log(p) - math.log(p_duoyin) # 计算总代价

                total_cost = pre_cost + add_cost

                if total_cost < min_cost: # 更新最小代价和选择的前一个字
                    min_cost = total_cost
                    choose_pre = pre_character
            now_dict[character] = (min_cost, choose_pre) # 存储当前字的最小代价和选择的前一个字

        beam = 15 # beam search的宽度
        if len(now_dict) > beam: # 如果当前字的候选列表超过beam宽度，进行剪枝
            now_dict = dict(sorted(now_dict.items(), key = lambda x : x[1][0])[:beam])

        ans.append(now_dict) # 将当前位置的汉字和代价存储到ans中

    # 回溯找到最优路径
    min_cost = float('inf')
    last_character = None
    for character, (cost, _) in ans[-1].items(): # 遍历最后一个位置的汉字，找到最小代价和对应的汉字
        if cost < min_cost:
            min_cost = cost
            last_character = character  
    result = [] # 存储结果

    for i in range(len(ans)-1, -1, -1): # 从后往前回溯
        result.append(last_character)
        last_character = ans[i][last_character][1] # 更新为前一个汉字
    result.reverse() # 反转
    print(''.join(result)) # 输出 

# 2. 停止计时探针
end_time = time.perf_counter()
decode_cost_time = end_time - start_time

# 3. 安全打印时间（输出到终端，不进文件）
print(f"🚀 501个测试样例全部解码完毕！", file=sys.stderr)
print(f"⏱️ 推理总耗时: {decode_cost_time:.4f} 秒", file=sys.stderr)
print(f"⚡ 平均每句耗时: {(decode_cost_time / 501) * 1000:.2f} 毫秒", file=sys.stderr)


        
