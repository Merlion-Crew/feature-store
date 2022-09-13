import pandas
import numpy as np

base_folder='./data/'
filename=f'{base_folder}installments_payments.csv'

main_df=pandas.read_csv(filename)
for id, chunk_df in  enumerate(np.array_split(main_df, 2)): # Two chunks
    chunk_df.to_csv(f'{base_folder}/installments_payments{id}.csv')
