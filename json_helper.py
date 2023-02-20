import json


def store_files_info(json_path, files_data):
    files_dict = {}
    for (path, accessed) in files_data:
        files_dict[path] = accessed
    write_json(json_path, files_dict)


def write_json(file_path, data):
    with open(file_path, "w") as outfile:
        json.dump(data, outfile)


def read_json(file_path):
    # Opening JSON file
    try:
        with open(file_path, 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)
    except FileNotFoundError:
        return {}
    return json_object

