import yfinance as yf
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Fetch S&P 500 data
sp500 = yf.Ticker("^GSPC")  
data = sp500.history(period="max")  # Fetch full data

# Ensure data is fetched
if data.empty:
    raise ValueError("No data found for S&P 500. Try adjusting the period or check Yahoo Finance.")

# Filter last 10 years
data = data.loc["2014-03-05":]

# Drop columns if they exist
for col in ["Dividends", "Stock Splits"]:
    if col in data.columns:
        data.drop(columns=[col], inplace=True)

print("Data successfully fetched and cleaned!")
print(data.head())

# Creating target variable (tomorrow's price movement)
data["Tomorrow"] = data["Close"].shift(-1)
data["Target"] = (data["Tomorrow"] > data["Close"]).astype(int)
data.drop(columns=["Tomorrow"], inplace=True)

# Feature Engineering
data["EMA_10"] = data["Close"].ewm(span=10, adjust=False).mean()
data["Buy_Signal"] = (data["Open"] > data["EMA_10"]).astype(int)
data["Sell_Signal"] = (data["Open"] < data["EMA_10"]).astype(int)

# Add more technical indicators
data["MA_50"] = data["Close"].rolling(window=50).mean()
data["Returns"] = data["Close"].pct_change()
data["Volatility"] = data["Returns"].rolling(window=20).std()

# Dropping NaN values
data.dropna(inplace=True)

# Defining features and target
features = [
    "Open", "High", "Low", "Close", "Volume", 
    "EMA_10", "Buy_Signal", "Sell_Signal", 
    "MA_50", "Returns", "Volatility"
]
X = data[features]
y = data["Target"]

# Splitting dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

# Model Training
model = RandomForestClassifier(
    n_estimators=100, 
    random_state=42, 
    max_depth=10,  # Added to prevent overfitting
    min_samples_split=5,
    min_samples_leaf=2
)
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Model Evaluation
accuracy = accuracy_score(y_test, y_pred)
print("\nModel Performance:")
print("Accuracy Score:", accuracy)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Feature Importance
feature_importance = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print("\nFeature Importance:")
print(feature_importance)

# Visualization 1: Close Price and Moving Averages
plt.figure(figsize=(15, 10))
plt.subplot(2, 1, 1)
plt.plot(data.index, data["Close"], label="Close Price")
plt.plot(data.index, data["EMA_10"], label="10-day EMA", color="red")
plt.plot(data.index, data["MA_50"], label="50-day MA", color="green")
plt.title("S&P 500 Closing Price, EMA & Moving Average")
plt.legend()
plt.xlabel("Date")
plt.ylabel("Price")
plt.xticks(rotation=45)

# Visualization 2: Feature Importance
plt.subplot(2, 1, 2)
feature_importance.plot(x='feature', y='importance', kind='bar', ax=plt.gca())
plt.title("Feature Importance in Price Movement Prediction")
plt.xlabel("Features")
plt.ylabel("Importance")
plt.tight_layout()

plt.show()