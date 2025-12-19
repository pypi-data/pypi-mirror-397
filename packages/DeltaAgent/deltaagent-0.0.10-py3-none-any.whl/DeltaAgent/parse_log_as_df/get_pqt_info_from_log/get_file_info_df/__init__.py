import pandas as pd

from .get_commits_ls import get_commits_ls
from .keep_valid_and_attach_ptn import keep_valid_and_attach_ptn

def get_file_info_df(json_dict, keep_valid=None):

    if keep_valid is None:
        keep_valid = True

    commits_ls = get_commits_ls(json_dict)
    df_cmt = pd.DataFrame(commits_ls)
    df_cmt['mod_time'] = pd.to_datetime(df_cmt['mod_time'], unit='ms') 
    # df_pqt = df_cmt.groupby(['path', 'operation'])[['mod_time', 'partition']].last().unstack()

    if keep_valid:
        df_pqt_with_ptn = keep_valid_and_attach_ptn(df_cmt)
        df_pqt_rtn = df_pqt_with_ptn
        # columns example: ['mod_time', 'org_id', '_p_date']
        # index: 'path'
    else:
        df_pqt_rtn = df_cmt
        # columns: ['path', 'operation', 'mod_time', 'partition']

    return df_pqt_rtn

    