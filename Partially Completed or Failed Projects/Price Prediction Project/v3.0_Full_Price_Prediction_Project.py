import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_absolute_percentage_error

# Fetch Stock Data
def get_stock_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    return data['Close']

# Prepare Data
def prepare_data(data, time_steps=60):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data.values.reshape(-1, 1))
    X, Y = [], []
    for i in range(time_steps, len(scaled_data)):
        X.append(scaled_data[i-time_steps:i, 0])
        Y.append(scaled_data[i, 0])
    return np.array(X), np.array(Y), scaler

# Split Data
def split_data(X, Y, train_size=0.8):
    train_size = int(len(X) * train_size)
    return X[:train_size], Y[:train_size], X[train_size:], Y[train_size:]

# Build Model
def build_lstm_model(input_shape):
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(25),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Predict and Evaluate
def predict_and_plot(model, X_test, Y_test, scaler, actual_data):
    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)
    actual_prices = scaler.inverse_transform(Y_test.reshape(-1, 1))
    accuracy = 100 - mean_absolute_percentage_error(actual_prices, predictions) * 100
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(actual_data.index[-len(actual_prices):], actual_prices, label='Actual Price', color='blue')
    plt.plot(actual_data.index[-len(predictions):], predictions, label='Predicted Price', color='red')
    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.title('Stock Price Prediction')
    plt.legend()
    plt.show()
    
    print(f'Prediction Accuracy: {accuracy:.2f}%')

# Run Project
if __name__ == "__main__":
    stock_ticker = 'GOOG'
    start_date = '2020-01-01'
    end_date = '2024-01-01'
    
    data = get_stock_data(stock_ticker, start_date, end_date)
    X, Y, scaler = prepare_data(data)
    X_train, Y_train, X_test, Y_test = split_data(X, Y)
    
    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
    
    model = build_lstm_model((X_train.shape[1], 1))
    model.fit(X_train, Y_train, epochs=50, batch_size=32)
    
    predict_and_plot(model, X_test, Y_test, scaler, data)