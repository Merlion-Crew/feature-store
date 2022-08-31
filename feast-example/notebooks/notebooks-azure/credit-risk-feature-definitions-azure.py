# Databricks notebook source
# MAGIC %md
# MAGIC # Feature Definition and Registration
# MAGIC This notebook has all **Feature Definitions and Feature Registrations** pertaining to the Home Credit Risk Default usecase
# MAGIC 
# MAGIC 
# MAGIC ### Walkthrough of Feature definition and Registration process
# MAGIC 1. Install all Library dependencies (Optionally you can install these libraries at the cluster level instead of notebook level)
# MAGIC 2. Mount the Storage Account in DBFS (needed to access any data you have from storage account)
# MAGIC 3. Create an environment variable with the Service Principal secret (Databricks settings should already have secrets redacted, so nobody can view/display the secrets)
# MAGIC    1. This environment variable is needed for accessing the registry during FEAST feature store initialization
# MAGIC 4. Create the Feast feature_store Configuration yaml file in the databricks workspace (via web terminal)
# MAGIC 5. Define Feature, Entity, Feature View and Feature Service for the risk model usecase
# MAGIC 6. Register the features to the registry (Azure blob)
# MAGIC 7. [Optional] List all feature views and feature service
# MAGIC 8. [Optional] Update an existing registry with new feature view
# MAGIC 9. [Optional] Update a feature service with a new feature view

# COMMAND ----------

# MAGIC %md
# MAGIC #### Install all Library dependencies in cluster
# MAGIC 1. In Databricks, go to Compute > YOUR-CLUSTER > Libraries > Install new
# MAGIC 2. Select PyPI and install the following dependencies
# MAGIC 
# MAGIC #### Dependencies
# MAGIC 1. **feast-azure-provider==0.3.0** | Feast Azure Provider (FEAST - Open source Feature Store)
# MAGIC 2. **snowflake-connector-python==2.7.4** | Snowflake Python Connector (SNOWFLAKE - Offline Storage system for features)
# MAGIC 3. **pyarrow==6.0.1**

# COMMAND ----------

# OPTIONAL: Run this to log only Errors and not clutter the stdout
import logging
logger = spark._jvm.org.apache.log4j
logging.getLogger("py4j.java_gateway").setLevel(logging.ERROR)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Clone repository where feature-store.yaml is located
# MAGIC This is used to fetch any data stored in the storage account

# COMMAND ----------

USER = "YOUR-GITLAB-USERNAME"
PAT = "YOUR-GITLAB-PAT-TOKEN" # GitLab Personal Access Token

# Clone main repository
!git clone https://$USER:$PAT@gitlab.com/YOUR-PROJECT/NAME.git

## Clone a branch
#!git clone -b YOUR-BRANCH-NAME --single-branch https://$USER:$PAT@gitlab.com/YOUR-PROJECT/NAME.git

# COMMAND ----------

# [DEBUG-OPTIONAL] Read config feature-store.yaml
!cat ./feature-store/notebooks/feature_repo/dev/feature_store.yaml

# COMMAND ----------

# MAGIC %md
# MAGIC #### Set Environment Variables
# MAGIC 
# MAGIC Set environment variables of Azure Resources and Snowflake offline store

# COMMAND ----------

storage_account_name = "YOUR-AZURE-STORAGE-ACCOUNT-NAME"
blob_container_name = "fs-reg-container" # Default
feast_registry_filename = "registry.db" # Default
snowflake_role_name = "YOUR-SNOWFLAKE-ROLE-NAME" # eg:ACCOUNTADMIN
snowflake_compute_name = "YOUR-SNOWFLAKE-COMPUTE-NAME" # eg:COMPUTE_WH
snowflake_database_name = "YOUR-SNOWFLAKE-DATABASE-NAME" # eg:CREDIT_FEATURES

# COMMAND ----------

# MAGIC %md
# MAGIC ###### Retrieve secret from Azure Key Vault
# MAGIC 
# MAGIC Fetch secrets from Azure Key Vault and set the secret as an environment variable.
# MAGIC 
# MAGIC This is used by feast during the feature registration to Azure Blob Container

# COMMAND ----------

# Reference - Command to fetch secret from Azure keyvault using Databricks Scope
# dbutils.secrets.get(scope = "<scope-name>", key = "<azure-keyvault-secret-name>")

import os

