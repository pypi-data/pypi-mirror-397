"""
skIearn - A comprehensive KDD (Knowledge Discovery in Databases) code library.

This package provides ready-to-use code snippets for common data science tasks including:
- Statistical analysis
- Normality and homogeneity tests
- Outlier detection and treatment
- Data normalization and standardization
- Missing value imputation
- Class imbalance handling
- Classification and Regression models
- Model evaluation metrics
- Machine Learning pipelines
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
    # NEW: Machine Learning snippets
    train_test_split_code,
    pipeline_model,
    naive_bayes,
    knn_classifier,
    knn_regressor,
    logistic_regression,
    random_forest_classifier,
    random_forest_regressor,
    pca_analysis,
    metriques_classification_complet,
    metriques_regression,
    cross_validation,
    hyperparameter_tuning,
    # Functions
    help,
    afficher_code,
    afficher_menu,
)

__version__ = "1.1.0"
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
    # Machine Learning snippets
    "train_test_split_code",
    "pipeline_model",
    "naive_bayes",
    "knn_classifier",
    "knn_regressor",
    "logistic_regression",
    "random_forest_classifier",
    "random_forest_regressor",
    "pca_analysis",
    "metriques_classification_complet",
    "metriques_regression",
    "cross_validation",
    "hyperparameter_tuning",
    # Functions
    "help",
    "afficher_code",
    "afficher_menu",
]
