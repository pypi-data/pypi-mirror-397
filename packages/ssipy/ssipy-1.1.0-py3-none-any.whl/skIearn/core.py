"""
============================================================================
CODE KDD PAR PARTIES - VARIABLES POUR CHAQUE TÂCHE
Chaque variable contient le code complet avec ses imports pour accomplir la tâche
============================================================================
"""

# ============================================================================
# IMPORTS NÉCESSAIRES (tous ensemble)
# ============================================================================

imports = '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats.mstats import winsorize
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, PowerTransformer
from sklearn.impute import SimpleImputer, KNNImputer, IterativeImputer
from sklearn.neighbors import LocalOutlierFactor, KNeighborsClassifier, KNeighborsRegressor
from sklearn.ensemble import IsolationForest, RandomForestClassifier, RandomForestRegressor
from sklearn.covariance import EmpiricalCovariance
from sklearn.metrics import (classification_report, confusion_matrix, 
                            balanced_accuracy_score, matthews_corrcoef,
                            roc_curve, auc, precision_recall_curve, f1_score,
                            accuracy_score, precision_score, recall_score,
                            mean_squared_error, mean_absolute_error, r2_score,
                            mean_absolute_percentage_error)
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.decomposition import PCA
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from imblearn.over_sampling import SMOTE, ADASYN, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler
import warnings
warnings.filterwarnings('ignore')
'''

# ============================================================================
# 1. STATISTIQUES DESCRIPTIVES
# ============================================================================

stats_descriptives = '''
import numpy as np
from scipy import stats

data = np.array([12, 15, 18, 20, 22, 25, 28, 30, 35, 40])

moyenne = np.mean(data)
mediane = np.median(data)
mode = stats.mode(data, keepdims=True).mode[0]

ecart_type = np.std(data, ddof=1)
variance = np.var(data, ddof=1)
q1 = np.percentile(data, 25)
q3 = np.percentile(data, 75)
iqr = q3 - q1
etendue = np.max(data) - np.min(data)

cv = (ecart_type / moyenne) * 100

skewness = stats.skew(data)
kurtosis = stats.kurtosis(data)

print(f"Moyenne: {moyenne:.2f}")
print(f"Médiane: {mediane:.2f}")
print(f"Écart-type: {ecart_type:.2f}")
print(f"IQR: {iqr:.2f}")
print(f"Skewness: {skewness:.4f}")
print(f"Kurtosis: {kurtosis:.4f}")
'''

# ============================================================================
# 2. TAILLE D'ÉCHANTILLON
# ============================================================================

taille_echantillon = '''
import numpy as np


# Formule de Cochran (population infinie)
p = 0.5  # Proportion
e = 0.05  # Marge d'erreur
z = 1.96  # Niveau de confiance 95%
q = 1 - p
n_cochran = (z**2 * p * q) / (e**2)
n_cochran = int(np.ceil(n_cochran))
print(f"Taille échantillon (Cochran): {n_cochran}")

# Formule de Cochran modifiée (population finie)
N = 10000  # Taille population
n0 = n_cochran
n_fini = n0 / (1 + (n0 - 1) / N)
n_fini = int(np.ceil(n_fini))
print(f"Taille échantillon (Cochran fini): {n_fini}")

# Formule de Yamane
n_yamane = N / (1 + N * e**2)
n_yamane = int(np.ceil(n_yamane))
print(f"Taille échantillon (Yamane): {n_yamane}")
'''

# ============================================================================
# 3. TESTS DE NORMALITÉ
# ============================================================================

tests_normalite = '''
import numpy as np
from scipy import stats

# TESTS DE NORMALITÉ
data = np.random.normal(100, 15, 1000)

# Skewness et Kurtosis
skewness = stats.skew(data)
kurtosis = stats.kurtosis(data)
print(f"Skewness: {skewness:.4f}")
print(f"Kurtosis: {kurtosis:.4f}")

# Test de Shapiro-Wilk
stat_sw, p_sw = stats.shapiro(data)
print(f"Shapiro-Wilk: stat={stat_sw:.4f}, p={p_sw:.4f}")
print(f"Normal: {'OUI' if p_sw > 0.05 else 'NON'}")

# Test de Kolmogorov-Smirnov
stat_ks, p_ks = stats.kstest(data, 'norm', args=(np.mean(data), np.std(data)))
print(f"KS: stat={stat_ks:.4f}, p={p_ks:.4f}")
print(f"Normal: {'OUI' if p_ks > 0.05 else 'NON'}")

# Test de D'Agostino-Pearson
stat_da, p_da = stats.normaltest(data)
print(f"D'Agostino: stat={stat_da:.4f}, p={p_da:.4f}")
print(f"Normal: {'OUI' if p_da > 0.05 else 'NON'}")

# Test d'Anderson-Darling
result_ad = stats.anderson(data)
print(f"Anderson-Darling: stat={result_ad.statistic:.4f}")
for i, (crit, sig) in enumerate(zip(result_ad.critical_values, result_ad.significance_level)):
    print(f"  Niveau {sig}%: critique = {crit:.3f}")
'''

# ============================================================================
# 4. TESTS D'HOMOGÉNÉITÉ
# ============================================================================

tests_homogeneite = '''
import numpy as np
from scipy import stats

# TESTS D'HOMOGÉNÉITÉ DES VARIANCES
group1 = np.random.normal(100, 10, 30)
group2 = np.random.normal(105, 10, 30)
group3 = np.random.normal(95, 12, 30)

# Test de Bartlett
stat_b, p_b = stats.bartlett(group1, group2, group3)
print(f"Bartlett: stat={stat_b:.4f}, p={p_b:.4f}")
print(f"Homogène: {'OUI' if p_b > 0.05 else 'NON'}")

# Test de Levene
stat_l, p_l = stats.levene(group1, group2, group3)
print(f"Levene: stat={stat_l:.4f}, p={p_l:.4f}")
print(f"Homogène: {'OUI' if p_l > 0.05 else 'NON'}")

# Test de Fligner-Killeen
stat_f, p_f = stats.fligner(group1, group2, group3)
print(f"Fligner: stat={stat_f:.4f}, p={p_f:.4f}")
print(f"Homogène: {'OUI' if p_f > 0.05 else 'NON'}")
'''

# ============================================================================
# 5. DÉTECTION OUTLIERS - MÉTHODE IQR
# ============================================================================

outliers_iqr = '''
import numpy as np

# DÉTECTION OUTLIERS - MÉTHODE IQR (TUKEY)
data = np.array([10, 12, 14, 15, 18, 20, 22, 100, 150])

# Calcul IQR
q1 = np.percentile(data, 25)
q3 = np.percentile(data, 75)
iqr = q3 - q1

# Bornes
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr

# Identification outliers
outliers = data[(data < lower_bound) | (data > upper_bound)]

print(f"Q1: {q1:.2f}, Q3: {q3:.2f}, IQR: {iqr:.2f}")
print(f"Bornes: [{lower_bound:.2f}, {upper_bound:.2f}]")
print(f"Outliers: {outliers}")
print(f"Nombre: {len(outliers)} ({len(outliers)/len(data)*100:.2f}%)")
'''

# ============================================================================
# 6. DÉTECTION OUTLIERS - Z-SCORE
# ============================================================================

outliers_zscore = '''
import numpy as np
from scipy import stats

