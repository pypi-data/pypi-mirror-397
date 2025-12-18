import json

# Method 1: Read JSON from a file
def read_json_file(file_path):
    """Read JSON data from a file"""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data