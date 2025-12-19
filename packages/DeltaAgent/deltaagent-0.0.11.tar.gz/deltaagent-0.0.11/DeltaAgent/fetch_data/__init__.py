
from .fetch_parquet_files import fetch_parquet_files

def fetch_data(df_pqt_wt_ptn):

    account_name = df_pqt_wt_ptn.attrs['account_name']
    account_key = df_pqt_wt_ptn.attrs['account_key']
    container_name = df_pqt_wt_ptn.attrs['container_name']
    table_path = df_pqt_wt_ptn.attrs['table_path']
    df_emd = fetch_parquet_files(container_name, account_name, account_key, table_path, df_pqt_wt_ptn)

    df_emd.attrs = df_pqt_wt_ptn.attrs

    return df_emd