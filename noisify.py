import argparse, gzip, json, sys
import random
import numpy as np
from operator import itemgetter
''' Add artificial noise to data based on given distribution '''


def make_distribution(loc):
	dist = json.load(open(loc, "r"))
	distribution = {}
	for key, replacement_dict in dist.items():
		#print(key)
		if key in replacement_dict:
			del replacement_dict[key]
		new_values = []
		new_keys = []
		replacement_sum = sum(replacement_dict.values())

		for replacement_key, replacement_value in replacement_dict.items():
			new_values.append([replacement_value / replacement_sum, replacement_key])
		#float + +  doesn't necessarily add to 1.0 (0.9999999..), so
		new_values.sort(key=itemgetter(0))
		values, keys = [v[0] for v in new_values], [v[1] for v in new_values]
		if len(new_values) != 0:
			distribution[key] = [values, keys]

		#print(distribution[key])
	#	input()

	return distribution

def noisify(input_loc, distribution, noise_level):
	data = open(input_loc, "r").readlines()
	noisified_sentences = []
	for sent in data:
		sent = sent.strip()
		if not sent: continue
		print(sent)
		sent = list(sent)
		sent_indexes = list(range(len(sent)))
		char_indexes = np.random.choice(sent_indexes, int(len(sent_indexes) * float(noise_level)))
		for char_index in char_indexes:
			char = sent[char_index]
			if char in distribution:
				char_distribution_values, char_distribution_keys = distribution[char]
				new_char = np.random.choice(char_distribution_keys, p=char_distribution_values)
			else:
				new_char = char
			sent[char_index] = new_char
		noisified_sentences.append("".join(sent))
		print("".join(sent))
		print()
	return noisified_sentences


if __name__ == "__main__":

	parser = argparse.ArgumentParser("Generate noisy data. Input needs to be sentence per line.")
	parser.add_argument("--input", help="Input file. One sentence per line.", required=True)
	parser.add_argument("--distribution", help="Character distribution file. JSON-format, key per character, value = dictionary of replacement_key:count values", required=True)
	parser.add_argument("--noise_level", help="Amount of noise to generate, default=0.1", default=0.1, type=float)
	args = parser.parse_args()
	print(args)
	distribution = make_distribution(args.distribution)
	noisify(args.input, distribution, args.noise_level)
