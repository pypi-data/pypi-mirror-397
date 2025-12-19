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
from sklearn.neighbors import LocalOutlierFactor
from sklearn.ensemble import IsolationForest
from sklearn.covariance import EmpiricalCovariance
from sklearn.metrics import (classification_report, confusion_matrix, 
                            balanced_accuracy_score, matthews_corrcoef,
                            roc_curve, auc, precision_recall_curve, f1_score)
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

# STATISTIQUES DESCRIPTIVES
data = np.array([12, 15, 18, 20, 22, 25, 28, 30, 35, 40])

# Mesures de tendance centrale
moyenne = np.mean(data)
mediane = np.median(data)
mode = stats.mode(data, keepdims=True).mode[0]

# Mesures de dispersion
ecart_type = np.std(data, ddof=1)
variance = np.var(data, ddof=1)
q1 = np.percentile(data, 25)
q3 = np.percentile(data, 75)
iqr = q3 - q1
etendue = np.max(data) - np.min(data)

# Coefficient de variation
cv = (ecart_type / moyenne) * 100

# Forme de distribution
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

# CALCUL TAILLE D'ÉCHANTILLON

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

# Créer et entraîner modèle
X, y = make_classification(n_samples=1000, weights=[0.7, 0.3], random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
y_pred_proba = clf.predict_proba(X_test)[:, 1]

# Matrice de confusion
cm = confusion_matrix(y_test, y_pred)
print("Matrice de Confusion:")
print(cm)

# Métriques
ba = balanced_accuracy_score(y_test, y_pred)
mcc = matthews_corrcoef(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"\\nBalanced Accuracy: {ba:.4f}")
print(f"MCC: {mcc:.4f}")
print(f"F1-Score: {f1:.4f}")

# ROC-AUC
roc_auc = roc_auc_score(y_test, y_pred_proba)
print(f"ROC-AUC: {roc_auc:.4f}")

# Classification Report
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

# VISUALISATION DE LA NORMALITÉ
data = np.random.normal(100, 15, 1000)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Histogramme
axes[0, 0].hist(data, bins=30, edgecolor='black', alpha=0.7)
axes[0, 0].axvline(np.mean(data), color='r', linestyle='--', label='Moyenne')
axes[0, 0].axvline(np.median(data), color='g', linestyle='--', label='Médiane')
axes[0, 0].set_title('Histogramme')
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)

# Q-Q Plot
stats.probplot(data, dist="norm", plot=axes[0, 1])
axes[0, 1].set_title('Q-Q Plot')
axes[0, 1].grid(alpha=0.3)

# Boxplot
axes[1, 0].boxplot(data)
axes[1, 0].set_title('Boxplot')
axes[1, 0].grid(alpha=0.3)

# Densité
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

# VISUALISATION COURBES ROC ET PRECISION-RECALL

# Préparer données
X, y = make_classification(n_samples=1000, weights=[0.7, 0.3], random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)
y_pred_proba = clf.predict_proba(X_test)[:, 1]

# Courbes
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)

axes[0].plot(fpr, tpr, lw=2, label=f'ROC (AUC = {roc_auc:.2f})')
axes[0].plot([0, 1], [0, 1], 'k--', lw=2)
axes[0].set_xlabel('False Positive Rate')
axes[0].set_ylabel('True Positive Rate')
axes[0].set_title('ROC Curve')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Precision-Recall Curve
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

# ANALYSE EXPLORATOIRE COMPLÈTE
df = pd.DataFrame(np.random.randn(1000, 5), columns=['A', 'B', 'C', 'D', 'E'])
df['Target'] = np.random.choice([0, 1], size=1000, p=[0.7, 0.3])

# 1. Informations générales
print("="*80)
print("INFORMATIONS GÉNÉRALES")
print("="*80)
print(df.info())

# 2. Statistiques descriptives
print("\\n" + "="*80)
print("STATISTIQUES DESCRIPTIVES")
print("="*80)
print(df.describe())

# 3. Valeurs manquantes
print("\\n" + "="*80)
print("VALEURS MANQUANTES")
print("="*80)
print(df.isnull().sum())

# 4. Duplicates
print("\\n" + "="*80)
print("VALEURS DUPLIQUÉES")
print("="*80)
print(f"Nombre de duplicates: {df.duplicated().sum()}")

# 5. Distribution target
print("\\n" + "="*80)
print("DISTRIBUTION TARGET")
print("="*80)
print(df['Target'].value_counts())
print("\\nPourcentages:")
print(df['Target'].value_counts(normalize=True) * 100)

# 6. Corrélations
print("\\n" + "="*80)
print("MATRICE DE CORRÉLATION")
print("="*80)
numeric_cols = df.select_dtypes(include=[np.number]).columns
corr_matrix = df[numeric_cols].corr()
print(corr_matrix)

# 7. Visualisation corrélations
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0)
plt.title('Matrice de Corrélation')
plt.tight_layout()
plt.show()
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
        'eda': eda_complete
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

ÉVALUATION ET VISUALISATION:
  - metriques         : Métriques de classification
  - viz_normalite     : Visualisation normalité
  - viz_roc           : Courbes ROC et Precision-Recall
  - eda               : Analyse exploratoire complète

AUTRES:
  - all               : Afficher tout le code
    """)
    print("="*80)
