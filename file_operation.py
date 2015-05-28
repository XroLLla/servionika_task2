import os
import json


def read_json(file_path):
    try:
        file_data = []
        with open(file_path, 'r') as file_out:
            file_data = json.loads(file_out.read())
        result = {}
        for info in file_data:
            result[info['filename']] = info
        return result
    except IOError:
        return None
