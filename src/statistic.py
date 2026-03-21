import json
from collections import Counter, defaultdict
import re
import os
import sys

def get_valid_characters(filepath): # 读取一二级汉字表
    valid_characters = set()
    with open(filepath, 'r', encoding = 'gbk', errors = 'ignore') as file:
        for line in file:
            for character in line.strip():
                valid_characters.add(character)
    return valid_characters

def clean_html(html_text): # 用正则表达式去除HTML标签
    text = re.sub(r'<[^>]+>', '', html_text)
    return text

def read_corpus(corpus_path, valid_characters): #读文件，统计一元和二元词频
    unigram_counts = Counter()
    bigram_counts = defaultdict(Counter)

    with open(corpus_path, 'r', encoding = 'gbk', errors = 'ignore') as file:
        for linenum, line in enumerate(file, 1):
            line = line.strip()
            if not line:
                continue

            try:
                news_dict = json.loads(line)
            except json.JSONDecodeError:
                # 跳过无法解析的行
                continue

            title = news_dict.get('title', '').strip()
            html = news_dict.get('html', '').strip()

            text = clean_html(html)
            content = title + ' ' + text

            sentence = []
            for character in content:
                if character in valid_characters:
                    sentence.append(character)
                else:
                    # 遇到了非汉字，则统计当前句子
                    if sentence:
                        # 统计一元词频
                        unigram_counts.update(sentence)

                        # 统计二元词频，拿前后两个字循环累加
                        for c1, c2 in zip(sentence[:-1], sentence[1:]):
                            bigram_counts[c1][c2] += 1
                        sentence = [] # 清空当前句子
            if sentence: # 处理最后一个句子
                unigram_counts.update(sentence)
                for c1, c2 in zip(sentence[:-1], sentence[1:]):
                    bigram_counts[c1][c2] += 1
    return unigram_counts, bigram_counts

def read_weibo(filepath, valid_characters):
    unigram_counts = Counter()
    bigram_counts = defaultdict(Counter)

    with open(filepath, 'r', encoding = 'utf-8', errors = 'ignore') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            try:
                weibo_dict = json.loads(line)
                content = weibo_dict.get('content', '').strip()
            except json.JSONDecodeError:
                continue

            sentence = []
            for character in content:
                if character in valid_characters:
                    sentence.append(character)
                else:
                    if sentence:
                        unigram_counts.update(sentence)
                        for c1, c2 in zip(sentence[:-1], sentence[1:]):
                            bigram_counts[c1][c2] += 1
                        sentence = []
            if sentence:
                unigram_counts.update(sentence)
                for c1, c2 in zip(sentence[:-1], sentence[1:]):
                    bigram_counts[c1][c2] += 1
    return unigram_counts, bigram_counts

if __name__ == "__main__":
    valid_characters_file = './data/一二级汉字表.txt'
    corpus_file = './corpus/sina_news_gbk'
    weibo_file = './corpus/SMP2020/usual_train_new.txt'

    use_weibo = '--weibo' in sys.argv
    
    valid_characters = get_valid_characters(valid_characters_file)

    total_unigrams = Counter()
    total_bigrams = defaultdict(Counter)

    if os.path.exists(corpus_file):
        for filename in os.listdir(corpus_file):
            if filename.endswith('.txt') and '2016' in filename:
                file_path = os.path.join(corpus_file, filename)
                uni, bi = read_corpus(file_path, valid_characters)
                total_unigrams.update(uni)
                for key, counter in bi.items():
                    total_bigrams[key].update(counter)

    if use_weibo:
        print("处理微博语料...")
        if os.path.exists(weibo_file):
            uni, bi = read_weibo(weibo_file, valid_characters)
            weight = 500

            for key, value in uni.items():
                total_unigrams[key] += value * weight

            for key, counter in bi.items():
                for k2, v in counter.items():
                    total_bigrams[key][k2] += v * weight
            print("微博语料处理完成")
        else:
            print("微博语料文件不存在，跳过微博统计")

    with open('./data/unigram.json', 'w', encoding = 'utf-8') as file:
        json.dump(dict(total_unigrams), file, ensure_ascii = False)

    total_bigrams = {key : dict(counter) for key, counter in total_bigrams.items()} 
    with open('./data/bigram.json', 'w', encoding = 'utf-8') as file:
        json.dump(total_bigrams, file, ensure_ascii = False)