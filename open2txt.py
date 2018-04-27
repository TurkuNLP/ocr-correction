"""
Converts our hackish OpenNMT format to clean text.
"""

import argparse


def opennmt2txt(data):
    """
    Converts OpenNMT output to a readable format
    """
    res = []
    for line in data:
        clean_line = line.replace('<BEG>', '').replace(' ', '').replace('_', ' ')
        res.append(clean_line)
    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_path')
    parser.add_argument('out_path')
    args = parser.parse_args()
    
    data = open(args.in_path)
    clean_data = opennmt2txt(data)
    
    with open(args.out_path, 'wt') as out_f:
        out_f.writelines(clean_data)