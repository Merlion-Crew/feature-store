# Feathr Home credit default notebooks

These notebooks are conversions from the `feast` implementation to `feathr` implementation that was created to explore the `feast` capabilities.

The following to note:
1. 3 Notebooks
    1. `burea_bureau-balance.ipynb` - this notebook has two datasource, the `bureau.csv` and `bureau_balance.csv` which were then mereded using `bureau.csv` as a spine dataset.
    1. `instalment-payments_credit_card_balance.ipynb` - this notebook has two datasource, the `installments_payments.csv` and `credit_card_balance.csv` which were then merged using `installments_payments.csv` as a spine dataset.
    1. `static_features.ipynb` - this notebook has only one datasource - a pass through, from the `application_train.csv`
1. These notebooks demonstrates the `pre-processing` feature of `feathr` only.


## Setup
1. Provisioning:
    1. Run `scripts/azure_resource_provision.sh`
        1. Make sure to change the `<SUBCRIPTION_ID>` and set `<RESOUCE_PREFFIX>` fields
        1. Please take note of the output, it would be needed to run the notebook
    1. Environment variables on the notebooks
        1. Make sure to change this cell with the correct values
            - os.environ['REDIS_PASSWORD'] = ''
            - os.environ['AZURE_CLIENT_ID'] = ''
            - os.environ['AZURE_TENANT_ID'] = '' 
            - os.environ['AZURE_CLIENT_SECRET'] = ''
1. Upload the csv files to the storage
    1. Download the `Home Credit Default Risk` data from [Kaggle](https://www.kaggle.com/competitions/home-credit-default-risk/data) and store it in the `data` folder.
    1. Run the `scripts/upload_home_credit_data.sh` to upload it to the provisioned storage.
        1. Make sure to substitute the values
        1. This script would upload all of the `csv` file inside the `data` folder.
1. Update the python libraries of `Azure Synapse`
    1. Go to the provisioned `Azure Synapse`
    1. Click the `Apache Spark pools` of `Analytic pools` (left pane) and select the `Spark` pool to update.
    1. On the Spark pool page, click on the `Packages` of `Settings` (left pane). From here click the `Upload` button of `Requirements file` to upload the `requirements.txt`.
    1. Check from the `Azure Synapse` studio to check the updating process.
        1. Open the `Azure Synapse` studio
        1. Go to `Monitor` in the left pane and `Apache Spark applications` pane. In this pane you could verify the status of the job that is running to update the Spark pool.

## Notes on the notebooks
1. These notebooks only utilized the `pre-processing` feature of `feathr`.
1. There are several gotchas on these notebooks:
    1. If anchors have an aggregated feature and an on-the-fly column features, the anchors should have separate datasource - even though they are pointing to the same csv.
    1. If anchors have pass-thru and a created on-the-fly column features, they could be on the same datasource.
    1. Can't mix a pass-thru and a window aggregated/transformed feature definition.
    1. Pre processing methods
        1. Expects a Spark Dataframe as input and output.
            1. The `feast` implementation uses Panda Dataframe, so, to minimize code conversion between the the two, inside the pre processing method the passed dataframe (Spark) would be converted into Panda dataframe prior to calling the Panda methods (same method from the `feast` implementation). After the Panda dataframe manipulation, this dataframe would be converted back to Spark dataframe as a return value.
        1. Can't do method chaining (calling another method) inside the pre processing method. To overcome this limitation, a nested function is used (function within a function). So the `feathr` spark job could execute the pre processing method, then this method would in turn call other methods that is inside the preprocessing methods.
            ``` python
            def bureau_preprocessing(df: DataFrame) -> DataFrame:
                
                def bureauBalanceRollingCreditLoan(df):
                    PASS
                
                df = bureauBalanceRollingCreditLoan(df)
                return df
            ```
        1. Importing Python packages has to be inside the pre processing methods.
            ``` python
            def bureau_preprocessing(df: DataFrame) -> DataFrame:
                import datetime
                import pandas as pd
                from pyspark import sql
                from sklearn.preprocessing import OneHotEncoder, MinMaxScaler

                def bureauBalanceRollingCreditLoan(df):
                    PASS
                
                df = bureauBalanceRollingCreditLoan(df)
                return df
            ```
        1. During feature definition, `feathr` assumes that the `feature`(column) is in the datasource. So it's is important to check if the output features of the pre processing methods contains the fields defined in the feature defition. This is the reason that in the pre processing method, there is a Panda merge method call. And subsequently, after this method call, a column rename is called. This is because that during the merge call, if there is a same column name, Panda would rename the duplicates with a suffix of `_x` and the other with `_y`. Removing the `_x` suffix (only) would retain the original column name that is being referenced in the feature definition.
    1. At the time of this writing, UDF transformation still has some problems, so it was not used in these notebooks. For example, if using a UDF expression such as `if_else` the spark job would always fail. The `feathr` team is currently fixing this issue.