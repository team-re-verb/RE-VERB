import numpy as np
from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.models import load_model

from ge2e_loss import GE2E_loss


def preapare_model():
    model = Sequential()
    model.add(LSTM(768, input_shape=(40,1), return_sequences=True))
    model.add(LSTM(768, input_shape=(50,1), return_sequences=True))
    model.add(LSTM(768, input_shape=(50,1), return_sequences=True))
    model.add(Dense(50))

    #The d-vector model is a 3-layer LSTM network with a final linear layer.
    #Each LSTM layer has 768 nodes, with projection of
    #256 nodes

    model.compile(loss=GE2E_loss, optimizer='adam', metrics=['acuracy'])
    
    return model


def get_dataset():
    return ""


def train_model():
    ( (X_train, X_test), (Y_train, Y_test) ) = get_dataset()
    model = preapare_model()

    model.fit(X_train, Y_train, epoches=5, verbose=1) #Need to find from paper how many epoches
    score = model.evaluate(X_test, Y_test, verbose=2)

    print(f'model score: {score}')
    print('saving model as model.h5')

    model.save('model.h5')



if __name__ == "__main__":
    train_model()