# DÉTECTION OUTLIERS - Z-SCORE
data = np.array([10, 12, 14, 15, 18, 20, 22, 100, 150])

# Calcul Z-scores
z_scores = np.abs(stats.zscore(data))

# Seuil (généralement 3)
seuil = 3
outliers = data[z_scores > seuil]

print(f"Z-scores: {z_scores}")
print(f"Outliers (|Z| > {seuil}): {outliers}")
print(f"Nombre: {len(outliers)}")
'''

# ============================================================================
# 7. DÉTECTION OUTLIERS - Z-SCORE ROBUSTE
# ============================================================================

outliers_zscore_robuste = '''
import numpy as np

# DÉTECTION OUTLIERS - Z-SCORE ROBUSTE (MAD)
data = np.array([10, 12, 14, 15, 18, 20, 22, 100, 150])

# Calcul MAD
median = np.median(data)
mad = np.median(np.abs(data - median))

# Z-score robuste
z_robust = (data - median) / (1.4826 * mad)

# Seuil
seuil = 3
outliers = data[np.abs(z_robust) > seuil]

print(f"Médiane: {median:.2f}")
print(f"MAD: {mad:.2f}")
print(f"Z-robust: {z_robust}")
print(f"Outliers: {outliers}")
'''

# ============================================================================
# 8. DÉTECTION OUTLIERS - MAHALANOBIS
# ============================================================================

outliers_mahalanobis = '''
import numpy as np
from scipy import stats
from sklearn.covariance import EmpiricalCovariance

# DÉTECTION OUTLIERS - DISTANCE DE MAHALANOBIS (multivariée)
X = np.random.randn(100, 2)
X = np.vstack([X, [[10, 10], [-10, -10]]])  # Ajouter outliers

# Calcul distance de Mahalanobis
cov = EmpiricalCovariance().fit(X)
mahal_dist = cov.mahalanobis(X)

# Seuil (chi2 à 97.5% pour p dimensions)
threshold = stats.chi2.ppf(0.975, df=X.shape[1])
outliers_idx = mahal_dist > threshold

print(f"Seuil: {threshold:.2f}")
print(f"Nombre outliers: {np.sum(outliers_idx)}")
print(f"Indices outliers: {np.where(outliers_idx)[0]}")
'''

# ============================================================================
# 9. DÉTECTION OUTLIERS - LOF
# ============================================================================

outliers_lof = '''
import numpy as np
from sklearn.neighbors import LocalOutlierFactor

# DÉTECTION OUTLIERS - LOCAL OUTLIER FACTOR
X = np.random.randn(100, 2)
X = np.vstack([X, [[10, 10], [-10, -10]]])  # Ajouter outliers

# LOF
lof = LocalOutlierFactor(n_neighbors=20)
outliers_pred = lof.fit_predict(X)
outliers_idx = outliers_pred == -1

print(f"Nombre outliers: {np.sum(outliers_idx)}")
print(f"Indices: {np.where(outliers_idx)[0]}")
'''

# ============================================================================
# 10. DÉTECTION OUTLIERS - ISOLATION FOREST
# ============================================================================

outliers_isolation_forest = '''
import numpy as np
from sklearn.ensemble import IsolationForest

# DÉTECTION OUTLIERS - ISOLATION FOREST
X = np.random.randn(100, 2)
X = np.vstack([X, [[10, 10], [-10, -10]]])  # Ajouter outliers

# Isolation Forest
iso = IsolationForest(contamination=0.1, random_state=42)
outliers_pred = iso.fit_predict(X)
outliers_idx = outliers_pred == -1

print(f"Nombre outliers: {np.sum(outliers_idx)}")
print(f"Indices: {np.where(outliers_idx)[0]}")
'''

# ============================================================================
# 11. TRAITEMENT OUTLIERS - WINSORISATION
# ============================================================================

traitement_winsorisation = '''
import numpy as np
from scipy.stats.mstats import winsorize

# WINSORISATION DES OUTLIERS
data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 100])

# Winsorisation (clipper 5% de chaque côté)
data_wins = winsorize(data, limits=[0.05, 0.05])

print(f"Original: {data}")
print(f"Winsorisé: {data_wins}")

# Méthode manuelle avec IQR
q1 = np.percentile(data, 25)
q3 = np.percentile(data, 75)
iqr = q3 - q1
lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr
data_clipped = np.clip(data, lower, upper)

print(f"Clipped (IQR): {data_clipped}")
'''

# ============================================================================
# 12. NORMALISATION MIN-MAX
# ============================================================================

normalisation_minmax = '''
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# NORMALISATION MIN-MAX [0, 1]
data = np.array([1, 2, 3, 4, 5, 100])

# Méthode 1: Formule manuelle
data_norm = (data - data.min()) / (data.max() - data.min())
print(f"Min-Max manuel: {data_norm}")

# Méthode 2: Sklearn
scaler = MinMaxScaler()
data_norm_sk = scaler.fit_transform(data.reshape(-1, 1)).flatten()
print(f"Min-Max sklearn: {data_norm_sk}")
'''

# ============================================================================
# 13. STANDARDISATION Z-SCORE
# ============================================================================

standardisation_zscore = '''
import numpy as np
from sklearn.preprocessing import StandardScaler

# STANDARDISATION Z-SCORE
data = np.array([1, 2, 3, 4, 5, 100])

# Méthode 1: Formule manuelle
mean = np.mean(data)
std = np.std(data, ddof=1)
data_std = (data - mean) / std
print(f"Z-score manuel: {data_std}")

# Méthode 2: Sklearn
scaler = StandardScaler()
data_std_sk = scaler.fit_transform(data.reshape(-1, 1)).flatten()
print(f"Z-score sklearn: {data_std_sk}")
'''

# ============================================================================
# 14. STANDARDISATION ROBUSTE
# ============================================================================

standardisation_robuste = '''
import numpy as np
from sklearn.preprocessing import RobustScaler

# STANDARDISATION ROBUSTE (avec médiane et IQR)
data = np.array([1, 2, 3, 4, 5, 100])

# Méthode 1: Formule manuelle
median = np.median(data)
q1 = np.percentile(data, 25)
q3 = np.percentile(data, 75)
iqr = q3 - q1
data_robust = (data - median) / iqr
print(f"Robuste manuel: {data_robust}")

# Méthode 2: Sklearn
scaler = RobustScaler()
data_robust_sk = scaler.fit_transform(data.reshape(-1, 1)).flatten()
print(f"Robuste sklearn: {data_robust_sk}")
'''

# ============================================================================
# 15. TRANSFORMATION BOX-COX
# ============================================================================

transformation_boxcox = '''
import numpy as np
from sklearn.preprocessing import PowerTransformer

# TRANSFORMATION BOX-COX (données positives uniquement)
data = np.array([1, 2, 3, 4, 5, 100])

# S'assurer que données sont positives
data_pos = np.abs(data) + 1

# Box-Cox
pt = PowerTransformer(method='box-cox')
data_boxcox = pt.fit_transform(data_pos.reshape(-1, 1)).flatten()

print(f"Original: {data}")
print(f"Box-Cox: {data_boxcox}")
print(f"Lambda optimal: {pt.lambdas_[0]:.4f}")
'''

# ============================================================================
# 16. TRANSFORMATION YEO-JOHNSON
# ============================================================================

transformation_yeojohnson = '''
import numpy as np
from sklearn.preprocessing import PowerTransformer

