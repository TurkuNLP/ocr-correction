def doc2sentences(document, single_tokens=False, input_index=1):
    """
    Concatenates tokens in a document and splits the result into sentences.
    The sentence splitting relies on the gold standard data, i.e. this will easen the task.
    Returns both gold and OCR sentences
    
    single_tokens = True will return single tokens instead of sentences.
    input_index = 1 -> current ocr, 2 -> tesseract
    """
    gold_sentences = []
    ocr_sentences = []
    gold_sentence = []
    ocr_sentence = []
    for token in document[1]:
        gold_token = token[0]
        ocr_token = token[input_index]
        gold_sentence.append(gold_token)
        # The OCR data may have caps after the alignment with the gold standard data.
        if ocr_token:
            ocr_sentence.append(ocr_token)
        # else:
        #     ocr_sentence.append('')
        if single_tokens:
            gold_sentences.append(gold_sentence)
            ocr_sentences.append(ocr_sentence)
            gold_sentence = []
            ocr_sentence = []
        elif gold_token.endswith('.'):
            gold_sentences.append(gold_sentence)
            ocr_sentences.append(ocr_sentence)
            gold_sentence = []
            ocr_sentence = []
    # Add the final sentences if it didn't end in a full stop
    if len(gold_sentence) > 0:
        gold_sentences.append(gold_sentence)
        ocr_sentences.append(ocr_sentence)
    
    # import pdb; pdb.set_trace()
    gold_sentences = [' '.join(s) for s in gold_sentences]
    ocr_sentences = [' '.join(s) for s in ocr_sentences]
    
    return gold_sentences, ocr_sentences