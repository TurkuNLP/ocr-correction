import argparse, gzip, json, sys
import random
import numpy as np
from operator import itemgetter
from natsort import natsorted
''' Add artificial noise to data based on given distribution '''


def make_distribution(loc, retain_actual):
	dist = json.load(open(loc, "r"))
	distribution = {}
	for key, replacement_dict in dist.items():

		if not retain_actual:
			if key in replacement_dict:
				del replacement_dict[key]
		new_values = []
		new_keys = []
		replacement_sum = sum(replacement_dict.values())

		for replacement_key, replacement_value in replacement_dict.items():
			new_values.append([replacement_value / replacement_sum, replacement_key])
		new_values.sort(key=itemgetter(0))
		values, keys = [v[0] for v in new_values], [v[1] for v in new_values]
		if len(new_values) != 0:
			distribution[key] = [values, keys]

	return distribution

def noisify(input_loc, output_loc, distribution, noise_level):
	data = json.load(gzip.open(input_loc, "rt"))
	documents = []
	done = 0
	data_keys = natsorted(list(data.keys()))
	for document_id in data_keys:
		document_text = data[document_id]
		if not document_text: continue

		print("Done: {}/{}".format(done, len(data)), end="\r")

		done += 1
		doc_list = [document_id]
		document_text = " ".join(document_text.split()) ##remove new line etc.

		orig_text = document_text
		text = list(document_text)

		text_indexes = list(range(len(text)))
		char_indexes = np.random.choice(text_indexes, int(len(text_indexes) * float(noise_level)))

		for char_index in char_indexes:
			char = text[char_index]
			if char in distribution:
				char_distribution_values, char_distribution_keys = distribution[char]
				new_char = np.random.choice(char_distribution_keys, p=char_distribution_values)
				if new_char in [" ", "\t", "\n"]:
					new_char = char
			else:
				new_char = char
			text[char_index] = new_char

		text = "".join(text)
		orig_words = orig_text.split(" ")
		noise_words = text.split(" ")
		assert len(orig_words) == len(noise_words)

		word_pairs = []
		for i in range(0, len(orig_words)):
			word_pairs.append([orig_words[i], noise_words[i]])

		doc_list.append(word_pairs)
		documents.append(doc_list)

	gzip.open(output_loc, "wt").write(json.dumps(documents))


if __name__ == "__main__":

	parser = argparse.ArgumentParser("Generate noisy data. Input needs to be JSON-format, key = doc_id, value = text")
	parser.add_argument("--input", help="Input file.", required=True)
	parser.add_argument("--output", help="Output file.", required=True)
	parser.add_argument("--distribution", help="Character distribution file. JSON-format, key per character, value = dictionary of replacement_key:count values", required=True)
	parser.add_argument("--retain_actual", help="Whether to retain the actual key in the distribution", default=False, action="store_true")
	parser.add_argument("--noise_level", help="Amount of noise to generate, default=0.1", default=0.1, type=float)
	args = parser.parse_args()
	print(args)
	distribution = make_distribution(args.distribution, args.retain_actual)
	noisify(args.input, args.output, distribution, args.noise_level)
