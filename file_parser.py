import json
import re
import os

class SearchMode:
    MATCH_ALL = "MATCH_ALL"
    MATCH_ONE = "MATCH_ONE"
    LIST = [MATCH_ALL, MATCH_ONE]

EXTENSION_LIST = ['.py', '.txt', '.js']

def gather_lines(query_name, dir_path, regex_list, mode=SearchMode.MATCH_ALL, max_chars=-1, min_chars=-1):
    if mode not in SearchMode.LIST:
        raise ValueError("invalid search mode: %s" % mode)

    if not os.path.isdir(dir_path):
        raise ValueError("invalid dir_path: %s" % dir_path)

    line_matches = []
    file_count = 0

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_count += 1
            ext = os.path.splitext(os.path.join(root, file))[1]
            if ext in EXTENSION_LIST:
                with open(os.path.join(root, file), 'r') as code_file:
                    lines = code_file.readlines()
                    for i in range(len(lines)):
                        if max_chars != -1 and len(lines[i]) > max_chars:
                            continue
                        if min_chars != -1 and len(lines[i]) < min_chars:
                            continue

                        matches = 0
                        for regex in regex_list:
                            if re.search(regex, lines[i]):
                                matches += 1
                        if mode == SearchMode.MATCH_ALL and matches == len(regex_list):
                            line_matches.append(lines[i])
                        elif mode == SearchMode.MATCH_ONE and matches > 0:
                            line_matches.append(lines[i])

    with open(os.path.join('source/', query_name) + '.json', 'w') as file:
        json.dump(line_matches, file)

    print('Matched %d lines of code from %d files in dir %s' % (len(line_matches), file_count, dir_path))
    print('Results written to file %s' % (query_name + '.json'))

