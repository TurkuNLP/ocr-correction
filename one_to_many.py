import gzip, json, tqdm
from align import needle

if __name__ == "__main__":

    data_location = "data/values.gz"
    d = json.load(gzip.open(data_location, "rt"))

    one_to_many_c = 0
    lines = 0
    wrong = 0
    tot = 0
    for line in tqdm.tqdm(d):
        gold, tesseract, ocr = line[5], line[7], line[8]
        if None in [gold, tesseract, ocr]: continue
        if len(gold) != len(ocr):
            #print(gold, ocr)
            symbol, s1, s2 = needle(gold, ocr)
            #print(s1)
            #print(symbol)
            #print(s2)
            c = s1.count("-")
            one_to_many_c += c
            lines += 1
            if abs(len(gold) - len(ocr)) > 8:
                print(gold, ocr)
                wrong += 1
        tot += 1
    print(one_to_many_c, lines, wrong, tot)
