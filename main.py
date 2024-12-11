import ccxt
import pandas as pd
import numpy as np
import time
import json
from datetime import datetime, timedelta, timezone
import os

# Initialize Kraken exchange
exchange = ccxt.kraken()

# Parameters
SYMBOL = 'BTC/USD'          # Trading pair
FETCH_INTERVAL = 3          # Fetch data every 3 seconds
SMA_WINDOW_SECONDS = 60     # 1-minute SMA window
INITIAL_CAPITAL = 10000     # Starting with $10,000
HISTORY_FILE = 'trading_history.json'  # File to store trading history

# Utility Functions

def load_trading_history():
    """
    Loads trading history from the HISTORY_FILE.
    Returns a dictionary with 'transactions' and 'portfolio_history'.
    If the file doesn't exist, returns empty lists.
    """
    if not os.path.exists(HISTORY_FILE):
        return {'transactions': [], 'portfolio_history': []}
    try:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
            # Convert timestamp strings back to datetime objects
            for txn in history.get('transactions', []):
                txn['timestamp'] = datetime.fromisoformat(txn['timestamp'])
            for portfolio in history.get('portfolio_history', []):
                portfolio['timestamp'] = datetime.fromisoformat(portfolio['timestamp'])
            return history
    except Exception as e:
        print(f"Error loading trading history: {e}")
        return {'transactions': [], 'portfolio_history': []}

def save_trading_history(history):
    """
    Saves trading history to the HISTORY_FILE.
    Converts datetime objects to ISO format strings for JSON serialization.
    """
    try:
        # Create a serializable copy
        serializable_history = {
            'transactions': [
                {
                    'timestamp': txn['timestamp'].isoformat(),
                    'action': txn['action'],
                    'price': txn['price'],
                    'btc_holding': txn['btc_holding'],
                    'capital': txn['capital']
                } for txn in history.get('transactions', [])
            ],
            'portfolio_history': [
                {
                    'timestamp': portfolio['timestamp'].isoformat(),
                    'portfolio_value': portfolio['portfolio_value']
                } for portfolio in history.get('portfolio_history', [])
            ]
        }
        with open(HISTORY_FILE, 'w') as f:
            json.dump(serializable_history, f, indent=4)
    except Exception as e:
        print(f"Error saving trading history: {e}")

def display_transaction_history(history):
    """
    Displays all transactions in a formatted table.
    """
    transactions = history.get('transactions', [])
    if not transactions:
        print("\nNo transactions found.\n")
        return
    df_txn = pd.DataFrame(transactions)
    df_txn['timestamp'] = df_txn['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S %Z')
    df_txn = df_txn[['timestamp', 'action', 'price', 'btc_holding', 'capital']]
    print("\n--- Transaction History ---")
    print(df_txn.to_string(index=False))
    print("----------------------------\n")

# Main Functions

