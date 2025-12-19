
import pandas as pd
from tqdm.notebook import tqdm
from adlfs import AzureBlobFileSystem

def fetch_parquet_files(container_name, account_name, account_key, deltatable_path, df_pqt_wt_ptn):

    abfs = AzureBlobFileSystem(account_name=account_name, 
                           account_key=account_key, 
                           container_name=container_name)
    
    base_path = f'abfss://{container_name}@{account_name}.dfs.core.windows.net/'

    partition_cols = df_pqt_wt_ptn.columns[1:]

    df_query = pd.DataFrame()

    pqt_total = df_pqt_wt_ptn.shape[0]
    for idx_path, sr_part in tqdm(df_pqt_wt_ptn.iterrows(), total=pqt_total):
        # break
        print(idx_path)
        sample_file_path = base_path + deltatable_path + '/' + idx_path
        df_pq = pd.read_parquet(sample_file_path, filesystem=abfs)
        for col in partition_cols:
            df_pq[col] = sr_part[col]
        df_query = pd.concat([df_query, df_pq])

    return df_query