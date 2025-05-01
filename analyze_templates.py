import json
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import numpy as np
from datetime import datetime

def load_json(file_path):
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None

def save_chart(fig, filename):
    """保存图表"""
    charts_dir = 'charts'
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    full_path = os.path.join(charts_dir, f"{filename}_{timestamp}.png")
    fig.savefig(full_path, bbox_inches='tight', dpi=300)
    print(f"Chart saved to {full_path}")

def analyze_templates(templates):
    """分析模板数据并生成统计结果"""
    # 基本统计
    total_templates = len(templates)
    
    # 统计有效的模板（有测试数据的）
    tested_templates = [t for t in templates if t.get('test_count', 0) > 0]
    total_tested = len(tested_templates)
    
    # 汇总测试数据
    total_tests = sum(t.get('test_count', 0) for t in templates)
    total_successes = sum(t.get('success_count', 0) for t in templates)
    
    # 计算总体成功率
    overall_success_rate = total_successes / total_tests if total_tests > 0 else 0
    
    # 创建各种计数器
    base_type_counts = Counter()
    original_id_counts = Counter()
    question_id_counts = Counter()
    strategies_counts = Counter()
    
    # 每个策略的成功率统计
    strategy_success = defaultdict(lambda: {'tests': 0, 'successes': 0})
    base_type_success = defaultdict(lambda: {'tests': 0, 'successes': 0})
    
    # 收集所有成功率数据用于分布分析
    success_rates = []
    
    # 最成功和最不成功的模板
    top_templates = []
    bottom_templates = []
    
    # 处理每个模板
    for template in templates:
        # 基本类型统计
        base_type = template.get('base_type', 'unknown')
        base_type_counts[base_type] += 1
        
        # 原始ID统计
        original_id = template.get('original_id', 'unknown')
        original_id_counts[original_id] += 1
        
        # 问题ID统计
        question_id = template.get('question_id', 'unknown')
        question_id_counts[question_id] += 1
        
        # 策略统计
        strategies = template.get('strategies', [])
        for strategy in strategies:
            strategies_counts[strategy] += 1
        
        # 测试和成功数据
        test_count = template.get('test_count', 0)
        success_count = template.get('success_count', 0)
        
        # 只处理有测试数据的模板
        if test_count > 0:
            # 计算成功率
            success_rate = success_count / test_count
            success_rates.append((template['id'], success_rate, test_count))
            
            # 更新策略成功率统计
            for strategy in strategies:
                strategy_success[strategy]['tests'] += test_count
                strategy_success[strategy]['successes'] += success_count
            
            # 更新基本类型成功率统计
            base_type_success[base_type]['tests'] += test_count
            base_type_success[base_type]['successes'] += success_count
    
    # 对成功率排序，找出最高和最低的
    success_rates.sort(key=lambda x: x[1], reverse=True)
    top_templates = success_rates[:10]  # 成功率最高的10个
    bottom_templates = success_rates[-10:]  # 成功率最低的10个
    
    # 计算策略成功率
    strategy_success_rates = {
        strategy: data['successes'] / data['tests'] if data['tests'] > 0 else 0
        for strategy, data in strategy_success.items()
    }
    
    # 计算基本类型成功率
    base_type_success_rates = {
        base_type: data['successes'] / data['tests'] if data['tests'] > 0 else 0
        for base_type, data in base_type_success.items()
    }
    
    # 生成结果报告
    report = {
        'basic_stats': {
            'total_templates': total_templates,
            'total_tested': total_tested,
            'total_tests': total_tests,
            'total_successes': total_successes,
            'overall_success_rate': overall_success_rate
        },
        'base_type_counts': dict(base_type_counts),
        'original_id_counts': dict(original_id_counts),
        'question_id_counts': dict(question_id_counts),
        'strategies_counts': dict(strategies_counts),
        'strategy_success_rates': strategy_success_rates,
        'base_type_success_rates': base_type_success_rates,
        'top_templates': top_templates,
        'bottom_templates': bottom_templates,
        'success_rate_distribution': success_rates
    }
    
    return report

