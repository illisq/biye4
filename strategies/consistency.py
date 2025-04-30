# 一致性变异策略

import os
import random
import nltk
from nltk.corpus import wordnet
from utils import call_assistant_llm

# 下载必要的NLTK数据
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')

def char_level_mutate(text):
    """字符级别变异：随机插入、突变符号和字母"""
    chars = list(text)
    # 随机位置
    pos = random.randint(0, len(chars)-1)
    # 随机操作：插入(i)、替换(r)
    op = random.choice(['i', 'r'])
    
    if op == 'i':
        # 随机插入特殊字符或空格
        special_chars = [' ', '.', ',', '!', '?', '-', '_']
        chars.insert(pos, random.choice(special_chars))
        mutated = ''.join(chars)
        # 验证长度确实增加了1
        assert len(mutated) == len(text) + 1
        return mutated
    else:
        # 随机替换为相似字符
        char_map = {
            'a': ['@', '4'],
            'e': ['3'],
            'i': ['1', '!'],
            'o': ['0'],
            's': ['5', '$'],
            't': ['7'],
            ' ': ['_', '-']
        }
        if chars[pos].lower() in char_map:
            chars[pos] = random.choice(char_map[chars[pos].lower()])
        mutated = ''.join(chars)
        # 验证长度保持不变
        assert len(mutated) == len(text)
        return mutated

def word_level_mutate(text):
    """单词级别变异：使用WordNet替换同义词"""
    words = nltk.word_tokenize(text)
    pos_tags = nltk.pos_tag(words)
    
    for i, (word, pos) in enumerate(pos_tags):
        # 只处理名词(N)、动词(V)、形容词(J)、副词(R)
        if pos[0] in ['N', 'V', 'J', 'R'] and random.random() < 0.3:  # 30%概率替换
            synsets = wordnet.synsets(word)
            if synsets:
                # 获取所有同义词
                synonyms = []
                for syn in synsets:
                    for lemma in syn.lemmas():
                        if lemma.name() != word:
                            synonyms.append(lemma.name())
                
                if synonyms:
                    words[i] = random.choice(synonyms)
    
    return ' '.join(words)

def sentence_level_mutate(text, question):
    """句子级别变异：使用辅助LLM重写句子，保持意思不变"""
    prompt = f"""这句话："{text}"
还有什么表达方式？要求：
1. 意思必须完全相同
2. 措辞和结构要有变化
3. 直接返回新的表达，不要解释

问题背景（帮助你理解上下文）：{question['question']}"""

    mutated = call_assistant_llm(prompt)
    return mutated if mutated else text

def consistency_mutate(template_text, question):
    """
    一致性变异策略：随机选择1-3种变异方法组合使用
    """
    log = f"[一致性变异] 原始文本:\n{template_text}"
    
    # 可用的变异方法
    mutation_methods = [
        ('char', char_level_mutate),
        ('word', word_level_mutate),
        ('sentence', lambda x: sentence_level_mutate(x, question))
    ]
    
    # 随机选择1-3种方法
    n_methods = random.randint(1, 3)
    selected_methods = random.sample(mutation_methods, n_methods)
    
    mutated = template_text
    for method_name, method_func in selected_methods:
        old_text = mutated
        mutated = method_func(mutated)
        log += f"\n[一致性变异] 使用{method_name}方法:\n{old_text} ->\n{mutated}"
    
    return mutated, log
