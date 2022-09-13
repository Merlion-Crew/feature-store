import pandas as pd
import pandavro as pdx
import glob
import os
import datetime

# 1. Load csv
df_csv = pd.read_csv('data/bureau.csv')
# 2. Add TRAN_DATE
df_csv = df_csv.assign(TRAN_DATE=lambda x: datetime.datetime(2021,1,1,11,34,44).strftime('%Y-%m-%d %X'))
print(df_csv)
# 3. Save the new csv
df_csv.to_csv('data/bureau_all_time.csv')