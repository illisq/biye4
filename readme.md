# LLM Fuzzing Test Framework

A comprehensive framework for testing and evaluating Large Language Models (LLMs) through various fuzzing strategies and template-based testing.

## Overview

This project implements a sophisticated testing framework for LLMs that combines multiple testing strategies including hallucination detection, jailbreak attempts, and consistency checking. The framework uses template-based testing and can analyze the effectiveness of different testing strategies and their combinations.

## Project Structure

```
├── main.py                 # Main execution script
├── test_api.py            # API testing utilities
├── test_templates.py      # Template testing implementation
├── analyze_templates.py   # Template analysis tools
├── compare_templates.py   # Template comparison functionality
├── analyze_strategy_combinations.py  # Strategy combination analysis
├── charting_script.py     # Chart generation for analysis
├── clearer_chart_script.py # Enhanced chart visualization
├── utils.py              # Utility functions
├── strategies/           # Testing strategy implementations
│   ├── hallucination.py
│   ├── jailbreak.py
│   └── consistency.py
├── data/                 # Data directory
│   ├── questions_pool.json
│   └── template_pool.json
├── log/                  # Log files
├── analysis_charts/      # Analysis visualization
├── comparison_charts/    # Comparison results
├── strategy_charts/      # Strategy analysis charts
└── clearer_charts/       # Enhanced visualization charts
```

## Features

- Multiple testing strategies:
  - Hallucination detection
  - Jailbreak attempts
  - Consistency checking
- Template-based testing system
- Strategy combination analysis
- Automated reporting and visualization
- Comprehensive logging system
- Performance metrics tracking

## Prerequisites

- Python 3.x
- Required packages (see requirements.txt):
  - python-dotenv
  - Other dependencies listed in requirements.txt

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your LLM API key:
   ```
   LLM_API_KEY=your_api_key_here
   ```

## Usage

### Running Tests

1. Basic test execution:
   ```bash
   python main.py
   ```

2. Template testing:
   ```bash
   python test_templates.py
   ```

3. Strategy analysis:
   ```bash
   python analyze_strategy_combinations.py
   ```

### Analysis and Visualization

- Generate analysis charts:
  ```bash
  python charting_script.py
  ```

- Generate enhanced visualizations:
  ```bash
  python clearer_chart_script.py
  ```

## Output

The framework generates several types of outputs:
- Test logs in the `log/` directory
- Analysis charts in `analysis_charts/`
- Comparison results in `comparison_charts/`
- Strategy analysis in `strategy_charts/`
- Enhanced visualizations in `clearer_charts/`

## Contributing

Feel free to submit issues and enhancement requests.

