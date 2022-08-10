# Databricks notebook source
import pandas as pd
import numpy as np
import datetime
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
import warnings
warnings.filterwarnings("ignore")
import os

# COMMAND ----------

base_folder='/dbfs/FileStore/tables/'
application_train = pd.read_csv(f'{base_folder}application_train.csv')
application_test = pd.read_csv(f'{base_folder}application_test.csv')
bureau = pd.read_csv(f'{base_folder}bureau.csv')
bureau_balance = pd.read_csv(f'{base_folder}bureau_balance.csv')
credit_card_balance = pd.read_csv(f'{base_folder}credit_card_balance.csv')
pos_cash_balance = pd.read_csv(f'{base_folder}POS_CASH_balance.csv')
previous_application = pd.read_csv(f'{base_folder}previous_application.csv')
homecredit_columns_description = pd.read_csv(f'{base_folder}HomeCredit_columns_description.csv',encoding='latin1')

installments_payments0 = pd.read_csv(f'{base_folder}installments_payments0.csv')
installments_payments1 = pd.read_csv(f'{base_folder}installments_payments1.csv')
installments_payments_names=[
    'SK_ID_PREV',
    'SK_ID_CURR',
    'NUM_INSTALMENT_VERSION',
    'NUM_INSTALMENT_NUMBER',
    'DAYS_INSTALMENT',
    'DAYS_ENTRY_PAYMENT',
    'AMT_INSTALMENT',
    'AMT_PAYMENT'
]
installments_payments = pd.concat([installments_payments1[installments_payments_names], installments_payments1[installments_payments_names]], axis=0)


# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. static features

# COMMAND ----------

application_train['EVENT_TIMESTAMP']=datetime.datetime(2022,2,24)
application_train['CREATED_TIMESTAMP']=datetime.datetime.now()
application_train.head()
static_features = spark.createDataFrame(application_train)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Bureau features
# MAGIC 
# MAGIC 1. parent dataset: bureau.csv 
# MAGIC     - count aggregation features created
# MAGIC     - average aggregation features created
# MAGIC     - debt:credit ratio feature created
# MAGIC 1. child dataset: bureau_balance.csv
# MAGIC     - rolling window credit loan status feature will be created and joined to parent dataset
# MAGIC 1. combinig/joining both datasets, which will be aggregated in line with primary key ("SK_ID_CURR) of application_train (target dataframe) with the following features:
# MAGIC     - count aggregation features created
# MAGIC     - average aggregation features created
# MAGIC     - debt:credit ratio feature
# MAGIC     - created rolling window credit loan status feature will be created and joined to parent dataset

# COMMAND ----------

# MAGIC %md
# MAGIC ### a. Child Dataset: bureau_balance.csv
# MAGIC  
# MAGIC #### Feature Creation: Rolling Window Credit Loan Status
# MAGIC 
# MAGIC rolling window Exponential Moving Average is derived and the mean is used as the feature

# COMMAND ----------

def bureauBalanceRollingCreditLoan(df):
    df_final = df.copy()
    df_final['STATUS'] = df_final['STATUS'].replace(['X','C'],'0')
    df_final['STATUS'] = pd.to_numeric(df_final['STATUS'])
    df_final = df_final.groupby("SK_ID_BUREAU")['STATUS'].agg(
        lambda x: x.ewm(span=x.shape[0], adjust=False).mean().mean()
    )
    df_final = df_final.reset_index(name="CREDIT_STATUS_EMA_AVG")
    df_final = df_final.set_index('SK_ID_BUREAU')
    return df_final

bureau_balance_rolling_features = spark.createDataFrame(bureauBalanceRollingCreditLoan(bureau_balance)).select('CREDIT_STATUS_EMA_AVG').distinct()

# COMMAND ----------

# MAGIC %md
# MAGIC ### b. Parent Dataset: bureau.csv
# MAGIC 
# MAGIC #### Feature Creation: Aggregation Features - Count
# MAGIC  
# MAGIC - Number of loans
# MAGIC - Number of loans prolonged
# MAGIC - Percentage of active loans
# MAGIC - Number of type of loans

# COMMAND ----------

pd.__version__

# COMMAND ----------

