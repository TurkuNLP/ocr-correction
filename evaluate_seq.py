import argparse
from itertools import zip_longest
from sklearn.metrics import accuracy_score
from editdistance import eval as edit_eval
import Levenshtein
import numpy as np
from align import needle

''' Evaluate sequence2sequence results '''

def make_mapping(pred_seq, gold_seq, alphabet):
	assert len(set(pred_seq)) + len(set(gold_seq)) < len(alphabet) # Too long sequence for the best hack, of all time
	mapping = {}
	reverse = {}
	mapped_pred, mapped_gold = [], []
	for i in range(len(pred_seq)):
		token = pred_seq[i]
		if token not in mapping:
			letter = alphabet.pop()
			mapping[token] = letter
			reverse[letter] = token
		mapped_pred.append(mapping[token])

	for i in range(len(gold_seq)):
		token = gold_seq[i]
		if token not in mapping:
			letter = alphabet.pop()
			mapping[token] = letter
			reverse[letter] = token
		mapped_gold.append(mapping[token])
	mapped_gold = "".join(mapped_gold)
	mapped_pred = "".join(mapped_pred)

	return mapped_pred, mapped_gold, mapping, reverse

def evaluate(pred_f, gold_f):
	predictions = open(pred_f, "r").readlines()
	gold = open(gold_f, "r").readlines()

	true, pred = [], []

	cer_stats = [0, 0, 0, 0]
	wer_stats = [0, 0, 0, 0]
	ins, sub, delet, gold_chars = 0,0,0,0


	for i in range(len(predictions)):
		pred_seq, gold_seq = predictions[i].strip(), gold[i].strip()
		print(pred_seq, "\t",  gold_seq)
		pred_seq, gold_seq = predictions[i].strip().split(" "), gold[i].strip().split(" ")

	# 	## Hack of a lifetime
		alphabet = list(set(list("abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVXQ0123456789")))
		mapped_pred, mapped_gold, mapping, reverse = make_mapping(pred_seq, gold_seq, alphabet)

		edit_operations = Levenshtein.editops(mapped_gold, mapped_pred)
		indx_used = set()
		## Getting all pairs here instead of just calculating CER and WER, so
		## at a later time we can calculate errors and whatnot

		for op in edit_operations:
			print(op)
			rev_gold = reverse[mapped_gold[op[1]]]
			rev_pred = reverse[mapped_pred[op[2]]]
			print(rev_gold, rev_pred)
			if op[0] == "replace":
				true.append(rev_gold)
				pred.append(rev_pred)
				sub += 1
			elif op[0] == "insert":
				true.append("")
				pred.append(rev_pred)
				ins += 1
			else:
				delet += 1
				true.append(rev_gold)
				pred.append("")
			indx_used.add(op[1])

		for i in range(len(mapped_gold)):
			if i not in indx_used:
				true.append(reverse[mapped_gold[i]])
				pred.append(reverse[mapped_gold[i]])

	print(true)
	print(pred)

	wer = 1 - accuracy_score(true, pred)
	cer = 0

	print("WER: {} \nCER: {}".format(wer, cer))








if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Evaluate seq2seq accuracy.")
	parser.add_argument("--pred", required=True)
	parser.add_argument("--gold", required=True)

	args = parser.parse_args()
	print(args)

	evaluate(args.pred, args.gold)
