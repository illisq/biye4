import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from collections import Counter
import os

# Create directory for output charts if it doesn't exist
os.makedirs('analysis_charts', exist_ok=True)

# Load the JSON files
with open('data/origin_template_pool.json', 'r', encoding='utf-8') as f:
    origin_templates = json.load(f)

with open('data/template_pool.json', 'r', encoding='utf-8') as f:
    templates = json.load(f)

# Extract data for visualization
def extract_template_data(templates):
    strategies = []
    base_types = []
    success_rates = []
    success_counts = []
    test_counts = []
    
    for template in templates:
        # Extract strategies
        template_strategies = template.get('strategies', [])
        strategies.extend(template_strategies)
        
        # Extract base type
        base_type = template.get('base_type', 'unknown')
        base_types.append(base_type)
        
        # Calculate success rate
        test_count = template.get('test_count', 0)
        success_count = template.get('success_count', 0)
        test_counts.append(test_count)
        success_counts.append(success_count)
        
        if test_count > 0:
            success_rate = (success_count / test_count) * 100
        else:
            success_rate = 0
            
        success_rates.append(success_rate)
    
    return {
        'strategies': strategies,
        'base_types': base_types,
        'success_rates': success_rates,
        'success_counts': success_counts,
        'test_counts': test_counts
    }

origin_data = extract_template_data(origin_templates)
template_data = extract_template_data(templates)

# 1. Create a combined pie chart comparison of base types
plt.figure(figsize=(14, 7))

plt.subplot(1, 2, 1)
origin_base_counts = Counter(origin_data['base_types'])
plt.pie([origin_base_counts[t] for t in sorted(origin_base_counts.keys())], 
        labels=[f"{t}\n({origin_base_counts[t]})" for t in sorted(origin_base_counts.keys())],
        autopct='%1.1f%%', shadow=True, startangle=90, colors=sns.color_palette("pastel"))
plt.title('Original Template Base Types')

plt.subplot(1, 2, 2)
template_base_counts = Counter(template_data['base_types'])
plt.pie([template_base_counts[t] for t in sorted(template_base_counts.keys())], 
        labels=[f"{t}\n({template_base_counts[t]})" for t in sorted(template_base_counts.keys())],
        autopct='%1.1f%%', shadow=True, startangle=90, colors=sns.color_palette("pastel"))
plt.title('New Template Base Types')

plt.suptitle('Comparison of Template Base Type Distribution', fontsize=16)
plt.tight_layout()
plt.savefig('analysis_charts/base_type_pie_comparison.png')
plt.close()

# 2. Create a box plot to compare success rates by base type
plt.figure(figsize=(14, 8))

# Organize data for box plots
origin_base_types = origin_data['base_types']
origin_success_rates = origin_data['success_rates']

template_base_types = template_data['base_types']
template_success_rates = template_data['success_rates']

# Combine data for plotting
plot_data = pd.DataFrame({
    'Base Type': origin_base_types + template_base_types,
    'Success Rate': origin_success_rates + template_success_rates,
    'Source': ['Original'] * len(origin_base_types) + ['New'] * len(template_base_types)
})

# Create the box plot
sns.boxplot(x='Base Type', y='Success Rate', hue='Source', data=plot_data)