def aggCountBureau(df):
    agg = df.groupby("SK_ID_CURR")
    # count number of loans
    df_final = pd.DataFrame(agg['SK_ID_CURR'].agg('count').reset_index(name='NUM_CREDIT_COUNT'))
    # count number of loans prolonged
    loans_prolonged = agg['CNT_CREDIT_PROLONG'].sum().reset_index(name='CREDIT_PROLONG_COUNT').set_index("SK_ID_CURR")
    df_final = df_final.join(loans_prolonged,on='SK_ID_CURR')
    # count percentage of active loans
    active_loans = agg['CREDIT_ACTIVE'].value_counts().reset_index(name='ACTIVE_LOANS_COUNT')
    active_loans = active_loans[active_loans['CREDIT_ACTIVE'] == 'Active'][['SK_ID_CURR','ACTIVE_LOANS_COUNT']].set_index("SK_ID_CURR")
    df_final = df_final.join(active_loans,on='SK_ID_CURR')
    df_final['ACTIVE_LOANS_PERCENT'] = df_final['ACTIVE_LOANS_COUNT']/df_final['NUM_CREDIT_COUNT']
    df_final.drop(["ACTIVE_LOANS_COUNT"], axis=1, inplace=True)
    df_final['ACTIVE_LOANS_PERCENT'] = df_final['ACTIVE_LOANS_PERCENT'].fillna(0)
    # count credit type
    # one hot encode
    ohe = OneHotEncoder(sparse=False)
    ohe_fit = ohe.fit_transform(df[["CREDIT_TYPE"]])
    credit_type = pd.DataFrame(ohe_fit, columns = ohe.get_feature_names(["CREDIT_TYPE"]))
    credit_type.insert(loc=0, column='SK_ID_CURR', value=df['SK_ID_CURR'].values)
    credit_type = credit_type.groupby("SK_ID_CURR").sum()
    df_final = df_final.join(credit_type, on="SK_ID_CURR")
    df_final = df_final.set_index("SK_ID_CURR")
    return df_final

aggregated_count_buurea_features = spark.createDataFrame(aggCountBureau(bureau))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Feature Creation: Aggregation Features - Average
# MAGIC 
# MAGIC 
# MAGIC - Average number of days between loans
# MAGIC - Average number of overdue days of overdue loans

# COMMAND ----------

def aggAvgBureau(df):
    agg = df.groupby('SK_ID_CURR')
    # average of CREDIT_DAY_OVERDUE
    final_df = agg['CREDIT_DAY_OVERDUE'].mean().reset_index(name = "CREDIT_DAY_OVERDUE_MEAN")
    # average of days between credits of DAYS_CREDIT
    days_credit_between = pd.DataFrame(df['SK_ID_CURR'])
    days_credit_between['diff'] = agg['DAYS_CREDIT'].diff()
    days_credit_between = days_credit_between.groupby("SK_ID_CURR")['diff'].mean().reset_index(name = 'DAYS_CREDIT_BETWEEN_MEAN')
    days_credit_between.set_index("SK_ID_CURR",inplace=True)
    final_df = final_df.join(days_credit_between, on='SK_ID_CURR')
    final_df = final_df.set_index("SK_ID_CURR")
    return final_df

agg_avg_bureau_features = spark.createDataFrame(aggAvgBureau(bureau)).select('CREDIT_DAY_OVERDUE_MEAN').distinct()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Feature Creation: debt credit ratio
# MAGIC 
# MAGIC ratio of AMT_CREDIT_SUM_DEBT to AMT_CREDIT_SUM created

# COMMAND ----------

def debtCreditRatio(df):
    #get debt:credit ratio
    df['DEBT_CREDIT_RATIO'] = df['AMT_CREDIT_SUM_DEBT']/df['AMT_CREDIT_SUM']
    df_final = df.groupby('SK_ID_CURR')['DEBT_CREDIT_RATIO'].mean().reset_index(name='DEBT_CREDIT_RATIO')
    df_final = df_final.set_index("SK_ID_CURR")   
    return df_final

debt_credit_ratio_features = spark.createDataFrame(debtCreditRatio(bureau))

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Combining bureau features:

# COMMAND ----------

def bureauFeatures(bureau, bureau_balance):
    dfs = []
    # handling features for bureau_balance
    bureau_balance_rolling_loan = bureauBalanceRollingCreditLoan(bureau_balance)
    bureau_df = bureau.copy()
    bureau_df = bureau_df.join(bureau_balance_rolling_loan,on="SK_ID_BUREAU")
    bureau_df["CREDIT_STATUS_EMA_AVG"] = bureau_df['CREDIT_STATUS_EMA_AVG'].fillna(0)
    bureau_df = bureau_df.groupby("SK_ID_CURR")["CREDIT_STATUS_EMA_AVG"].mean()
    dfs.append(bureau_df)
    dfs.append(aggCountBureau(bureau))
    dfs.append(aggAvgBureau(bureau))
    dfs.append(debtCreditRatio(bureau))
    final_df = dfs.pop()
    while dfs:
        final_df = final_df.join(dfs.pop(),on='SK_ID_CURR')
    return final_df

