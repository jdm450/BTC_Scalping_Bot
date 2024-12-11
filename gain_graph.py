import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Replace 'portfolio_data.json' with your actual JSON file path
json_file_path = 'trading_history.json'

# Step 1: Load JSON Data
try:
    with open(json_file_path, 'r') as file:
        data = json.load(file)
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    exit()

# Ensure data is a list
if isinstance(data, dict):
    # If the JSON is a single dictionary, wrap it in a list
    data = [data]
elif not isinstance(data, list):
    print("JSON data is neither a list nor a dictionary.")
    exit()

# Step 2: Parse Timestamps and Portfolio Values
timestamps = []
portfolio_values = []
missing_timestamp = 0
missing_portfolio = 0

for idx, entry in enumerate(data):
    # Check for 'timestamp' and 'portfolio_value' keys
    if 'timestamp' not in entry:
        print(f"Entry {idx} is missing 'timestamp' key.")
        missing_timestamp += 1
        continue
    if 'portfolio_value' not in entry:
        print(f"Entry {idx} is missing 'portfolio_value' key.")
        missing_portfolio += 1
        continue

    # Parse the timestamp string into a datetime object
    try:
        timestamp = datetime.fromisoformat(entry['timestamp'])
    except ValueError as e:
        print(f"Error parsing timestamp in entry {idx}: {entry['timestamp']}")
        continue
    timestamps.append(timestamp)

    # Get the portfolio value
    portfolio_values.append(entry['portfolio_value'])

# Report missing keys
if missing_timestamp > 0 or missing_portfolio > 0:
    print(f"Total entries missing 'timestamp': {missing_timestamp}")
    print(f"Total entries missing 'portfolio_value': {missing_portfolio}")

# Check if we have data
if not timestamps or not portfolio_values:
    print("No valid data found in the JSON file.")
    exit()

# Step 3: Calculate Percent Increase
initial_value = portfolio_values[0]
percent_increase = [(value - initial_value) / initial_value * 100 for value in portfolio_values]

# Step 4: Plot the Data
plt.figure(figsize=(12, 6))
plt.plot(timestamps, percent_increase, marker='o', linestyle='-')

# Formatting the plot
plt.title('Portfolio Value Percent Increase Over Time')
plt.xlabel('Time')
plt.ylabel('Percent Increase (%)')
plt.grid(True)

# Improve date formatting on the x-axis
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())

plt.gcf().autofmt_xdate()  # Rotate date labels

plt.tight_layout()
plt.show()