def print_report(report):
    """打印分析报告"""
    # 基本统计
    basic_stats = report['basic_stats']
    print("\n===== 基本统计 =====")
    print(f"总模板数: {basic_stats['total_templates']}")
    print(f"已测试模板数: {basic_stats['total_tested']}")
    print(f"总测试次数: {basic_stats['total_tests']}")
    print(f"总成功次数: {basic_stats['total_successes']}")
    print(f"总体成功率: {basic_stats['overall_success_rate']:.2%}")
    
    # 基本类型统计
    print("\n===== 基本类型统计 =====")
    for base_type, count in sorted(report['base_type_counts'].items(), key=lambda x: x[1], reverse=True):
        print(f"{base_type}: {count} 模板")
    
    # 原始ID统计
    print("\n===== 原始ID统计 (Top 10) =====")
    for original_id, count in sorted(report['original_id_counts'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"原始ID {original_id}: {count} 模板")
    
    # 问题ID统计
    print("\n===== 问题ID统计 (Top 10) =====")
    for question_id, count in sorted(report['question_id_counts'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"问题ID {question_id}: {count} 模板")
    
    # 策略统计
    print("\n===== 策略统计 =====")
    for strategy, count in sorted(report['strategies_counts'].items(), key=lambda x: x[1], reverse=True):
        print(f"策略 {strategy}: 在 {count} 个模板中使用")
    
    # 策略成功率
    print("\n===== 策略成功率 =====")
    for strategy, rate in sorted(report['strategy_success_rates'].items(), key=lambda x: x[1], reverse=True):
        tests = report['strategy_success_rates'].get(strategy, 0)
        print(f"策略 {strategy}: {rate:.2%}")
    
    # 基本类型成功率
    print("\n===== 基本类型成功率 =====")
    for base_type, rate in sorted(report['base_type_success_rates'].items(), key=lambda x: x[1], reverse=True):
        print(f"类型 {base_type}: {rate:.2%}")
    
    # 最成功的模板
    print("\n===== 最成功的模板 (Top 10) =====")
    for template_id, rate, tests in report['top_templates']:
        print(f"模板 {template_id}: 成功率 {rate:.2%}, 测试次数 {tests}")
    
    # 最不成功的模板
    print("\n===== 最不成功的模板 (Bottom 10) =====")
    for template_id, rate, tests in reversed(report['bottom_templates']):
        print(f"模板 {template_id}: 成功率 {rate:.2%}, 测试次数 {tests}")

def create_charts(report):
    """创建可视化图表"""
    # 创建图表保存目录
    charts_dir = 'charts'
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    
    # 图1: 基本类型分布饼图
    fig, ax = plt.subplots(figsize=(10, 6))
    base_types = report['base_type_counts']
    labels = list(base_types.keys())
    sizes = list(base_types.values())
    
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('模板基本类型分布')
    save_chart(fig, 'base_type_distribution')
    plt.close(fig)
    
    # 图2: 策略分布条形图
    fig, ax = plt.subplots(figsize=(12, 6))
    strategies = report['strategies_counts']
    labels = list(strategies.keys())
    counts = list(strategies.values())
    
    bars = ax.bar(labels, counts)
    ax.set_xlabel('策略')
    ax.set_ylabel('模板数量')
    ax.set_title('策略分布')
    
    # 为每个条形添加标签
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 点的垂直偏移
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    save_chart(fig, 'strategy_distribution')
    plt.close(fig)
    
    # 图3: 成功率分布直方图
    fig, ax = plt.subplots(figsize=(12, 6))
    success_rates = [rate for _, rate, _ in report['success_rate_distribution']]
    
    ax.hist(success_rates, bins=20, alpha=0.7, color='blue', edgecolor='black')
    ax.set_xlabel('成功率')
    ax.set_ylabel('模板数量')
    ax.set_title('成功率分布')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    save_chart(fig, 'success_rate_distribution')
    plt.close(fig)
    
    # 图4: 策略成功率条形图
    fig, ax = plt.subplots(figsize=(12, 6))
    strategy_rates = report['strategy_success_rates']
    labels = list(strategy_rates.keys())
    rates = list(strategy_rates.values())
    
    bars = ax.bar(labels, [rate * 100 for rate in rates])  # 转换为百分比
    ax.set_xlabel('策略')
    ax.set_ylabel('成功率 (%)')
    ax.set_title('各策略成功率')
    
    # 为每个条形添加标签
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 点的垂直偏移
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    save_chart(fig, 'strategy_success_rates')
    plt.close(fig)
    
    # 图5: 基本类型成功率条形图
    fig, ax = plt.subplots(figsize=(12, 6))
    base_type_rates = report['base_type_success_rates']
    labels = list(base_type_rates.keys())
    rates = list(base_type_rates.values())
    
    bars = ax.bar(labels, [rate * 100 for rate in rates])  # 转换为百分比
    ax.set_xlabel('基本类型')
    ax.set_ylabel('成功率 (%)')
    ax.set_title('各基本类型成功率')
    
    # 为每个条形添加标签
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 点的垂直偏移
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    save_chart(fig, 'base_type_success_rates')
    plt.close(fig)

def export_to_csv(report, output_dir='exports'):
    """将报告数据导出为CSV文件"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 导出基本统计数据
    basic_stats_df = pd.DataFrame([report['basic_stats']])
    basic_stats_df.to_csv(f"{output_dir}/basic_stats_{timestamp}.csv", index=False)
    
    # 导出基本类型计数
    base_type_df = pd.DataFrame(list(report['base_type_counts'].items()), columns=['base_type', 'count'])
    base_type_df.to_csv(f"{output_dir}/base_type_counts_{timestamp}.csv", index=False)
    
    # 导出策略计数
    strategies_df = pd.DataFrame(list(report['strategies_counts'].items()), columns=['strategy', 'count'])
    strategies_df.to_csv(f"{output_dir}/strategies_counts_{timestamp}.csv", index=False)
    
    # 导出策略成功率
    strategy_rates_df = pd.DataFrame(list(report['strategy_success_rates'].items()), columns=['strategy', 'success_rate'])
    strategy_rates_df.to_csv(f"{output_dir}/strategy_success_rates_{timestamp}.csv", index=False)
    
    # 导出类型成功率
    base_type_rates_df = pd.DataFrame(list(report['base_type_success_rates'].items()), columns=['base_type', 'success_rate'])
    base_type_rates_df.to_csv(f"{output_dir}/base_type_success_rates_{timestamp}.csv", index=False)
    
    # 导出模板成功率
    success_rates_df = pd.DataFrame(report['success_rate_distribution'], columns=['template_id', 'success_rate', 'test_count'])
    success_rates_df.to_csv(f"{output_dir}/template_success_rates_{timestamp}.csv", index=False)
    
    print(f"CSV报表已导出到 {output_dir} 目录")

def main():
    if len(sys.argv) > 1:
        template_pool_path = sys.argv[1]
    else:
        template_pool_path = 'data/template_pool.json'
    
    print(f"分析模板池: {template_pool_path}")
    
    # 加载模板数据
    templates = load_json(template_pool_path)
    if not templates:
        print("Error: Failed to load template data.")
        return
    
    # 分析模板
    report = analyze_templates(templates)
    
    # 打印报告
    print_report(report)
    
    # 创建可视化图表
    try:
        create_charts(report)
    except Exception as e:
        print(f"Warning: Could not create charts: {e}")
    
    # 导出CSV文件
    try:
        export_to_csv(report)
    except Exception as e:
        print(f"Warning: Could not export to CSV: {e}")

if __name__ == "__main__":
    main() 