# COMMAND ----------

bureau_features = bureauFeatures(bureau, bureau_balance)
bureau_features = bureau_features.reset_index()
bureau_features['EVENT_TIMESTAMP']=datetime.datetime(2022,2,24)
bureau_features['CREATED_TIMESTAMP']=datetime.datetime.now()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3 Previous loan feature view
# MAGIC 
# MAGIC #### a. Installments_payments.csv
# MAGIC The following features are created and used from installments_payments.csv:
# MAGIC   - percentage of missed installments payments
# MAGIC   - Average percentage of unpaid payments for each missed payment
# MAGIC   - Average of unpaid payments for each missed payment
# MAGIC 
# MAGIC #### Feature Creation: Installment Payments Features

# COMMAND ----------

def aggAvgInstalments(df):
    df_ = df.copy()
    df_['INSTALMENT_MISSED'] = (df_['AMT_INSTALMENT'] > df_['AMT_PAYMENT']).astype(int)
    df_['AMT_UNPAID'] = df_['AMT_INSTALMENT'] - df_['AMT_PAYMENT']
    df_['PERC_UNPAID'] = df_['AMT_UNPAID']/df_['AMT_INSTALMENT']
    df_ = df_.fillna(0)
    agg = df_.groupby("SK_ID_CURR")
    # percentage of missed payments
    missed_instalments = agg['INSTALMENT_MISSED'].agg(lambda x: x.sum()/x.count()). \
        reset_index().set_index("SK_ID_CURR")
    # percentage of payments difference for each missed payment
    avg_percent_unpaid = agg['PERC_UNPAID'].mean().reset_index().set_index("SK_ID_CURR")
    # average payments difference for each missed payment
    avg_unpaid = agg['AMT_UNPAID'].mean().reset_index().set_index("SK_ID_CURR")
    final_df = missed_instalments
    final_df = final_df.join(avg_percent_unpaid, on='SK_ID_CURR')
    final_df = final_df.join(avg_unpaid,on="SK_ID_CURR")
    return final_df

pd_installment_payments_features=aggAvgInstalments(installments_payments).drop_duplicates()

installment_payments_features = spark.createDataFrame(pd_installment_payments_features).select('INSTALMENT_MISSED').distinct()

# COMMAND ----------

# MAGIC %md
# MAGIC ### b. Credit_Card_Balance.csv
# MAGIC 
# MAGIC The following features are created and used from credit_card_balance.csv
# MAGIC   - Average credit balancerolling window credit balance mean
# MAGIC   - Feature Creation: Average Credit Balance

# COMMAND ----------

def avgCreditBalance(df):
    df_ = df.copy()
    df_['AMT_BALANCE'] = pd.to_numeric(df_['AMT_BALANCE'])
    return df_.groupby('SK_ID_CURR')['AMT_BALANCE'].mean() 

# COMMAND ----------

# MAGIC %md
# MAGIC ### Feature Creation: Rolling Window EMA Credit Balance Mean

# COMMAND ----------

def creditCardBalanceRollingBalance(df):
    df_final = df.copy()
    df_final = df_final.sort_values(by="MONTHS_BALANCE")
    df_final = df_final.groupby("SK_ID_CURR")['AMT_BALANCE'].agg(
        lambda x: x.ewm(span=x.shape[0], adjust=False).mean().mean()
    )
    df_final = df_final.reset_index(name="CREDIT_CARD_BALANCE_EMA_AVG")
    df_final = df_final.set_index('SK_ID_CURR')
    return df_final

# COMMAND ----------

# MAGIC %md
# MAGIC ### c. Combining Features for Credit Card Balance

# COMMAND ----------

def creditCardFeatures(credit_card_balance):
    dfs = []
    dfs.append(avgCreditBalance(credit_card_balance))
    dfs.append(creditCardBalanceRollingBalance(credit_card_balance))
    final_df = dfs.pop()
    while dfs:
        final_df = final_df.join(dfs.pop(),on='SK_ID_CURR')
    return final_df

pd_credit_card_balance_features=creditCardFeatures(credit_card_balance)

credit_card_balance_features = spark.createDataFrame(pd_credit_card_balance_features)

