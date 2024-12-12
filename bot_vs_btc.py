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

# Adjust Data Frame for Bitcoin Price
btc_price_df = pd.json_normalize(data, 'transactions')
btc_price_df['price'] = btc_price_df['price'].astype(int)
price_df = btc_price_df['price']
price_df = price_df.drop(price_df.index[0:52])

# Add Percent Increase Column for Account Value
df_pct_increase = ((df - df.iloc[0]) / df.iloc[0]) * 100

# Add Percent Increase Column for BTC Price
df_btc_pct = ((price_df - price_df.iloc[0]) / price_df.iloc[0]) * 100

# Plot data
plt.style.use('dark_background')

ax = df_pct_increase.plot(kind='line', figsize=(14,8), label='Scalping Bot', color='red')
plt.plot(df_btc_pct, label='BTC Price', color='gainsboro')
plt.title('BTC Scalping Bot', fontsize=16)
plt.xlabel('Starts: 12/10/2024 1:00 PM', fontsize=14)
plt.ylabel('Percent Increase', fontsize=14)
plt.grid(color='dimgray')
plt.legend()

plt.xticks([])

ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.yaxis.set_major_locator(MultipleLocator(2.5))

plt.show()
