import json

def parse_jsonl_as_dict(data, jsonl_dict):

    # here jsonl means non-standard json where multiple json objs exist as multiple lines in a json file
    for line in str(data, encoding='utf-8').split('\n'):
        print('.', end='')
        if len(line) > 0:
            jsonl_dict.append(json.loads(line))
    
    print('') # print the end of the a line