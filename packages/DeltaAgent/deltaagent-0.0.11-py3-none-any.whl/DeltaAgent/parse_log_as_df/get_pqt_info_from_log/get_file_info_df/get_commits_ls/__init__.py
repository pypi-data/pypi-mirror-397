
def get_commits_ls(json_dict):

    commits_ls = []
    for operation in json_dict:
        if 'add' in operation:
            commit_dict = {}
            commit_dict['operation'] = 'add'
            # print(operation)
            commit_dict['path'] = operation['add']['path']
            commit_dict['mod_time'] = operation['add']['modificationTime']
            commit_dict['data_change'] = operation['add']['dataChange']
            commit_dict['partition'] = operation['add']['partitionValues']
            commits_ls.append(commit_dict)
        elif 'remove' in operation:
            commit_dict = {}
            commit_dict['operation'] = 'remove'
            # print(operation)
            commit_dict['path'] = operation['remove']['path']
            commit_dict['mod_time'] = operation['remove']['deletionTimestamp']
            commit_dict['data_change'] = operation['remove']['dataChange']
            commit_dict['partition'] = operation['remove']['partitionValues']
            commits_ls.append(commit_dict)

    return commits_ls

# example: [{'operation': , 'path': , 'mod_time': , 'data_change': }]