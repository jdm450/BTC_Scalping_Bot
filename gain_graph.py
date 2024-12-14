import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import MultipleLocator

# Load data
with open('trading_history.json', 'r') as file:
    data = json.load(file)

# Adjust Data Frame for Account Value
transactions_df = pd.json_normalize(data, 'transactions')
transactions_df['capital'] = transactions_df['capital'].astype(int)
filtered_df = transactions_df[transactions_df['capital'] != 0]
capital_df = filtered_df['capital']
df = capital_df.drop(capital_df.index[0:26])

# Add Percent Increase Column for Account Value
df_pct_increase = ((df - df.iloc[0]) / df.iloc[0]) * 100

# Plot data
plt.style.use('dark_background')
plt.figure(figsize=(14, 8))
plt.plot(df, label='Scalping Bot Account Value', color='red')
plt.title('BTC Scalping Bot', fontsize=16)
plt.xlabel('Starts: 12/10/2024 1:00 PM', fontsize=14)
plt.ylabel('Account Value', fontsize=14)  # Changed to match the data being plotted

# Customize y-axis
ax = plt.gca()  # Get current axis
ax.set_ylim(bottom=20000)  # Set the y-axis to start at 20,000
ax.yaxis.set_major_locator(MultipleLocator(1000))  # Set major ticks every 2,000

plt.grid(color='dimgray')
plt.xticks([])  # Remove x-axis ticks if not needed
plt.legend()
plt.show()
