
from .parse_jsonl_as_dict import parse_jsonl_as_dict
from .get_file_info_df import get_file_info_df

def get_pqt_info_from_log(azure_service_client, container_name, deltatable_path, 
                          log_folder_name=None, 
                          keep_valid=None):

    if log_folder_name is None:
        log_folder_name = '_delta_log'

    delta_log_path = deltatable_path + '/' + log_folder_name
    azure_dir_client = azure_service_client.get_directory_client(file_system=container_name, directory=delta_log_path)
    azure_file_system_client = azure_service_client.get_file_system_client(file_system=container_name)

    json_dict = []
    for file_path_item in azure_dir_client.get_paths():
        if not file_path_item['is_directory']:
            print(file_path_item['name'])
            file_path_name = file_path_item['name']
            if file_path_name[-5:] == '.json':
                file_client = azure_file_system_client.get_file_client(file_path_name)
                data = file_client.download_file().readall()
                parse_jsonl_as_dict(data, json_dict)
    df_pqt = get_file_info_df(json_dict, keep_valid=keep_valid)

    return df_pqt
    # if keep_valid=True:
    # columns example: ['mod_time', 'org_id', '_p_date']
    # index: path
    # else:
    # columns: ['path', 'operation', 'mod_time', 'partition']