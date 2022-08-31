# This is an example feature definition file
from datetime import timedelta
from google.protobuf.duration_pb2 import Duration

from feast import Entity, Feature, FeatureView, FileSource, ValueType, FeatureService

customer_info_table = FileSource(
    path="../data/static_feature_table.parquet",
    event_timestamp_column="EVENT_TIMESTAMP",
)

bureau_feature_table = FileSource(
    path="../data/bureau_feature_table.parquet",
    event_timestamp_column="EVENT_TIMESTAMP",
)

previous_loan_feature_table = FileSource(
    path="../data/previous_loan_features_table.parquet",
    event_timestamp_column="EVENT_TIMESTAMP",
)

customer =  Entity(name="SK_ID_CURR", value_type=ValueType.INT64, description="customer id",)


customer_stats_view = FeatureView(
    name="static_feature_view",
    entities=["SK_ID_CURR"],
    ttl=timedelta(days=90),
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
    online=True,
    batch_source=customer_info_table,
    tags={},
)


bureau_view = FeatureView(
    name="bureau_feature_view",
    entities=["SK_ID_CURR"],
    ttl=timedelta(days=90),
    online=True,
    batch_source=bureau_feature_table,
    tags={},
)

previous_loan_view = FeatureView(
    name="previous_loan_feature_view",
    entities=["SK_ID_CURR"],
    ttl=timedelta(days=90),
    online=True,
    batch_source=previous_loan_feature_table,
    tags={},
)

cust_fs = FeatureService(
    name="credit_model_1",
    features=[customer_stats_view, bureau_view, previous_loan_view[["AMT_BALANCE"]]]
)
