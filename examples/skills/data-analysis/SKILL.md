---
name: data-analysis
description: Analyze datasets, create visualizations, and perform statistical analysis using Python data science libraries. Use for data exploration, cleaning, and insights.
license: Apache 2.0
---

# Data Analysis Skill

This skill provides comprehensive data analysis capabilities using Python's data science ecosystem.

## Core Capabilities

### Data Loading and Cleaning
- Load data from various formats (CSV, JSON, Excel, databases)
- Handle missing values and data type conversions
- Detect and remove duplicates
- Data validation and quality checks

### Exploratory Data Analysis
- Generate descriptive statistics
- Create data distributions and histograms
- Correlation analysis
- Outlier detection

### Data Visualization
- Create plots with matplotlib and seaborn
- Interactive visualizations with plotly
- Statistical plots (box plots, scatter plots, heatmaps)
- Time series visualizations

### Statistical Analysis
- Hypothesis testing
- Regression analysis
- Classification and clustering
- Time series analysis

## Required Libraries

```python
pip install pandas numpy matplotlib seaborn scipy scikit-learn plotly
```

## Quick Start Examples

### Load and Explore Data
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('data.csv')

# Basic info
print(df.info())
print(df.describe())

# Check for missing values
print(df.isnull().sum())
```

### Create Visualizations
```python
# Distribution plot
plt.figure(figsize=(10, 6))
sns.histplot(df['column_name'], bins=30)
plt.title('Distribution of Column')
plt.show()

# Correlation heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
plt.title('Correlation Matrix')
plt.show()
```

### Statistical Analysis
```python
from scipy import stats

# T-test
group1 = df[df['category'] == 'A']['value']
group2 = df[df['category'] == 'B']['value']
t_stat, p_value = stats.ttest_ind(group1, group2)
print(f"T-statistic: {t_stat}, P-value: {p_value}")
```

## Best Practices

1. Always explore data structure and quality first
2. Handle missing values appropriately for your analysis
3. Validate assumptions before applying statistical tests
4. Use appropriate visualizations for your data types
5. Document your analysis process and findings
