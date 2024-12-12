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
ax = df_pct_increase.plot(kind='line', figsize=(14,8), color='red')
plt.title('BTC Scalping Bot', fontsize=16)
plt.xlabel('Starts: 12/10/2024 1:00 PM', fontsize=14)
plt.ylabel('Percent Increase', fontsize=14)
plt.grid(color='dimgray')

plt.xticks([])

ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.yaxis.set_major_locator(MultipleLocator(2.5))

plt.show()