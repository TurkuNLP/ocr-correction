import argparse
from itertools import zip_longest
from sklearn.metrics import accuracy_score
from editdistance import eval as edit_eval
from Levenshtein import distance

''' Evaluate results, just accuracy for now '''

def evaluate(pred_f, gold_f):
	predictions = open(pred_f, "r").readlines()
	gold = open(gold_f, "r").readlines()

	p, t = [], []

	w_edits = 0
	w_gold = 0
	c_edits = 0
	c_gold = 0

	for i in range(len(predictions)):
		pred_seq, gold_seq = predictions[i].strip().split(" "), gold[i].strip().split(" ")

		edits = edit_eval(pred_seq, gold_seq)
		w_edits += edits
		w_gold += len(gold_seq)

		edits = edit_eval(predictions[i], gold[i])
		c_edits += edits
		c_gold += len(gold[i])

	wer = w_edits / w_gold
	cer = c_edits / c_gold
	print("WER: {}".format(wer))
	print("CER: {}".format(cer))


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Evaluate seq2seq accuracy.")
	parser.add_argument("--pred", required=True)
	parser.add_argument("--gold", required=True)

	args = parser.parse_args()
	print(args)

	evaluate(args.pred, args.gold)