os.environ['REGISTRY_PATH'] = f"https://{storage_account_name}.blob.core.windows.net/{blob_container_name}/{feast_registry_filename}"
os.environ['SNOWFLAKE_ACC'] = dbutils.secrets.get(scope = "<scope-name>", key = "<azure-keyvault-secret-name>") # eg: myscope, SNOWFLAKE-ACC
os.environ['SNOWFLAKE_USER'] = dbutils.secrets.get(scope = "<scope-name>", key = "<azure-keyvault-secret-name>") # eg: myscope, SNOWFLAKE-USER
os.environ['SNOWFLAKE_PASS'] = dbutils.secrets.get(scope = "<scope-name>", key = "<azure-keyvault-secret-name>") # eg: myscope, SNOWFLAKE-PASS
os.environ['REDIS_CONN_STRING'] = dbutils.secrets.get(scope = "<scope-name>", key = "<azure-keyvault-secret-name>") # eg: myscope, REDIS-CONN-STRING
os.environ['REGISTRY_BLOB_KEY'] = dbutils.secrets.get(scope = "<scope-name>", key = "<azure-keyvault-secret-name>") # eg: myscope, REGISTRY-BLOB-KEY
#Note: REGISTRY-BLOB-KEY is storage account access key
#    : REDIS-CONN-STRING example <redis-name>.redis.cache.windows.net:6380,password=<some-password>,ssl=True,abortConnect=False


# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC #### Entity, Features, Feature View and Feature Service Definition
# MAGIC 
# MAGIC For the "Home Credit Risk Default" modeling usecase,
# MAGIC - use Snowflake tables as source of feature values
# MAGIC - register entity, feature views and feature service
# MAGIC 
# MAGIC The Feast Infrastructure Configuration (yaml) file is stored in the databricks cluster workspace via the web-terminal.
# MAGIC 
# MAGIC Copy of this yaml file can be found in the storage account.

# COMMAND ----------

from datetime import timedelta
from feast import Entity
from feast import FeatureStore
from feast import FeatureService
from feast import FeatureView
from feast import SnowflakeSource
from feast import ValueType
from google.protobuf.json_format import MessageToDict

#Configuration
repo_path = "./feature-store/notebooks/feature_repo/dev" #Feast Feature Repo Path
fs = FeatureStore(repo_path)

##
###Source Data
##
bureau_feature_table = SnowflakeSource(
    database=database_name,
    schema="PUBLIC",
    table="BUREAU_FEATURE_TABLE", #SNOWFLAKE TABLE NAME
    event_timestamp_column="EVENT_TIMESTAMP",
)

previous_loan_feature_table = SnowflakeSource(
    database=database_name,
    schema="PUBLIC",
    table="PREVIOUS_LOAN_FEATURES_TABLE",
    event_timestamp_column="EVENT_TIMESTAMP",
)

#Entity definition
customer =  Entity(name="SK_ID_CURR", value_type=ValueType.INT64, description="customer id",)

#Feature View(s) definition
bureau_view = FeatureView(
    name="bureau_feature_view",
    entities=["SK_ID_CURR"],
    ttl=timedelta(days=100),
    online=False,
    batch_source=bureau_feature_table,
    tags={},
)

previous_loan_view = FeatureView(
    name="previous_loan_feature_view",
    entities=["SK_ID_CURR"],
    ttl=timedelta(days=100),
    online=False,
    batch_source=previous_loan_feature_table,
    tags={},
)

#Feature Service Definition
risk_model_bureau_fs = FeatureService(
    name="risk_model_bureau_fs",
    features=[bureau_view, previous_loan_view]
)

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC #### Feature Registration via FEAST
# MAGIC 
# MAGIC - Register Features, Entity, Feature Views and Feature Service using Feast.
# MAGIC - Feature registration implies storing the definitions and associated metadata into Azure Blob Container
# MAGIC - List the feature views from the registry to ensure the registration was successful

# COMMAND ----------

repo_path = "./feature-store/notebooks/feature_repo/dev" #Feast Feature Repo Path
fs = FeatureStore(repo_path)
fs.apply([customer, bureau_view, previous_loan_view, risk_model_bureau_fs])
# List features from registry
print("====FEATURE VIEWS====")
fv_list = fs.list_feature_views()
for fv in fv_list:
    d=MessageToDict(fv.to_proto())
    print("Feature View Name:", d['spec']['name'])
    print("Entities:", d['spec']['entities'])
    print("Features:", d['spec']['features'])
    print("Source Type:", d['spec']['batchSource']['dataSourceClassType'])
    print("\n")

print("====FEATURE SERVICE====")
fs_list = fs.list_feature_services()
for fserv in fs_list:
    d=MessageToDict(fserv.to_proto())
    print("Feature Service Name:", d['spec']['name'])
    print("Feature Views:", d['spec']['features'])
    print("\n")


# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC #### Feature Consumption using Feast from the registry
# MAGIC 
# MAGIC - Use the Feature Service to fetch features from the feature store
# MAGIC - Convert it to a dataframe for use as input to model
# MAGIC 
# MAGIC This is simply to demonstrate and validate that the features registered across feature views are relavant for the usecase

# COMMAND ----------

