# Notebook data

 1. Download the `Home Credit Default Risk` data from [Kaggle](https://www.kaggle.com/competitions/home-credit-default-risk/data) and store it in this folder (`data`).
    1. Create the `csv` for the `bureau` and `bureau_balance` spine dataset.
        1. Run the `scripts/add_time_to_csv.py` to generate the `bureau_all_time.csv`.
    1. Run the `scripts/upload_home_credit_data.sh` to upload it to the provisioned storage.
        1. Make sure to substitute the values
        1. This script would upload all of the `csv` file inside the `data` folder.