"""
Interactive documentation viewer for skiearn package
"""

import os
import sys
from pathlib import Path

# Save reference to built-in print before it gets shadowed
_print = print

# Define all documentation files with descriptions
DOCS = {
    '1': {
        'file': '01_data_preparation.txt',
        'title': 'Data Preparation & Formalism',
        'topics': 'Variable types, IID, splits, leakage, dimensionality, bias-variance'
    },
    '2': {
        'file': '02_statistics_distributions.txt',
        'title': 'Statistics & Distributions',
        'topics': 'Mean/median/variance, skewness/kurtosis, normality tests'
    },
    '3': {
        'file': '03_hypothesis_testing.txt',
        'title': 'Hypothesis Testing',
        'topics': 'Z-tests, t-tests, ANOVA, Chi-square, permutation tests, bootstrap'
    },
    '4': {
        'file': '04_causality_features.txt',
        'title': 'Causality & Feature Selection',
        'topics': 'Causality, confounders, Simpson\'s paradox, feature selection'
    },
    '5': {
        'file': '05_outliers_robust.txt',
        'title': 'Outliers & Robust Statistics',
        'topics': 'Z-score, IQR, MAD, LOF, Isolation Forest, robust scaling'
    },
    '6': {
        'file': '06_supervised_learning.txt',
        'title': 'Supervised Learning',
        'topics': 'Linear/logistic regression, Ridge, Lasso, KNN, SVM, Trees, Forests'
    },
    '7': {
        'file': '07_model_evaluation.txt',
        'title': 'Model Evaluation & Comparison',
        'topics': 'Metrics, ROC-AUC, PR-AUC, cross-validation, model comparison'
    },
    '8': {
        'file': '08_imbalanced_missing.txt',
        'title': 'Imbalanced & Missing Data',
        'topics': 'SMOTE, sampling, MCAR/MAR/MNAR, imputation methods'
    },
    '9': {
        'file': '09_explainability_viz.txt',
        'title': 'Explainability & Visualization',
        'topics': 'SHAP, LIME, all visualization techniques, diagnostic plots'
    },
    '10': {
        'file': '10_dimensionality_clustering.txt',
        'title': 'Dimensionality & Clustering',
        'topics': 'PCA, t-SNE, K-Means, Hierarchical, DBSCAN, cluster validation'
    },
    '11': {
        'file': '11_advanced_topics.txt',
        'title': 'Advanced Topics',
        'topics': 'Time series, association rules, information theory, probability'
    },
    '12': {
        'file': '12_encoding_validation.txt',
        'title': 'Encoding & Validation',
        'topics': 'All encoding techniques, validation strategies, data quality'
    },
    '13': {
        'file': '13_exam_traps.txt',
        'title': 'Exam Traps & Pitfalls ⚠️',
        'topics': 'Common mistakes, data leakage, invalid tests, preprocessing errors'
    },
    'r': {
        'file': 'README.txt',
        'title': 'README - Study Guide Overview',
        'topics': 'Structure, file organization, study strategy'
    },
    's': {
        'file': 'STUDY_GUIDE.txt',
        'title': 'Study Guide - Recommended Path',
        'topics': 'Week-by-week study plan, quick tips'
    },
    'v': {
        'file': 'VERIFICATION_COMPLETE.txt',
        'title': 'Verification Document',
        'topics': 'Complete section mapping, verification that nothing was missed'
    }
}


def get_docs_dir():
    """Get the documentation directory path"""
    return Path(__file__).parent / 'docs'


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_menu():
    """Display the interactive menu"""
    _print("=" * 80)
    _print(" " * 20 + "SKIEARN DOCUMENTATION VIEWER")
    _print(" " * 15 + "Knowledge Discovery & Data Mining Study Guide")
    _print("=" * 80)
    _print()
    
    # Print main documentation files
    _print("📚 MAIN DOCUMENTATION:")
    for key in sorted([k for k in DOCS.keys() if k.isdigit()], key=int):
        doc = DOCS[key]
        _print(f"  [{key:>2}] {doc['title']}")
        _print(f"      └─ {doc['topics']}")
        _print()
    
    # Print additional resources
    _print("📖 ADDITIONAL RESOURCES:")
    for key in ['r', 's', 'v']:
        doc = DOCS[key]
        _print(f"  [{key.upper()}] {doc['title']}")
        _print(f"      └─ {doc['topics']}")
        _print()
    
    _print("=" * 80)
    _print("  [A] View ALL files sequentially")
    _print("  [Q] Quit")
    _print("=" * 80)


def read_file(filename):
    """Read and return file contents"""
    docs_dir = get_docs_dir()
    filepath = docs_dir / filename
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"❌ Error: File '{filename}' not found in {docs_dir}"
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"


def display_file(key):
    """Display the contents of a selected file"""
    if key not in DOCS:
        _print("\n❌ Invalid selection. Please try again.\n")
        return
    
    doc = DOCS[key]
    clear_screen()
    
    _print("=" * 80)
    _print(f" {doc['title']}")
    _print("=" * 80)
    _print(f"File: {doc['file']}")
    _print(f"Topics: {doc['topics']}")
    _print("=" * 80)
    _print()
    
    content = read_file(doc['file'])
    _print(content)
    
    _print()
    _print("=" * 80)
    _print("End of file")
    _print("=" * 80)


def view_all_files():
    """View all main documentation files sequentially"""
    clear_screen()
    _print("📚 Viewing ALL documentation files...\n")
    
    for key in sorted([k for k in DOCS.keys() if k.isdigit()], key=int):
        doc = DOCS[key]
        _print("\n" + "=" * 80)
        _print(f" [{key}] {doc['title']}")
        _print("=" * 80)
        _print(f"File: {doc['file']}")
        _print("=" * 80)
        _print()
        
        content = read_file(doc['file'])
        _print(content)
        
        _print("\n" + "=" * 80)
        _print(f"End of {doc['file']}")
        _print("=" * 80)
        
        if key != '13':  # Don't prompt after last file
            response = input("\nPress ENTER to continue to next file, or 'Q' to return to menu: ")
            if response.lower() == 'q':
                return
            clear_screen()


def print():
    """Main entry point - Display interactive documentation viewer"""
    try:
        while True:
            clear_screen()
            print_menu()
            
            choice = input("\n📖 Enter your choice: ").strip().lower()
            
            if choice == 'q':
                clear_screen()
                _print("\n✅ Thank you for using SKIEARN Documentation!")
                _print("Good luck with your KDD exam! 🎓\n")
                break
            
            elif choice == 'a':
                view_all_files()
                input("\n\nPress ENTER to return to menu...")
            
            elif choice in DOCS:
                display_file(choice)
                input("\n\nPress ENTER to return to menu...")
            
            else:
                _print("\n❌ Invalid choice. Please try again.")
                input("Press ENTER to continue...")
    
    except KeyboardInterrupt:
        clear_screen()
        _print("\n\n✅ Program interrupted. Goodbye! 🎓\n")


# Allow running as script too
if __name__ == "__main__":
    print()
