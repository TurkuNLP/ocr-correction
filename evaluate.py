import argparse
from itertools import zip_longest
from sklearn.metrics import accuracy_score

''' Evaluate results, just accuracy for now '''

def evaluate(pred_f, gold_f, eval_level, truncate):
	predictions = open(pred_f, "r").readlines()
	gold = open(gold_f, "r").readlines()

	p, t = [], []

	for i in range(len(predictions)):
			pred_seq, gold_seq = predictions[i].strip().split(" "), gold[i].strip().split(" ")

			if eval_level == "char":
				##TODO Align if this is ever used
				pass
			else:
				## if pred is messed up, it will be longer/shorter
				# Now we penalize the predictions if they are longer than the gold sequence
				if truncate:
					for i in range(len(gold_seq)):
						p.append(pred_seq[i] if len(pred_seq) > i else '')
						t.append(gold_seq[i])						
				else:
					for pred_token, gold_token in zip_longest(pred_seq, gold_seq, fillvalue=''):
						p.append(pred_token)
						t.append(gold_token)
					
	acc = accuracy_score(p, t)
	print("Prediction accuracy: {}".format(acc))


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Evaluate seq2seq accuracy.")
	parser.add_argument("--pred", required=True)
	parser.add_argument("--gold", required=True)
	parser.add_argument("--eval_level", help="char or word, default=word", default="word")
	parser.add_argument("--truncate", help="Truncate predictions to gold length", action="store_true")

	args = parser.parse_args()
	print(args)

	evaluate(args.pred, args.gold, args.eval_level, args.truncate)
