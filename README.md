# ocr-correction
Post-processing OCR errors with seq2seq models

# Running OpenNMT
Preprocessing: 
`python preprocess.py -train_src ../data/open_nmt_train_input.txt -train_tgt ../data/open_nmt_train_output.txt -valid_src ../data/open_nmt_devel_input.txt -valid_tgt ../data/open_nmt_devel_output.txt -save_data ../data/open/open -src_seq_length 10000 -tgt_seq_length 10000 -src_seq_length_trunc 500 -tgt_seq_length_trunc 500`
Training: 
`python train.py -data ../data/open/open -save_model ../models/open/open -gpuid 0`

99% of the data is within the 500 character limit.

# Evaluate

Evaluation script takes in two files, predictions and gold. Each file has one sentence per line.
`python3 evaluate.py --pred pred_file.txt --gold gold_file.txt`

