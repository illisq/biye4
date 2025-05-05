import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from collections import Counter
from matplotlib.font_manager import FontProperties

# 创建输出目录
os.makedirs('clearer_charts', exist_ok=True)

# 加载JSON文件
with open('data/origin_template_pool.json', 'r', encoding='utf-8') as f:
    origin_templates = json.load(f)

with open('data/template_pool.json', 'r', encoding='utf-8') as f:
    templates = json.load(f)

# 基础统计数据
def get_basic_stats(templates):
    total_templates = len(templates)
    tested_templates = len([t for t in templates if t.get('test_count', 0) > 0])
    total_tests = sum(t.get('test_count', 0) for t in templates)
    total_successes = sum(t.get('success_count', 0) for t in templates)
    success_rate = (total_successes / total_tests) * 100 if total_tests > 0 else 0
    
    return {
        'total_templates': total_templates,
        'tested_templates': tested_templates,
        'total_tests': total_tests,
        'total_successes': total_successes,
        'success_rate': success_rate
    }

orig_stats = get_basic_stats(origin_templates)
new_stats = get_basic_stats(templates)

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 设置风格
plt.style.use('ggplot')

# 1. 更清晰的基础统计数据图表 - 分离为两个图表
# 1.1 模板数量和测试模板数量
fig, ax = plt.subplots(figsize=(10, 6))
labels = ['模板总数\n(Total Templates)', '测试模板数\n(Tested Templates)']
orig_values = [orig_stats['total_templates'], orig_stats['tested_templates']]
new_values = [new_stats['total_templates'], new_stats['tested_templates']]

x = np.arange(len(labels))
width = 0.35

rects1 = ax.bar(x - width/2, orig_values, width, label='原始模板集 (Original)', color='#5DA5DA')
rects2 = ax.bar(x + width/2, new_values, width, label='当前模板集 (Current)', color='#F15854')

# 添加数据标签
def add_labels(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=10, fontweight='bold')

add_labels(rects1)
add_labels(rects2)