from datetime import datetime
from feast import FeatureStore
import pandas as pd

repo_path = "./feature-store/notebooks/feature_repo/dev" #Feast Feature Repo Path
fs = FeatureStore(repo_path)
feature_service = fs.get_feature_service("risk_model_bureau_fs")
entity_df = pd.DataFrame.from_dict(
    {
        "SK_ID_CURR": [100002, 100003, 100004],
        "label": [1, 0, 1],
        "event_timestamp": [
            datetime(2022,2,24),
            datetime(2022,2,24),
            datetime(2022,2,24),
        ],
    }
)

bureau_df = fs.get_historical_features(
    entity_df=entity_df,
    features=feature_service
).to_df()

print(bureau_df.head(5))


# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC #### [OPTIONAL] Updating an existing Feature Registry
# MAGIC 
# MAGIC - Add and register a new Feature view to an existing registry

# COMMAND ----------

##Adding a new FeatureView to existing registry
from feast import Feature

#Configuration
repo_path = "./feature-store/notebooks/feature_repo/dev" #Feast Feature Repo Path
fs = FeatureStore(repo_path)

customer_info_table = SnowflakeSource(
    database=snowflake_database_name,
    schema="PUBLIC",
    table="CUSTOMER_FEATURES_TABLE",
    event_timestamp_column="EVENT_TIMESTAMP",
)

#Entity definition
customer =  Entity(name="SK_ID_CURR", value_type=ValueType.INT64, description="customer id",)

#Feature View definition
customer_view = FeatureView(
    name="customer_info_view",
    entities=["SK_ID_CURR"],
    ttl=timedelta(days=100),
    features=[
        Feature(name="OCCUPATION_TYPE", dtype=ValueType.STRING),
        Feature(name="AMT_INCOME_TOTAL", dtype=ValueType.FLOAT),
        Feature(name="NAME_INCOME_TYPE", dtype=ValueType.STRING),
        Feature(name="DAYS_LAST_PHONE_CHANGE", dtype=ValueType.FLOAT),
        Feature(name="ORGANIZATION_TYPE", dtype=ValueType.STRING),
        Feature(name="AMT_CREDIT", dtype=ValueType.FLOAT),
        Feature(name="AMT_GOODS_PRICE", dtype=ValueType.FLOAT),
        Feature(name="DAYS_REGISTRATION", dtype=ValueType.FLOAT),
        Feature(name="AMT_ANNUITY", dtype=ValueType.FLOAT),
        Feature(name="CODE_GENDER", dtype=ValueType.STRING),
        Feature(name="DAYS_ID_PUBLISH", dtype=ValueType.INT64),
        Feature(name="NAME_EDUCATION_TYPE", dtype=ValueType.STRING),
        Feature(name="DAYS_EMPLOYED", dtype=ValueType.INT64),
        Feature(name="DAYS_BIRTH", dtype=ValueType.INT64),
        Feature(name="EXT_SOURCE_1", dtype=ValueType.FLOAT),
        Feature(name="EXT_SOURCE_2", dtype=ValueType.FLOAT),
        Feature(name="EXT_SOURCE_3", dtype=ValueType.FLOAT),
    ],

    online=False,
    batch_source=customer_info_table,
    tags={},
)

#Feature Registration
fs.apply([customer, customer_view])


# COMMAND ----------

# MAGIC %md
# MAGIC #### [OPTIONAL] List all feature views and service from Registry
# MAGIC 
# MAGIC With the addition of new feature views/service, list all metadata from the registry to see the changes

# COMMAND ----------

# List features from registry
print("====FEATURE VIEWS====")
fv_list = fs.list_feature_views()
for fv in fv_list:
    d=MessageToDict(fv.to_proto())
    print("Feature View Name:", d['spec']['name'])
    print("Entities:", d['spec']['entities'])
    print("Features:", d['spec']['features'])
    print("Source Type:", d['spec']['batchSource']['dataSourceClassType'])
    print("\n")

print("====FEATURE SERVICE====")
fs_list = fs.list_feature_services()
for fserv in fs_list:
    d=MessageToDict(fserv.to_proto())
    print("Feature Service Name:", d['spec']['name'])
    print("Feature Views:", d['spec']['features'])
    print("\n")


# COMMAND ----------

#Update Feature Service Definition
risk_model_fs = FeatureService(
    name="risk_model_fs",
    features=[bureau_view, previous_loan_view, customer_view]
)

fs.apply(risk_model_fs)

# COMMAND ----------

print("====FEATURE SERVICE====")
fs_list = fs.list_feature_services()
for fserv in fs_list:
    d=MessageToDict(fserv.to_proto())
    print("Feature Service Name:", d['spec']['name'])
    print("Feature Views:", d['spec']['features'])
    print("\n")