def start_trading_bot():
    """
    Starts the live trading bot.
    """
    # Load existing trading history
    history = load_trading_history()
    transactions = history['transactions']
    portfolio_history = history['portfolio_history']
    
    # Initialize trading variables
    if portfolio_history:
        # Start with the last portfolio value
        capital = portfolio_history[-1]['portfolio_value']
        btc_holding = 0  # Assuming all positions were closed
        position = 0
        print(f"\nResuming with Capital: ${capital:.2f}")
    else:
        capital = INITIAL_CAPITAL
        btc_holding = 0
        position = 0
        print(f"\nInitial Capital: ${INITIAL_CAPITAL}")
    
    prev_relation = 'none'
    
    # Initialize DataFrame to store fetched prices
    # Columns: ['price']
    # Index: ['timestamp'] with UTC timezone
    df = pd.DataFrame(columns=['price'])
    df.index = pd.to_datetime(df.index).tz_localize('UTC')  # Ensure index is timezone-aware
    
    print(f"Starting trading bot at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("Monitoring BTC/USD price and 1-minute SMA crossover signals...\n")
    
    try:
        while True:
            # Fetch current price
            current_price = fetch_current_price()
            if current_price is None or np.isnan(current_price):
                # Skip this iteration if price fetching failed or returned NaN
                time.sleep(FETCH_INTERVAL)
                continue
    
            # Use timezone-aware UTC datetime
            current_time = datetime.now(timezone.utc)
    
            # Update DataFrame with the latest price and assign back to df
            df = update_dataframe(current_time, current_price, df)
    
            # Calculate the current SMA
            current_sma = calculate_sma(df)
    
            if current_sma is None:
                print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}] Not enough data to calculate SMA.")
                time.sleep(FETCH_INTERVAL)
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
                    transaction = {
                        'timestamp': current_time,
                        'action': 'BUY',
                        'price': current_price,
                        'btc_holding': btc_holding,
                        'capital': capital
                    }
                    transactions.append(transaction)
                    print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}] BUY at ${current_price:.2f} | BTC Holdings: {btc_holding:.6f}")
            elif prev_relation == 'above' and current_relation == 'below':
                # Sell signal
                if position == 1:
                    capital = btc_holding * current_price
                    btc_holding = 0
                    position = 0
                    transaction = {
                        'timestamp': current_time,
                        'action': 'SELL',
                        'price': current_price,
                        'btc_holding': btc_holding,
                        'capital': capital
                    }
                    transactions.append(transaction)
                    print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}] SELL at ${current_price:.2f} | Cash: ${capital:.2f}")
    
            # Update previous relation
            prev_relation = current_relation
    
            # Record portfolio value
            portfolio_value = capital + btc_holding * current_price
            portfolio_entry = {'timestamp': current_time, 'portfolio_value': portfolio_value}
            portfolio_history.append(portfolio_entry)
    
            # Save updated history to JSON file
            history = {'transactions': transactions, 'portfolio_history': portfolio_history}
            save_trading_history(history)
    
            # Wait for the next fetch
            time.sleep(FETCH_INTERVAL)
    
    except KeyboardInterrupt:
        # Handle script termination
        final_portfolio = capital + btc_holding * current_price
        portfolio_entry = {'timestamp': current_time, 'portfolio_value': final_portfolio}
        portfolio_history.append(portfolio_entry)
        history = {'transactions': transactions, 'portfolio_history': portfolio_history}
        save_trading_history(history)
        print("\n--- Trading Bot Stopped ---")
        print(f"Final Portfolio Value: ${final_portfolio:.2f}")
        print(f"Total Return: {((final_portfolio - (INITIAL_CAPITAL if not portfolio_history else portfolio_history[0]['portfolio_value'])) / (INITIAL_CAPITAL if not portfolio_history else portfolio_history[0]['portfolio_value'])) * 100:.2f}%\n")

def view_transaction_history():
    """
    Displays all past transactions.
    """
    history = load_trading_history()
    display_transaction_history(history)

def update_dataframe(current_time, current_price, df):
    """
    Adds the latest price to the DataFrame and maintains the SMA window.
    """
    # Create a new row as a DataFrame with 'price' column
    new_row = pd.DataFrame({
        'price': [current_price]
    }, index=[current_time])
    
    # Ensure that 'price' is not NaN
    if not new_row.empty and not new_row['price'].isna().any():
        # Concatenate the new_row to df
        df = pd.concat([df, new_row])
        # Keep only data within the SMA window
        cutoff_time = current_time - timedelta(seconds=SMA_WINDOW_SECONDS)
        df = df[df.index > cutoff_time]
    else:
        print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}] Skipping concatenation due to empty or invalid new_row.")
    
    # Return the updated DataFrame
    return df

def calculate_sma(df):
    """
    Calculates the Simple Moving Average (SMA) over the defined window.
    Returns the SMA value or None if insufficient data.
    """
    if df.empty:
        return None
    return df['price'].mean()

def fetch_current_price():
    """
    Fetches the current BTC/USD price from Kraken.
    Returns the last price or None if fetching fails.
    """
    try:
        ticker = exchange.fetch_ticker(SYMBOL)
        return ticker['last']
    except Exception as e:
        print(f"Error fetching ticker data: {e}")
        return None

# Menu Interface

def display_menu():
    """
    Displays the main menu and handles user input.
    """
    while True:
        print("=== BTC Trading Bot ===")
        print("1. Start Trading Bot")
        print("2. View Transaction History")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ").strip()
        
        if choice == '1':
            start_trading_bot()
        elif choice == '2':
            view_transaction_history()
        elif choice == '3':
            print("Exiting the trading bot. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.\n")

# Entry Point

if __name__ == "__main__":
    display_menu()
