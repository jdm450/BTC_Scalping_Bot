import ccxt
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

# Initialize Kraken exchange
exchange = ccxt.kraken()

# Parameters
symbol = 'BTC/USD'        # Trading pair
fetch_interval = 3        # Fetch data every 3 seconds
sma_window_seconds = 60   # 1-minute SMA window
initial_capital = 10000   # Starting with $10,000

# Initialize trading variables
capital = initial_capital
btc_holding = 0
position = 0  # 0 = no position, 1 = holding BTC
portfolio_history = []

# Initialize DataFrame to store fetched prices
# Columns: ['timestamp', 'price']
df = pd.DataFrame(columns=['timestamp', 'price'])

# Function to fetch the current price
def fetch_current_price():
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        print(f"Error fetching ticker data: {e}")
        return None

# Function to update the DataFrame with the latest price
def update_dataframe(current_time, current_price):
    global df
    new_row = pd.DataFrame({
        'timestamp': [current_time],
        'price': [current_price]
    })
    new_row.set_index('timestamp', inplace=True)
    df = pd.concat([df, new_row])
    # Keep only data within the SMA window
    cutoff_time = current_time - timedelta(seconds=sma_window_seconds)
    df = df[df.index > cutoff_time]

# Function to calculate the SMA
def calculate_sma():
    if df.empty:
        return None
    return df['price'].mean()

# Initialize previous relation for crossover detection
prev_sma = calculate_sma()
prev_relation = 'none'

print(f"Initial Capital: ${initial_capital}")
print(f"Starting trading bot at {datetime.utcnow()} UTC")
print("Monitoring BTC/USD price and 1-minute SMA crossover signals...\n")

try:
    while True:
        # Fetch current price
        current_price = fetch_current_price()
        if current_price is None:
            # Skip this iteration if price fetching failed
            time.sleep(fetch_interval)
            continue

        current_time = datetime.utcnow()

        # Update DataFrame with the latest price
        update_dataframe(current_time, current_price)

        # Calculate the current SMA
        current_sma = calculate_sma()

        if current_sma is None:
            print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] Not enough data to calculate SMA.")
            time.sleep(fetch_interval)
            continue

        # Determine the current relationship between price and SMA
        if current_price > current_sma:
            current_relation = 'above'
        elif current_price < current_sma:
            current_relation = 'below'
        else:
            current_relation = 'equal'

        # Detect crossover
        if prev_relation == 'below' and current_relation == 'above':
            # Buy signal
            if position == 0:
                btc_holding = capital / current_price
                capital = 0
                position = 1
                print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] BUY at ${current_price:.2f} | BTC Holdings: {btc_holding:.6f}")
        elif prev_relation == 'above' and current_relation == 'below':
            # Sell signal
            if position == 1:
                capital = btc_holding * current_price
                btc_holding = 0
                position = 0
                print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] SELL at ${current_price:.2f} | Cash: ${capital:.2f}")

        # Update previous relation
        prev_relation = current_relation

        # Record portfolio value
        portfolio_value = capital + btc_holding * current_price
        portfolio_history.append({'timestamp': current_time, 'portfolio_value': portfolio_value})

        # Wait for the next fetch
        time.sleep(fetch_interval)

except KeyboardInterrupt:
    # Handle script termination
    final_portfolio = capital + btc_holding * current_price
    print("\n--- Trading Bot Stopped ---")
    print(f"Final Portfolio Value: ${final_portfolio:.2f}")
    print(f"Total Return: {((final_portfolio - initial_capital) / initial_capital) * 100:.2f}%")