# TRANSFORMATION YEO-JOHNSON (accepte valeurs négatives)
data = np.array([-5, -2, 0, 2, 5, 100])

# Yeo-Johnson
pt = PowerTransformer(method='yeo-johnson')
data_yeo = pt.fit_transform(data.reshape(-1, 1)).flatten()

print(f"Original: {data}")
print(f"Yeo-Johnson: {data_yeo}")
print(f"Lambda optimal: {pt.lambdas_[0]:.4f}")
'''

# ============================================================================
# 17. IMPUTATION VALEURS MANQUANTES - MOYENNE
# ============================================================================

imputation_moyenne = '''
import numpy as np
from sklearn.impute import SimpleImputer

# IMPUTATION PAR MOYENNE
data = np.array([1, 2, np.nan, 4, 5, np.nan, 7, 8])

# Méthode 1: Manuelle
mean = np.nanmean(data)
data_imputed = np.where(np.isnan(data), mean, data)
print(f"Moyenne: {mean:.2f}")
print(f"Données imputées: {data_imputed}")

# Méthode 2: Sklearn
imputer = SimpleImputer(strategy='mean')
data_imputed_sk = imputer.fit_transform(data.reshape(-1, 1)).flatten()
print(f"Sklearn: {data_imputed_sk}")
'''

# ============================================================================
# 18. IMPUTATION VALEURS MANQUANTES - MÉDIANE
# ============================================================================

imputation_mediane = '''
import numpy as np
from sklearn.impute import SimpleImputer

# IMPUTATION PAR MÉDIANE
data = np.array([1, 2, np.nan, 4, 5, np.nan, 7, 100])

# Méthode 1: Manuelle
median = np.nanmedian(data)
data_imputed = np.where(np.isnan(data), median, data)
print(f"Médiane: {median:.2f}")
print(f"Données imputées: {data_imputed}")

# Méthode 2: Sklearn
imputer = SimpleImputer(strategy='median')
data_imputed_sk = imputer.fit_transform(data.reshape(-1, 1)).flatten()
print(f"Sklearn: {data_imputed_sk}")
'''

# ============================================================================
# 19. IMPUTATION VALEURS MANQUANTES - KNN
# ============================================================================

imputation_knn = '''
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer

# IMPUTATION PAR KNN
df = pd.DataFrame({
    'A': [1, 2, np.nan, 4, 5],
    'B': [5, np.nan, np.nan, 8, 10],
    'C': [1, 2, 3, 4, 5]
})

print("Avant imputation:")
print(df)

# KNN Imputer
imputer = KNNImputer(n_neighbors=2)
data_imputed = imputer.fit_transform(df)
df_imputed = pd.DataFrame(data_imputed, columns=df.columns)

print("\\nAprès imputation KNN:")
print(df_imputed)
'''

# ============================================================================
# 20. IMPUTATION VALEURS MANQUANTES - MICE
# ============================================================================

imputation_mice = '''
import numpy as np
import pandas as pd
from sklearn.impute import IterativeImputer

# IMPUTATION PAR MICE (Iterative)
df = pd.DataFrame({
    'A': [1, 2, np.nan, 4, 5],
    'B': [5, np.nan, np.nan, 8, 10],
    'C': [1, 2, 3, 4, 5]
})

print("Avant imputation:")
print(df)

# MICE (Iterative Imputer)
imputer = IterativeImputer(random_state=0, max_iter=10)
data_imputed = imputer.fit_transform(df)
df_imputed = pd.DataFrame(data_imputed, columns=df.columns)

print("\\nAprès imputation MICE:")
print(df_imputed)
'''

# ============================================================================
# 21. GESTION DÉSÉQUILIBRE - RANDOM OVERSAMPLING
# ============================================================================

oversampling = '''
import numpy as np
from sklearn.datasets import make_classification
from imblearn.over_sampling import RandomOverSampler

# RANDOM OVERSAMPLING

# Créer données déséquilibrées
X, y = make_classification(n_samples=1000, n_features=20, 
                          weights=[0.9, 0.1], random_state=42)

print(f"Distribution originale: {np.bincount(y)}")

# Random Oversampling
ros = RandomOverSampler(random_state=42)
X_resampled, y_resampled = ros.fit_resample(X, y)

print(f"Après oversampling: {np.bincount(y_resampled)}")
'''

# ============================================================================
# 22. GESTION DÉSÉQUILIBRE - RANDOM UNDERSAMPLING
# ============================================================================

undersampling = '''
import numpy as np
from sklearn.datasets import make_classification
from imblearn.under_sampling import RandomUnderSampler

# RANDOM UNDERSAMPLING

# Créer données déséquilibrées
X, y = make_classification(n_samples=1000, n_features=20, 
                          weights=[0.9, 0.1], random_state=42)

print(f"Distribution originale: {np.bincount(y)}")

# Random Undersampling
rus = RandomUnderSampler(random_state=42)
X_resampled, y_resampled = rus.fit_resample(X, y)

print(f"Après undersampling: {np.bincount(y_resampled)}")
'''

# ============================================================================
# 23. GESTION DÉSÉQUILIBRE - SMOTE
# ============================================================================

smote = '''
import numpy as np
from sklearn.datasets import make_classification
from imblearn.over_sampling import SMOTE

# SMOTE (Synthetic Minority Over-sampling Technique)

# Créer données déséquilibrées
X, y = make_classification(n_samples=1000, n_features=20, 
                          weights=[0.9, 0.1], random_state=42)

print(f"Distribution originale: {np.bincount(y)}")

# SMOTE
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

print(f"Après SMOTE: {np.bincount(y_resampled)}")
'''

# ============================================================================
# 24. GESTION DÉSÉQUILIBRE - ADASYN
# ============================================================================

adasyn = '''
import numpy as np
from sklearn.datasets import make_classification
from imblearn.over_sampling import ADASYN

# ADASYN (Adaptive Synthetic Sampling)

# Créer données déséquilibrées
X, y = make_classification(n_samples=1000, n_features=20, 
                          weights=[0.9, 0.1], random_state=42)

print(f"Distribution originale: {np.bincount(y)}")

# ADASYN
adasyn = ADASYN(random_state=42)
X_resampled, y_resampled = adasyn.fit_resample(X, y)

print(f"Après ADASYN: {np.bincount(y_resampled)}")
'''

# ============================================================================
# 25. MÉTRIQUES CLASSIFICATION
# ============================================================================

metriques_classification = '''
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (classification_report, confusion_matrix, 
                            balanced_accuracy_score, matthews_corrcoef,
                            f1_score, roc_auc_score)

# MÉTRIQUES DE CLASSIFICATION

X, y = make_classification(n_samples=1000, weights=[0.7, 0.3], random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
y_pred_proba = clf.predict_proba(X_test)[:, 1]

cm = confusion_matrix(y_test, y_pred)
print("Matrice de Confusion:")
print(cm)

ba = balanced_accuracy_score(y_test, y_pred)
mcc = matthews_corrcoef(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"\\nBalanced Accuracy: {ba:.4f}")
print(f"MCC: {mcc:.4f}")
print(f"F1-Score: {f1:.4f}")

roc_auc = roc_auc_score(y_test, y_pred_proba)
print(f"ROC-AUC: {roc_auc:.4f}")

print("\\nClassification Report:")
print(classification_report(y_test, y_pred))
'''

# ============================================================================
# 26. VISUALISATION NORMALITÉ
# ============================================================================

visualisation_normalite = '''
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

data = np.random.normal(100, 15, 1000)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))


