import os
from feast import FeatureStore
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from datetime import timedelta, datetime
from airflow.models import Variable

credential = DefaultAzureCredential(managed_identity_client_id=Variable.get("CONTOSO_USER_MSI_CLIENT_ID"))
kv = SecretClient(Variable.get("KEY_VAULT_URL"), credential=credential)

os.environ['SNOWFLAKE_ROLE_NAME'] = kv.get_secret("SNOWFLAKE-ROLE-NAME").value
os.environ['SNOWFLAKE_COMPUTE_NAME'] = kv.get_secret("SNOWFLAKE-COMPUTE-NAME").value
os.environ['SNOWFLAKE_DB_NAME'] = kv.get_secret("SNOWFLAKE-DB").value
os.environ['SNOWFLAKE_ACC'] = kv.get_secret("SNOWFLAKE-ACC").value
os.environ['SNOWFLAKE_USER'] = kv.get_secret("SNOWFLAKE-USER").value
os.environ['SNOWFLAKE_PASS'] = kv.get_secret("SNOWFLAKE-PASS").value
os.environ['REDIS_CONN_STRING'] = kv.get_secret("REDIS-CONN-STRING").value
os.environ['REGISTRY_PATH'] = kv.get_secret("FEAST-REGISTRY-PATH").value


#Configuration
repo_path = os.getenv('AIRFLOW_HOME')+"/dags/repo/feature_repo/"+Variable.get("ENV") # Feast Feature Repo Path
fs = FeatureStore(repo_path)

# materialize all values from a year ago
fs.materialize(start_date=datetime.utcnow() - timedelta(days=365), end_date=datetime.utcnow() - timedelta(minutes=10))
