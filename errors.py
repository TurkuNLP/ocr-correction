import argparse
from itertools import zip_longest
from collections import defaultdict
from sklearn.metrics import accuracy_score

from Levenshtein import distance

''' Evaluate results, just accuracy for now '''

def evaluate(source_f, pred_f, gold_f, eval_level, truncate):
    predictions = open(pred_f, "r").readlines()
    gold = open(gold_f, "r").readlines()
    source = open(source_f, "r").readlines()

    s, p, t = [], [], []

    edits = 0
    gold_characters = 0

    corrected_difference = defaultdict(int) # How many wrong characters were in the input if the model was able to fix it
    broken_difference = defaultdict(int) # Broken in general
    destroy_count = 0
    fixed_count = 0

    for i in range(len(predictions)):
            pred_seq, gold_seq, source_seq = predictions[i].strip().split(" "), gold[i].strip().split(" "), source[i].strip().split(" ")
            
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
                    for pred_token, gold_token, source_token in zip_longest(pred_seq, gold_seq, source_seq, fillvalue=''):
                        p.append(pred_token)
                        t.append(gold_token)
                        s.append(source_token)
                        
                        # Source is correct and the model destroys it
                        if source_token == gold_token != pred_token:
                            destroy_count += 1
                        
                        ocr_dis = distance(gold_token, source_token)
                        broken_difference[ocr_dis] += 1
                        
                        if source_token != gold_token == pred_token:
                            corrected_difference[ocr_dis] += 1
                            fixed_count += 1
                        
                        
                        edits += distance(gold_token, pred_token)
                        gold_characters += len(gold_token)
                    
    acc = accuracy_score(p, t)
    char_accuracy = 1 - edits/gold_characters
    print("Token level accuracy: {}".format(acc))
    print("Character level accuracy: {}".format(char_accuracy))
    print("Token level error rate for already correct words: {}".format(destroy_count/len(s)))

    print("Character errors per token in original data:")
    for i in sorted(broken_difference):
        print('%s: %.2f %s' % (i, broken_difference[i]/len(s)*100, broken_difference[i]))

    print("Character errors per token in fixed tokens:")
    for i in sorted(corrected_difference):
        print('%s: %.2f %s' % (i, corrected_difference[i]/fixed_count*100, corrected_difference[i]))
        
    print("Character errors per token in fixed tokens relative to the number of such errors in the data:")
    for i in sorted(corrected_difference):
        print('%s: %.2f (%s/%s)' % (i, corrected_difference[i]/broken_difference.get(i)*100, corrected_difference[i], broken_difference[i]))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Evaluate seq2seq accuracy.")
    parser.add_argument("--pred", required=True)
    parser.add_argument("--gold", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--eval_level", help="char or word, default=word", default="word")
    parser.add_argument("--truncate", help="Truncate predictions to gold length", action="store_true")

    args = parser.parse_args()
    print(args)

    evaluate(args.input, args.pred, args.gold, args.eval_level, args.truncate)
