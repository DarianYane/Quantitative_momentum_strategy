"""Quantitative Momentum Strategy

For this project, we're going to build an investing strategy that selects the 50 stocks with the highest price momentum.
"""

import numpy as np #The Numpy numerical computing library
import pandas as pd #The Pandas data science library
import requests #The requests library for HTTP requests in Python
import xlsxwriter #The XlsxWriter libarary for 
import math #The Python math module
from scipy import stats #The SciPy stats module

import warnings #importo los warnings por el score
from statistics import mean

#Importing Our List of Stocks
stocks = pd.read_csv('sp_500_stocks.csv')
from secrets import IEX_CLOUD_API_TOKEN

#Making Our First API Call
symbol = 'AAPL'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/stats?token={IEX_CLOUD_API_TOKEN}'
data = requests.get(api_url).json()

#Executing A Batch API Call & Building Our DataFrame
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]   
        
symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

my_columns = ['Ticker', 'Price', 'One-Year Price Return', 'Number of Shares to Buy']

#Now we need to create a blank DataFrame and add our data to the data frame one-by-one.
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

#Calculating Momentum Percentiles
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


#Calculating the HQM Score
for row in hqm_dataframe.index:
    momentum_percentiles = []
    for time_period in time_periods:
        momentum_percentiles.append(hqm_dataframe.loc[row, f'{time_period} Return Percentile'])
    hqm_dataframe.loc[row, 'HQM Score'] = mean(momentum_percentiles)*100

#Selecting the 50 Best Momentum Stocks¶
hqm_dataframe.sort_values(by = 'HQM Score', ascending = False, inplace=True)
hqm_dataframe = hqm_dataframe[:50]
hqm_dataframe.reset_index(drop = True, inplace=True)


#Calculating the Number of Shares to Buy
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

#Formatting Our Excel Output
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

#Saving Our Excel Output
writer.save()
