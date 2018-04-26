import gzip, json, pickle

import numpy as np
from keras.models import Model, load_model
from keras.layers import Input, LSTM, Dense
from keras.callbacks import EarlyStopping, ModelCheckpoint

from utils import doc2sentences

'''
seq2seq in Keras.
'''


batch_size = 32
max_sent_count = 1000000
max_sent_len = 250
epochs = 100

lstm_dim = 256
data_train = "data/train.json.gz"
data_test = "data/test.json.gz"
data_devel = "data/devel.json.gz"

def read_data(location, train_args=None, verbose=False):
    input_texts, target_texts = [], []
    input_chars, target_chars = set(), set()
    data = json.load(gzip.open(location, "rt"))
    for doc_i, document in enumerate(data):
        gold, ocr = doc2sentences(document)
        if len(input_texts) >= max_sent_count: break
        for i in range(len(gold)):
            if len(input_texts) >= max_sent_count: break
            input_text, target_text = ocr[i], gold[i]
            input_text = input_text[:max_sent_len]
            target_text = target_text[:max_sent_len]
            ## add start seq and end seq chars to gold (target)
            target_text = "\t" + target_text + "\n"
            input_texts.append(input_text)
            target_texts.append(target_text)
            input_chars = input_chars.union(set(input_text))
            target_chars = target_chars.union(set(target_text))

    if train_args:
        input_chars, target_chars, num_encoder_tokens, num_decoder_tokens = train_args[0:4]
        max_enc_length, max_dec_length, input_char_map, target_char_map = train_args[4:8]
        rev_input_char_map, rev_target_char_map = train_args[8:10]
    else:
        input_chars, target_chars = sorted(list(input_chars)), sorted(list(target_chars))
        num_encoder_tokens = len(input_chars)
        num_decoder_tokens = len(target_chars)
        max_enc_length = max([len(sent) for sent in input_texts])
        max_dec_length = max([len(sent) for sent in target_texts])
        input_char_map = dict([(char, i) for i, char in enumerate(input_chars)])
        target_char_map = dict([(char, i) for i , char in enumerate(target_chars)])
        rev_input_char_map = {v:k for k,v in input_char_map.items()}
        rev_target_char_map = {v:k for k,v in target_char_map.items()}
        train_args = [input_chars, target_chars, num_encoder_tokens, num_decoder_tokens,
                        max_enc_length, max_dec_length, input_char_map, target_char_map,
                        rev_input_char_map, rev_target_char_map]

    encoder_input_data = np.zeros((len(input_texts), max_enc_length, num_encoder_tokens))
    decoder_input_data = np.zeros((len(input_texts), max_dec_length, num_decoder_tokens))
    decoder_target_data = np.zeros((len(input_texts), max_dec_length, num_decoder_tokens))

    for i, texts in enumerate(zip(input_texts, target_texts)):
        input_text, target_text = texts
        for char_i, char in enumerate(input_text):
            if char_i == max_enc_length: break
            if char in input_char_map:
                encoder_input_data[i, char_i, input_char_map[char]] = 1.
        for char_i, char in enumerate(target_text):
            if char_i == max_dec_length: break
            if char in target_char_map:
                decoder_input_data[i, char_i, target_char_map[char]] = 1.
                if char_i > 0: ## target = +1 timestep
                    decoder_target_data[i, char_i-1, target_char_map[char]] = 1.

    if verbose:
        print("Number of sentences: {}".format(len(input_texts)))
        print("Number of unique input tokens: {}".format(num_encoder_tokens))
        print("Number of unique output tokens: {}".format(num_decoder_tokens))
        print("Max sequence length for inputs: {}".format(max_enc_length))
        print("Max sequence length for outputs: {}".format(max_dec_length))

    return [input_texts, target_texts], encoder_input_data, decoder_input_data, decoder_target_data, train_args

