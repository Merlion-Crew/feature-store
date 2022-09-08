# Feast Materialize to online store


### 1. Follow the steps from [airflow on aks setup](airflow-on-aks-setup.md) to set up an airflow image

The following should be set up after following the guide:

- Airflow image on AKS
- DAGs sync-ed up either through baking into docker image or through the GitSync functionality
- Ensure that the CeleryExecutor is used as Executor

Note: This step can be skipped if an Airflow image on AKS is already initialized.

### 2. Follow the steps on [managed identities on aks setup](https://gitlab.com/merlion-crew/feature-store/-/blob/cbtham-akspy/docs/python-container-setup.md#setting-up-aad-pod-identity) to get your managed identities set up

This would give you access to the relevant azure resources from the AKS cluster, namely:
- the blob storage account with the registry.db file
- the Azure key vault with the secrets

### 3. Create a key vault or use a key vault of your choice in Azure and put in the key vault the following secrets:

```
REDIS-CONN-STRING
SNOWFLAKE-ACC
SNOWFLAKE-USER
SNOWFLAKE-PASS
SNOWFLAKE-COMPUTE-NAME
SNOWFLAKE-DB
SNOWFLAKE-ROLE-NAME
```

Keep safe the URL of the key vault. This will be used in the next step.

### 4. Give your managed identity created in step two access to:
- the blob storage account with the registry.db file
- the Azure key vault with the secrets

Feel free to use the Azure portal.

### 5. Start up the Airflow instance and set up these three variables on the UI:

```
ENV - environment of choice, dev, uat, prod (keep to "dev" if unsure)
CONTOSO_USER_MSI_CLIENT_ID - Application ID of the managed identity created in step 2
KEY_VAULT_URL - URL of the key vault used in step 3
```

### 6. Check out your git branch of choice and copy one file and one folder from master to your branch:

- [materialization invoker DAG](dags/materialization_invoker.py) into your dags folder
- [feast_materialize folder](scripts/feast_materialize) to the scripts folder

Commit and push to your branch. After one minute, the files should all be synced to your Airflow instance. This can be double checked from the Airflow UI.

### 7. Run the materialization dag on Airflow!

# Troubleshooting

1. It takes time for the managed identity label to be set up correctly. Do a ` kubectl get pods ` and check if the status of the `airflow-worker-0' pod is 'Running'.

2. If authentication is failing, double check the IAM access on the blob storage and the key vault to make sure your managed identity has access to the resources


