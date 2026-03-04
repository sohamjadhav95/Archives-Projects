import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

class StockPricePrediction:
    def __init__(self, ticker, start_date, end_date):
        """
        Initialize the stock price prediction model
        
        :param ticker: Stock ticker symbol
        :param start_date: Start date for data collection
        :param end_date: End date for data collection
        """
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
    def fetch_stock_data(self):
        """
        Fetch stock data from Yahoo Finance
        
        :return: Pandas DataFrame with stock data
        """
        try:
            # Fetch stock data with auto_adjust=True to ensure correct pricing
            data = yf.download(self.ticker, start=self.start_date, end=self.end_date, auto_adjust=True)
            
            # Check if data is empty
            if data.empty:
                raise ValueError(f"No data found for ticker {self.ticker} in the specified date range.")
            
            # Use closing price for prediction, with fallback options
            if 'Adj Close' in data.columns:
                return data[['Adj Close']]
            elif 'Close' in data.columns:
                return data[['Close']]
            else:
                raise KeyError("No closing price column found in the data.")
        
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            raise
    
    def prepare_data(self, data, look_back=60):
        """
        Prepare data for LSTM model
        
        :param data: Stock price data
        :param look_back: Number of previous days to use for prediction
        :return: Scaled data, X_train, y_train, X_test, y_test
        """
        # Ensure data is numpy array
        if isinstance(data, pd.DataFrame):
            data = data.values
        
        # Normalize the data
        scaled_data = self.scaler.fit_transform(data)
        
        # Prepare training data
        X, y = [], []
        for i in range(look_back, len(scaled_data)):
            X.append(scaled_data[i-look_back:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        return scaled_data, X_train, y_train, X_test, y_test
    
    def build_lstm_model(self, input_shape):
        """
        Build LSTM neural network model
        
        :param input_shape: Shape of input data
        :return: Compiled Keras model
        """
        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(units=50, return_sequences=False),
            Dropout(0.2),
            Dense(units=25, activation='relu'),
            Dense(units=1)
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
        return model
    
    def train_model(self, X_train, y_train, X_test, y_test):
        """
        Train the LSTM model
        
        :param X_train: Training input data
        :param y_train: Training target data
        :param X_test: Testing input data
        :param y_test: Testing target data
        """
        # Train the model
        self.model = self.build_lstm_model(X_train.shape[1:])
        
        # Early stopping to prevent overfitting
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss', 
            patience=10, 
            restore_best_weights=True
        )
        
        history = self.model.fit(
            X_train, y_train, 
            epochs=100,  # Increased epochs with early stopping 
            batch_size=32, 
            validation_data=(X_test, y_test),
            callbacks=[early_stopping],
            verbose=1
        )
        
        return history
    
    def predict_prices(self, scaled_data, X_test, y_test):
        """
        Predict stock prices and calculate accuracy
        
        :param scaled_data: Scaled stock price data
        :param X_test: Test input data
        :param y_test: Test target data
        :return: Predicted and actual prices
        """
        # Make predictions
        predictions = self.model.predict(X_test)
        
        # Inverse transform the predictions and actual values
        predictions = self.scaler.inverse_transform(predictions)
        y_test = self.scaler.inverse_transform(y_test.reshape(-1, 1))
        
        # Calculate accuracy metrics
        mae = mean_absolute_error(y_test, predictions)
        mse = mean_squared_error(y_test, predictions)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, predictions)
        
        # Calculate accuracy percentage (R-squared as percentage)
        accuracy_percentage = r2 * 100
        
        print(f"\n--- Model Performance Metrics ---")
        print(f"Mean Absolute Error: ${mae:.2f}")
        print(f"Root Mean Squared Error: ${rmse:.2f}")
        print(f"R-squared Accuracy: {accuracy_percentage:.2f}%")
        
        return predictions, y_test
    
    def plot_results(self, predictions, actual):
        """
        Plot actual vs predicted stock prices
        
        :param predictions: Predicted stock prices
        :param actual: Actual stock prices
        """
        plt.figure(figsize=(15, 8))
        plt.plot(actual, label='Actual Price', color='blue', alpha=0.7)
        plt.plot(predictions, label='Predicted Price', color='red', alpha=0.7)
        plt.title(f'{self.ticker} Stock Price Prediction', fontsize=16)
        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Stock Price ($)', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()
    
    def run_prediction(self):
        """
        Run the entire stock price prediction process
        """
        try:
            # Fetch stock data
            data = self.fetch_stock_data()
            
            # Prepare data
            scaled_data, X_train, y_train, X_test, y_test = self.prepare_data(data)
            
            # Train the model
            history = self.train_model(X_train, y_train, X_test, y_test)
            
            # Predict prices and get accuracy
            predictions, actual = self.predict_prices(scaled_data, X_test, y_test)
            
            # Plot results
            self.plot_results(predictions, actual)
            
            return predictions, actual
        
        except Exception as e:
            print(f"An error occurred during prediction: {e}")
            return None, None

# Example usage
if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore')  # Suppress warnings
    
    try:
        # Choose a specific stock and date range
        stock_predictor = StockPricePrediction(
            ticker='AAPL',  # Apple stock as an example
            start_date='2020-01-01', 
            end_date='2024-03-01'
        )
        
        # Run the prediction
        stock_predictor.run_prediction()
    
    except Exception as e:
        print(f"Error in main execution: {e}")