axes[0, 0].hist(data, bins=30, edgecolor='black', alpha=0.7)
axes[0, 0].axvline(np.mean(data), color='r', linestyle='--', label='Moyenne')
axes[0, 0].axvline(np.median(data), color='g', linestyle='--', label='Médiane')
axes[0, 0].set_title('Histogramme')
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)

stats.probplot(data, dist="norm", plot=axes[0, 1])
axes[0, 1].set_title('Q-Q Plot')
axes[0, 1].grid(alpha=0.3)

axes[1, 0].boxplot(data)
axes[1, 0].set_title('Boxplot')
axes[1, 0].grid(alpha=0.3)

axes[1, 1].hist(data, bins=30, density=True, alpha=0.7, edgecolor='black')
axes[1, 1].set_title('Densité')
axes[1, 1].grid(alpha=0.3)

plt.tight_layout()
plt.show()
'''

# ============================================================================
# 27. VISUALISATION COURBES ROC ET PR
# ============================================================================

visualisation_roc_pr = '''
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, auc, precision_recall_curve


X, y = make_classification(n_samples=1000, weights=[0.7, 0.3], random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)
y_pred_proba = clf.predict_proba(X_test)[:, 1]


fig, axes = plt.subplots(1, 2, figsize=(12, 5))

fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)

axes[0].plot(fpr, tpr, lw=2, label=f'ROC (AUC = {roc_auc:.2f})')
axes[0].plot([0, 1], [0, 1], 'k--', lw=2)
axes[0].set_xlabel('False Positive Rate')
axes[0].set_ylabel('True Positive Rate')
axes[0].set_title('ROC Curve')
axes[0].legend()
axes[0].grid(alpha=0.3)

precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
pr_auc = auc(recall, precision)

axes[1].plot(recall, precision, lw=2, label=f'PR (AUC = {pr_auc:.2f})')
axes[1].set_xlabel('Recall')
axes[1].set_ylabel('Precision')
axes[1].set_title('Precision-Recall Curve')
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.show()
'''

# ============================================================================
# 28. ANALYSE EXPLORATOIRE COMPLÈTE
# ============================================================================

eda_complete = '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.DataFrame(np.random.randn(1000, 5), columns=['A', 'B', 'C', 'D', 'E'])
df['Target'] = np.random.choice([0, 1], size=1000, p=[0.7, 0.3])

print("INFORMATIONS GÉNÉRALES")
print(df.info())

print("\\n" + "="*80)
print("STATISTIQUES DESCRIPTIVES")
print("="*80)
print(df.describe())

print("\\n" + "="*80)
print("VALEURS MANQUANTES")
print("="*80)
print(df.isnull().sum())

µprint("\\n" + "="*80)
print("VALEURS DUPLIQUÉES")
print("="*80)
print(f"Nombre de duplicates: {df.duplicated().sum()}")

print("\\n" + "="*80)
print("DISTRIBUTION TARGET")
print("="*80)
print(df['Target'].value_counts())
print("\\nPourcentages:")
print(df['Target'].value_counts(normalize=True) * 100)

print("MATRICE DE CORRÉLATION")
numeric_cols = df.select_dtypes(include=[np.number]).columns
corr_matrix = df[numeric_cols].corr()
print(corr_matrix)

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0)
plt.title('Matrice de Corrélation')
plt.tight_layout()
plt.show()
'''

# ============================================================================
# 29. TRAIN TEST SPLIT
# ============================================================================

train_test_split_code = '''
import numpy as np
from sklearn.model_selection import train_test_split

# TRAIN TEST SPLIT
# Données exemple
X = np.random.randn(1000, 10)  # 1000 échantillons, 10 features
y = np.random.choice([0, 1], size=1000)  # Classification binaire

# Split simple (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2,           # 20% pour le test
    random_state=42,         # Reproductibilité
    stratify=y               # Préserve la distribution des classes
)

print(f"Taille totale: {len(X)}")
print(f"Taille train: {len(X_train)} ({len(X_train)/len(X)*100:.1f}%)")
print(f"Taille test: {len(X_test)} ({len(X_test)/len(X)*100:.1f}%)")

# Split train/validation/test (60/20/20)
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp  # 0.25 * 0.8 = 0.2
)

print(f"\\nSplit 3-way:")
print(f"Train: {len(X_train)} ({len(X_train)/len(X)*100:.1f}%)")
print(f"Validation: {len(X_val)} ({len(X_val)/len(X)*100:.1f}%)")
print(f"Test: {len(X_test)} ({len(X_test)/len(X)*100:.1f}%)")
'''

# ============================================================================
# 30. PIPELINE MODEL
# ============================================================================

pipeline_model = '''
import numpy as np
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score

# PIPELINE MODEL
X = np.random.randn(500, 20)
y = np.random.choice([0, 1], size=500)

# Pipeline avec syntaxe explicite
pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='mean')),      # 1. Imputation
    ('scaler', StandardScaler()),                      # 2. Standardisation
    ('pca', PCA(n_components=10)),                     # 3. Réduction dimensionnalité
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))  # 4. Modèle
])

# Alternative: make_pipeline (noms automatiques)
pipeline_simple = make_pipeline(
    SimpleImputer(strategy='mean'),
    StandardScaler(),
    PCA(n_components=10),
    LogisticRegression(max_iter=1000)
)

# Entraînement
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
pipeline.fit(X_train, y_train)

# Prédiction
y_pred = pipeline.predict(X_test)
accuracy = pipeline.score(X_test, y_test)
print(f"Accuracy: {accuracy:.4f}")

# Cross-validation avec pipeline
scores = cross_val_score(pipeline, X, y, cv=5, scoring='accuracy')
print(f"CV Scores: {scores}")
print(f"Mean CV Score: {scores.mean():.4f} (+/- {scores.std()*2:.4f})")

# Accéder aux étapes du pipeline
print(f"\\nÉtapes du pipeline: {pipeline.named_steps.keys()}")
'''

# ============================================================================
# 31. NAIVE BAYES
# ============================================================================

naive_bayes = '''
import numpy as np
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# NAIVE BAYES CLASSIFIER
X = np.random.randn(1000, 10)
y = np.random.choice([0, 1, 2], size=1000)  # Classification multiclasse

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 1. Gaussian Naive Bayes (pour données continues)
gnb = GaussianNB()
gnb.fit(X_train, y_train)
y_pred_gnb = gnb.predict(X_test)
print("=== Gaussian Naive Bayes ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred_gnb):.4f}")

# Probabilités de prédiction
y_proba = gnb.predict_proba(X_test)
print(f"Probabilités (3 premiers): \\n{y_proba[:3]}")

# 2. Multinomial Naive Bayes (pour données de comptage, ex: text)
# Nécessite des valeurs positives
X_pos = np.abs(X)
X_train_pos, X_test_pos, _, _ = train_test_split(X_pos, y, test_size=0.2, random_state=42)
mnb = MultinomialNB(alpha=1.0)  # Lissage Laplace
mnb.fit(X_train_pos, y_train)
y_pred_mnb = mnb.predict(X_test_pos)
print("\\n=== Multinomial Naive Bayes ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred_mnb):.4f}")

# 3. Bernoulli Naive Bayes (pour données binaires)
X_binary = (X > 0).astype(int)
X_train_bin, X_test_bin, _, _ = train_test_split(X_binary, y, test_size=0.2, random_state=42)
bnb = BernoulliNB(alpha=1.0)
bnb.fit(X_train_bin, y_train)
y_pred_bnb = bnb.predict(X_test_bin)
print("\\n=== Bernoulli Naive Bayes ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred_bnb):.4f}")

# Cross-validation
scores = cross_val_score(gnb, X, y, cv=5, scoring='accuracy')
print(f"\\nGaussian NB CV Score: {scores.mean():.4f} (+/- {scores.std()*2:.4f})")

# Rapport de classification
print("\\n=== Rapport de Classification (Gaussian NB) ===")
print(classification_report(y_test, y_pred_gnb))
'''