def make_models(train_args):
    num_encoder_tokens, num_decoder_tokens = train_args[2:4]
    encoder_inputs = Input(shape=(None, num_encoder_tokens))
    encoder = LSTM(lstm_dim, return_state=True)
    encoder_outputs, enc_state_h, enc_state_c = encoder(encoder_inputs)
    ##discard outputs

    encoder_states = [enc_state_h, enc_state_c]
    decoder_inputs = Input(shape=(None, num_decoder_tokens))
    decoder = LSTM(lstm_dim, return_sequences=True, return_state=True)
    decoder_outputs, dec_state_h, dec_state_c = decoder(decoder_inputs, initial_state=encoder_states)
    ##discard decoder states

    decoder_out = Dense(num_decoder_tokens, activation="softmax")
    decoder_outputs = decoder_out(decoder_outputs)

    train_model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
    train_model.compile(optimizer="rmsprop", loss="categorical_crossentropy")

    encoder_model = Model(encoder_inputs, encoder_states)

    decoder_input_state_h = Input(shape=(lstm_dim, ))
    decoder_input_state_c = Input(shape=(lstm_dim, ))
    decoder_states_inputs = [decoder_input_state_h, decoder_input_state_c]
    decoder_outputs, dec_state_h, dec_state_c = decoder(decoder_inputs, initial_state=decoder_states_inputs)
    decoder_states = [dec_state_h, dec_state_c]
    decoder_outputs = decoder_out(decoder_outputs)
    decoder_model = Model([decoder_inputs] + decoder_states_inputs, [decoder_outputs] + decoder_states)

    return train_model, encoder_model, decoder_model

def test_model(encoder_model, decoder_model, texts, enc_inp, dec_inp, dec_target, train_args):
    input_texts, target_texts = texts
    for i in range(len(input_texts)):
        input_sentence = enc_inp[i:i+1]
        decoded_sentence = decode_sentence(input_sentence, train_args)
        print("Input sentence: {}\nDecoded sentence: {}\nTarget sentence: {}\n\n".format(input_texts[i], decoded_sentence, target_texts[i]))

def decode_sentence(input_sequence, train_args):
    num_decoder_tokens, max_decoder_length = train_args[3], train_args[5]
    target_char_map, rev_target_char_map = train_args[7], train_args[9]
    states = encoder_model.predict(input_sequence)
    target_sequence = np.zeros((1, 1, num_decoder_tokens))
    target_sequence[0, 0, target_char_map["\t"]] = 1.

    keep_running = True
    decoded_chars = []
    while keep_running:
        output_tokens, h, c = decoder_model.predict([target_sequence] + states)
        dec_char_index = np.argmax(output_tokens[0, -1, :])
        dec_char = rev_target_char_map[dec_char_index]
        decoded_chars.append(dec_char)
        target_sequence = np.zeros((1, 1, num_decoder_tokens))
        target_sequence[0, 0, dec_char_index] = 1.
        states = [h, c]
        if dec_char == "\n" or len(decoded_chars) > max_decoder_length:
            keep_running = False

    return "".join(decoded_chars)


def save_models(train_model, encoder_model, decoder_model, train_args):
    for f in zip([train_model, encoder_model, decoder_model], ["models/train.h5", "models/encoder.h5", "models/decoder.h5"]):
        f[0].save(f[1])
    with open("models/train_args.pkl", "wb") as pf:
        pickle.dump(train_args, pf)

if __name__ == "__main__":

    train_texts, train_enc_inp, train_dec_inp, train_dec_target, train_args = read_data(data_train, verbose=True)
    train_model, encoder_model, decoder_model = make_models(train_args)
    devel_texts, devel_enc_inp, devel_dec_inp, devel_dec_target, _ = read_data(data_devel, train_args=train_args)
    checkpoint = ModelCheckpoint("models/train-{epoch:03d}.h5", verbose=1, monitor="val_loss", save_best_only=True)
    early_stop = EarlyStopping(monitor="val_loss", patience=5, verbose=0)
    train_model.fit([train_enc_inp, train_dec_inp], train_dec_target, batch_size=batch_size, epochs=epochs, callbacks=[early_stop, checkpoint], validation_data=([devel_enc_inp, devel_dec_inp], devel_dec_target))
    save_models(train_model, encoder_model, decoder_model, train_args)

    #train_model, encoder_model, decoder_model, train_args = load_models()
    test_texts, test_enc_inp, test_dec_inp, test_dec_target, _ = read_data(data_test, train_args=train_args)
    test_model(encoder_model, decoder_model, test_texts, test_enc_inp, test_dec_inp, test_dec_target, train_args)
