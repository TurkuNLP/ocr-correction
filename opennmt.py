"""
Converts data to the OpenNMT data format.
"""
import argparse
import json
import gzip
import os

from utils import doc2sentences

parser = argparse.ArgumentParser()
parser.add_argument('in_dir')
parser.add_argument('out_dir')
args = parser.parse_args()

for filename in ['train.json.gz', 'devel.json.gz', 'test.json.gz']:
    data = json.load(gzip.open(os.path.join(args.in_dir, filename), 'rt'))
    gold_sentences = []
    ocr_sentences = []
    for document in data:
        gold, ocr = doc2sentences(document)
        gold_sentences += gold
        ocr_sentences += ocr
    
    gold_max_len = max([len(s) for s in gold_sentences])
    ocr_max_len = max([len(s) for s in ocr_sentences])
    
    print('Maximum sentence lengths for %s set in characters: %s / %s (gold/ocr)' % (filename.split('.')[0], gold_max_len, ocr_max_len))
    
    # OpenNMT assumes tokens separated with whitespace as the input,
    # but we are using it as a character level model.
    # Thus we want to replace the original whitespaces with an underscore
    # and separate individual characters with whitespace
    open_nmt_input = [' '.join(sentence.replace(' ', '_')) + '\n' for sentence in ocr_sentences]
    open_nmt_output = [' '.join(sentence.replace(' ', '_')) + '\n' for sentence in gold_sentences]
    
    split = filename.split('.')[0]
    
    oinput_file = open(os.path.join(args.out_dir, 'src_%s.txt' % split), 'wt')
    oinput_file.writelines(open_nmt_input)
    
    ooutput_file = open(os.path.join(args.out_dir, 'tgt_%s.txt' % split), 'wt')
    ooutput_file.writelines(open_nmt_output)

