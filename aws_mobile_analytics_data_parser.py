import os
import fnmatch
import gzip
import json
import re

def parse_data_in_directory(directory):
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, '*.gz'):
            matches.append(os.path.join(root, filename))
    
    data = []
    
    for match in matches:
        with gzip.open(match, 'r') as f:
            for json_part in f.read().split("\n"):
                if json_part:
                    data.append(json.loads(json_part))
    return data


def jprint(d):
    print json.dumps(d, sort_keys=True, indent=4, separators=(',', ': '))


