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

def save_chart(fig, filename, charts_dir='comparison_charts'):
    """Save chart to file"""
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    full_path = os.path.join(charts_dir, f"{filename}_{timestamp}.png")
    fig.savefig(full_path, bbox_inches='tight', dpi=300)
    print(f"Chart saved to {full_path}")

def analyze_templates(templates):
    """Analyze template data and generate statistics"""
    # Basic statistics
    total_templates = len(templates)
    
    # Count templates with test data
    tested_templates = [t for t in templates if t.get('test_count', 0) > 0]
    total_tested = len(tested_templates)
    
    # Summarize test data
    total_tests = sum(t.get('test_count', 0) for t in templates)
    total_successes = sum(t.get('success_count', 0) for t in templates)
    
    # Calculate overall success rate
    overall_success_rate = total_successes / total_tests if total_tests > 0 else 0
    
    # Create counters for different aspects
    base_type_counts = Counter()
    original_id_counts = Counter()
    question_id_counts = Counter()
    strategies_counts = Counter()
    
    # Statistics for strategy success rates
    strategy_success = defaultdict(lambda: {'tests': 0, 'successes': 0})
    base_type_success = defaultdict(lambda: {'tests': 0, 'successes': 0})
    
    # Collect success rate data for distribution analysis
    success_rates = []
    
    # Process each template
    for template in templates:
        # Basic type statistics
        base_type = template.get('base_type', 'unknown')
        base_type_counts[base_type] += 1
        
        # Original ID statistics
        original_id = template.get('original_id', 'unknown')
        original_id_counts[original_id] += 1
        
        # Question ID statistics
        question_id = template.get('question_id', 'unknown')
        question_id_counts[question_id] += 1
        
        # Strategy statistics
        strategies = template.get('strategies', [])
        for strategy in strategies:
            strategies_counts[strategy] += 1
        
        # Test and success data
        test_count = template.get('test_count', 0)
        success_count = template.get('success_count', 0)
        
        # Only process templates with test data
        if test_count > 0:
            # Calculate success rate
            success_rate = success_count / test_count
            success_rates.append((template['id'], success_rate, test_count))
            
            # Update strategy success rate statistics
            for strategy in strategies:
                strategy_success[strategy]['tests'] += test_count
                strategy_success[strategy]['successes'] += success_count
            
            # Update basic type success rate statistics
            base_type_success[base_type]['tests'] += test_count
            base_type_success[base_type]['successes'] += success_count
    
    # Sort success rates, find highest and lowest
    success_rates.sort(key=lambda x: x[1], reverse=True)
    top_templates = success_rates[:10]  # Top 10 highest
    bottom_templates = success_rates[-10:]  # Bottom 10 lowest
    
    # Calculate strategy success rates
    strategy_success_rates = {
        strategy: data['successes'] / data['tests'] if data['tests'] > 0 else 0
        for strategy, data in strategy_success.items()
    }
    
    # Calculate basic type success rates
    base_type_success_rates = {
        base_type: data['successes'] / data['tests'] if data['tests'] > 0 else 0
        for base_type, data in base_type_success.items()
    }
    
    # Generate result report
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

