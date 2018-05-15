import gzip, json, os, tqdm, sys, argparse, random, pickle
from operator import itemgetter


'''
Generates random texts from clustered word frequencies obtained from clusters with > 20 hits
'''

def generate_texts(cluster_location, min_frequency):
	data = []
	files = os.listdir(cluster_location)
	corr = 0
	miss = 0
	for filename in tqdm.tqdm(files):
		cluster_data = json.load(gzip.open(cluster_location + "/" + filename, "rt"))
		for cluster_id, cluster_word_freqs in cluster_data.items():
			words = []
			for word_dict in cluster_word_freqs:
				max_k, max_v = max(word_dict.items(), key=itemgetter(1))
				total = sum(word_dict.values())
				if max_v > min_frequency and len(max_k) > 1:
					for word, freq in word_dict.items():
						if word == max_k:
							if len(word_dict) > 1 and freq > total-freq:
								freq = total-freq
							elif len(word_dict) == 1:
								if freq > 10:
									freq = 20
							corr += freq
						else: miss += freq
						for i in range(freq):
							words.append([max_k, word])
			#random.shuffle(words)
			data.append([cluster_id, words])
	print("Correct: {}\nWrong: {}".format(corr, miss))
	return data

if __name__ == "__main__":

	parser = argparse.ArgumentParser("Generate 'texts' from clustered word frqeuencies")
	parser.add_argument("--input", help="Location of folder with the cluster files", required=True)
	parser.add_argument("--min_freq", default=10, type=int)
	parser.add_argument("--output")

	args = parser.parse_args()
	data = generate_texts(args.input, args.min_freq)
	if args.output:
		with open(args.output, "wb") as pf:
			pickle.dump(data, pf)
	else:
		print(data)
