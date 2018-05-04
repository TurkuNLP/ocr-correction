"""
Converts original tokenized data into full documents.
"""
import gzip
import json
import argparse
from collections import defaultdict

def convert(in_path, out_path):
    documents = defaultdict(list)
    data = json.load(gzip.open(in_path, 'rt'))
    for line in data:
        pub_id = line[3].rsplit('_', 1)[0] # The last part of the id is a page number and we want to exclude it since an article may span over multiple pages
        gold = line[5]
        current = line[7]
        tesseract = line[6]
        documents[pub_id].append((gold, current, tesseract))
    
    out_f = gzip.open(out_path, 'wt')
    out_f.write(json.dumps(list(documents.items()), indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Convert National library OCR data into another format.')
    parser.add_argument('input')
    parser.add_argument('output')
    args = parser.parse_args()
    convert(args.input, args.output)