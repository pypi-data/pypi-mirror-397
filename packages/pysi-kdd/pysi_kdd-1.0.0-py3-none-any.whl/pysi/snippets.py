"""
PySI - Ultimate Overkill Raw Snippets Collection
"""

SNIPPETS = {
    # ==========================================
    # 0. DATA MANIPULATION (Pandas/Numpy)
    # ==========================================
    "pandas_basics": {
        "cat": "Data Manipulation",
        "imports": "import pandas as pd",
        "code": """# Inspection
print(df.shape, df.columns)
print(df.info())
print(df.describe())
print(df.isnull().sum())
print(df['col'].value_counts(normalize=True))
print(df.head())

# Selection
subset = df[['col1', 'col2']]
row = df.loc[0] # Label
row = df.iloc[0] # Index
mask = df[df['col'] > 0]
query = df.query('col > 0 & col2 == "A"')"""
    },
    "pandas_cleaning": {
        "cat": "Data Manipulation",
        "imports": "import pandas as pd\nimport numpy as np",
        "code": """# Missing Values
df_drop = df.dropna() # Drop rows with NaN
df_drop_col = df.dropna(axis=1) # Drop cols
df_fill = df.fillna(0)
df_fill_mean = df.fillna(df.mean())
df_ffill = df.fillna(method='ffill')

# Duplicates
df_dedup = df.drop_duplicates()
df_dedup_subset = df.drop_duplicates(subset=['col1'])

# Types
df['col'] = df['col'].astype(float)
df['date'] = pd.to_datetime(df['date'])"""
    },
    "pandas_transform": {
        "cat": "Data Manipulation",
        "imports": "import pandas as pd",
        "code": """# Apply/Map
df['new'] = df['col'].apply(lambda x: x**2)
df['cat_code'] = df['cat'].map({'A': 1, 'B': 2})
df['col'] = df['col'].replace(-999, np.nan)

# String Ops
df['lower'] = df['text'].str.lower()
df['contains'] = df['text'].str.contains('pattern')

# Rename
df = df.rename(columns={'old': 'new'})
df = df.reset_index(drop=True)"""
    },
    "pandas_grouping": {
        "cat": "Data Manipulation",
        "imports": "import pandas as pd",
        "code": """# GroupBy
grp = df.groupby('cat')['val'].mean()
grp_agg = df.groupby('cat').agg({'val': ['mean', 'std'], 'val2': 'count'})

# Pivot
piv = df.pivot_table(index='row', columns='col', values='val', aggfunc='mean')

# Crosstab
ct = pd.crosstab(df['cat1'], df['cat2'], normalize='index')"""
    },
    "pandas_merge": {
        "cat": "Data Manipulation",
        "imports": "import pandas as pd",
        "code": """# Concat (Stack)
df_all = pd.concat([df1, df2], axis=0)

# Merge (Join)
df_merged = pd.merge(df1, df2, on='key', how='inner') # left, right, outer
df_joined = df1.join(df2, lsuffix='_l', rsuffix='_r')"""
    },
    "numpy_basics": {
        "cat": "Data Manipulation",
        "imports": "import numpy as np",
        "code": """# Arrays
arr = np.array([1, 2, 3])
zeros = np.zeros((3, 3))
ones = np.ones((2, 2))
range_arr = np.arange(0, 10, 2)
linspace = np.linspace(0, 1, 5)

# Reshape
reshaped = arr.reshape(-1, 1)

# Random
rand = np.random.rand(3, 3) # [0, 1)
randn = np.random.randn(3, 3) # Normal
randint = np.random.randint(0, 10, (3, 3))
np.random.seed(42)"""
    },

    # ==========================================
    # 1. DATA LOADING & BASICS
    # ==========================================
    "load_csv": {
        "cat": "Data Loading",
        "imports": "import pandas as pd",
        "code": """df = pd.read_csv("data.csv")"""
    },
    "load_sklearn": {
        "cat": "Data Loading",
        "imports": "from sklearn.datasets import fetch_california_housing, load_breast_cancer, load_iris\nimport pandas as pd",
        "code": """# California Housing
data = fetch_california_housing()
df = pd.DataFrame(data.data, columns=data.feature_names)
df['target'] = data.target

# Breast Cancer
data = load_breast_cancer()
df = pd.DataFrame(data.data, columns=data.feature_names)
df['target'] = data.target"""
    },
    "basic_stats": {
        "cat": "Statistics",
        "imports": "import numpy as np\nfrom scipy import stats",
        "code": """mean = np.mean(data)
median = np.median(data)
mode = stats.mode(data, keepdims=True).mode[0]
variance = np.var(data, ddof=1)
std_dev = np.std(data, ddof=1)
cv = std_dev / mean * 100
skewness = stats.skew(data)
kurtosis = stats.kurtosis(data)"""
    },
    "sample_size": {
        "cat": "Statistics",
        "imports": "",
        "code": """# Cochran (Infinite Pop)
n0 = (Z**2 * p * (1-p)) / e**2

# Cochran (Finite Pop)
n = n0 / (1 + (n0 - 1) / N)

# Yamane
n = N / (1 + N * e**2)

# Z-scores: 90%=1.645, 95%=1.96, 99%=2.576"""
    },
    "normality_tests": {
        "cat": "Statistics",
        "imports": "from scipy.stats import shapiro, kstest, normaltest, anderson",
        "code": """# Shapiro-Wilk (n < 5000)
stat, p = shapiro(data)

# Kolmogorov-Smirnov
stat, p = kstest(data, 'norm', args=(np.mean(data), np.std(data)))

# D'Agostino-Pearson (n >= 20)
stat, p = normaltest(data)

# Anderson-Darling
result = anderson(data, dist='norm')"""
    },
    "homogeneity_tests": {
        "cat": "Statistics",
        "imports": "from scipy.stats import bartlett, levene, fligner",
        "code": """# Bartlett (assumes normality)
stat, p = bartlett(g1, g2, g3)

# Levene (robust)
stat, p = levene(g1, g2, g3)

# Fligner-Killeen (non-parametric)
stat, p = fligner(g1, g2, g3)"""
    },
    "hypothesis_tests": {
        "cat": "Statistics",
        "imports": "from scipy.stats import ttest_ind, f_oneway, mannwhitneyu, kruskal, chi2_contingency",
        "code": """# T-test (2 groups)
stat, p = ttest_ind(g1, g2)

# ANOVA (3+ groups)
stat, p = f_oneway(g1, g2, g3)

# Mann-Whitney U (non-parametric t-test)
stat, p = mannwhitneyu(g1, g2)

# Kruskal-Wallis (non-parametric ANOVA)
stat, p = kruskal(g1, g2, g3)

# Chi-Square (Categorical)
chi2, p, dof, ex = chi2_contingency(pd.crosstab(v1, v2))"""
    },

    # ==========================================
    # 2. PREPROCESSING
    # ==========================================
    "missing_values": {
        "cat": "Preprocessing",
        "imports": "from sklearn.impute import SimpleImputer, KNNImputer\nfrom sklearn.experimental import enable_iterative_imputer\nfrom sklearn.impute import IterativeImputer",
        "code": """# Simple (Mean/Median)
imp = SimpleImputer(strategy='mean')
X_imp = imp.fit_transform(X)

# KNN
imp_knn = KNNImputer(n_neighbors=5)
X_knn = imp_knn.fit_transform(X)

# MICE (Iterative)
imp_mice = IterativeImputer(random_state=42)
X_mice = imp_mice.fit_transform(X)"""
    },
    "scaling": {
        "cat": "Preprocessing",
        "imports": "from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler",
        "code": """# Min-Max (0-1)
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Standard (Z-score)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Robust (Median/IQR)
scaler = RobustScaler()
X_scaled = scaler.fit_transform(X)"""
    },
    "transformations": {
        "cat": "Preprocessing",
        "imports": "from sklearn.preprocessing import PowerTransformer\nimport numpy as np",
        "code": """# Box-Cox (Positive only)
pt = PowerTransformer(method='box-cox')
X_trans = pt.fit_transform(X)

# Yeo-Johnson (All values)
pt = PowerTransformer(method='yeo-johnson')
X_trans = pt.fit_transform(X)

# Log
X_log = np.log1p(X)"""
    },
    "encoding": {
        "cat": "Preprocessing",
        "imports": "from sklearn.preprocessing import LabelEncoder, OneHotEncoder\nimport pandas as pd",
        "code": """# Label Encoding
le = LabelEncoder()
y_enc = le.fit_transform(y)

# One-Hot Encoding
enc = OneHotEncoder(sparse=False, drop='first')
X_enc = enc.fit_transform(X_cat)

# Pandas Dummies
df_enc = pd.get_dummies(df, columns=['col'], drop_first=True)

# Target Encoding (Manual)
means = df.groupby('cat')['target'].mean()
df['cat_enc'] = df['cat'].map(means)"""
    },

    # ==========================================
    # 3. FEATURE ENGINEERING
    # ==========================================
    "feature_selection": {
        "cat": "Feature Engineering",
        "imports": """from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif, chi2, VarianceThreshold, RFE, RFECV
from sklearn.linear_model import Lasso, LogisticRegression""",
        "code": """# Filter: Variance
sel = VarianceThreshold(threshold=0.1)

# Filter: K-Best (ANOVA/Chi2/Mutual Info)
sel = SelectKBest(score_func=f_classif, k=10)
X_new = sel.fit_transform(X, y)

# Wrapper: RFE
rfe = RFE(estimator=LogisticRegression(), n_features_to_select=10)
X_new = rfe.fit_transform(X, y)

# Embedded: Lasso
lasso = Lasso(alpha=0.01)
lasso.fit(X, y)
feats = np.where(lasso.coef_ != 0)[0]"""
    },
    "dim_reduction": {
        "cat": "Feature Engineering",
        "imports": "from sklearn.decomposition import PCA, KernelPCA\nfrom sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA\nfrom sklearn.manifold import TSNE",
        "code": """# PCA
pca = PCA(n_components=0.95) # Keep 95% variance
X_pca = pca.fit_transform(X)

# LDA (Supervised)
lda = LDA(n_components=2)
X_lda = lda.fit_transform(X, y)

# t-SNE (Visualization)
tsne = TSNE(n_components=2)
X_tsne = tsne.fit_transform(X)

# Kernel PCA (Non-linear)
kpca = KernelPCA(n_components=2, kernel='rbf')
X_kpca = kpca.fit_transform(X)"""
    },

    # ==========================================
    # 4. OUTLIERS
    # ==========================================
    "outlier_detection": {
        "cat": "Outliers",
        "imports": "import numpy as np\nfrom sklearn.ensemble import IsolationForest\nfrom sklearn.neighbors import LocalOutlierFactor\nfrom sklearn.cluster import DBSCAN",
        "code": """# IQR
Q1, Q3 = np.percentile(data, [25, 75])
IQR = Q3 - Q1
outliers = (data < Q1 - 1.5*IQR) | (data > Q3 + 1.5*IQR)

# Z-Score
z = np.abs((data - np.mean(data)) / np.std(data))
outliers = z > 3

# Isolation Forest
iso = IsolationForest(contamination=0.1)
y_pred = iso.fit_predict(X) # -1 = outlier

# LOF
lof = LocalOutlierFactor(contamination=0.1)
y_pred = lof.fit_predict(X)

# DBSCAN
db = DBSCAN(eps=0.5, min_samples=5)
y_pred = db.fit_predict(X) # -1 = noise"""
    },
    "outlier_treatment": {
        "cat": "Outliers",
        "imports": "from scipy.stats.mstats import winsorize",
        "code": """# Winsorization (Cap at 5th and 95th percentiles)
data_clean = winsorize(data, limits=[0.05, 0.05])"""
    },

    # ==========================================
    # 5. BALANCING
    # ==========================================
    "class_imbalance": {
        "cat": "Balancing",
        "imports": "from imblearn.over_sampling import SMOTE, ADASYN, RandomOverSampler\nfrom imblearn.under_sampling import RandomUnderSampler, NearMiss, TomekLinks",
        "code": """# Oversampling
smote = SMOTE()
adasyn = ADASYN()
ros = RandomOverSampler()
X_res, y_res = smote.fit_resample(X, y)

# Undersampling
rus = RandomUnderSampler()
nm = NearMiss(version=1)
tl = TomekLinks()
X_res, y_res = rus.fit_resample(X, y)"""
    },

    # ==========================================
    # 6. REGRESSION MODELS
    # ==========================================
    "reg_linear": {
        "cat": "Regression",
        "imports": "from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet",
        "code": """lr = LinearRegression()
ridge = Ridge(alpha=1.0)
lasso = Lasso(alpha=1.0)
enet = ElasticNet(alpha=1.0, l1_ratio=0.5)"""
    },
    "reg_nonlinear": {
        "cat": "Regression",
        "imports": """from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import xgboost as xgb""",
        "code": """knn = KNeighborsRegressor(n_neighbors=5)
svr = SVR(kernel='rbf')
tree = DecisionTreeRegressor(max_depth=5)
rf = RandomForestRegressor(n_estimators=100)
gb = GradientBoostingRegressor()
xgb_reg = xgb.XGBRegressor()"""
    },
    "reg_polynomial": {
        "cat": "Regression",
        "imports": "from sklearn.preprocessing import PolynomialFeatures\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.linear_model import LinearRegression",
        "code": """model = Pipeline([
    ('poly', PolynomialFeatures(degree=2)),
    ('linear', LinearRegression())
])"""
    },

    # ==========================================
    # 7. CLASSIFICATION MODELS
    # ==========================================
    "clf_models": {
        "cat": "Classification",
        "imports": """from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier""",
        "code": """lr = LogisticRegression()
knn = KNeighborsClassifier(n_neighbors=5)
nb = GaussianNB()
svm = SVC(probability=True)
tree = DecisionTreeClassifier()
rf = RandomForestClassifier(n_estimators=100)
mlp = MLPClassifier()"""
    },
    "clf_balanced": {
        "cat": "Classification",
        "imports": "from sklearn.linear_model import LogisticRegression\nfrom imblearn.ensemble import BalancedRandomForestClassifier, EasyEnsembleClassifier",
        "code": """lr_bal = LogisticRegression(class_weight='balanced')
brf = BalancedRandomForestClassifier()
eec = EasyEnsembleClassifier()"""
    },

    # ==========================================
    # 8. ENSEMBLE
    # ==========================================
    "ensemble_methods": {
        "cat": "Ensemble",
        "imports": "from sklearn.ensemble import BaggingRegressor, StackingRegressor, VotingRegressor, AdaBoostRegressor",
        "code": """# Bagging
bag = BaggingRegressor(base_estimator=DecisionTreeRegressor(), n_estimators=50)

# AdaBoost
ada = AdaBoostRegressor(n_estimators=50)

# Voting
vote = VotingRegressor([('lr', lr), ('rf', rf)])

# Stacking
stack = StackingRegressor(estimators=[('lr', lr), ('rf', rf)], final_estimator=LinearRegression())"""
    },

    # ==========================================
    # 9. EVALUATION
    # ==========================================
    "metrics_reg": {
        "cat": "Evaluation",
        "imports": "from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error\nimport numpy as np",
        "code": """mse = mean_squared_error(y_true, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_true, y_pred)
r2 = r2_score(y_true, y_pred)
mape = mean_absolute_percentage_error(y_true, y_pred)

# Adjusted R2
n, p = X.shape
r2_adj = 1 - (1-r2)*(n-1)/(n-p-1)"""
    },
    "metrics_clf": {
        "cat": "Evaluation",
        "imports": "from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, matthews_corrcoef, balanced_accuracy_score, confusion_matrix, classification_report",
        "code": """acc = accuracy_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)
roc = roc_auc_score(y_true, y_proba)
mcc = matthews_corrcoef(y_true, y_pred)
bal_acc = balanced_accuracy_score(y_true, y_pred)
cm = confusion_matrix(y_true, y_pred)
report = classification_report(y_true, y_pred)"""
    },
    "residuals": {
        "cat": "Evaluation",
        "imports": "from statsmodels.stats.diagnostic import het_breuschpagan\nfrom statsmodels.stats.stattools import durbin_watson\nimport matplotlib.pyplot as plt\nimport scipy.stats as stats",
        "code": """resid = y_true - y_pred

# Durbin-Watson (Autocorrelation, ideal=2)
dw = durbin_watson(resid)

# Breusch-Pagan (Heteroscedasticity)
bp = het_breuschpagan(resid, X)

# Q-Q Plot
stats.probplot(resid, dist="norm", plot=plt)
plt.show()"""
    },

    # ==========================================
    # 10. VALIDATION & TUNING
    # ==========================================
    "cross_validation": {
        "cat": "Validation",
        "imports": "from sklearn.model_selection import cross_val_score, KFold, StratifiedKFold, LeaveOneOut",
        "code": """kf = KFold(n_splits=5, shuffle=True)
skf = StratifiedKFold(n_splits=5, shuffle=True)
loo = LeaveOneOut()

scores = cross_val_score(model, X, y, cv=kf, scoring='accuracy')
print(f"Mean: {scores.mean():.3f} +/- {scores.std()*2:.3f}")"""
    },
    "tuning": {
        "cat": "Validation",
        "imports": "from sklearn.model_selection import GridSearchCV, RandomizedSearchCV\nfrom scipy.stats import uniform",
        "code": """# Grid Search
param_grid = {'C': [0.1, 1, 10]}
grid = GridSearchCV(model, param_grid, cv=5)
grid.fit(X, y)

# Random Search
param_dist = {'C': uniform(0.1, 10)}
rand = RandomizedSearchCV(model, param_dist, n_iter=20, cv=5)
rand.fit(X, y)"""
    },

    # ==========================================
    # 11. ADVANCED
    # ==========================================
    "causal_inference": {
        "cat": "Advanced",
        "imports": "from sklearn.linear_model import LinearRegression",
        "code": """# Control for confounder Z
# Model: Y ~ X + Z
model = LinearRegression()
model.fit(df[['X', 'Z']], df['Y'])
causal_effect = model.coef_[0]"""
    },
    "explainability": {
        "cat": "Advanced",
        "imports": "import shap",
        "code": """# SHAP
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

shap.summary_plot(shap_values, X)
shap.force_plot(explainer.expected_value, shap_values[0,:], X.iloc[0,:])"""
    },

    # ==========================================
    # 12. CHEATSHEET
    # ==========================================
    "cheatsheet": {
        "cat": "Reference",
        "imports": "",
        "code": """NORMALITY: Shapiro (n<5000), KS, D'Agostino
HOMOGENEITY: Bartlett (normal), Levene (robust), Fligner (non-param)
OUTLIERS: IQR (1.5), Z-Score (>3), LOF (density), IsoForest (high-dim)
SCALING: MinMax (0-1), Standard (Z), Robust (Median/IQR)
IMBALANCE: F1, ROC-AUC, MCC, BalancedAcc (Avoid Accuracy!)
SELECTION: Filter (Chi2/ANOVA), Wrapper (RFE), Embedded (Lasso/RF)
SAMPLE SIZE: Cochran (Z^2*p*q/e^2), Yamane (N/(1+Ne^2))"""
    }
}

CATS = sorted(set(s["cat"] for s in SNIPPETS.values()))