# ============================================================================
# 32. K-NEAREST NEIGHBORS (KNN)
# ============================================================================

knn_classifier = '''
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt

# KNN CLASSIFIER
X = np.random.randn(500, 10)
y = np.random.choice([0, 1], size=500)

# IMPORTANT: Standardiser les données pour KNN
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# KNN simple
knn = KNeighborsClassifier(
    n_neighbors=5,           # Nombre de voisins
    weights='uniform',       # 'uniform' ou 'distance'
    metric='euclidean',      # Distance: 'euclidean', 'manhattan', 'minkowski'
    n_jobs=-1                # Utiliser tous les CPUs
)
knn.fit(X_train, y_train)
y_pred = knn.predict(X_test)
print(f"Accuracy (k=5): {accuracy_score(y_test, y_pred):.4f}")

# Trouver le meilleur k
k_range = range(1, 31)
scores = []
for k in k_range:
    knn_temp = KNeighborsClassifier(n_neighbors=k)
    cv_scores = cross_val_score(knn_temp, X_scaled, y, cv=5, scoring='accuracy')
    scores.append(cv_scores.mean())

best_k = k_range[np.argmax(scores)]
print(f"\\nMeilleur k: {best_k} avec accuracy: {max(scores):.4f}")

# GridSearch pour optimisation
param_grid = {
    'n_neighbors': [3, 5, 7, 9, 11],
    'weights': ['uniform', 'distance'],
    'metric': ['euclidean', 'manhattan']
}
grid_search = GridSearchCV(KNeighborsClassifier(), param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_scaled, y)
print(f"\\nMeilleurs paramètres: {grid_search.best_params_}")
print(f"Meilleur score: {grid_search.best_score_:.4f}")

# Visualisation
plt.figure(figsize=(10, 5))
plt.plot(k_range, scores, 'bo-')
plt.xlabel('Nombre de voisins (k)')
plt.ylabel('Accuracy (CV)')
plt.title('Accuracy vs K')
plt.axvline(x=best_k, color='r', linestyle='--', label=f'Best k={best_k}')
plt.legend()
plt.grid(True)
plt.show()
'''

knn_regressor = '''
import numpy as np
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# KNN REGRESSOR
X = np.random.randn(500, 10)
y = 3 * X[:, 0] + 2 * X[:, 1] + np.random.randn(500) * 0.5  # Variable continue

# Standardiser
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# KNN Regressor
knn_reg = KNeighborsRegressor(
    n_neighbors=5,
    weights='distance',      # Pondérer par l'inverse de la distance
    metric='euclidean'
)
knn_reg.fit(X_train, y_train)
y_pred = knn_reg.predict(X_test)

# Métriques
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("=== KNN Regressor ===")
print(f"MSE: {mse:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"MAE: {mae:.4f}")
print(f"R²: {r2:.4f}")

# Cross-validation
cv_scores = cross_val_score(knn_reg, X_scaled, y, cv=5, scoring='r2')
print(f"\\nCV R² Score: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
'''

# ============================================================================
# 33. LOGISTIC REGRESSION
# ============================================================================

logistic_regression = '''
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt

# LOGISTIC REGRESSION
X = np.random.randn(1000, 10)
y = np.random.choice([0, 1], size=1000)

# Standardiser (recommandé pour régression logistique)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# Régression logistique simple
log_reg = LogisticRegression(
    penalty='l2',            # Régularisation: 'l1', 'l2', 'elasticnet', None
    C=1.0,                   # Inverse de la force de régularisation
    solver='lbfgs',          # 'lbfgs', 'liblinear', 'saga'
    max_iter=1000,
    random_state=42
)
log_reg.fit(X_train, y_train)

# Prédictions
y_pred = log_reg.predict(X_test)
y_proba = log_reg.predict_proba(X_test)[:, 1]

# Métriques
from sklearn.metrics import accuracy_score
print("=== Logistic Regression ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.4f}")

# Coefficients (interprétabilité)
print(f"\\nCoefficients: {log_reg.coef_[0][:5]}...")  # 5 premiers
print(f"Intercept: {log_reg.intercept_[0]:.4f}")

# Classification multiclasse
y_multi = np.random.choice([0, 1, 2], size=1000)
log_reg_multi = LogisticRegression(
    multi_class='multinomial',   # 'ovr' ou 'multinomial'
    solver='lbfgs',
    max_iter=1000
)
log_reg_multi.fit(X_scaled, y_multi)
print(f"\\nMulticlass accuracy: {log_reg_multi.score(X_scaled, y_multi):.4f}")

# GridSearch
param_grid = {
    'C': [0.01, 0.1, 1, 10, 100],
    'penalty': ['l1', 'l2'],
    'solver': ['liblinear']
}
grid_search = GridSearchCV(LogisticRegression(max_iter=1000), param_grid, cv=5)
grid_search.fit(X_scaled, y)
print(f"\\nMeilleurs paramètres: {grid_search.best_params_}")
print(f"Meilleur score: {grid_search.best_score_:.4f}")

# Rapport de classification
print("\\n=== Rapport de Classification ===")
print(classification_report(y_test, y_pred))
'''

# ============================================================================
# 34. RANDOM FOREST
# ============================================================================

random_forest_classifier = '''
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt

# RANDOM FOREST CLASSIFIER
X = np.random.randn(1000, 20)
y = np.random.choice([0, 1], size=1000)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Random Forest
rf = RandomForestClassifier(
    n_estimators=100,        # Nombre d'arbres
    max_depth=10,            # Profondeur max (None = illimité)
    min_samples_split=2,     # Min échantillons pour split
    min_samples_leaf=1,      # Min échantillons par feuille
    max_features='sqrt',     # Features par split: 'sqrt', 'log2', int, float
    bootstrap=True,          # Échantillonnage avec remplacement
    oob_score=True,          # Out-of-bag score
    n_jobs=-1,               # Parallélisation
    random_state=42
)
rf.fit(X_train, y_train)

# Prédictions
y_pred = rf.predict(X_test)
y_proba = rf.predict_proba(X_test)[:, 1]

print("=== Random Forest Classifier ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"OOB Score: {rf.oob_score_:.4f}")

# Importance des features
feature_importance = rf.feature_importances_
indices = np.argsort(feature_importance)[::-1]

print("\\nTop 10 Feature Importances:")
for i in range(10):
    print(f"  Feature {indices[i]}: {feature_importance[indices[i]]:.4f}")

# Visualisation importance
plt.figure(figsize=(10, 6))
plt.bar(range(len(feature_importance)), feature_importance[indices])
plt.xlabel('Feature Index')
plt.ylabel('Importance')
plt.title('Feature Importances - Random Forest')
plt.show()

# GridSearch
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15, None],
    'min_samples_split': [2, 5, 10]
}
grid_search = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=3, n_jobs=-1)
grid_search.fit(X_train, y_train)
print(f"\\nMeilleurs paramètres: {grid_search.best_params_}")
print(f"Meilleur score: {grid_search.best_score_:.4f}")

# Rapport
print("\\n=== Rapport de Classification ===")
print(classification_report(y_test, y_pred))
'''

