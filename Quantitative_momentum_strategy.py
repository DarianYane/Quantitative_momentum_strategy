"""Quantitative Momentum Strategy
"Momentum investing" means investing in the stocks that have increased in price the most.

For this project, we're going to build an investing strategy that selects the 50 stocks with the highest price momentum.
From there, we will calculate recommended trades for an equal-weight portfolio of these 50 stocks.

Library Imports
The first thing we need to do is import the open-source software libraries that we'll be using in this tutorial."""

import numpy as np #The Numpy numerical computing library
import pandas as pd #The Pandas data science library
import requests #The requests library for HTTP requests in Python
import xlsxwriter #The XlsxWriter libarary for 
import math #The Python math module
from scipy import stats #The SciPy stats module

import warnings #importo los warnings por el score
from statistics import mean

"""Importing Our List of Stocks
As before, we'll need to import our list of stocks and our API token before proceeding.
Make sure the .csv file is still in your working directory and import it with the following command:"""

stocks = pd.read_csv('sp_500_stocks.csv')
from secrets import IEX_CLOUD_API_TOKEN

"""Making Our First API Call
It's now time to make the first version of our momentum screener!

We need to get one-year price returns for each stock in the universe. Here's how."""

symbol = 'AAPL'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/stats?token={IEX_CLOUD_API_TOKEN}'
data = requests.get(api_url).json()
#print(data)

"""Parsing Our API Call
This API call has all the information we need. We can parse it using the same square-bracket notation as in the first project of this course. Here is an example."""

#print(data['year1ChangePercent'])

"""Executing A Batch API Call & Building Our DataFrame
Just like in our first project, it's now time to execute several batch API calls and add the information we need to our DataFrame.

We'll start by running the following code cell, which contains some code we already built last time that we can re-use for this project. More specifically, it contains a function called chunks that we can use to divide our list of securities into groups of 100."""

# Function sourced from 
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]   
        
symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#     print(symbol_strings[i])

my_columns = ['Ticker', 'Price', 'One-Year Price Return', 'Number of Shares to Buy']

"""Now we need to create a blank DataFrame and add our data to the data frame one-by-one."""

"""Elimino todo el código que sigue porque estamos haciendo un nuevo dataframe"""
"""
final_dataframe = pd.DataFrame(columns = my_columns)

for symbol_string in symbol_strings:
#     print(symbol_strings)
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        #print(symbol)
        n_final_dataframe = pd.DataFrame(
                                        pd.Series([symbol, 
                                                    data[symbol]['quote']['latestPrice'], 
                                                    data[symbol]['stats']['year1ChangePercent'], 
                                                    'N/A'],
                                                        index = my_columns), 
                                        )
        n_final_dataframe = n_final_dataframe.transpose( )
        final_dataframe = pd.concat([final_dataframe, n_final_dataframe], join="inner") # el inner es para quitar los encabezados en común
"""

"""Removing Low-Momentum Stocks
The investment strategy that we're building seeks to identify the 50 highest-momentum stocks in the S&P 500.

Because of this, the next thing we need to do is remove all the stocks in our DataFrame that fall below this momentum threshold. We'll sort the DataFrame by the stocks' one-year price return, and drop all stocks outside the top 50."""

"""Elimino todo el código que sigue porque estamos haciendo un nuevo dataframe"""
"""
final_dataframe.sort_values('One-Year Price Return', ascending = False, inplace = True)
final_dataframe = final_dataframe[:50]
final_dataframe.reset_index(drop = True, inplace = True) # resetea el index y me arregla todos los 0's que habían quedado (esto tb se podría incorporar en el primer ejercicio)
"""

"""Calculating the Number of Shares to Buy
Just like in the last project, we now need to calculate the number of shares we need to buy. The one change we're going to make is wrapping this functionality inside a function, since we'll be using it again later in this Jupyter Notebook."""