def compare_reports(report1, report2):
    """Compare two analysis reports and generate comparison data"""
    comparison = {}
    
    # Compare basic stats
    basic_diff = {}
    for key in report1['basic_stats']:
        val1 = report1['basic_stats'][key]
        val2 = report2['basic_stats'][key]
        
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            diff = val2 - val1
            pct_change = ((val2 / val1) - 1) * 100 if val1 != 0 else float('inf')
            basic_diff[key] = {
                'original': val1,
                'current': val2,
                'diff': diff,
                'pct_change': pct_change
            }
    
    comparison['basic_stats'] = basic_diff
    
    # Compare base type counts
    base_type_diff = {}
    all_base_types = set(report1['base_type_counts'].keys()) | set(report2['base_type_counts'].keys())
    
    for base_type in all_base_types:
        val1 = report1['base_type_counts'].get(base_type, 0)
        val2 = report2['base_type_counts'].get(base_type, 0)
        
        diff = val2 - val1
        pct_change = ((val2 / val1) - 1) * 100 if val1 != 0 else float('inf')
        base_type_diff[base_type] = {
            'original': val1,
            'current': val2,
            'diff': diff,
            'pct_change': pct_change
        }
    
    comparison['base_type_counts'] = base_type_diff
    
    # Compare strategy counts
    strategy_diff = {}
    all_strategies = set(report1['strategies_counts'].keys()) | set(report2['strategies_counts'].keys())
    
    for strategy in all_strategies:
        val1 = report1['strategies_counts'].get(strategy, 0)
        val2 = report2['strategies_counts'].get(strategy, 0)
        
        diff = val2 - val1
        pct_change = ((val2 / val1) - 1) * 100 if val1 != 0 else float('inf')
        strategy_diff[strategy] = {
            'original': val1,
            'current': val2,
            'diff': diff,
            'pct_change': pct_change
        }
    
    comparison['strategies_counts'] = strategy_diff
    
    # Compare strategy success rates
    strategy_rate_diff = {}
    all_strategies = set(report1['strategy_success_rates'].keys()) | set(report2['strategy_success_rates'].keys())
    
    for strategy in all_strategies:
        val1 = report1['strategy_success_rates'].get(strategy, 0)
        val2 = report2['strategy_success_rates'].get(strategy, 0)
        
        diff = val2 - val1
        pct_change = ((val2 / val1) - 1) * 100 if val1 != 0 else float('inf')
        strategy_rate_diff[strategy] = {
            'original': val1,
            'current': val2,
            'diff': diff,
            'pct_change': pct_change
        }
    
    comparison['strategy_success_rates'] = strategy_rate_diff
    
    # Compare base type success rates
    base_type_rate_diff = {}
    all_base_types = set(report1['base_type_success_rates'].keys()) | set(report2['base_type_success_rates'].keys())
    
    for base_type in all_base_types:
        val1 = report1['base_type_success_rates'].get(base_type, 0)
        val2 = report2['base_type_success_rates'].get(base_type, 0)
        
        diff = val2 - val1
        pct_change = ((val2 / val1) - 1) * 100 if val1 != 0 else float('inf')
        base_type_rate_diff[base_type] = {
            'original': val1,
            'current': val2,
            'diff': diff,
            'pct_change': pct_change
        }
    
    comparison['base_type_success_rates'] = base_type_rate_diff
    
    return comparison

