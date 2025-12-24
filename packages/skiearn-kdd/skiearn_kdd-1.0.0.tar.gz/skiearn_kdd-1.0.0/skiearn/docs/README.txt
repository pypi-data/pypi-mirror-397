# ==========================================================================================
# Knowledge Discovery in Databases (KDD) — Complete Study Guide
# ==========================================================================================

This comprehensive study guide contains EVERY concept, formalism, and test required for 
university-level Knowledge Discovery / Data Mining exams.

## 📚 File Organization (13 Categories)

1. **01_data_preparation.txt**
   - Variable types (nominal, ordinal, interval, ratio)
   - IID assumption
   - Train/validation/test splits
   - Data leakage
   - Curse of dimensionality
   - Bias-variance tradeoff

2. **02_statistics_distributions.txt**
   - Descriptive statistics (mean, median, variance)
   - Skewness and kurtosis
   - Central Limit Theorem
   - Normality tests (Shapiro-Wilk, KS, Anderson-Darling)

3. **03_hypothesis_testing.txt**
   - Z-tests and t-tests
   - ANOVA and Kruskal-Wallis
   - Chi-square and Fisher exact tests
   - Permutation tests and bootstrap
   - Multiple testing corrections

4. **04_causality_features.txt**
   - Correlation vs causation
   - Confounders and Simpson's paradox
   - Causal graphs and backdoor criterion
   - Feature selection methods
   - Multicollinearity (VIF)

5. **05_outliers_robust.txt**
   - Z-score, IQR, and MAD detection
   - Local Outlier Factor (LOF)
   - Isolation Forest
   - Robust scaling
   - Influence on estimators

6. **06_supervised_learning.txt**
   - Linear and logistic regression
   - Ridge and Lasso
   - K-Nearest Neighbors
   - Naive Bayes
   - SVM, Decision Trees, Random Forest
   - Gradient Boosting

7. **07_model_evaluation.txt**
   - Regression metrics (RMSE, MAE, R²)
   - Classification metrics (accuracy, precision, recall, F1)
   - ROC-AUC and PR-AUC
   - Cross-validation techniques
   - Statistical model comparison

8. **08_imbalanced_missing.txt**
   - Class imbalance handling
   - SMOTE and sampling techniques
   - Missing data theory (MCAR, MAR, MNAR)
   - Imputation methods

9. **09_explainability_viz.txt**
   - SHAP and LIME
   - Feature importance
   - Visualization as statistical reasoning
   - Diagnostic plots (residuals, Q-Q, ROC)

10. **10_dimensionality_clustering.txt**
    - PCA and Factor Analysis
    - Kernel PCA and t-SNE
    - K-Means and Hierarchical clustering
    - DBSCAN and Spectral clustering
    - Cluster validation metrics

11. **11_advanced_topics.txt**
    - Time series analysis
    - Concept drift detection
    - Association rule mining
    - Information theory
    - Distance metrics

12. **12_encoding_validation.txt**
    - All encoding techniques (one-hot, ordinal, target, WoE)
    - Validation strategies
    - Data quality checks
    - Target preprocessing

13. **13_exam_traps.txt**
    - Common exam pitfalls
    - Data leakage examples
    - Invalid statistical tests
    - Misinterpreting p-values
    - Preprocessing errors
    - Metric selection mistakes

## 🔧 Required Libraries

pip install numpy pandas scipy scikit-learn matplotlib seaborn statsmodels shap lime imbalanced-learn pingouin scikit-posthocs missingno category_encoders

## 📖 How to Use This Guide

1. **Start with the README** (this file) to understand the structure
2. **Work through files sequentially** for comprehensive coverage
3. **Focus on exam_traps.txt** before the test for common pitfalls
4. **Use as reference** - each file is self-contained with theory + code + interpretation
5. **Practice the code** - all examples are executable and demonstrate concepts

## ⚠️ Important Notes

- NO external or invented abstractions are used
- All code uses official Python APIs
- Each function includes mathematical and Python-specific explanations
- Assumptions and caveats are clearly stated
- Common exam traps are highlighted throughout

## 🎯 Exam Preparation Strategy

1. Review data_preparation.txt for foundational concepts
2. Master hypothesis_testing.txt for statistical inference
3. Understand causality_features.txt for proper interpretation
4. Study model_evaluation.txt for performance assessment
5. Memorize exam_traps.txt to avoid common mistakes

## 📝 Legend

- TYPICAL EXAM TRAP: Highlighted pitfalls
- INTERPRET: How to read results
- NULL HYPOTHESIS: Statistical test assumptions
- ASSUMPTION: Required conditions
- PITFALL: Common mistakes

Good luck with your KDD exam! 🎓
