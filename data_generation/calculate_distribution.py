import gzip, json, sys, os, tqdm, subprocess, numpy

class CharacterDistributionCalculator:

	def __init__(self, data, sample_count=-1, cull_distribution=False, min_cull_length=3):
		self.data = data #List of lists of text clusters, i.e similar texts. Full data or generator
		self.sample_count = sample_count #How many lists to read, -1 = all
		self.cull_distribution = cull_distribution
		self.min_cull_length = min_cull_length
		self.align_type = "one_against_all"

	def calculate_character_distribution(self):
		character_distribution = {}
		for cluster_i, cluster in enumerate(tqdm.tqdm(self.data, desc="Going through clusters...")):
			if cluster_i >= self.sample_count:
				break
			if self.align_type == "all_against_all":

				for i in range(0, len(cluster)):
					curr_cl = list(cluster)
					curr_origin = curr_cl.pop(i)
					for hit in curr_cl:
						alignment = self.align(curr_origin, hit)
						self.extract_distribution(alignment, character_distribution)
			elif self.align_type == "one_against_all":

				origin = cluster.pop([numpy.argmax(cluster)])
				for hit in cluster:
					alignment = self.align(origin, hit)
					self.extract_distribution(alignment, character_distribution)

		if self.cull_distribution:
			self.cull_distribution_words(character_distribution)
		return character_distribution

	def cull_distribution_words(self, character_distribution):
		for start_key in list(character_distribution.keys()):
			if len(start_key) > self.min_cull_length:
				del character_distribution[key]

		for start, comp in character_distribution.items():
			for comp_key in list(comp.keys()):
				if len(comp_key) > self.min_cull_length:
					del comp[comp_key]


	def extract_distribution(self, alignment, character_distribution):
		orig, comp = alignment
		skip = False
		#for i in range(0, len(orig)):
		i = 0
		while i != len(orig):
			orig_char, comp_char = orig[i], comp[i]
			if orig_char == comp_char: ## SAME
				character_distribution[orig_char] = character_distribution.get(orig_char, {})
				character_distribution[orig_char][orig_char] = character_distribution[orig_char].get(orig_char, 0) + 1
			elif orig_char == "-": ## DELETION
				orig_char = comp_char
				new_char = "DEL"
				character_distribution[orig_char] = character_distribution.get(orig_char, {})
				character_distribution[orig_char][new_char] = character_distribution[orig_char].get(new_char, 0) + 1
			elif comp_char == "-": ##INSERTION
				extra = 0
				while True:
					if len(comp) > i+extra+1 and comp[i+extra] == "-":
						extra += 1
					else:
						break
				comp_char = comp[i+extra]
				new_char = "".join(orig[i:i+extra])
				character_distribution[comp_char] = character_distribution.get(comp_char, {})
				character_distribution[comp_char][new_char] = character_distribution[comp_char].get(new_char, 0) + 1
				i += extra
			else:  ## MISMATCH
				character_distribution[orig_char] = character_distribution.get(orig_char, {})
				character_distribution[orig_char][comp_char] = character_distribution[orig_char].get(comp_char, 0) + 1
			i += 1



	def align(self, seq1, seq2):
		from alignment import needle
		align = needle(seq1, seq2)
		return align[0], align[2]



def generate_cluster_texts(cluster_location, language):
	clusters = os.listdir(cluster_location)
	for cluster_i, cluster in enumerate(clusters):
		cluster_data = json.load(gzip.open(cluster_location + "/" + cluster, "rt"))
		for cluster_key, cluster_info in cluster_data.items():
			texts = []
			if cluster_info["start_language"] != language:
				continue

			for hit in cluster_info["hits"]:
				texts.append(hit["text"].replace("-", "|"))
			yield texts

def save_char_distribution(distribution, save_file):
	gzip.open(save_file, "wt").write(json.dumps(distribution))

if __name__ == "__main__":



	cluster_location = "/home/avjves/oldsuomi/linking/formatted_clusters/"
	save_file = "new_char_replacement_with_del.gz"
	language = "fin"
	cluster_data_gen = generate_cluster_texts(cluster_location, language)
	cdc = CharacterDistributionCalculator(cluster_data_gen, sample_count=1000, cull_distribution=True)
	char_distribution = cdc.calculate_character_distribution()
	save_char_distribution(char_distribution, save_file)
	print(json.dumps(char_distribution))
