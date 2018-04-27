"""
Helper to read OpenNMT predictions
"""

import argparse
import itertools

from open2txt import opennmt2txt

parser = argparse.ArgumentParser()
parser.add_argument('input')
parser.add_argument('predictions')
parser.add_argument('gold', nargs='?')

args = parser.parse_args()

input_data = open(args.input)
pred_data = open(args.predictions)
if args.gold:
    gold_data = open(args.gold)
else:
    gold_data = []
    
s = [opennmt2txt(data) for data in [input_data, pred_data, gold_data]]

for i, p, g in itertools.zip_longest(*s):
    print(''.join([i, p, str(g)]))
    print('\n')