"""Elimino todo el código que sigue porque estamos haciendo un nuevo dataframe"""
"""
def portfolio_input():
    global portfolio_size
    #portfolio_size = input("Enter the value of your portfolio:")
    portfolio_size = 100000

    try:
        val = float(portfolio_size)
    except ValueError:
        print("That's not a number! \n Try again:")
        portfolio_size = input("Enter the value of your portfolio:")

portfolio_input()

position_size = float(portfolio_size) / len(final_dataframe.index)
#print(position_size)
for i in range(0, len(final_dataframe['Ticker'])):
    final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / final_dataframe['Price'][i])

#print(final_dataframe)
"""

"""Building a Better (and More Realistic) Momentum Strategy
Real-world quantitative investment firms differentiate between "high quality" and "low quality" momentum stocks:

+ High-quality momentum stocks show "slow and steady" outperformance over long periods of time
+ Low-quality momentum stocks might not show any momentum for a long time, and then surge upwards.

The reason why high-quality momentum stocks are preferred is because low-quality momentum can often be cause by short-term news that is unlikely to be repeated in the future (such as an FDA approval for a biotechnology company).

To identify high-quality momentum, we're going to build a strategy that selects stocks from the highest percentiles of:

1-month price returns
3-month price returns
6-month price returns
1-year price returns
Let's start by building our DataFrame. You'll notice that I use the abbreviation hqm often. It stands for high-quality momentum."""

hqm_columns = [
                'Ticker', 
                'Price', 
                'Number of Shares to Buy', 
                'One-Year Price Return', 
                'One-Year Return Percentile',
                'Six-Month Price Return',
                'Six-Month Return Percentile',
                'Three-Month Price Return',
                'Three-Month Return Percentile',
                'One-Month Price Return',
                'One-Month Return Percentile',
                'HQM Score'
                ]

hqm_dataframe = pd.DataFrame(columns = hqm_columns)

for symbol_string in symbol_strings:
#     print(symbol_strings)
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        n_final_dataframe = pd.DataFrame(
                                        pd.Series([symbol, 
                                                   data[symbol]['quote']['latestPrice'],
                                                   'N/A',
                                                   data[symbol]['stats']['year1ChangePercent'],
                                                   'N/A',
                                                   data[symbol]['stats']['month6ChangePercent'],
                                                   'N/A',
                                                   data[symbol]['stats']['month3ChangePercent'],
                                                   'N/A',
                                                   data[symbol]['stats']['month1ChangePercent'],
                                                   'N/A',
                                                   'N/A'
                                                   ], 
                                                  index = hqm_columns), 
                                        )
        n_final_dataframe = n_final_dataframe.transpose( )
        hqm_dataframe = pd.concat([hqm_dataframe, n_final_dataframe], join="inner") # el inner es para quitar los encabezados en común

hqm_dataframe.reset_index(drop = True, inplace = True) # resetea el index y me arregla todos los 0's que habían quedado (esto tb se podría incorporar en el primer ejercicio)

"""Calculating Momentum Percentiles
We now need to calculate momentum percentile scores for every stock in the universe.
More specifically, we need to calculate percentile scores for the following metrics for every stock:

One-Year Price Return
Six-Month Price Return
Three-Month Price Return
One-Month Price Return
Here's how we'll do this:"""


time_periods = [
                'One-Year',
                'Six-Month',
                'Three-Month',
                'One-Month'
                ]


for row in hqm_dataframe.index:
    for time_period in time_periods:
        a = hqm_dataframe.loc[row, f'{time_period} Price Return']
        # Busco los None y los remplazo por el float 0.0
        if a == None:
            #print(row)
            #print(f'A {time_period} Price Return')
            hqm_dataframe.loc[row, f'{time_period} Price Return'] = 0.0

for row in hqm_dataframe.index:
    for time_period in time_periods:
        # Hago una segunda bísqueda de control
        b = hqm_dataframe.loc[row, f'{time_period} Price Return']
        if b == None:
            print('siguen los errores')

# Deshabilito los warnings
warnings.filterwarnings("ignore")

for row in hqm_dataframe.index:
    for time_period in time_periods:
        hqm_dataframe.loc[row, f'{time_period} Return Percentile'] = stats.percentileofscore(hqm_dataframe[f'{time_period} Price Return'], hqm_dataframe.loc[row, f'{time_period} Price Return'])/100

# Habilito los warnings
warnings.filterwarnings("always")


