import pydot
import graphviz
from keras.layers import Dense, Dropout, LSTM, Embedding, Activation, Lambda
from keras.engine import Input, Model, InputSpec
from keras.preprocessing.sequence import pad_sequences
from keras.utils import plot_model
from keras.utils.data_utils import get_file
from keras.models import Sequential
from keras import backend as K
from keras.models import model_from_json
from kerastoolbox.visu import plot_weights
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import theano
import tensorflow as tf


RNN_HIDDEN_DIM = 256
EMBEDDING_DIM = 50
epochs = 1000

input_file = 'input.csv'
test_file = 'test.csv'

def letter_to_index(letter):
    _alphabet = 'ATGC'
    return next((i for i, _letter in enumerate(_alphabet) if _letter == letter), None)

def load_data(test_split = 0.2):
    print ('Loading data...')
    df = pd.read_csv(input_file)
    df['sequence'] = df['sequence'].apply(lambda x: [int(letter_to_index(e)) for e in x])
    df = df.reindex(np.random.permutation(df.index))
    train_size = int(len(df) * (1 - test_split))
    X_train = df['sequence'].values[:train_size]
    y_train = np.array(df['target'].values[:train_size])
    X_test = np.array(df['sequence'].values[train_size:])
    y_test = np.array(df['target'].values[train_size:])
    return pad_sequences(X_train), y_train, pad_sequences(X_test), y_test

def create_model(input_length, rnn_hidden_dim=RNN_HIDDEN_DIM):
    print ('Creating model...')
    model = Sequential()
    model.add(Embedding(input_dim = 188, output_dim = EMBEDDING_DIM, input_length = input_length, name='embedding_layer'))

    model.add(LSTM(output_dim=rnn_hidden_dim, activation='sigmoid', inner_activation='hard_sigmoid', return_sequences=True, name='recurrent_layer'))

    model.add(Dropout(0.5))
    model.add(LSTM(output_dim=rnn_hidden_dim, activation='sigmoid', inner_activation='hard_sigmoid'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))
    print ('Compiling...')
    model.compile(loss='binary_crossentropy',
                  optimizer='rmsprop',
                  metrics=['accuracy'])
    return model

def create_plots(history):
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig('accuracy.png')
    plt.clf()

    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig('loss.png')
    plt.clf()

X_train, y_train, X_test, y_test = load_data()
model = create_model(len(X_train[0]))

print ('Fitting model...')
history = model.fit(X_train, y_train, batch_size=128, nb_epoch=epochs, validation_split = 0.1, verbose = 1)


# serialize model to JSON
model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights("model.h5")
print("Saved model to disk")

create_plots(history)
plot_model(model, to_file='model.png')

# summarize history for loss
score, acc = model.evaluate(X_test, y_test, batch_size=1)

print('Test score:', score)
print('Test accuracy:', acc)

