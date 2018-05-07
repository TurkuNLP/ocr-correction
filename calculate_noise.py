import gzip, json, sys

if __name__ == "__main__":

	filen = sys.argv[1]
	d = json.load(open(filen, "r"))
	char_noises = []
	tot_n = 0
	tot_c = 0
	for char, replacements in d.items():
		if char not in replacements:
			continue
		n_count = 0
		c_count = replacements.get(char, 0)
		for replacement, value in replacements.items():
			if char == replacement:
				continue
			n_count += value
		char_noises.append([n_count / (n_count + c_count), char])
		tot_n += n_count
		tot_c += c_count	

	just_values = [v[0] for v in char_noises]
	print("Noise: {}".format(sum(just_values) / len(just_values)))
	print("Total noise: {}".format(tot_n / tot_c))
