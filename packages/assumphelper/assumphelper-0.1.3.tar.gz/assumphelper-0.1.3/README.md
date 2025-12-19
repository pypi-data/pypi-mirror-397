# AssumHelp
# Overview
This Jupyter notebook provides a comprehensive framework for testing the fundamental assumptions of linear regression models. It implements automated diagnostic tools to check whether your regression model meets the statistical requirements necessary for valid inference and prediction.
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


# Purpose
Linear regression models rely on several key assumptions to produce reliable results. Violations of these assumptions can lead to biased estimates, incorrect standard errors, and unreliable predictions. This notebook provides a systematic approach to:

Test regression assumptions using formal statistical tests
Visualize diagnostic plots to identify assumption violations
Interpret results with clear, actionable guidance
Generate comprehensive reports summarizing all diagnostic findings
# Key Features
# 🧪 Statistical Tests Implemented
Ramsey RESET Test - Tests for linearity assumptions

Breusch-Pagan Test - Tests for homoscedasticity (constant variance)

Shapiro-Wilk Test - Tests for normality of residuals

Durbin-Watson Test - Tests for independence of residuals

# Developers
**[Kirstine Roise G. Moog]** 

Our distinguish Leader &  Inceptionist & Structural Design 

**[Rodel P. Badilla]**

Our Assistant Leader
# Leaders Roles
- Designed clean separation of concerns  
- Implementing codes engine  
- Created visualization tools
- Enhanced plotting capabilities 

**[Hannah Dennisse Y. Aque]**

**[James Walte C. Prollo]**

**[Zell Caamino]**

# Roles

Back (support)
- Built comprehensive test suite  
- Wrote user documentation.
- Quality assurance  

# 📊 Diagnostic Visualizations
Residuals vs Fitted Plot - Linearity and homoscedasticity assessment

Scale-Location Plot - Homoscedasticity verification

Q-Q Plot - Normality assessment

Residuals vs Order Plot - Independence verification

# 🎯 Automated Interpretation
Built-in interpretation guides for all statistical tests
Clear guidance on what to look for in diagnostic plots
Automated result summaries with actionable recommendations
# Architecture
# Core Classes
# Hypothesis (Base Class)
The foundational class that stores regression models and data, providing common functionality for all diagnostic tests.

# Linearity
Purpose: Tests the linearity assumption
Methods: test_linearity(), plot_linearity()
Test: Ramsey RESET test
Plot: Residuals vs Fitted values
# Homoscedasticity
Purpose: Tests for constant variance of residuals
Methods: test_homoscedasticity(), plot_homoscedasticity()
Test: Breusch-Pagan test
Plot: Scale-Location plot
# Normality
Purpose: Tests normality of residuals
Methods: test_normality(), plot_normality()
Test: Shapiro-Wilk test
Plot: Q-Q plot
# Independence
Purpose: Tests independence of residuals
Methods: test_independence(), plot_independence()
Test: Durbin-Watson statistic
Plot: Residuals vs Order plot
# DiagnosticSummary
Purpose: Comprehensive reporting of all diagnostic results
Methods: show_summary()
Features: Consolidated results and interpretations
# Dependencies
import numpy as np
import pandas as pd
import scipy.stats as sp
from scipy.stats import f
import statsmodels.api as sm
import matplotlib.pyplot as plt
import sklearn as sk
import os

# Required packages:

numpy - Numerical computations
pandas - Data manipulation
scipy - Statistical tests
statsmodels - Regression analysis and statistical tests
matplotlib - Plotting and visualization
scikit-learn - Machine learning utilities
# Installation
Install the required packages using pip:

```bash
pip install AssumpHelp
```

# Usage
Basic Workflow
Prepare your data and model

# Your regression model (scikit-learn or similar)
```bash
model = YourRegressionModel()
X = your_features
y = your_target
Initialize diagnostic classes

linearity_test = Linearity(model, X, y)
homoscedasticity_test = Homoscedasticity(model, X, y)
normality_test = Normality(model, X, y)
independence_test = Independence(model, X, y)
Run tests and generate plots

# Test assumptions
linearity_test.test_linearity()
linearity_test.plot_linearity()

homoscedasticity_test.test_homoscedasticity()
homoscedasticity_test.plot_homoscedasticity()

normality_test.test_normality()
normality_test.plot_normality()

independence_test.test_independence()
independence_test.plot_independence()
Generate comprehensive summary

summary = DiagnosticSummary(linearity_test, homoscedasticity_test, 
                          normality_test, independence_test)
summary.show_summary()
```
# Advanced Features
# Feature Scaling
Use the fit_transform() method to standardize features before testing:

linearity_test.fit_transform()
Custom Interpretation
The notebook includes built-in interpretation guides that provide:

Clear explanations of p-value significance,Visual cues for plot interpretation,Actionable recommendations for addressing violations
Statistical Tests Explained
# Ramsey RESET Test
Null Hypothesis: The model is correctly specified (linear)
Alternative Hypothesis: The model is misspecified (non-linear relationships exist)
Interpretation: High p-value (> 0.05) suggests linearity is maintained
# Breusch-Pagan Test
Null Hypothesis: Homoscedasticity (constant variance)
Alternative Hypothesis: Heteroscedasticity (non-constant variance)
Interpretation: High p-value (> 0.05) suggests homoscedasticity is maintained
# Shapiro-Wilk Test
Null Hypothesis: Residuals are normally distributed
Alternative Hypothesis: Residuals are not normally distributed
Interpretation: High p-value (> 0.05) suggests normality is maintained
# Durbin-Watson Test
Range: 0 to 4
Interpretation:
~2.0: No autocorrelation
< 2.0: Positive autocorrelation
2.0: Negative autocorrelation

# Diagnostic Plots Guide
Residuals vs Fitted Plot
Look for: Random scatter around zero
Problem indicators: Patterns, curves, or funnel shapes
Indicates: Linearity and homoscedasticity issues
# Scale-Location Plot
Look for: Horizontal line with random spread
Problem indicators: Increasing/decreasing spread
Indicates: Heteroscedasticity
# Q-Q Plot
Look for: Points following the straight line
Problem indicators: S-shaped curves or deviations at tails
Indicates: Non-normality
# Residuals vs Order Plot
Look for: Random scatter with no patterns
Problem indicators: Trends, cycles, or autocorrelation
Indicates: Independence violations
# Common Issues and Solutions
# Linearity Violations
Solutions: Transform variables, add polynomial terms, use non-linear models
# Heteroscedasticity
Solutions: Transform dependent variable, use weighted least squares, robust standard errors
# Non-Normality
Solutions: Transform variables, increase sample size, use non-parametric methods

# The framework generates:

Statistical test results with test statistics and p-values
Diagnostic plots with interpretation guides
Comprehensive summary consolidating all findings
Actionable recommendations for addressing violations
# Best Practices
Always test assumptions before interpreting regression results
Use multiple diagnostic methods (both tests and plots)
Consider sample size when interpreting test results
Address violations systematically rather than ignoring them
Document all diagnostic procedures for reproducibility
# Limitations
Tests assume sufficient sample size for reliable results
Some tests are sensitive to outliers
Visual interpretation requires experience and judgment
Multiple testing may increase Type I error rates
# Contributing
This framework is designed to be extensible. Common enhancements include:

Additional statistical tests
Custom visualization options
Integration with other modeling frameworks
Automated remediation suggestions
# License
This project is licensed under the MIT License – see the LICENSE file for details.

Note: This diagnostic framework helps ensure the validity of your regression analysis by systematically checking fundamental statistical assumptions. Regular use of these tools will improve the reliability and interpretability of your regression models.
