import os

def sf_feature_store_config(repo_path, path, account, username, pwd):
    
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)

    sf_feature_store_config="""
    project: eh_credit_01
    registry: 
        registry_store_type: feast_azure_provider.registry_store.AzBlobRegistryStore
        path: {}    
    provider: feast_azure_provider.azure_provider.AzureProvider
    offline_store:
        type: snowflake.offline
        account: {}
        user: {}
        password: {}
        role: DSA_USER_ROLE
        warehouse: COMMON_WH
        database: TEST
    online_store:
        type: sqlite
        path: /home/azureuser/data/online.db
    """.format(path, account, username, pwd)

    with open(repo_path+'/feature_store.yaml', 'w') as f:
        lines = f.write(sf_feature_store_config)
    print("Updated feature store setting.")