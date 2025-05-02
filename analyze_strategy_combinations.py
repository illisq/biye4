import json
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import numpy as np
from datetime import datetime

def load_json(file_path):
    """Load JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None

def save_chart(fig, filename, charts_dir='strategy_charts'):
    """Save chart to file"""
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    full_path = os.path.join(charts_dir, f"{filename}_{timestamp}.png")
    fig.savefig(full_path, bbox_inches='tight', dpi=300)
    print(f"Chart saved to {full_path}")

def analyze_strategy_combinations(templates):
    """Analyze success rates of different strategy combinations"""
    # Dictionary to store data for each strategy combination
    strategy_combinations = defaultdict(lambda: {'templates': 0, 'tests': 0, 'successes': 0})
    
    # Process each template
    for template in templates:
        # Get the strategy combination
        strategies = template.get('strategies', [])
        if not strategies:
            continue
            
        # Sort strategies to ensure consistent combination key
        strategies.sort()
        combo_key = '+'.join(strategies)
        
        # Get test and success counts
        test_count = template.get('test_count', 0)
        success_count = template.get('success_count', 0)
        
        # Only count templates with test data
        if test_count > 0:
            strategy_combinations[combo_key]['templates'] += 1
            strategy_combinations[combo_key]['tests'] += test_count
            strategy_combinations[combo_key]['successes'] += success_count
    
    # Calculate success rates for each combination
    combo_success_rates = {}
    for combo, data in strategy_combinations.items():
        if data['tests'] > 0:
            success_rate = data['successes'] / data['tests']
            combo_success_rates[combo] = {
                'success_rate': success_rate,
                'tests': data['tests'],
                'templates': data['templates'],
                'successes': data['successes']
            }
    
    return combo_success_rates

def generate_combination_report(combo_success_rates, file_path='strategy_combination_report.txt'):
    """Generate and save strategy combination report"""
    lines = []
    lines.append("==================================================")
    lines.append("       STRATEGY COMBINATION SUCCESS RATE REPORT")
    lines.append("==================================================")
    lines.append(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Sort combinations by success rate (highest first)
    sorted_combos = sorted(combo_success_rates.items(), key=lambda x: x[1]['success_rate'], reverse=True)
    
    lines.append("==================================================")
    lines.append("STRATEGY COMBINATIONS RANKED BY SUCCESS RATE")
    lines.append("==================================================")
    
    # Print each combination's data
    for i, (combo, data) in enumerate(sorted_combos, 1):
        lines.append(f"Rank {i}: Strategy Combination: {combo}")
        lines.append(f"  Success Rate: {data['success_rate']:.2%}")
        lines.append(f"  Templates: {data['templates']}")
        lines.append(f"  Total Tests: {data['tests']}")
        lines.append(f"  Successful Tests: {data['successes']}")
        lines.append("")
    
    # Write to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"Strategy combination report saved to {file_path}")
    return lines

def create_combination_charts(combo_success_rates):
    """Create charts for strategy combinations"""
    # Filter out combinations with very few tests
    min_tests = 5  # Minimum number of tests to be included
    filtered_combos = {k: v for k, v in combo_success_rates.items() if v['tests'] >= min_tests}
    
    if not filtered_combos:
        print("Warning: No combinations have enough tests for meaningful charts")
        return
    
    # Sort combinations by success rate (highest first)
    sorted_combos = sorted(filtered_combos.items(), key=lambda x: x[1]['success_rate'], reverse=True)
    
    # 1. Success Rate Bar Chart (Top 10)
    top_n = min(10, len(sorted_combos))
    top_combos = sorted_combos[:top_n]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Prepare data
    labels = [combo for combo, _ in top_combos]
    rates = [data['success_rate'] * 100 for _, data in top_combos]
    
    # Create bars
    bars = ax.bar(labels, rates, color='skyblue')
    
    # Add labels and title
    ax.set_xlabel('Strategy Combination')
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('Top Strategy Combinations by Success Rate')
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    save_chart(fig, 'top_strategy_combinations')
    plt.close(fig)
    
    # 2. Success Rate vs Test Count Scatter Plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Prepare data
    x = [data['tests'] for _, data in sorted_combos]
    y = [data['success_rate'] * 100 for _, data in sorted_combos]
    labels = [combo for combo, _ in sorted_combos]
    
    # Create scatter plot with varying sizes based on number of templates
    sizes = [data['templates'] * 20 for _, data in sorted_combos]  # Scale for visibility
    scatter = ax.scatter(x, y, s=sizes, alpha=0.6, c=range(len(sorted_combos)), cmap='viridis')
    
    # Add labels for points
    for i, label in enumerate(labels):
        ax.annotate(label,
                    xy=(x[i], y[i]),
                    xytext=(5, 0),
                    textcoords="offset points",
                    fontsize=8)
    
    # Add labels and title
    ax.set_xlabel('Number of Tests')
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('Strategy Combination Success Rate vs Test Count')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Add a colorbar legend
    cbar = plt.colorbar(scatter)
    cbar.set_label('Combination Rank (by Success Rate)')
    
    plt.tight_layout()
    save_chart(fig, 'strategy_combination_scatter')
    plt.close(fig)
    
    # 3. Strategy Impact Chart
    # For each individual strategy, calculate its effect when added to combinations
    strategy_impact = defaultdict(list)
    
    # Find unique individual strategies across all combinations
    all_strategies = set()
    for combo in combo_success_rates.keys():
        strategies = combo.split('+')
        all_strategies.update(strategies)
    
    # For each individual strategy, find combinations with and without it
    for strategy in all_strategies:
        # Combinations that include this strategy
        with_strategy = {k: v for k, v in combo_success_rates.items() 
                         if strategy in k.split('+')}
        
        # Combinations that don't include this strategy
        without_strategy = {k: v for k, v in combo_success_rates.items() 
                           if strategy not in k.split('+')}
        
        # Calculate average success rates
        if with_strategy and without_strategy:
            avg_with = sum(v['success_rate'] * v['tests'] for v in with_strategy.values()) / sum(v['tests'] for v in with_strategy.values())
            avg_without = sum(v['success_rate'] * v['tests'] for v in without_strategy.values()) / sum(v['tests'] for v in without_strategy.values())
            
            impact = avg_with - avg_without
            strategy_impact[strategy] = {
                'with': avg_with, 
                'without': avg_without, 
                'impact': impact,
                'tests_with': sum(v['tests'] for v in with_strategy.values()),
                'tests_without': sum(v['tests'] for v in without_strategy.values())
            }
    
    # Create impact chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Sort strategies by impact
    sorted_impacts = sorted(strategy_impact.items(), key=lambda x: x[1]['impact'], reverse=True)
    
    # Prepare data
    labels = [strategy for strategy, _ in sorted_impacts]
    impacts = [data['impact'] * 100 for _, data in sorted_impacts]
    
    # Create bars
    bars = ax.bar(labels, impacts, color=['green' if i >= 0 else 'red' for i in impacts])
    
    # Add labels and title
    ax.set_xlabel('Strategy')
    ax.set_ylabel('Impact on Success Rate (%)')
    ax.set_title('Impact of Each Strategy on Success Rate')
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.tight_layout()
    save_chart(fig, 'strategy_impact')
    plt.close(fig)

def analyze_triple_strategy_combinations(templates):
    """Analyze the effectiveness of combinations containing exactly three strategies"""
    # Dictionary to store data for triple strategy combinations
    triple_combos = defaultdict(lambda: {'templates': 0, 'tests': 0, 'successes': 0})
    
    # Process each template
    for template in templates:
        # Get the strategy combination
        strategies = template.get('strategies', [])
        
        # Only consider templates with exactly 3 strategies
        if len(strategies) != 3:
            continue
            
        # Sort strategies to ensure consistent combination key
        strategies.sort()
        combo_key = '+'.join(strategies)
        
        # Get test and success counts
        test_count = template.get('test_count', 0)
        success_count = template.get('success_count', 0)
        
        # Only count templates with test data
        if test_count > 0:
            triple_combos[combo_key]['templates'] += 1
            triple_combos[combo_key]['tests'] += test_count
            triple_combos[combo_key]['successes'] += success_count
    
    # Calculate success rates for each triple combination
    triple_success_rates = {}
    for combo, data in triple_combos.items():
        if data['tests'] > 0:
            success_rate = data['successes'] / data['tests']
            triple_success_rates[combo] = {
                'success_rate': success_rate,
                'tests': data['tests'],
                'templates': data['templates'],
                'successes': data['successes']
            }
    
    return triple_success_rates

def analyze_strategy_orders(templates):
    """分析策略顺序的影响"""
    fine_tuned_templates = [t for t in templates if t.get('fine_tuned', False)]
    
    if not fine_tuned_templates:
        print("未找到经过精细调整的模板数据。")
        return {}
    
    print(f"找到 {len(fine_tuned_templates)} 个经过精细调整的模板")
    
    # 按策略组合分组
    strategy_orders = defaultdict(list)
    for template in fine_tuned_templates:
        # 获取策略组合（不考虑顺序）
        strategies = sorted(template.get('strategies', []))
        combo_key = '+'.join(strategies)
        
        # 获取实际使用的顺序
        actual_order = template.get('strategies', [])
        order_key = '+'.join(actual_order)
        
        # 收集性能数据
        permutation_results = template.get('permutation_results', {})
        success_rate = permutation_results.get('success_rate', 0)
        tested_permutations = permutation_results.get('tested_permutations', 0)
        
        strategy_orders[combo_key].append({
            'template_id': template.get('id'),
            'order': actual_order,
            'order_key': order_key,
            'success_rate': success_rate,
            'tested_permutations': tested_permutations
        })
    
    # 分析每种组合的最佳顺序
    best_orders = {}
    for combo, orders in strategy_orders.items():
        # 按成功率排序
        sorted_orders = sorted(orders, key=lambda x: x['success_rate'], reverse=True)
        
        # 计算每种顺序的平均成功率
        order_stats = defaultdict(lambda: {'count': 0, 'total_success_rate': 0, 'templates': []})
        for order in orders:
            order_key = order['order_key']
            order_stats[order_key]['count'] += 1
            order_stats[order_key]['total_success_rate'] += order['success_rate']
            order_stats[order_key]['templates'].append(order['template_id'])
        
        # 计算平均成功率
        for order_key, stats in order_stats.items():
            stats['avg_success_rate'] = stats['total_success_rate'] / stats['count']
        
        # 按平均成功率排序
        sorted_stats = sorted(order_stats.items(), key=lambda x: x[1]['avg_success_rate'], reverse=True)
        
        best_orders[combo] = {
            'best_order': sorted_orders[0]['order'] if sorted_orders else None,
            'best_success_rate': sorted_orders[0]['success_rate'] if sorted_orders else 0,
            'all_orders': sorted_stats
        }
    
    return best_orders

def generate_strategy_order_report(best_orders, file_path='strategy_order_report.txt'):
    """生成策略顺序报告"""
    lines = []
    lines.append("==================================================")
    lines.append("            策略顺序影响分析报告")
    lines.append("==================================================")
    lines.append(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # 按最佳成功率排序
    sorted_combos = sorted(best_orders.items(), key=lambda x: x[1]['best_success_rate'], reverse=True)
    
    for combo, data in sorted_combos:
        lines.append(f"策略组合: {combo}")
        lines.append("--------------------------------------------------")
        lines.append(f"最佳顺序: {'+'.join(data['best_order']) if data['best_order'] else '无数据'}")
        lines.append(f"最佳成功率: {data['best_success_rate']:.2f}")
        lines.append("")
        
        lines.append("所有顺序排名:")
        for i, (order_key, stats) in enumerate(data['all_orders'], 1):
            lines.append(f"  {i}. 顺序: {order_key}")
            lines.append(f"     平均成功率: {stats['avg_success_rate']:.2f}")
            lines.append(f"     模板数量: {stats['count']}")
            lines.append(f"     模板ID: {', '.join(stats['templates'])}")
            lines.append("")
        
        lines.append("==================================================")
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"策略顺序分析报告已保存到 {file_path}")
    return lines

def create_strategy_order_chart(best_orders):
    """为策略顺序创建可视化图表"""
    if not best_orders:
        print("没有足够的数据创建策略顺序图表")
        return
    
    # 只选择有超过一种顺序的组合
    multi_order_combos = {k: v for k, v in best_orders.items() 
                          if len(v['all_orders']) > 1}
    
    if not multi_order_combos:
        print("没有组合有多种顺序，无法创建比较图表")
        return
    
    # 1. 为每个组合创建顺序成功率对比图
    for combo, data in multi_order_combos.items():
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 提取数据
        orders = [order for order, _ in data['all_orders']]
        success_rates = [stats['avg_success_rate'] * 100 for _, stats in data['all_orders']]
        counts = [stats['count'] for _, stats in data['all_orders']]
        
        # 创建条形图
        bars = ax.bar(range(len(orders)), success_rates, color='skyblue')
        
        # 添加标签和标题
        ax.set_xlabel('策略顺序')
        ax.set_ylabel('平均成功率 (%)')
        ax.set_title(f'策略组合 {combo} 的不同顺序成功率')
        ax.set_xticks(range(len(orders)))
        ax.set_xticklabels(orders, rotation=45, ha='right')
        
        # 在条形上添加数值标签
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.annotate(f'{height:.1f}%\n(n={counts[i]})',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        plt.tight_layout()
        safe_combo = combo.replace('+', '_')
        save_chart(fig, f'strategy_order_{safe_combo}')
        plt.close(fig)
    
    # 2. 创建汇总图表，显示所有组合的最佳顺序
    sorted_combos = sorted(best_orders.items(), 
                           key=lambda x: x[1]['best_success_rate'], 
                           reverse=True)[:10]  # 只取前10个
    
    if len(sorted_combos) > 1:
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 提取数据
        combos = [combo for combo, _ in sorted_combos]
        best_orders = ['+'.join(data['best_order']) if data['best_order'] else 'N/A' 
                       for _, data in sorted_combos]
        success_rates = [data['best_success_rate'] * 100 for _, data in sorted_combos]
        
        # 创建条形图
        y_pos = range(len(combos))
        bars = ax.barh(y_pos, success_rates, color='lightgreen')
        
        # 添加标签和标题
        ax.set_yticks(y_pos)
        ax.set_yticklabels(combos)
        ax.set_xlabel('最佳成功率 (%)')
        ax.set_ylabel('策略组合')
        ax.set_title('不同策略组合的最佳顺序成功率')
        
        # 在条形上添加顺序和成功率标签
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.annotate(f'{width:.1f}% - 顺序: {best_orders[i]}',
                       xy=(width, bar.get_y() + bar.get_height()/2),
                       xytext=(5, 0),
                       textcoords="offset points",
                       va='center')
        
        plt.tight_layout()
        save_chart(fig, 'best_strategy_orders')
        plt.close(fig)

def main():
    # Define file path
    if len(sys.argv) > 1:
        template_pool_path = sys.argv[1]
    else:
        template_pool_path = 'data/template_pool.json'
    
    print(f"Analyzing strategy combinations in: {template_pool_path}")
    
    # Load template data
    templates = load_json(template_pool_path)
    if not templates:
        print("Error: Failed to load template data.")
        return
    
    # Analyze all strategy combinations
    combo_success_rates = analyze_strategy_combinations(templates)
    
    if not combo_success_rates:
        print("No strategy combinations found with test data.")
        return
    
    # Generate and save text report
    report_path = f"strategy_combination_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    generate_combination_report(combo_success_rates, report_path)
    
    # Create combination charts
    try:
        create_combination_charts(combo_success_rates)
    except Exception as e:
        print(f"Warning: Could not create combination charts: {e}")
        
    # Analyze triple strategy combinations specifically
    triple_success_rates = analyze_triple_strategy_combinations(templates)
    
    # Generate additional report for triple combinations
    if triple_success_rates:
        triple_report_path = f"triple_strategy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        lines = []
        lines.append("==================================================")
        lines.append("       TRIPLE STRATEGY COMBINATION REPORT")
        lines.append("==================================================")
        lines.append(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Sort combinations by success rate (highest first)
        sorted_triples = sorted(triple_success_rates.items(), key=lambda x: x[1]['success_rate'], reverse=True)
        
        for i, (combo, data) in enumerate(sorted_triples, 1):
            lines.append(f"Rank {i}: Triple Combination: {combo}")
            lines.append(f"  Success Rate: {data['success_rate']:.2%}")
            lines.append(f"  Templates: {data['templates']}")
            lines.append(f"  Total Tests: {data['tests']}")
            lines.append(f"  Successful Tests: {data['successes']}")
            lines.append("")
        
        # Write to file
        with open(triple_report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"Triple strategy combination report saved to {triple_report_path}")
        
        # Create chart for triple combinations
        try:
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Get top triples
            top_n = min(10, len(sorted_triples))
            top_triples = sorted_triples[:top_n]
            
            # Prepare data
            labels = [combo for combo, _ in top_triples]
            rates = [data['success_rate'] * 100 for _, data in top_triples]
            
            # Create bars
            bars = ax.bar(labels, rates, color='lightgreen')
            
            # Add labels and title
            ax.set_xlabel('Triple Strategy Combination')
            ax.set_ylabel('Success Rate (%)')
            ax.set_title('Top Triple Strategy Combinations by Success Rate')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}%',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom')
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            save_chart(fig, 'top_triple_combinations')
            plt.close(fig)
        except Exception as e:
            print(f"Warning: Could not create triple combination chart: {e}")

    # 分析策略顺序
    best_orders = analyze_strategy_orders(templates)
    
    if best_orders:
        order_report_path = f"strategy_order_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        generate_strategy_order_report(best_orders, order_report_path)
        
        try:
            create_strategy_order_chart(best_orders)
        except Exception as e:
            print(f"警告: 无法创建策略顺序图表: {e}")

if __name__ == "__main__":
    main() 