# COMMAND ----------

prev_loan_features = pd_installment_payments_features.join(pd_credit_card_balance_features,on="SK_ID_CURR").reset_index()
prev_loan_features = prev_loan_features.fillna(0)
prev_loan_features['EVENT_TIMESTAMP']=datetime.datetime(2022,2,24)
prev_loan_features['CREATED_TIMESTAMP']=datetime.datetime.now()
prev_loan_features.head()

# COMMAND ----------

# MAGIC %md
# MAGIC # Feature Store Ingestion
# MAGIC 
# MAGIC Now that we have computed the features, let's put them into a feature store!%md

# COMMAND ----------

# MAGIC %sql 
# MAGIC CREATE DATABASE IF NOT EXISTS feature_store_home_credit_bureau_data;

# COMMAND ----------

from databricks import feature_store

fs = feature_store.FeatureStoreClient()

# COMMAND ----------

# This cell uses an API introduced with Databricks Runtime 10.2 ML.
# If your cluster is running Databricks Runtime 10.1 ML or below, skip or comment out this cell and uncomment and run Cmd 20.

spark.conf.set("spark.sql.shuffle.partitions", "5")

fs.create_table(
    name="feature_store_home_credit_bureau_data.installment_payments_features",
    primary_keys=["INSTALMENT_MISSED"],
    df=installment_payments_features,
    description="Installment Payments Features",
)

fs.create_table(
    name="feature_store_home_credit_bureau_data.bureau_balance_rolling_features",
    primary_keys=["CREDIT_STATUS_EMA_AVG"],
    df=bureau_balance_rolling_features,
    description="Bureau Balance Rolling Credit Features",
)

fs.create_table(
    name="feature_store_home_credit_bureau_data.agg_avg_bureau_features",
    primary_keys=["CREDIT_DAY_OVERDUE_MEAN"],
    df=agg_avg_bureau_features,
    description="Aggregate Avg Bureau Features",
)

fs.create_table(
    name="feature_store_home_credit_bureau_data.static_feature_table",
    primary_keys=["SK_ID_CURR"],
    df=spark.createDataFrame(application_train),
    description="Application (static) features"
)
bureau_features_df=spark.createDataFrame(bureau_features) \
    .withColumnRenamed('SK_ID_CURR', 'SK_ID_CURR') \
    .withColumnRenamed('DEBT_CREDIT_RATIO', 'DEBT_CREDIT_RATIO') \
    .withColumnRenamed('CREDIT_DAY_OVERDUE_MEAN', 'CREDIT_DAY_OVERDUE_MEAN') \
    .withColumnRenamed('DAYS_CREDIT_BETWEEN_MEAN', 'DAYS_CREDIT_BETWEEN_MEAN') \
    .withColumnRenamed('NUM_CREDIT_COUNT', 'NUM_CREDIT_COUNT') \
    .withColumnRenamed('CREDIT_PROLONG_COUNT', 'CREDIT_PROLONG_COUNT') \
    .withColumnRenamed('ACTIVE_LOANS_PERCENT', 'ACTIVE_LOANS_PERCENT') \
    .withColumnRenamed('CREDIT_TYPE_Another type of loan', 'CREDIT_TYPE_Another_type_of_loan') \
    .withColumnRenamed('CREDIT_TYPE_Car loan', 'CREDIT_TYPE_Car_loan') \
    .withColumnRenamed('CREDIT_TYPE_Cash loan (non-earmarked)', 'CREDIT_TYPE_Cash_loan_non_earmarked') \
    .withColumnRenamed('CREDIT_TYPE_Consumer credit', 'CREDIT_TYPE_Consumer_credit') \
    .withColumnRenamed('CREDIT_TYPE_Credit card', 'CREDIT_TYPE_Credit_card') \
    .withColumnRenamed('CREDIT_TYPE_Interbank credit', 'CREDIT_TYPE_Interbank_credit') \
    .withColumnRenamed('CREDIT_TYPE_Loan for business development', 'CREDIT_TYPE_Loan_for_business_development') \
    .withColumnRenamed('CREDIT_TYPE_Loan for purchase of shares (margin lending)', 'CREDIT_TYPE_Loan_for_purchase_of_shares_margin_lending') \
    .withColumnRenamed('CREDIT_TYPE_Loan for the purchase of equipment', 'CREDIT_TYPE_Loan_for_the_purchase_of_equipment') \
    .withColumnRenamed('CREDIT_TYPE_Loan for working capital replenishment', 'CREDIT_TYPE_Loan_for_working_capital_replenishment') \
    .withColumnRenamed('CREDIT_TYPE_Microloan', 'CREDIT_TYPE_Microloan') \
    .withColumnRenamed('CREDIT_TYPE_Mobile operator loan', 'CREDIT_TYPE_Mobile_operator_loan') \
    .withColumnRenamed('CREDIT_TYPE_Mortgage', 'CREDIT_TYPE_Mortgage') \
    .withColumnRenamed('CREDIT_TYPE_Real estate loan', 'CREDIT_TYPE_Real_estate_loan') \
    .withColumnRenamed('CREDIT_TYPE_Unknown type of loan', 'CREDIT_TYPE_Unknown_type_of_loan') \
    .withColumnRenamed('CREDIT_STATUS_EMA_AVG', 'CREDIT_STATUS_EMA_AVG') \
    .withColumnRenamed('EVENT_TIMESTAMP', 'EVENT_TIMESTAMP') \
    .withColumnRenamed('CREATED_TIMESTAMP', 'CREATED_TIMESTAMP')