def generate_comparison_text(comparison, file_path='template_comparison_report.txt'):
    """Generate and save comparison text report"""
    lines = []
    lines.append("==================================================")
    lines.append("       TEMPLATE POOL COMPARISON REPORT")
    lines.append("==================================================")
    lines.append(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Basic statistics comparison
    lines.append("==================================================")
    lines.append("BASIC STATISTICS COMPARISON")
    lines.append("==================================================")
    
    for key, data in comparison['basic_stats'].items():
        # Format the key for better readability
        formatted_key = key.replace('_', ' ').title()
        
        # Format percentage values
        if 'rate' in key.lower():
            original_val = f"{data['original']:.2%}"
            current_val = f"{data['current']:.2%}"
            diff_val = f"{data['diff']:.2%}"
        else:
            original_val = f"{data['original']}"
            current_val = f"{data['current']}"
            diff_val = f"{data['diff']}"
            
        # Add comparison information
        lines.append(f"{formatted_key}:")
        lines.append(f"  Original: {original_val}")
        lines.append(f"  Current:  {current_val}")
        lines.append(f"  Change:   {diff_val} ({data['pct_change']:.2f}%)")
        lines.append("")
    
    # Base type counts comparison
    lines.append("==================================================")
    lines.append("BASE TYPE DISTRIBUTION COMPARISON")
    lines.append("==================================================")
    
    for base_type, data in sorted(comparison['base_type_counts'].items(), 
                                 key=lambda x: abs(x[1]['diff']), reverse=True):
        lines.append(f"Base Type: {base_type}")
        lines.append(f"  Original: {data['original']} templates")
        lines.append(f"  Current:  {data['current']} templates")
        lines.append(f"  Change:   {data['diff']} templates ({data['pct_change']:.2f}%)")
        lines.append("")
    
    # Strategy counts comparison
    lines.append("==================================================")
    lines.append("STRATEGY USAGE COMPARISON")
    lines.append("==================================================")
    
    for strategy, data in sorted(comparison['strategies_counts'].items(), 
                               key=lambda x: abs(x[1]['diff']), reverse=True):
        lines.append(f"Strategy: {strategy}")
        lines.append(f"  Original: {data['original']} templates")
        lines.append(f"  Current:  {data['current']} templates")
        lines.append(f"  Change:   {data['diff']} templates ({data['pct_change']:.2f}%)")
        lines.append("")
    
    # Strategy success rates comparison
    lines.append("==================================================")
    lines.append("STRATEGY SUCCESS RATE COMPARISON")
    lines.append("==================================================")
    
    for strategy, data in sorted(comparison['strategy_success_rates'].items(), 
                               key=lambda x: abs(x[1]['diff']), reverse=True):
        lines.append(f"Strategy: {strategy}")
        lines.append(f"  Original: {data['original']:.2%}")
        lines.append(f"  Current:  {data['current']:.2%}")
        lines.append(f"  Change:   {data['diff']:.2%} ({data['pct_change']:.2f}%)")
        lines.append("")
    
    # Base type success rates comparison
    lines.append("==================================================")
    lines.append("BASE TYPE SUCCESS RATE COMPARISON")
    lines.append("==================================================")
    
    for base_type, data in sorted(comparison['base_type_success_rates'].items(), 
                               key=lambda x: abs(x[1]['diff']), reverse=True):
        lines.append(f"Base Type: {base_type}")
        lines.append(f"  Original: {data['original']:.2%}")
        lines.append(f"  Current:  {data['current']:.2%}")
        lines.append(f"  Change:   {data['diff']:.2%} ({data['pct_change']:.2f}%)")
        lines.append("")
    
    # Write to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"Comparison report saved to {file_path}")
    return lines

def create_comparison_charts(report1, report2, comparison):
    """Create comparison charts"""
    # Set plot style
    plt.style.use('ggplot')
    
    # 1. Basic stats comparison chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Filter only numeric values
    numeric_stats = {k: v for k, v in comparison['basic_stats'].items() 
                    if isinstance(v['original'], (int, float)) and k != 'overall_success_rate'}
    
    # Prepare data
    labels = [k.replace('_', ' ').title() for k in numeric_stats.keys()]
    orig_values = [v['original'] for v in numeric_stats.values()]
    curr_values = [v['current'] for v in numeric_stats.values()]
    
    # Set positions
    x = np.arange(len(labels))
    width = 0.35
    
    # Create bars
    rects1 = ax.bar(x - width/2, orig_values, width, label='Original', color='skyblue')
    rects2 = ax.bar(x + width/2, curr_values, width, label='Current', color='lightcoral')
    
    # Add labels and title
    ax.set_xlabel('Metric')
    ax.set_ylabel('Count')
    ax.set_title('Basic Statistics Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    
    # Add value labels
    for rect in rects1 + rects2:
        height = rect.get_height()
        ax.annotate(f'{height}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    plt.tight_layout()
    save_chart(fig, 'basic_stats_comparison')
    plt.close(fig)
    
    # 2. Success Rate Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    
    orig_rate = report1['basic_stats']['overall_success_rate'] * 100
    curr_rate = report2['basic_stats']['overall_success_rate'] * 100
    
    bars = ax.bar(['Original', 'Current'], [orig_rate, curr_rate], color=['skyblue', 'lightcoral'])
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('Overall Success Rate Comparison')
    plt.tight_layout()
    save_chart(fig, 'success_rate_comparison')
    plt.close(fig)
    
    # 3. Base Type Count Comparison
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Get all base types from both reports
    all_base_types = sorted(set(report1['base_type_counts'].keys()) | set(report2['base_type_counts'].keys()))
    
    # Prepare data
    orig_values = [report1['base_type_counts'].get(bt, 0) for bt in all_base_types]
    curr_values = [report2['base_type_counts'].get(bt, 0) for bt in all_base_types]
    
    # Set positions
    x = np.arange(len(all_base_types))
    width = 0.35
    
    # Create bars
    rects1 = ax.bar(x - width/2, orig_values, width, label='Original', color='skyblue')
    rects2 = ax.bar(x + width/2, curr_values, width, label='Current', color='lightcoral')
    
    # Add labels and title
    ax.set_xlabel('Base Type')
    ax.set_ylabel('Count')
    ax.set_title('Base Type Distribution Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(all_base_types)
    ax.legend()
    
    # Add value labels
    for rect in rects1 + rects2:
        height = rect.get_height()
        if height > 0:  # Only add label if bar has height
            ax.annotate(f'{height}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
    
    plt.tight_layout()
    save_chart(fig, 'base_type_comparison')
    plt.close(fig)
    
    # 4. Strategy Success Rate Comparison
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Get all strategies from both reports
    all_strategies = sorted(set(report1['strategy_success_rates'].keys()) | set(report2['strategy_success_rates'].keys()))
    
    # Prepare data
    orig_values = [report1['strategy_success_rates'].get(s, 0) * 100 for s in all_strategies]
    curr_values = [report2['strategy_success_rates'].get(s, 0) * 100 for s in all_strategies]
    
    # Set positions
    x = np.arange(len(all_strategies))
    width = 0.35
    
    # Create bars
    rects1 = ax.bar(x - width/2, orig_values, width, label='Original', color='skyblue')
    rects2 = ax.bar(x + width/2, curr_values, width, label='Current', color='lightcoral')
    
    # Add labels and title
    ax.set_xlabel('Strategy')
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('Strategy Success Rate Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(all_strategies)
    ax.legend()
    
    # Add value labels
    for rect in rects1 + rects2:
        height = rect.get_height()
        if height > 0:  # Only add label if bar has height
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
    
    plt.tight_layout()
    save_chart(fig, 'strategy_success_rate_comparison')
    plt.close(fig)
    
    # 5. Base Type Success Rate Comparison
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Get all base types from both reports
    all_base_types = sorted(set(report1['base_type_success_rates'].keys()) | set(report2['base_type_success_rates'].keys()))
    
    # Prepare data
    orig_values = [report1['base_type_success_rates'].get(bt, 0) * 100 for bt in all_base_types]
    curr_values = [report2['base_type_success_rates'].get(bt, 0) * 100 for bt in all_base_types]
    
    # Set positions
    x = np.arange(len(all_base_types))
    width = 0.35
    
    # Create bars
    rects1 = ax.bar(x - width/2, orig_values, width, label='Original', color='skyblue')
    rects2 = ax.bar(x + width/2, curr_values, width, label='Current', color='lightcoral')
    
    # Add labels and title
    ax.set_xlabel('Base Type')
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('Base Type Success Rate Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(all_base_types)
    ax.legend()
    
    # Add value labels
    for rect in rects1 + rects2:
        height = rect.get_height()
        if height > 0:  # Only add label if bar has height
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
    
    plt.tight_layout()
    save_chart(fig, 'base_type_success_rate_comparison')
    plt.close(fig)

def main():
    # Define file paths
    original_path = 'data/origin_template_pool.json'
    current_path = 'data/template_pool.json'
    
    print(f"Comparing template pools:")
    print(f"Original: {original_path}")
    print(f"Current: {current_path}")
    
    # Load template data
    original_templates = load_json(original_path)
    current_templates = load_json(current_path)
    
    if not original_templates or not current_templates:
        print("Error: Failed to load template data.")
        return
    
    # Analyze templates
    original_report = analyze_templates(original_templates)
    current_report = analyze_templates(current_templates)
    
    # Compare reports
    comparison = compare_reports(original_report, current_report)
    
    # Generate and save text report
    report_path = f"template_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    generate_comparison_text(comparison, report_path)
    
    # Create comparison charts
    try:
        create_comparison_charts(original_report, current_report, comparison)
    except Exception as e:
        print(f"Warning: Could not create comparison charts: {e}")

if __name__ == "__main__":
    main() 