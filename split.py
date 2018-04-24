"""
Splits data into train/devel/test with 60%/20%/20% ratios on document level.
Document here is a single number from a given publication.
The whole number is not included, but there may be several pages including multiple news articles.
"""
import json
import argparse
import gzip
import os

import numpy as np
np.random.seed(42) # Fix the random state for consistent data split

from sklearn.model_selection import train_test_split

parser = argparse.ArgumentParser()
parser.add_argument('input_file')
parser.add_argument('out_dir')
args = parser.parse_args()

data = json.load(gzip.open(args.input_file, 'rt'))
train, devtest = train_test_split(data, test_size=0.4)
devel, test = train_test_split(devtest, test_size=0.5)

print('Documents total/train/devel/test: %s / %s / %s / %s' % (len(data), len(train), len(devel), len(test)))

for split_data, filename in zip([train, devel, test], ['train.json.gz', 'devel.json.gz', 'test.json.gz']):
    f = gzip.open(os.path.join(args.out_dir, filename), 'wt')
    f.write(json.dumps(split_data, indent=2))
