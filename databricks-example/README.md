# Databricks Feature Store Home credit default notebooks

## Notebook - Feature Transformation and Ingestion - dbNotebook.py

Open this notebook in the databricks workspace.

## Setup
1. Upload the csv files to the databricks workspace
    1. Download the `Home Credit Default Risk` data from [Kaggle](https://www.kaggle.com/competitions/home-credit-default-risk/data) and store it in the `data` folder.
    1. Split the `installments_payments.csv` into two - if you would encounter a databricks upload limit.
        1. Execute `./scripts/split_installments_payments.py`, this would create two `csv`'s, the `installments_payments0.csv` and `installments_payments1.csv`.
    1. Create databricks workspace in Azure portal.
        1. Follow the `Setup Azure Databricks instance` section of this document `./docs/setup-dbfs.md`.
    1. Upload the `csv` files to the newly created databricks workspace.
        1. Select the `Data` section (main menu - left panel), then click `Create Table`.
            1. On the `Upload File` tab, drop or browse the `csv` files to be uploaded. Upload all files downloaded from `Kaggle` except for `installments_payments.csv`. The `installments_payments0.csv` and `installments_payments1.csv` would be uploaded instead - the output of the splitting section.
1. Setup Azure SQL to publish online
    1. Follow this [link](https://docs.microsoft.com/en-us/azure/azure-sql/database/single-database-create-quickstart?view=azuresql&tabs=azure-portal) to setup the Azure SQL.
    1. On the last cell of the notebook, supply the neccessary information to connect to the newly creted Azure SQL.