"""Calculating the HQM Score
We'll now calculate our HQM Score, which is the high-quality momentum score that we'll use to filter for stocks in this investing strategy.
The HQM Score will be the arithmetic mean of the 4 momentum percentile scores that we calculated in the last section.
To calculate arithmetic mean, we will use the mean function from Python's built-in statistics module."""

for row in hqm_dataframe.index:
    momentum_percentiles = []
    for time_period in time_periods:
        momentum_percentiles.append(hqm_dataframe.loc[row, f'{time_period} Return Percentile'])
    hqm_dataframe.loc[row, 'HQM Score'] = mean(momentum_percentiles)*100

"""Selecting the 50 Best Momentum Stocks¶
As before, we can identify the 50 best momentum stocks in our universe by sorting the DataFrame on the HQM Score column and dropping all but the top 50 entries."""

hqm_dataframe.sort_values(by = 'HQM Score', ascending = False, inplace=True)
hqm_dataframe = hqm_dataframe[:50]
hqm_dataframe.reset_index(drop = True, inplace=True)


"""Calculating the Number of Shares to Buy
We'll use the portfolio_input function that we created earlier to accept our portfolio size. Then we will use similar logic in a for loop to calculate the number of shares to buy for each stock in our investment universe."""

def portfolio_input():
    global portfolio_size
    #portfolio_size = input("Enter the value of your portfolio:")
    portfolio_size = 100000

    try:
        val = float(portfolio_size)
    except ValueError:
        print("That's not a number! \n Try again:")
        portfolio_size = input("Enter the value of your portfolio:")

portfolio_input()


position_size = float(portfolio_size) / len(hqm_dataframe.index)
#print(position_size)

for i in hqm_dataframe.index:
    hqm_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / hqm_dataframe.loc[i, 'Price'])

"""Formatting Our Excel Output
We will be using the XlsxWriter library for Python to create nicely-formatted Excel files.

XlsxWriter is an excellent package and offers tons of customization. However, the tradeoff for this is that the library can seem very complicated to new users. Accordingly, this section will be fairly long because I want to do a good job of explaining how XlsxWriter works."""

writer = pd.ExcelWriter('momentum_strategy.xlsx', engine='xlsxwriter')
hqm_dataframe.to_excel(writer, sheet_name='Momentum Strategy', index = False)

"""Creating the Formats We'll Need For Our .xlsx File
You'll recall from our first project that formats include colors, fonts, and also symbols like % and $. We'll need four main formats for our Excel document:

String format for tickers
$XX.XX format for stock prices
$XX,XXX format for market capitalization
Integer format for the number of shares to purchase
Since we already built our formats in the last section of this course, I've included them below for you. Run this code cell before proceeding."""

background_color = '#0a0a23'
font_color = '#ffffff'

string_template = writer.book.add_format(
        {
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

dollar_template = writer.book.add_format(
        {
            'num_format':'$0.00',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

integer_template = writer.book.add_format(
        {
            'num_format':'0',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

percent_template = writer.book.add_format(
        {
            'num_format':'0.0%',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

column_formats = { 
                    'A': ['Ticker', string_template],
                    'B': ['Price', dollar_template],
                    'C': ['Number of Shares to Buy', integer_template],
                    'D': ['One-Year Price Return', percent_template],
                    'E': ['One-Year Return Percentile', percent_template],
                    'F': ['Six-Month Price Return', percent_template],
                    'G': ['Six-Month Return Percentile', percent_template],
                    'H': ['Three-Month Price Return', percent_template],
                    'I': ['Three-Month Return Percentile', percent_template],
                    'J': ['One-Month Price Return', percent_template],
                    'K': ['One-Month Return Percentile', percent_template],
                    'L': ['HQM Score', integer_template]
                    }

for column in column_formats.keys():
    writer.sheets['Momentum Strategy'].set_column(f'{column}:{column}', 20, column_formats[column][1])
    writer.sheets['Momentum Strategy'].write(f'{column}1', column_formats[column][0], string_template)

"""Saving Our Excel Output
As before, saving our Excel output is very easy:"""

writer.save()

print(hqm_dataframe)