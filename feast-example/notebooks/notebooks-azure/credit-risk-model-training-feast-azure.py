# Databricks notebook source
# MAGIC %md
# MAGIC ## Model Training with FEAST
# MAGIC - This notebook performs Model Training and Scoring by building the train/test dataset using features from Feast Feature Store
# MAGIC   - Feast for Feature Store
# MAGIC   - Uses Azure Storage Account
# MAGIC   - Uses MLFlow
# MAGIC
# MAGIC ### Prerequisites
# MAGIC - Ensure  **Feature Definitions and Feature Registrations** pertaining to the Home Credit Risk Default usecase is executed.

# COMMAND ----------

# All library installations

%pip install feast-azure-provider
%pip install azure-cli
%pip install snowflake-connector-python==2.7.4
%pip install pyarrow==6.0.1
%pip install lightgbm
%pip install mlflow

# COMMAND ----------

import logging
logger = spark._jvm.org.apache.log4j
logging.getLogger("py4j.java_gateway").setLevel(logging.ERROR)

# COMMAND ----------

!feast version

# COMMAND ----------

import lightgbm as lgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import metrics
import lightgbm as lgb
from sklearn.metrics import roc_auc_score, roc_curve

import matplotlib.pyplot as plt
import mlflow
import mlflow.lightgbm

import time
import warnings
warnings.filterwarnings("ignore")

from datetime import datetime, timedelta

from feast import FeatureStore

# COMMAND ----------

# load labels
id_train = pd.read_csv('/dbfs/FileStore/data/application_train.csv')[['SK_ID_CURR', 'TARGET']]

id_train.info()

# COMMAND ----------

# load features from Feast
fs = FeatureStore(repo_path="/databricks/driver/risk_model") #Feast Feature Repo Path

entity_df = pd.DataFrame.from_dict(
    {
        "SK_ID_CURR": id_train['SK_ID_CURR'].tolist(),
        "TARGET": id_train['TARGET'].tolist(),
        "event_timestamp": [datetime(2022,2,24)]*id_train.shape[0]
    }
)

# use feature service of this model
feature_service = fs.get_feature_service("risk_model_fs")
train_df = fs.get_historical_features(
    entity_df=entity_df,
    features=feature_service
).to_df()

# COMMAND ----------

train_df.info()

# COMMAND ----------

# created_timestamp will be a duplicated features for feature service, should list all features in Feature Service
#train_df = train_df.drop(columns=['bureau_feature_view__CREATED_TIMESTAMP', 'previous_loan_feature_view__CREATED_TIMESTAMP'])

# # drop id an timestamp
train_df = train_df.sort_values(by='SK_ID_CURR')
train_df = train_df.drop(columns = ['event_timestamp', 'SK_ID_CURR'])

# COMMAND ----------

train_df.info()

# COMMAND ----------

y = train_df['TARGET']
X = train_df.drop(columns = ['TARGET'])

# encode category features
for c in X.columns:
    col_type = X[c].dtype
    if col_type == 'object' or col_type.name == 'category':
        X[c] = X[c].astype('category')
        X[c] = X[c].cat.codes

# COMMAND ----------

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.6, random_state=42)
X_test, X_valid, y_test, y_valid = train_test_split(X_test, y_test, test_size=0.5, random_state=42)

print( len(X_train), len(y_train), sum(y_train))
print( len(X_valid), len(y_valid), sum(y_valid))
print( len(X_test), len(y_test), sum(y_test))

# COMMAND ----------

mlflow.lightgbm.autolog()

with mlflow.start_run(run_name="lgbm_simple"):

    # LightGBM parameters found by Bayesian optimization
    clf = lgb.LGBMClassifier(
                    objective="binary",
                    n_estimators=1000,
                    learning_rate=0.01,
                    num_leaves=34,
                    max_depth=9,
                    random_state=42
                )

    clf.fit(X_train,
            y_train,
            eval_set=[(X_valid, y_valid)],
            eval_metric=["AUC","binary_logloss"],
            verbose= 100,
            early_stopping_rounds= 100
           )

    # # evaluate model: ROC AUC
    y_pred_proba = clf.predict_proba(X_test)
    roc_auc = metrics.roc_auc_score(y_test, y_pred_proba[:, 1])
    print(f"ROC AUC score: {roc_auc:.2f}")


    # log metrics
    mlflow.log_metrics({"roc_auc": roc_auc})




# COMMAND ----------

# feature importance

import matplotlib.pyplot as plt
import seaborn as sns
feature_imp = pd.DataFrame(sorted(zip(clf.feature_importances_,X.columns)), columns=['Value','Feature'])

plt.figure(figsize=(10, 10))
sns.barplot(x="Value", y="Feature", data=feature_imp.sort_values(by="Value", ascending=False))
plt.tight_layout()
plt.show()
# feature_imp.sort_values(by="Value", ascending=False).head()
# plt.savefig('lgbm_importances-01.png')

# COMMAND ----------

# Evaluation

y_pred_proba = clf.predict_proba(X_test)[:, 1]
roc_auc = metrics.roc_auc_score(y_test, y_pred_proba)
print(f"ROC AUC score: {roc_auc:.2f}")

# COMMAND ----------

metrics.plot_roc_curve(clf, X_test, y_test)
plt.show()

# COMMAND ----------

# Data to plot precision - recall curve
precision, recall, thresholds = metrics.precision_recall_curve(y_test, y_pred_proba)
# Use AUC function to calculate the area under the curve of precision recall curve
auc_precision_recall = metrics.auc(recall, precision)
print(f"precision-recall AUC score: {auc_precision_recall:.2f}")

# COMMAND ----------

plt.plot(recall, precision)
plt.show()
