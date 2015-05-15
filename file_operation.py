import os
import json


def read_json(file_path):
    try:
        with open(file_path, 'r') as file_out:
            file_data = json.loads(file_out.read())
        return file_data
    except IOError:
        return None