fs.create_table(
    name="feature_store_home_credit_bureau_data.bureau_feature_table",
    primary_keys=["SK_ID_CURR"],
    df=bureau_features_df,
    description="Bureau features"
)

fs.create_table(
    name="feature_store_home_credit_bureau_data.prev_loan_features",
    primary_keys=["SK_ID_CURR"],
    df=spark.createDataFrame(prev_loan_features),
    description="Previous loands features"
)

# COMMAND ----------

# MAGIC %md
# MAGIC Troubleshooting

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM  feature_store_home_credit_bureau_data.prev_loan_features

# COMMAND ----------

# MAGIC %md
# MAGIC # Feature Look-up
# MAGIC 
# MAGIC Let's create a training data set using the features that we have put into the feature store!

# COMMAND ----------

from databricks.feature_store import FeatureLookup
import mlflow

installment_payments_features_table = "feature_store_home_credit_bureau_data.installment_payments_features"
bureau_balance_rolling_features_table = "feature_store_home_credit_bureau_data.bureau_balance_rolling_features"
agg_avg_bureau_features_table = "feature_store_home_credit_bureau_data.agg_avg_bureau_features"
bureau_feature_table = "feature_store_home_credit_bureau_data.bureau_feature_table"
prev_loan_features = "feature_store_home_credit_bureau_data.prev_loan_features"

installment_payments_feature_lookups = [
    FeatureLookup( 
      table_name = installment_payments_features_table,
      feature_names = "INSTALMENT_MISSED",
      lookup_key = ["INSTALMENT_MISSED"],
    )
]

bureau_balance_rolling_feature_lookups = [
    FeatureLookup( 
      table_name = bureau_balance_rolling_features_table,
      feature_names = "CREDIT_STATUS_EMA_AVG",
      lookup_key = ["CREDIT_STATUS_EMA_AVG"],
    )
]

agg_avg_bureau_feature_lookups = [
    FeatureLookup( 
      table_name = agg_avg_bureau_features_table,
      feature_names = "CREDIT_DAY_OVERDUE_MEAN",
      lookup_key = ["CREDIT_DAY_OVERDUE_MEAN"],
    )
]

bureau_feature_lookups = [
    FeatureLookup( 
      table_name = bureau_feature_table,
      feature_names = "BUREAU_FEATURES",
      lookup_key = ["SK_ID_CURR"],
    )
]

prev_loan_features_lookups = [
    FeatureLookup( 
      table_name = prev_loan_features,
      feature_names = "PREV_LOAN_FEATURES",
      lookup_key = ["SK_ID_CURR"],
    )
]

# COMMAND ----------

# MAGIC %md
# MAGIC # Create & Publish To Online Store
# MAGIC 
# MAGIC Before moving forward, please ensure you have an instance of an Azure SQL Database. Instructions on how to create and access one can be found here - https://docs.microsoft.com/en-us/azure/azure-sql/database/single-database-create-quickstart?view=azuresql&tabs=azure-portal

# COMMAND ----------

import datetime
from databricks.feature_store.online_store_spec.azure_sql_server_online_store_spec import AzureSqlServerSpec

online_store = AzureSqlServerSpec(
        hostname='',
        port=1433,
        user='',
        password='',  
        database_name='',
        table_name=''
)

fs.publish_table(
  name='feature_store_home_credit_bureau_data.installment_payments_features',
  online_store=online_store,
  mode='overwrite'
)

# COMMAND ----------


