"""
LSTM implementation for time series forecasting
with window size three i,e. use of t-2, t-1, and t
for prediction of value at t+1
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import logging
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import LSTM, Dense

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(asctime)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)


def train_test_split(data, fraction=0.7):
    training = int(len(data)*fraction)
    train = data[0:training, :]
    test = data[training:, :]
    return train, test


def prepare_data(data, look_back=3):
    dataX = []
    dataY = []
    for i in range(len(data)-look_back-1):
        temp = data[i:(i+look_back), 0]
        dataX.append(temp)
        dataY.append(data[i+look_back, 0])
    return np.array(dataX), np.array(dataY)


# get the data
df = pd.read_csv('data/AirPassengers.csv', usecols=[1], header=0, engine='python')
data = df.values
data = data.astype('float32')
# print(data[:5])


# split the data into train and test samples
train, test = train_test_split(data, fraction=0.7)
# print(len(train))
# print(len(test))

# prepare the uni-variate data in the form of X, y
trainX, trainY = prepare_data(train, look_back=3)
testX, testY = prepare_data(test, look_back=3)
# print(trainX[:5, :])

# scalar transformation as the prepared data
# fit and transform predictor and outcome variable separately.

scalar = MinMaxScaler(feature_range=(0, 1))

scalar_fitX = scalar.fit(trainX)
trainX = scalar_fitX.transform(trainX)
testX = scalar_fitX.transform(testX)

scalar_fitY = scalar.fit(trainY)
trainY = scalar_fitY.transform(trainY)
testY = scalar_fitY.transform(testY)



# create LSTM model
time_step = 3

# reshape the input in the form of [samples, time step, features]
trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

model = Sequential()
model.add(LSTM(5, activation='tanh', input_shape=(1, time_step)))
model.add(Dense(1))
model.summary()

# training and model fitting
model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(trainX, trainY, batch_size=1, epochs=100, verbose=2)

# prediction
train_pred = model.predict(trainX)
test_pred = model.predict(testX)
# print(train_pred.shape)
# print(train_pred[:5])

# the results are in the form of scaled value, so inverse the transformation
train_pred_inverse = scalar.inverse_transform(train_pred)
test_pred_inverse = scalar.inverse_transform(test_pred)
trainY_inverse = scalar.inverse_transform(trainY)
testY_inverse = scalar.inverse_transform(testY)

# logging.info('Training data : {}\n'.format(trainY_inverse[:5]))
# logging.info('Training data prediction: {}\n'.format(train_pred_inverse[:5]))
# logging.info('Test data : {}\n'.format(testY_inverse[:5]))
# logging.info('Test data prediction: {}\n'.format(test_pred_inverse[:5]))


# # RMSE calculation
# train_rmse = np.sqrt(mean_squared_error(trainY_inverse, train_pred_inverse))
# test_rmse = np.sqrt(mean_squared_error(testY_inverse, test_pred_inverse))
#
# logger.info('Training RMSE: {}'.format(train_rmse))
# logger.info('Test RMSE: {}'.format(test_rmse))
# #
# #
# # plotting the results and comparision
# # shift train predictions for plotting
# train_plot = np.empty_like(data)
# train_plot[:, :] = np.nan
# train_plot[time_step:len(trainY_inverse)+time_step, :] = trainY_inverse
#
# # shift test predictions for plotting
# test_plot = np.empty_like(data)
# test_plot[:, :] = np.nan
# test_plot[len(trainY_inverse)+(time_step*2)+1:len(data)-1, :] = testY_inverse
# #
# # plot baseline and predictions
# plt.plot(data, 'r', label='data')
# plt.plot(train_plot, 'g--', label='training')
# plt.plot(test_plot, 'b:', label='test')
# plt.legend(loc=0)
# plt.savefig('plots/ap_lstm_window_result.jpg')
# plt.show()