ax.set_title('模板数量与测试模板数量比较', fontsize=14, fontweight='bold')
ax.set_ylabel('数量 (Count)', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=11)
ax.legend(fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('clearer_charts/template_counts_comparison.png', dpi=300)
plt.close()

# 1.2 测试次数和成功次数
fig, ax = plt.subplots(figsize=(10, 6))
labels = ['测试总次数\n(Total Tests)', '成功次数\n(Total Successes)']
orig_values = [orig_stats['total_tests'], orig_stats['total_successes']]
new_values = [new_stats['total_tests'], new_stats['total_successes']]

x = np.arange(len(labels))
width = 0.35

rects1 = ax.bar(x - width/2, orig_values, width, label='原始模板集 (Original)', color='#5DA5DA')
rects2 = ax.bar(x + width/2, new_values, width, label='当前模板集 (Current)', color='#F15854')

add_labels(rects1)
add_labels(rects2)

ax.set_title('测试次数与成功次数比较', fontsize=14, fontweight='bold')
ax.set_ylabel('数量 (Count)', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=11)
ax.legend(fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('clearer_charts/tests_success_comparison.png', dpi=300)
plt.close()

# 1.3 成功率
fig, ax = plt.subplots(figsize=(10, 6))
labels = ['成功率 (Success Rate)']
orig_values = [orig_stats['success_rate']]
new_values = [new_stats['success_rate']]

x = np.arange(len(labels))
width = 0.35

rects1 = ax.bar(x - width/2, orig_values, width, label='原始模板集 (Original)', color='#5DA5DA')
rects2 = ax.bar(x + width/2, new_values, width, label='当前模板集 (Current)', color='#F15854')

# 添加百分比标签
for rect in rects1:
    height = rect.get_height()
    ax.annotate(f'{height:.2f}%',
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=10, fontweight='bold')

for rect in rects2:
    height = rect.get_height()
    ax.annotate(f'{height:.2f}%',
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=10, fontweight='bold')

ax.set_title('模板成功率比较', fontsize=14, fontweight='bold')
ax.set_ylabel('成功率 (%)', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=11)
ax.legend(fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('clearer_charts/success_rate_comparison.png', dpi=300)
plt.close()

# 2. 策略使用情况比较
def analyze_strategies(templates):
    strategies = []
    for template in templates:
        strategies.extend(template.get('strategies', []))
    return dict(Counter(strategies))

orig_strategies = analyze_strategies(origin_templates)
new_strategies = analyze_strategies(templates)

# 创建策略比较图
fig, ax = plt.subplots(figsize=(12, 7))

strategies = sorted(set(list(orig_strategies.keys()) + list(new_strategies.keys())))
orig_values = [orig_strategies.get(s, 0) for s in strategies]
new_values = [new_strategies.get(s, 0) for s in strategies]

x = np.arange(len(strategies))
width = 0.35

rects1 = ax.bar(x - width/2, orig_values, width, label='原始模板集 (Original)', color='#5DA5DA')
rects2 = ax.bar(x + width/2, new_values, width, label='当前模板集 (Current)', color='#F15854')

add_labels(rects1)
add_labels(rects2)

ax.set_title('策略使用情况比较', fontsize=14, fontweight='bold')
ax.set_xlabel('策略类型 (Strategy Type)', fontsize=12)
ax.set_ylabel('模板数量 (Count)', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(strategies, fontsize=11)
ax.legend(fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('clearer_charts/strategy_usage_comparison.png', dpi=300)
plt.close()

# 3. 基础类型分布比较
def analyze_base_types(templates):
    base_types = [t.get('base_type', 'unknown') for t in templates]
    return dict(Counter(base_types))

orig_base_types = analyze_base_types(origin_templates)
new_base_types = analyze_base_types(templates)

# 创建基础类型比较图
fig, ax = plt.subplots(figsize=(12, 7))

base_types = sorted(set(list(orig_base_types.keys()) + list(new_base_types.keys())))
orig_values = [orig_base_types.get(bt, 0) for bt in base_types]
new_values = [new_base_types.get(bt, 0) for bt in base_types]

x = np.arange(len(base_types))
width = 0.35

rects1 = ax.bar(x - width/2, orig_values, width, label='原始模板集 (Original)', color='#5DA5DA')
rects2 = ax.bar(x + width/2, new_values, width, label='当前模板集 (Current)', color='#F15854')

add_labels(rects1)
add_labels(rects2)

ax.set_title('基础类型分布比较', fontsize=14, fontweight='bold')
ax.set_xlabel('基础类型 (Base Type)', fontsize=12)
ax.set_ylabel('模板数量 (Count)', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(base_types, fontsize=11)
ax.legend(fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('clearer_charts/base_type_comparison.png', dpi=300)
plt.close()

# 4. 策略成功率比较
def analyze_strategy_success(templates):
    strategy_success = {}
    
    for template in templates:
        strategies = template.get('strategies', [])
        test_count = template.get('test_count', 0)
        success_count = template.get('success_count', 0)
        
        if test_count == 0:
            continue
        
        for strategy in strategies:
            if strategy not in strategy_success:
                strategy_success[strategy] = {'tests': 0, 'successes': 0}
            
            strategy_success[strategy]['tests'] += test_count
            strategy_success[strategy]['successes'] += success_count
    
    # 计算成功率
    result = {}
    for strategy, data in strategy_success.items():
        if data['tests'] > 0:
            result[strategy] = (data['successes'] / data['tests']) * 100
        else:
            result[strategy] = 0
    
    return result

orig_strategy_success = analyze_strategy_success(origin_templates)
new_strategy_success = analyze_strategy_success(templates)

# 创建策略成功率比较图
fig, ax = plt.subplots(figsize=(12, 7))

strategies = sorted(set(list(orig_strategy_success.keys()) + list(new_strategy_success.keys())))
orig_values = [orig_strategy_success.get(s, 0) for s in strategies]
new_values = [new_strategy_success.get(s, 0) for s in strategies]

x = np.arange(len(strategies))
width = 0.35

rects1 = ax.bar(x - width/2, orig_values, width, label='原始模板集 (Original)', color='#5DA5DA')
rects2 = ax.bar(x + width/2, new_values, width, label='当前模板集 (Current)', color='#F15854')

# 添加百分比标签
for rect in rects1:
    height = rect.get_height()
    if height > 0:
        ax.annotate(f'{height:.2f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=10, fontweight='bold')

for rect in rects2:
    height = rect.get_height()
    if height > 0:
        ax.annotate(f'{height:.2f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=10, fontweight='bold')

ax.set_title('策略成功率比较', fontsize=14, fontweight='bold')
ax.set_xlabel('策略类型 (Strategy Type)', fontsize=12)
ax.set_ylabel('成功率 (%)', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(strategies, fontsize=11)
ax.legend(fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('clearer_charts/strategy_success_rate_comparison.png', dpi=300)
plt.close()

# 5. 基础类型成功率比较
def analyze_base_type_success(templates):
    base_type_success = {}
    
    for template in templates:
        base_type = template.get('base_type', 'unknown')
        test_count = template.get('test_count', 0)
        success_count = template.get('success_count', 0)
        
        if test_count == 0:
            continue
        
        if base_type not in base_type_success:
            base_type_success[base_type] = {'tests': 0, 'successes': 0}
        
        base_type_success[base_type]['tests'] += test_count
        base_type_success[base_type]['successes'] += success_count
    
    # 计算成功率
    result = {}
    for base_type, data in base_type_success.items():
        if data['tests'] > 0:
            result[base_type] = (data['successes'] / data['tests']) * 100
        else:
            result[base_type] = 0
    
    return result

orig_base_type_success = analyze_base_type_success(origin_templates)
new_base_type_success = analyze_base_type_success(templates)

# 创建基础类型成功率比较图
fig, ax = plt.subplots(figsize=(12, 7))

base_types = sorted(set(list(orig_base_type_success.keys()) + list(new_base_type_success.keys())))
orig_values = [orig_base_type_success.get(bt, 0) for bt in base_types]
new_values = [new_base_type_success.get(bt, 0) for bt in base_types]

x = np.arange(len(base_types))
width = 0.35

rects1 = ax.bar(x - width/2, orig_values, width, label='原始模板集 (Original)', color='#5DA5DA')
rects2 = ax.bar(x + width/2, new_values, width, label='当前模板集 (Current)', color='#F15854')

# 添加百分比标签
for rect in rects1:
    height = rect.get_height()
    if height > 0:
        ax.annotate(f'{height:.2f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=10, fontweight='bold')

for rect in rects2:
    height = rect.get_height()
    if height > 0:
        ax.annotate(f'{height:.2f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=10, fontweight='bold')

ax.set_title('基础类型成功率比较', fontsize=14, fontweight='bold')
ax.set_xlabel('基础类型 (Base Type)', fontsize=12)
ax.set_ylabel('成功率 (%)', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(base_types, fontsize=11)
ax.legend(fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('clearer_charts/base_type_success_rate_comparison.png', dpi=300)
plt.close()

print("所有图表已成功生成在 'clearer_charts' 目录中。") 