random_forest_regressor = '''
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt

# RANDOM FOREST REGRESSOR
X = np.random.randn(1000, 20)
y = 3 * X[:, 0] + 2 * X[:, 1] - X[:, 2] + np.random.randn(1000) * 0.5

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Random Forest Regressor
rf_reg = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features='sqrt',
    bootstrap=True,
    oob_score=True,
    n_jobs=-1,
    random_state=42
)
rf_reg.fit(X_train, y_train)

# Prédictions
y_pred = rf_reg.predict(X_test)

# Métriques
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("=== Random Forest Regressor ===")
print(f"MSE: {mse:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"MAE: {mae:.4f}")
print(f"R²: {r2:.4f}")
print(f"OOB Score: {rf_reg.oob_score_:.4f}")

# Cross-validation
cv_scores = cross_val_score(rf_reg, X, y, cv=5, scoring='r2')
print(f"\\nCV R² Score: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")

# Feature importance
feature_importance = rf_reg.feature_importances_
indices = np.argsort(feature_importance)[::-1]

print("\\nTop 5 Feature Importances:")
for i in range(5):
    print(f"  Feature {indices[i]}: {feature_importance[indices[i]]:.4f}")

# Visualisation prédictions vs réel
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Valeurs Réelles')
plt.ylabel('Prédictions')
plt.title('Random Forest Regressor: Prédictions vs Réel')
plt.show()
'''

# ============================================================================
# 35. PCA (Principal Component Analysis)
# ============================================================================

pca_analysis = '''
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# PCA - ANALYSE EN COMPOSANTES PRINCIPALES
X = np.random.randn(500, 20)

# IMPORTANT: Standardiser avant PCA
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# PCA complète pour analyse
pca_full = PCA()
pca_full.fit(X_scaled)

# Variance expliquée
print("=== Analyse PCA ===")
print(f"Variance expliquée par composante:")
for i, var in enumerate(pca_full.explained_variance_ratio_[:10]):
    print(f"  PC{i+1}: {var:.4f} ({var*100:.2f}%)")

print(f"\\nVariance cumulée:")
cumsum = np.cumsum(pca_full.explained_variance_ratio_)
for i, cum in enumerate(cumsum[:10]):
    print(f"  PC1-PC{i+1}: {cum:.4f} ({cum*100:.2f}%)")

# Trouver n_components pour 95% de variance
n_95 = np.argmax(cumsum >= 0.95) + 1
print(f"\\nComposantes pour 95% variance: {n_95}")

# PCA avec n_components spécifique
pca = PCA(n_components=0.95)  # Garder 95% de variance
X_pca = pca.fit_transform(X_scaled)
print(f"\\nDimensions originales: {X_scaled.shape}")
print(f"Dimensions après PCA: {X_pca.shape}")

# PCA avec nombre fixe
pca_fixed = PCA(n_components=5)
X_pca_5 = pca_fixed.fit_transform(X_scaled)
print(f"\\nPCA avec 5 composantes:")
print(f"  Variance expliquée: {pca_fixed.explained_variance_ratio_.sum():.4f}")

# Visualisation Scree Plot
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.bar(range(1, 11), pca_full.explained_variance_ratio_[:10])
plt.xlabel('Composante Principale')
plt.ylabel('Variance Expliquée')
plt.title('Scree Plot')

plt.subplot(1, 2, 2)
plt.plot(range(1, len(cumsum)+1), cumsum, 'bo-')
plt.axhline(y=0.95, color='r', linestyle='--', label='95% variance')
plt.axvline(x=n_95, color='g', linestyle='--', label=f'n={n_95}')
plt.xlabel('Nombre de Composantes')
plt.ylabel('Variance Cumulée')
plt.title('Variance Cumulée')
plt.legend()

plt.tight_layout()
plt.show()

# Reconstruction inverse
X_reconstructed = pca.inverse_transform(X_pca)
reconstruction_error = np.mean((X_scaled - X_reconstructed) ** 2)
print(f"\\nErreur de reconstruction: {reconstruction_error:.6f}")
'''

# ============================================================================
# 36. MÉTRIQUES DE CLASSIFICATION (COMPLET)
# ============================================================================

metriques_classification_complet = '''
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, balanced_accuracy_score,
    matthews_corrcoef, cohen_kappa_score, roc_auc_score,
    precision_recall_curve, roc_curve, auc, log_loss,
    hamming_loss, jaccard_score
)
import matplotlib.pyplot as plt
import seaborn as sns

# MÉTRIQUES DE CLASSIFICATION
# Données exemple
y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1, 1, 0])
y_pred = np.array([0, 1, 1, 1, 0, 0, 0, 1, 1, 1])
y_proba = np.array([0.1, 0.6, 0.8, 0.9, 0.3, 0.4, 0.2, 0.85, 0.75, 0.55])

print("=== MÉTRIQUES DE BASE ===")
print(f"Accuracy: {accuracy_score(y_true, y_pred):.4f}")
print(f"Balanced Accuracy: {balanced_accuracy_score(y_true, y_pred):.4f}")
print(f"Precision: {precision_score(y_true, y_pred):.4f}")
print(f"Recall (Sensitivity): {recall_score(y_true, y_pred):.4f}")
print(f"F1-Score: {f1_score(y_true, y_pred):.4f}")

print("\\n=== MÉTRIQUES AVANCÉES ===")
print(f"Matthews Correlation Coefficient: {matthews_corrcoef(y_true, y_pred):.4f}")
print(f"Cohen's Kappa: {cohen_kappa_score(y_true, y_pred):.4f}")
print(f"Hamming Loss: {hamming_loss(y_true, y_pred):.4f}")
print(f"Jaccard Score: {jaccard_score(y_true, y_pred):.4f}")
print(f"Log Loss: {log_loss(y_true, y_proba):.4f}")
print(f"ROC-AUC: {roc_auc_score(y_true, y_proba):.4f}")

# Confusion Matrix
cm = confusion_matrix(y_true, y_pred)
print("\\n=== MATRICE DE CONFUSION ===")
print(f"TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]}")

# Calculs manuels depuis la matrice
tn, fp, fn, tp = cm.ravel()
specificity = tn / (tn + fp)
sensitivity = tp / (tp + fn)  # = recall
ppv = tp / (tp + fp)          # = precision
npv = tn / (tn + fn)

print(f"\\nSpécificité: {specificity:.4f}")
print(f"Sensibilité: {sensitivity:.4f}")
print(f"PPV (Precision): {ppv:.4f}")
print(f"NPV: {npv:.4f}")

# Rapport complet
print("\\n=== RAPPORT DE CLASSIFICATION ===")
print(classification_report(y_true, y_pred, target_names=['Classe 0', 'Classe 1']))

# Pour multiclasse
y_true_multi = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2, 0])
y_pred_multi = np.array([0, 1, 1, 0, 2, 2, 1, 1, 2, 0])
print("\\n=== MULTICLASSE ===")
print(f"Accuracy: {accuracy_score(y_true_multi, y_pred_multi):.4f}")
print(f"Macro F1: {f1_score(y_true_multi, y_pred_multi, average='macro'):.4f}")
print(f"Weighted F1: {f1_score(y_true_multi, y_pred_multi, average='weighted'):.4f}")
print(f"Micro F1: {f1_score(y_true_multi, y_pred_multi, average='micro'):.4f}")

# Visualisation
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Confusion Matrix
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0])
axes[0].set_xlabel('Prédit')
axes[0].set_ylabel('Réel')
axes[0].set_title('Matrice de Confusion')

# ROC Curve
fpr, tpr, _ = roc_curve(y_true, y_proba)
roc_auc = auc(fpr, tpr)
axes[1].plot(fpr, tpr, 'b-', label=f'ROC (AUC = {roc_auc:.2f})')
axes[1].plot([0, 1], [0, 1], 'r--')
axes[1].set_xlabel('False Positive Rate')
axes[1].set_ylabel('True Positive Rate')
axes[1].set_title('Courbe ROC')
axes[1].legend()

plt.tight_layout()
plt.show()
'''

