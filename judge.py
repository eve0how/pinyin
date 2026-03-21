import os

def evaluate(output_file, answer_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        outputs = [line.strip() for line in f if line.strip()]
        
    with open(answer_file, 'r', encoding='utf-8') as f:
        answers = [line.strip() for line in f if line.strip()]

    if len(outputs) != len(answers):
        print(f"⚠️ 警告：输出行数 ({len(outputs)}) 和答案行数 ({len(answers)}) 不一致！")
        return

    total_chars = 0
    correct_chars = 0
    
    total_sentences = len(answers)
    correct_sentences = 0

    for out_sent, ans_sent in zip(outputs, answers):
        # 1. 算句准确率：整句话一模一样才算对
        if out_sent == ans_sent:
            correct_sentences += 1
            
        # 2. 算字准确率：逐个字对比
        # 如果长度不一样，以标准答案的长度为基准算总字数
        total_chars += len(ans_sent) 
        for i in range(min(len(out_sent), len(ans_sent))):
            if out_sent[i] == ans_sent[i]:
                correct_chars += 1

    char_accuracy = (correct_chars / total_chars) * 100
    sentence_accuracy = (correct_sentences / total_sentences) * 100

    print("========== 🏆 评测结果 🏆 ==========")
    print(f"总句子数: {total_sentences}")
    print(f"总汉字数: {total_chars}")
    print("-" * 30)
    print(f"✨ 字准确率: {char_accuracy:.2f}% (满分要求: >= 80%)")
    print(f"✨ 句准确率: {sentence_accuracy:.2f}% (满分要求: >= 35%)")
    print("====================================")

if __name__ == '__main__':
    # 路径就用相对路径，因为你会在根目录运行它
    out_path = './data/output.txt'
    ans_path = './data/answer.txt'
    
    if not os.path.exists(out_path):
        print("找不到 output.txt！你是不是忘了运行 python main.py < data/input.txt > data/output.txt ？")
    elif not os.path.exists(ans_path):
        print("找不到 answer.txt！请确认助教的标准答案放在了 data 文件夹里。")
    else:
        evaluate(out_path, ans_path)