plt.title('Success Rate Distribution by Base Type')
plt.ylabel('Success Rate (%)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('analysis_charts/success_rate_boxplot.png')
plt.close()

# 3. Create a scatter plot showing relationship between test count and success rate
plt.figure(figsize=(14, 8))

# Combine data
scatter_data = pd.DataFrame({
    'Test Count': origin_data['test_counts'] + template_data['test_counts'],
    'Success Count': origin_data['success_counts'] + template_data['success_counts'],
    'Success Rate': origin_data['success_rates'] + template_data['success_rates'],
    'Source': ['Original'] * len(origin_data['test_counts']) + ['New'] * len(template_data['test_counts']),
    'Base Type': origin_data['base_types'] + template_data['base_types']
})

# Add size column for scatter plotting (size based on test count)
scatter_data['size'] = scatter_data['Test Count'] * 5

# Create the scatter plot
plt.figure(figsize=(14, 8))
sns.scatterplot(
    x='Test Count', 
    y='Success Rate', 
    hue='Source',
    style='Base Type',
    size='Test Count',
    sizes=(20, 200),
    alpha=0.7,
    data=scatter_data
)

plt.title('Relationship Between Test Count and Success Rate')
plt.ylabel('Success Rate (%)')
plt.xlabel('Number of Tests')
plt.grid(linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('analysis_charts/test_count_vs_success_rate.png')
plt.close()

# 4. Create a heatmap of strategy combinations and success rates
def get_strategy_combinations(templates):
    strategy_combinations = []
    success_rates_by_combo = {}
    
    for template in templates:
        strategies = sorted(template.get('strategies', []))
        if not strategies:
            continue
            
        combo = '+'.join(strategies)
        strategy_combinations.append(combo)
        
        # Track success rate for this combination
        test_count = template.get('test_count', 0)
        success_count = template.get('success_count', 0)
        
        if combo not in success_rates_by_combo:
            success_rates_by_combo[combo] = {'tests': 0, 'successes': 0}
            
        success_rates_by_combo[combo]['tests'] += test_count
        success_rates_by_combo[combo]['successes'] += success_count
    
    # Calculate average success rate for each combination
    for combo in success_rates_by_combo:
        if success_rates_by_combo[combo]['tests'] > 0:
            success_rates_by_combo[combo]['rate'] = (
                success_rates_by_combo[combo]['successes'] / 
                success_rates_by_combo[combo]['tests'] * 100
            )
        else:
            success_rates_by_combo[combo]['rate'] = 0
    
    return Counter(strategy_combinations), success_rates_by_combo

# Get strategy combinations for both template sets
origin_combos, origin_combo_rates = get_strategy_combinations(origin_templates)
template_combos, template_combo_rates = get_strategy_combinations(templates)

# Combine data for a comparison bar chart
all_combos = sorted(set(list(origin_combos.keys()) + list(template_combos.keys())))
combo_data = pd.DataFrame({
    'Strategy Combination': all_combos,
    'Original Count': [origin_combos.get(combo, 0) for combo in all_combos],
    'New Count': [template_combos.get(combo, 0) for combo in all_combos],
    'Original Success Rate': [origin_combo_rates.get(combo, {'rate': 0})['rate'] for combo in all_combos],
    'New Success Rate': [template_combo_rates.get(combo, {'rate': 0})['rate'] for combo in all_combos]
})

# Only show combinations that appear at least once in either template set
combo_data = combo_data[(combo_data['Original Count'] > 0) | (combo_data['New Count'] > 0)]

# Sort by total count (original + new)
combo_data['Total Count'] = combo_data['Original Count'] + combo_data['New Count']
combo_data = combo_data.sort_values(by='Total Count', ascending=False).head(10)  # Top 10 combinations

# Create bar chart for strategy combinations
plt.figure(figsize=(14, 8))
combo_data[['Strategy Combination', 'Original Count', 'New Count']].set_index('Strategy Combination').plot(
    kind='bar', figsize=(14, 8)
)
plt.title('Top 10 Strategy Combinations')
plt.ylabel('Number of Templates')
plt.xlabel('Strategy Combination')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('analysis_charts/strategy_combinations.png')
plt.close()

# Create a bar chart for success rates of strategy combinations
plt.figure(figsize=(14, 8))
combo_data[['Strategy Combination', 'Original Success Rate', 'New Success Rate']].set_index('Strategy Combination').plot(
    kind='bar', figsize=(14, 8)
)
plt.title('Success Rates of Top 10 Strategy Combinations')
plt.ylabel('Success Rate (%)')
plt.xlabel('Strategy Combination')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('analysis_charts/strategy_combination_success_rates.png')
plt.close()

print("Analysis charts generated successfully in the 'analysis_charts' directory.") 