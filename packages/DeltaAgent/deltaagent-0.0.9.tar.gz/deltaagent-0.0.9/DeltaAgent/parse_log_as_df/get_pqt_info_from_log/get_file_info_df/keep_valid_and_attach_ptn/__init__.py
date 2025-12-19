
import pandas as pd

def keep_valid_and_attach_ptn(df_pqt):

    df_pqt_pvt = df_pqt.groupby(['path', 'operation']).last()[['mod_time', 'partition']].unstack()

    # keep the info for valid existing parquet files
    column_for_remove = ('mod_time', 'remove')
    if column_for_remove in df_pqt_pvt.columns:
        df_pqt_exist = df_pqt_pvt.loc[df_pqt_pvt['mod_time']['remove'].isna()].drop(columns = [('mod_time', 'remove'), ('partition', 'remove')])
    else:
        df_pqt_exist = df_pqt_pvt

    # parse and attach the partition information
    df_pqt_exist_path = df_pqt_exist.droplevel('operation', axis=1)
    df_pqt_exist_ptn = df_pqt_exist_path['partition'].apply(pd.Series, dtype=pd.StringDtype()).convert_dtypes()
    # print(f'{df_pqt_exist_ptn = }')
    df_pqt_with_ptn = df_pqt_exist_path.merge(df_pqt_exist_ptn, left_index=True, right_index=True, how='left').drop(columns=['partition'])

    return df_pqt_with_ptn

    # columns example: ['mod_time', 'org_id', '_p_date']
    # index: path