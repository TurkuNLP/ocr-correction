import gzip, json, argparse, tqdm
import numpy as np

''' Generate text from tokens and their frequencies '''


def read_distribution(tokens):
	vocabulary = []
	probabilities = []
	token_data = json.load(open(tokens, "r"))
	total = sum(token_data.values())
	for token, token_count in token_data.items():
		prob = token_count/total
		vocabulary.append(token)
		probabilities.append(prob)
	distribution = {"vocabulary": vocabulary, "probabilities": probabilities}
	return distribution

def generate_docs(distribution, num_documents, doc_length):
	docs = {}
	doc_count = 0
	for i in tqdm.tqdm(range(num_documents)):
		words = np.random.choice(a=distribution["vocabulary"], size=doc_length, p=distribution["probabilities"])
		docs[doc_count] = " ".join(words)
		doc_count += 1
	return docs

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Generate text from tokens and their frequencies")
	parser.add_argument("--tokens", required=True)
	parser.add_argument("--num_documents", type=int, default=100)
	parser.add_argument("--doc_length", type=int, default=500)
	parser.add_argument("--output")

	args = parser.parse_args()
	print(args)
	token_distribution = read_distribution(args.tokens)
	docs = generate_docs(token_distribution, args.num_documents, args.doc_length)

	if args.output:
		with gzip.open(args.output, "wt") as gzf:
			gzf.write(json.dumps(docs))
	else:
		print(docs)