# ============================================================================
# 37. MÉTRIQUES DE RÉGRESSION
# ============================================================================

metriques_regression = '''
import numpy as np
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    mean_absolute_percentage_error, median_absolute_error,
    explained_variance_score, max_error
)
import matplotlib.pyplot as plt

# MÉTRIQUES DE RÉGRESSION
np.random.seed(42)
y_true = np.array([3.0, 5.0, 2.5, 7.0, 4.5, 6.0, 8.0, 3.5, 9.0, 5.5])
y_pred = np.array([2.8, 5.2, 2.3, 6.8, 4.2, 6.3, 7.5, 3.8, 8.7, 5.8])

print("=== MÉTRIQUES DE RÉGRESSION ===")

# MSE (Mean Squared Error)
mse = mean_squared_error(y_true, y_pred)
print(f"MSE (Mean Squared Error): {mse:.4f}")

# RMSE (Root Mean Squared Error)
rmse = np.sqrt(mse)
print(f"RMSE (Root MSE): {rmse:.4f}")

# MAE (Mean Absolute Error)
mae = mean_absolute_error(y_true, y_pred)
print(f"MAE (Mean Absolute Error): {mae:.4f}")

# Median Absolute Error (robuste aux outliers)
medae = median_absolute_error(y_true, y_pred)
print(f"Median Absolute Error: {medae:.4f}")

# MAPE (Mean Absolute Percentage Error)
mape = mean_absolute_percentage_error(y_true, y_pred)
print(f"MAPE (%): {mape*100:.2f}%")

# R² (Coefficient de détermination)
r2 = r2_score(y_true, y_pred)
print(f"R² Score: {r2:.4f}")

# R² ajusté
n = len(y_true)
p = 1  # Nombre de prédicteurs
r2_adj = 1 - (1 - r2) * (n - 1) / (n - p - 1)
print(f"R² Ajusté: {r2_adj:.4f}")

# Explained Variance Score
evs = explained_variance_score(y_true, y_pred)
print(f"Explained Variance: {evs:.4f}")

# Max Error
max_err = max_error(y_true, y_pred)
print(f"Max Error: {max_err:.4f}")

# Calculs manuels
print("\\n=== CALCULS MANUELS ===")
residuals = y_true - y_pred
ss_res = np.sum(residuals ** 2)          # Sum of Squared Residuals
ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)  # Total Sum of Squares
r2_manual = 1 - (ss_res / ss_tot)
print(f"R² (manuel): {r2_manual:.4f}")

# Interprétation R²
print("\\n=== INTERPRÉTATION R² ===")
if r2 >= 0.9:
    print("Excellent: Le modèle explique très bien la variance")
elif r2 >= 0.7:
    print("Bon: Le modèle explique bien la variance")
elif r2 >= 0.5:
    print("Modéré: Le modèle explique moyennement la variance")
else:
    print("Faible: Le modèle explique mal la variance")

# Visualisation
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Prédictions vs Réel
axes[0].scatter(y_true, y_pred, alpha=0.7)
axes[0].plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--')
axes[0].set_xlabel('Valeurs Réelles')
axes[0].set_ylabel('Prédictions')
axes[0].set_title(f'Prédictions vs Réel (R²={r2:.3f})')

# Résidus
axes[1].scatter(y_pred, residuals, alpha=0.7)
axes[1].axhline(y=0, color='r', linestyle='--')
axes[1].set_xlabel('Prédictions')
axes[1].set_ylabel('Résidus')
axes[1].set_title('Analyse des Résidus')

# Distribution des résidus
axes[2].hist(residuals, bins=10, edgecolor='black', alpha=0.7)
axes[2].axvline(x=0, color='r', linestyle='--')
axes[2].set_xlabel('Résidus')
axes[2].set_ylabel('Fréquence')
axes[2].set_title('Distribution des Résidus')

plt.tight_layout()
plt.show()
'''

# ============================================================================
# 38. CROSS-VALIDATION
# ============================================================================

cross_validation = '''
import numpy as np
from sklearn.model_selection import (
    cross_val_score, cross_validate, KFold, StratifiedKFold,
    LeaveOneOut, RepeatedKFold, RepeatedStratifiedKFold
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

# CROSS-VALIDATION
X = np.random.randn(500, 10)
y = np.random.choice([0, 1], size=500)

model = RandomForestClassifier(n_estimators=100, random_state=42)

# 1. Cross-validation simple
print("=== K-Fold Cross-Validation ===")
scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
print(f"Scores: {scores}")
print(f"Mean: {scores.mean():.4f} (+/- {scores.std()*2:.4f})")

# 2. Cross-validate avec plusieurs métriques
print("\\n=== Multi-Metric Cross-Validation ===")
scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
cv_results = cross_validate(model, X, y, cv=5, scoring=scoring, return_train_score=True)
for metric in scoring:
    print(f"{metric}: {cv_results['test_' + metric].mean():.4f} (+/- {cv_results['test_' + metric].std()*2:.4f})")

# 3. Stratified K-Fold (préserve distribution classes)
print("\\n=== Stratified K-Fold ===")
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores_skf = cross_val_score(model, X, y, cv=skf, scoring='accuracy')
print(f"Mean: {scores_skf.mean():.4f} (+/- {scores_skf.std()*2:.4f})")

# 4. Repeated K-Fold
print("\\n=== Repeated Stratified K-Fold ===")
rskf = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=42)
scores_rskf = cross_val_score(model, X, y, cv=rskf, scoring='accuracy')
print(f"Mean: {scores_rskf.mean():.4f} (+/- {scores_rskf.std()*2:.4f})")

# 5. Leave-One-Out (pour petits datasets)
print("\\n=== Leave-One-Out (sur subset) ===")
X_small, y_small = X[:50], y[:50]
loo = LeaveOneOut()
scores_loo = cross_val_score(LogisticRegression(max_iter=1000), X_small, y_small, cv=loo)
print(f"Mean: {scores_loo.mean():.4f}")

# 6. Manuel K-Fold pour accès aux indices
print("\\n=== K-Fold Manuel ===")
kf = KFold(n_splits=5, shuffle=True, random_state=42)
for fold, (train_idx, val_idx) in enumerate(kf.split(X)):
    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]
    model.fit(X_train, y_train)
    score = model.score(X_val, y_val)
    print(f"Fold {fold+1}: {score:.4f}")
'''

