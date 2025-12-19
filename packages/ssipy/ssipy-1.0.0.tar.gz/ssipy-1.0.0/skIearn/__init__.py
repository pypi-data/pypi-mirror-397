"""
skIearn - A comprehensive KDD (Knowledge Discovery in Databases) code library.

This package provides ready-to-use code snippets for common data science tasks including:
- Statistical analysis
- Normality and homogeneity tests
- Outlier detection and treatment
- Data normalization and standardization
- Missing value imputation
- Class imbalance handling
- Classification metrics
- Data visualization
"""

from .core import (
    # Code snippets as strings
    imports,
    stats_descriptives,
    taille_echantillon,
    tests_normalite,
    tests_homogeneite,
    outliers_iqr,
    outliers_zscore,
    outliers_zscore_robuste,
    outliers_mahalanobis,
    outliers_lof,
    outliers_isolation_forest,
    traitement_winsorisation,
    normalisation_minmax,
    standardisation_zscore,
    standardisation_robuste,
    transformation_boxcox,
    transformation_yeojohnson,
    imputation_moyenne,
    imputation_mediane,
    imputation_knn,
    imputation_mice,
    oversampling,
    undersampling,
    smote,
    adasyn,
    metriques_classification,
    visualisation_normalite,
    visualisation_roc_pr,
    eda_complete,
    # Functions
    help,
    afficher_code,
    afficher_menu,
)

__version__ = "1.0.0"
__author__ = "skIearn Contributors"
__all__ = [
    # Code snippets
    "imports",
    "stats_descriptives",
    "taille_echantillon",
    "tests_normalite",
    "tests_homogeneite",
    "outliers_iqr",
    "outliers_zscore",
    "outliers_zscore_robuste",
    "outliers_mahalanobis",
    "outliers_lof",
    "outliers_isolation_forest",
    "traitement_winsorisation",
    "normalisation_minmax",
    "standardisation_zscore",
    "standardisation_robuste",
    "transformation_boxcox",
    "transformation_yeojohnson",
    "imputation_moyenne",
    "imputation_mediane",
    "imputation_knn",
    "imputation_mice",
    "oversampling",
    "undersampling",
    "smote",
    "adasyn",
    "metriques_classification",
    "visualisation_normalite",
    "visualisation_roc_pr",
    "eda_complete",
    # Functions
    "help",
    "afficher_code",
    "afficher_menu",
]
