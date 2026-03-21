# 质检小脚本：找出 input.txt 里不存在的拼音
valid_pinyins = set()

# 1. 把所有合法的拼音装进集合
with open('./data/拼音汉字表.txt', 'r', encoding='gbk', errors='ignore') as f:
    for line in f:
        data = line.strip().split()
        if len(data) >= 2:
            valid_pinyins.add(data[0])

# 2. 逐行检查 input.txt
with open('./data/input.txt', 'r', encoding='utf-8') as f: # 注意你的input编码，如果是gbk就改一下
    for line_num, line in enumerate(f, 1):
        pinyin_list = line.strip().lower().split()
        for py in pinyin_list:
            if py not in valid_pinyins:
                print(f"⚠️ 警告：在第 {line_num} 行发现了非法拼音 -> '{py}'")

print("质检完成！")