# ============================================================================
# 39. GRID SEARCH ET RANDOM SEARCH
# ============================================================================

hyperparameter_tuning = '''
import numpy as np
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from scipy.stats import randint, uniform

# HYPERPARAMETER TUNING
X = np.random.randn(500, 10)
y = np.random.choice([0, 1], size=500)

# 1. Grid Search (recherche exhaustive)
print("=== Grid Search ===")
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=1
)
grid_search.fit(X, y)

print(f"\\nMeilleurs paramètres: {grid_search.best_params_}")
print(f"Meilleur score: {grid_search.best_score_:.4f}")
print(f"Meilleur modèle: {grid_search.best_estimator_}")

# 2. Randomized Search (plus rapide, échantillonnage aléatoire)
print("\\n=== Randomized Search ===")
param_distributions = {
    'n_estimators': randint(50, 300),
    'max_depth': randint(3, 20),
    'min_samples_split': randint(2, 20),
    'min_samples_leaf': randint(1, 10),
    'max_features': uniform(0.1, 0.9)
}

random_search = RandomizedSearchCV(
    RandomForestClassifier(random_state=42),
    param_distributions,
    n_iter=50,              # Nombre de combinaisons à tester
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    random_state=42,
    verbose=1
)
random_search.fit(X, y)

print(f"\\nMeilleurs paramètres: {random_search.best_params_}")
print(f"Meilleur score: {random_search.best_score_:.4f}")

# 3. Résultats détaillés
import pandas as pd
results_df = pd.DataFrame(grid_search.cv_results_)
print("\\n=== Top 5 combinaisons ===")
print(results_df.nsmallest(5, 'rank_test_score')[['params', 'mean_test_score', 'std_test_score']])
'''

# ============================================================================
# FONCTION PRINCIPALE POUR AFFICHER LE CODE
# ============================================================================
def help(a):
    """Affiche le menu des parties disponibles"""
    return print(a)

def afficher_code(partie):
    """Affiche le code pour une partie spécifique"""
    
    parties = {
        'imports': imports,
        'stats': stats_descriptives,
        'taille': taille_echantillon,
        'normalite': tests_normalite,
        'homogeneite': tests_homogeneite,
        'outliers_iqr': outliers_iqr,
        'outliers_zscore': outliers_zscore,
        'outliers_robust': outliers_zscore_robuste,
        'outliers_mahalanobis': outliers_mahalanobis,
        'outliers_lof': outliers_lof,
        'outliers_isolation': outliers_isolation_forest,
        'winsorisation': traitement_winsorisation,
        'norm_minmax': normalisation_minmax,
        'std_zscore': standardisation_zscore,
        'std_robuste': standardisation_robuste,
        'boxcox': transformation_boxcox,
        'yeojohnson': transformation_yeojohnson,
        'impute_mean': imputation_moyenne,
        'impute_median': imputation_mediane,
        'impute_knn': imputation_knn,
        'impute_mice': imputation_mice,
        'oversample': oversampling,
        'undersample': undersampling,
        'smote': smote,
        'adasyn': adasyn,
        'metriques': metriques_classification,
        'viz_normalite': visualisation_normalite,
        'viz_roc': visualisation_roc_pr,
        'eda': eda_complete,
        # NEW: Machine Learning
        'train_test_split': train_test_split_code,
        'pipeline': pipeline_model,
        'naive_bayes': naive_bayes,
        'knn_classifier': knn_classifier,
        'knn_regressor': knn_regressor,
        'logistic_regression': logistic_regression,
        'random_forest_classifier': random_forest_classifier,
        'random_forest_regressor': random_forest_regressor,
        'pca': pca_analysis,
        'metriques_classification': metriques_classification_complet,
        'metriques_regression': metriques_regression,
        'cross_validation': cross_validation,
        'hyperparameter_tuning': hyperparameter_tuning,
    }
    
    if partie.lower() == 'all':
        print("\n" + "="*80)
        print("TOUTES LES PARTIES DU CODE KDD")
        print("="*80 + "\n")
        for nom, code in parties.items():
            print(f"\n{'#'*80}")
            print(f"# {nom.upper()}")
            print(f"{'#'*80}")
            print(code)
    elif partie in parties:
        print(parties[partie])
    else:
        print("\nPartie non trouvée. Parties disponibles:")
        for nom in parties.keys():
            print(f"  - {nom}")

def afficher_menu():
    print("""
STATISTIQUES ET TESTS:
  - imports           : Tous les imports nécessaires
  - stats             : Statistiques descriptives
  - taille            : Calcul taille d'échantillon
  - normalite         : Tests de normalité
  - homogeneite       : Tests d'homogénéité des variances

DÉTECTION OUTLIERS:
  - outliers_iqr      : Méthode IQR (Tukey)
  - outliers_zscore   : Méthode Z-score
  - outliers_robust   : Z-score robuste (MAD)
  - outliers_mahalanobis : Distance de Mahalanobis
  - outliers_lof      : Local Outlier Factor
  - outliers_isolation : Isolation Forest

TRAITEMENT DONNÉES:
  - winsorisation     : Winsorisation des outliers
  - norm_minmax       : Normalisation Min-Max
  - std_zscore        : Standardisation Z-score
  - std_robuste       : Standardisation robuste
  - boxcox            : Transformation Box-Cox
  - yeojohnson        : Transformation Yeo-Johnson

VALEURS MANQUANTES:
  - impute_mean       : Imputation par moyenne
  - impute_median     : Imputation par médiane
  - impute_knn        : Imputation KNN
  - impute_mice       : Imputation MICE

DÉSÉQUILIBRE CLASSES:
  - oversample        : Random Oversampling
  - undersample       : Random Undersampling
  - smote             : SMOTE
  - adasyn            : ADASYN

MACHINE LEARNING - MODÈLES:
  - train_test_split  : Division train/test des données
  - pipeline          : Pipeline de preprocessing + modèle
  - naive_bayes       : Naive Bayes (Gaussian, Multinomial, Bernoulli)
  - knn_classifier    : K-Nearest Neighbors Classification
  - knn_regressor     : K-Nearest Neighbors Regression
  - logistic_regression : Régression Logistique
  - random_forest_classifier : Random Forest Classification
  - random_forest_regressor  : Random Forest Regression
  - pca               : PCA (Analyse en Composantes Principales)

MACHINE LEARNING - ÉVALUATION:
  - metriques_classification : Toutes les métriques de classification
  - metriques_regression     : Toutes les métriques de régression
  - cross_validation         : Cross-validation (K-Fold, Stratified, LOO)
  - hyperparameter_tuning    : GridSearch et RandomizedSearch

VISUALISATION:
  - metriques         : Métriques de classification (basique)
  - viz_normalite     : Visualisation normalité
  - viz_roc           : Courbes ROC et Precision-Recall
  - eda               : Analyse exploratoire complète

AUTRES:
  - all               : Afficher tout le code
    """)
