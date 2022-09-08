import pandas as pd
import numpy as np
import os
import json
import lightgbm as lgb
from feast import FeatureStore, RepoConfig
from feast.registry import RegistryConfig
from feast.infra.offline_stores.snowflake import SnowflakeOfflineStoreConfig
from feast.infra.online_stores.redis import RedisOnlineStoreConfig
import pickle

def init():
    global model
    global fs
    global feature_service

    feast_registry_path = os.getenv("REGISTRY_PATH")
    snowflake_acc = os.getenv("SNOWFLAKE_ACC")
    snowflake_user = os.getenv("SNOWFLAKE_USER")
    snowflake_pass = os.getenv("SNOWFLAKE_PASS")
    snowflake_compute_name= os.getenv("snowflake_compute_name")
    snowflake_database_name= os.getenv("snowflake_database_name")
    snowflake_role_name= os.getenv("snowflake_role_name")
    redis_conn_string = os.getenv("REDIS_CONN_STRING")


    print("connecting to registry...")
    reg_config = RegistryConfig(
        registry_store_type="feast_azure_provider.registry_store.AzBlobRegistryStore",
        path=feast_registry_path,
    )

    print("connecting to repo config...")
    repo_cfg = RepoConfig(
        project="dev",
        provider="feast_azure_provider.azure_provider.AzureProvider",
        registry=reg_config,
        offline_store=SnowflakeOfflineStoreConfig(
            account=snowflake_acc,
            user=snowflake_user,
            password=snowflake_pass,
            role=snowflake_role_name,
            database=snowflake_database_name,
            warehouse=snowflake_compute_name),
        online_store=RedisOnlineStoreConfig(connection_string=redis_conn_string)
    )

    print("connecting to feature store...")
    fs = FeatureStore(config=repo_cfg)

    ## load online features
    feature_service = fs.get_feature_service("credit_risk_model_fs")
    model_path = os.getenv("MODEL_PATH")
    ## Load Model
    model = pickle.load(open(f"{model_path}", "rb"))
    # model = lgb.Booster(model_file=model_path)

def run(data):
    rows = json.loads(data)

    features = fs.get_online_features(
        features=feature_service, entity_rows=[rows]
    ).to_df()
    features = features.fillna(np.nan)

    ## Prediction
    idx = 0
    example = pd.DataFrame(features.iloc[idx][1:]).T
    prob = model.predict_proba(example, pred_contrib=0)
    return( f"credit risk score of ID {features.iloc[idx][0]:.0f} is: {prob[0][1]}")

if __name__ == "__main__":
    init()
