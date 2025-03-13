import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)  # Suppress FutureWarnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prophet import Prophet
import yfinance as yf
from pandas_datareader import data as pdr
import math
import logging
from threading import Thread, Lock
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import requests
from bs4 import BeautifulSoup
from scipy.stats import linregress
from io import BytesIO
import base64
from flask import jsonify

STOCK_DATA = {}

end_date = datetime.now()
start_date = end_date.replace(year=end_date.year - 3)

END_DATE = end_date.strftime('%Y-%m-%d')
START_DATE = start_date.strftime('%Y-%m-%d')

def get_sp500_symbols():
  # Fetch S&P 500 companies from Wikipedia
  url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")

  table = soup.find("table", {"id": "constituents"})
  symbols_ciks = {}

  if table:
    rows = table.find_all("tr")[1:]  # Skip header row
    for row in rows:
      columns = row.find_all("td")
      if columns:
        symbol = columns[0].text.strip()
        cik = columns[6].text.strip().lstrip("0")  # Extract CIK and remove leading zeros

        # Keep only the first occurrence of each CIK
        if cik not in symbols_ciks:
          symbols_ciks[str(cik)] = symbol
        # else:
        #   print(symbol, cik)
  
  return sorted(symbols_ciks.values())  # Return sorted unique symbols

def get_stock_data():
    global STOCK_DATA

    stock_data = yf.download(
        tickers = get_sp500_symbols(),
        period = '2y',
        interval = '1d',
        threads = True,
    )

    stock_data.index.name = "Date"  # Ensure index has a name
    stock_data.columns.names = ["Price", "Ticker"]  # Set column names
    STOCK_DATA = {ticker: stock_data.xs(ticker, axis=1, level=1) for ticker in stock_data.columns.levels[1]}

    for _, stock_df in STOCK_DATA.items():
        stock_df.loc[:, 'pct'] = stock_df['Close'].pct_change()
    
    return STOCK_DATA

def predictStock(stock_name: str, prediction_days: int, show_chart=True) -> pd.DataFrame:
  df = STOCK_DATA[stock_name].copy()

  DAYS = prediction_days
  # df.columns = df.columns.droplevel(1)
  # Display first few rows
  # print(df.head())

  orig_df = df

  df = df.reset_index().rename(columns={'Date':'ds', 'Close':'y'})

  # Log Transform Data
  df['y'] = pd.DataFrame(np.log(df['y']))

  df_train = df[:(len(df)-1)]
  df_test = df[(len(df)-1):]

  # Model Fitting
  # instantiate the Prophet class
  mdl = Prophet(interval_width=0.95, daily_seasonality=True, yearly_seasonality=True)

  # fit the model on the training data
  mdl.fit(df_train)

  # define future time frame
  future = mdl.make_future_dataframe(periods=DAYS, freq='D')

  # generate the forecast
  forecast = mdl.predict(future)

  # retransform using e
  y_hat = np.exp(forecast['yhat'][(len(df)-1):])
  y_true = np.exp(df['y'])

  if show_chart:
    # Calculate moving averages for 50 days and 200 days
    y_true_50d = y_true.rolling(window=50).mean()  # 50-day moving average for actual prices

    y_hat2 = pd.concat([y_true[-50:], y_hat], ignore_index=False)
    y_hat_50d = y_hat2.rolling(window=50).mean()  # 50-day moving average for forecasted prices

    y_true_200d = y_true.rolling(window=200).mean()  # 200-day moving average for actual prices

    y_hat3 = pd.concat([y_true[-200:], y_hat], ignore_index=False)
    y_hat_200d = y_hat3.rolling(window=200).mean()  # 200-day moving average for forecasted prices

    # Plotting the original, forecasted, and moving averages
    plt.figure(figsize=(12, 6))  # Set figure size

    plt.plot(y_true[200:], label='Original', color='#006699')  # Plot original prices starting from index 200
    plt.plot(y_hat, color='#ff0066', label='Forecast')  # Plot forecasted prices starting from index 200
    plt.plot(y_true_50d[200:], label='50-Day Moving Average (Actual)', color='#33cc33')  # 50-day moving average (actual)
    plt.plot(y_hat_50d, label='50-Day Moving Average (Forecast)', linestyle='--', color='#33cc33')  # 50-day moving average (forecast)
    plt.plot(y_true_200d[200:], label='200-Day Moving Average (Actual)', color='#6699cc')  # 200-day moving average (actual)
    plt.plot(y_hat_200d, label='200-Day Moving Average (Forecast)', linestyle='--', color='#6699cc')  # 200-day moving average (forecast)

    # Labels and title
    plt.ylabel('Price')
    plt.xlabel('Date')
    plt.title(f"{stock_name}'s {prediction_days} day prediction from {END_DATE}")

    # Show legend
    plt.legend()

    # Show the plot
     # plt.show()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Convert the image to Base64
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    # Return the Base64 string as JSON response
    return jsonify({'plot': img_base64})

  last_date = orig_df.index.max()

  # Create a new DataFrame to hold the predicted values
  new_data = {'Close': []}
  new_index = []

  # Loop to populate the new DataFrame
  for i, value in enumerate(y_hat):
    new_date = last_date + pd.Timedelta(days=i+1)  # Start from last_date + 1
    new_index.append(new_date)
    new_data['Close'].append(value)

  # Convert to DataFrame
  new_df = pd.DataFrame(new_data, index=new_index)
  new_df.index.name = 'Date'  # Set the index name as 'Date'

  new_df["Predicted"] = True
  orig_df["Predicted"] = False
  df_combined = pd.concat([orig_df, new_df])

  return df_combined

def ptgChange():
  percent_changes = {}

  for ticker, df in STOCK_DATA.items():
    pct_changes = df['pct'].to_numpy()
    if len(pct_changes) != 0:
      pct_changes = np.delete(pct_changes, 0)  # Remove the first entry (NaN)
    percent_changes[ticker] = pct_changes

  return percent_changes

def correlation(stk1_name: str, stk2_name: str):

  # Extract percent change to numpy vectors and delete the first entry (NaN)
  percent_changes = ptgChange()

  # for ticker, df in data.items():
  #     pct_changes = df['pct'].to_numpy()
  #     pct_changes = np.delete(pct_changes, 0)  # Remove the first entry (NaN)
  #     percent_changes[ticker] = pct_changes

  # Now `percent_changes` contains the numpy arrays for each ticker without the NaN value
  # Now the data dictionary contains the dataframes with daily percent change for each ticker

  # Assuming 'percent_changes' dictionary is already populated

  # Extract percent change for SPY and AMZN
  stk1 = percent_changes[stk1_name]
  stk2 = percent_changes[stk2_name]

  # Plot
  plt.figure(figsize=(8, 6))
  plt.plot(stk1, stk2, '.', label=f'{stk1_name} vs {stk2_name}', color='b')
  plt.grid(True)
  plt.xlabel(f'{stk1_name} % Change')
  plt.ylabel(f'{stk2_name} % Change')
  plt.title(f'{stk1_name} vs {stk2_name} Daily % Change')

  # Perform linear regression calculating the slope (beta) and correlation (r_value)
  slope, intercept, r_value, p_value, std_err = linregress(stk1, stk2)

  # Plot regression line
  x = np.linspace(min(stk1), max(stk1), 100)
  plt.plot(x, slope * x + intercept, 'k', label=f'Regression Line: Beta={slope:.2f}')

  # Display the linear regression statistics on the plot
  plt.legend()

  # Print beta and correlation
  print('Beta (Slope):', slope)
  print('Correlation Coefficient (r):', r_value)
  print('R Squared:', r_value**2)

  # Show the plot
  # plt.show()

  img = BytesIO()
  plt.savefig(img, format='png')
  img.seek(0)

  # Convert the image to Base64
  img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

  # Return the Base64 string as JSON response
  return jsonify({'plot': img_base64})

def topFiveCorrelations():
  # Extract percent changes dynamically using a list comprehension

  # company_names = []
  # for ticker in company_name:
  #   if ticker in percent_changes:
  #     company_names.append(ticker)

  # data = [percent_changes[ticker] for ticker in company_names]

  percent_changes = ptgChange()
  data = [percent_change for _,percent_change in percent_changes.items()]

  # Create the DataFrame and transpose it
  pct_frame = pd.DataFrame(data).T  # Transpose to align percent changes as columns
  pct_frame.columns = percent_changes.keys() # Assign column names

  # Compute and display the correlation matrix
  corr_frame = pct_frame.corr()


  # Mask out the diagonal (self-correlations) by setting them to np.nan
  masked_corr = np.triu(np.ones_like(corr_frame, dtype=bool))

  # Flatten the correlation matrix, ignoring the diagonal values
  corr_values = corr_frame.where(~masked_corr).stack().sort_values(ascending=False)

  # Get the top 5 highest correlation pairs
  top_5_pairs = corr_values.head(10)

  # Print the top 5 highest correlations
  for tickers, value in top_5_pairs.items():
      print(f"{tickers[0]} and {tickers[1]}: {value:.2f}")


  return_list = []

  # Assuming the `percent_changes` dictionary is already populated
  # and `top_5_pairs` contains the top 5 highest correlation pairs

  # Loop over the top 5 correlation pairs
  for pair, value in top_5_pairs.items():
    ticker1, ticker2 = pair

    # Extract percent changes for the tickers
    data1 = percent_changes[ticker1]
    data2 = percent_changes[ticker2]

    # Plot the raw data
    plt.figure(figsize=(8, 5))
    plt.plot(data1, data2, '.', label=f'{ticker2} vs {ticker1}', color='b')
    plt.grid(True)
    plt.xlabel(f'{ticker1} % Change')
    plt.ylabel(f'{ticker2} % Change')
    plt.title(f'{ticker2} vs {ticker1} Daily % Change')

    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = linregress(data1, data2)

    # Plot the regression line
    x = np.linspace(min(data1), max(data1), 100)
    plt.plot(x, slope * x + intercept, 'k', label=f'Regression Line: Beta={slope:.2f}')

    # Display the linear regression statistics on the plot
    plt.legend()

    # Print beta and correlation
    print(f'{ticker1} and {ticker2}:')
    print(f'Beta (Slope): {slope:.2f}')
    print(f'Correlation Coefficient (r): {r_value:.2f}')
    print(f'R Squared: {r_value**2:.2f}\n')

    # Show the plot
    # plt.show()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Convert the image to Base64
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    # Return the Base64 string as JSON response
    return_list.append({'plot': img_base64, 'ticker1': ticker1, 'ticker2': ticker2, 'correlation': f"{r_value:.2f}", 'beta': f"{slope:.2f}"})
  
  return_list = sorted(return_list, key=lambda x: x['correlation'], reverse=True)
  for i in range(len(return_list)):
    return_list[i]['rank'] = (i + 1)
    return_list[i]['correlation'] = float(return_list[i]['correlation'])
    return_list[i]['beta'] = float(return_list[i]['beta'])

  return return_list

def topFiveCorrelationsForStock(target_stock):
  percent_changes = ptgChange()

  # Ensure the target stock is in the dataset
  if target_stock not in percent_changes:
      print(f"Error: {target_stock} not found in percent_changes.")
      return

  # company_names = []
  # for ticker in company_name:
  #   if ticker in percent_changes:
  #     company_names.append(ticker)

  # Create a DataFrame from the percent_changes dictionary
  data = [percent_change for _,percent_change in percent_changes.items()]

  # Create the DataFrame and transpose it
  pct_frame = pd.DataFrame(data).T  # Transpose to align percent changes as columns
  pct_frame.columns = percent_changes.keys() # Assign column names

  # Compute the correlation matrix
  corr_frame = pct_frame.corr()

  # Extract correlations for the target stock only
  target_corr = corr_frame[target_stock].drop(target_stock)  # Remove self-correlation

  # Get the top 5 highest correlations
  top_5_stocks = target_corr.sort_values(ascending=False).head(5)

  # Print the top 5 correlations
  print(f"Top 5 correlations for {target_stock}:")
  for ticker, value in top_5_stocks.items():
    print(f"{ticker}: {value:.2f}")

  return_list = []

  # Loop over the top 5 correlated stocks
  for ticker, value in top_5_stocks.items():
    # Extract percent changes for the target stock and the correlated stock
    data1 = percent_changes[target_stock]
    data2 = percent_changes[ticker]

    # Plot the raw data
    plt.figure(figsize=(8, 4))
    plt.plot(data1, data2, '.', label=f'{ticker} vs {target_stock}', color='b')
    plt.grid(True)
    plt.xlabel(f'{target_stock} % Change')
    plt.ylabel(f'{ticker} % Change')
    plt.title(f'{ticker} vs {target_stock} Daily % Change')

    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = linregress(data1, data2)

    # Plot the regression line
    x = np.linspace(min(data1), max(data1), 100)
    plt.plot(x, slope * x + intercept, 'k', label=f'Regression Line: Beta={slope:.2f}')

    # Display the linear regression statistics on the plot
    plt.legend()

    # Print beta and correlation
    print(f'{target_stock} and {ticker}:')
    print(f'Beta (Slope): {slope:.2f}')
    print(f'Correlation Coefficient (r): {r_value:.2f}')
    print(f'R Squared: {r_value**2:.2f}\n')

    # Show the plot
    # plt.show()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Convert the image to Base64
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    # Return the Base64 string as JSON response
    return_list.append({'plot': img_base64, 'ticker': ticker, 'correlation': f"{r_value:.2f}"})
  
  return jsonify(return_list)

#function to calculate SMA (was period=20)
def SMA(data, period=50, column='Close'):
  return data[column].rolling(window=period).mean()

#function to calculate EMA
def EMA(data,time_period, column='Close'):
  return data[column].ewm(span=time_period,adjust=False).mean()

#function to calculate DEMA
def DEMA(data, time_period, column):
  #calculate EMA for some time period
  ema = data[column].ewm(span=time_period,adjust=False).mean()
  #calculate the DEMA
  dema = 2*ema-ema.ewm(span=time_period,adjust=False).mean()
  return dema

#function to calculate MACD
def MACD(data,period_long=26,period_short=20,period_signal=9, column='Close'):

  #calculate short term exponential moving average (EMA)
  shortema = EMA(data,period_short,column=column) #mean() #typ 12 period exponentially smooth moving average

  #calculate long term exponential moving average (EMA) #type 26 period exponentially smooth moving average
  longema = EMA(data,period_long,column=column)

  #calculate MACD line and store in dataframe
  data['MACD'] = shortema - longema

  #calculate signal line
  data['Signal Line'] = EMA(data, period_signal, column='MACD') #typ 9 period exponentially smooth moving average

  return data

# create function to signal a buy/sell purchase
def buysellMACD(signal):
  buyonMACD = []
  sellonMACD = []
  flag = -1

  for i in range(0,len(signal)): #for enumerator from interval [0 to signal length]
    if signal['MACD'][i] > signal['Signal Line'][i]:
      sellonMACD.append(np.nan)
      if flag !=1:
        buyonMACD.append(signal['Close'][i])
        flag=1
      else:
        buyonMACD.append(np.nan)
        #sell.append(np.nan)

    elif signal['MACD'][i] < signal['Signal Line'][i]:
      buyonMACD.append(np.nan)
      if flag !=0:
        sellonMACD.append(signal['Close'][i])
        flag=0
      else:
        sellonMACD.append(np.nan)
        #buy.append(np.nan)

    else:
      buyonMACD.append(np.nan)
      sellonMACD.append(np.nan)

  return (buyonMACD , sellonMACD)

def MACDbuysellsignals(df, Stock, predicted=False):
  #show the buy signal v sell singal graphic form MACD
  plt.figure(figsize=(20,7))

  plt.scatter(df.index, df['Buy MACD Price'],color='green',label='Buy on MACD',marker='^', alpha=1)
  plt.scatter(df.index, df['Sell MACD Price'],color='r',label='Sell on MACD',marker='v', alpha=1)

  if predicted:
    #plt.plot(df["Close"], label='%s Close Price'%str(Stock),alpha=0.35)
    plt.plot(df[df['Predicted'] == False].index, df[df['Predicted'] == False]['Close'],
            label='Close Price (Original)', color='blue', alpha=0.35)

    plt.plot(df[df['Predicted'] == True].index, df[df['Predicted'] == True]['Close'],
            label='Close Price (Predicted)', color='orange', alpha=0.35)

    last_non_predicted = df[df['Predicted'] == False].iloc[-1]  # Last row where Predicted is False
    first_predicted = df[df['Predicted'] == True].iloc[0]  # First row where Predicted is True

    # Generate new data to connect these two points smoothly (interpolate)
    dates_to_interpolate = pd.date_range(last_non_predicted.name, first_predicted.name, freq='D')
    interpolated_values = np.linspace(last_non_predicted['Close'], first_predicted['Close'], len(dates_to_interpolate))

    # Plot the interpolated line segment (connecting the two segments)
    plt.plot(dates_to_interpolate, interpolated_values, color='orange', alpha=0.35)
  else:
    plt.plot(df["Close"], label='%s Close Price'%str(Stock),alpha=0.35)

  plt.title('%s Close Price Buy/Sell MACD Signals'%str(Stock))
  plt.xlabel('Date')
  plt.xticks()
  plt.ylabel('%s Close Price, USD($)'%str(Stock))
  plt.legend(loc='upper left')
  # plt.show()

  img = BytesIO()
  plt.savefig(img, format='png')
  img.seek(0)

  # Convert the image to Base64
  img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

  # Return the Base64 string as JSON response
  return jsonify({'plot': img_base64})

def buyAndSell(stock):
  df = STOCK_DATA[stock]
  MACD(df)
  a = buysellMACD(df)
  df['Buy MACD Price'] = a[0]
  df['Sell MACD Price'] = a[1]

  MACDbuysellsignals(df, stock)

def buyAndSellPredict(stock, combined_data=None):
  df = predictStock(stock, 365, False) if combined_data is None else combined_data
  df.columns = df.columns.get_level_values(0)

  MACD(df)
  a = buysellMACD(df)
  df['Buy MACD Price'] = a[0]
  df['Sell MACD Price'] = a[1]

  MACDbuysellsignals(df, stock, predicted=True)

def generate_chart(stock_name, selected_items=[]):
  # selected_items = ["Predicted", "200d SMA"]

  predicted = "Predicted" in selected_items
  buy_signals = "Buy Signals" in selected_items
  sell_signals = "Sell Signals" in selected_items
  sma_200 = "200d SMA" in selected_items
  sma_50 = "50d SMA" in selected_items

  if predicted:
    df = predictStock(stock_name, 365, False)
  else:
    df = STOCK_DATA[stock_name]

  # df.columns = df.columns.get_level_values(0)

  # Check if 'Predicted' column exists
  if 'Predicted' in df.columns:
    # Calculate moving averages for Real (Predicted == False) and Predicted (Predicted == True)
    if sma_50:
      # Real 50-day SMA (where Predicted is False)
      df['50d SMA Real'] = df[df['Predicted'] == False]['Close'].rolling(window=50).mean()

      # Predicted 50-day SMA (where Predicted is True)
      df['50d SMA Predicted'] = pd.concat([df[df['Predicted'] == False]['Close'], df[df['Predicted'] == True]['Close']], ignore_index=False).rolling(window=50).mean()

    if sma_200:
      # Real 200-day SMA (where Predicted is False)
      df['200d SMA Real'] = df[df['Predicted'] == False]['Close'].rolling(window=200).mean()

      # Predicted 200-day SMA (where Predicted is True)
      df['200d SMA Predicted'] = pd.concat([df[df['Predicted'] == False]['Close'], df[df['Predicted'] == True]['Close']], ignore_index=False).rolling(window=200).mean()
  else:
    # If 'Predicted' column doesn't exist, calculate SMAs for the entire data
    if sma_50:
      df['50d SMA Real'] = df['Close'].rolling(window=50).mean()

    if sma_200:
      df['200d SMA Real'] = df['Close'].rolling(window=200).mean()

  # Cut off 200 days so the SMA's don't look cut off
  if sma_200:
    df = df.iloc[200:]
  elif sma_50:
    df = df.iloc[50:]

  if buy_signals or sell_signals:
    MACD(df)
    a = buysellMACD(df)
    df['Buy MACD Price'] = a[0]
    df['Sell MACD Price'] = a[1]

    #show the buy signal v sell singal graphic form MACD
  plt.figure(figsize=(12,10))

  if buy_signals:
    plt.scatter(df.index, df['Buy MACD Price'],color='green',label='Buy on MACD',marker='^', alpha=1)

  if sell_signals:
    plt.scatter(df.index, df['Sell MACD Price'],color='r',label='Sell on MACD',marker='v', alpha=1)

  if predicted:
    #plt.plot(df["Close"], label='%s Close Price'%str(Stock),alpha=0.35)
    plt.plot(df[df['Predicted'] == False].index, df[df['Predicted'] == False]['Close'],
            label='Close Price (Original)', color='blue', alpha=0.35)

    plt.plot(df[df['Predicted'] == True].index, df[df['Predicted'] == True]['Close'],
            label='Close Price (Predicted)', color='orange', alpha=0.35)

    last_non_predicted = df[df['Predicted'] == False].iloc[-1]  # Last row where Predicted is False
    first_predicted = df[df['Predicted'] == True].iloc[0]  # First row where Predicted is True

    # Generate new data to connect these two points smoothly (interpolate)
    dates_to_interpolate = pd.date_range(last_non_predicted.name, first_predicted.name, freq='D')
    interpolated_values = np.linspace(last_non_predicted['Close'], first_predicted['Close'], len(dates_to_interpolate))

    # Plot the interpolated line segment (connecting the two segments)
    plt.plot(dates_to_interpolate, interpolated_values, color='orange', alpha=0.35)
  else:
    plt.plot(df["Close"], label='%s Close Price'%str(stock_name),alpha=0.35)

  # Plot Real 50-day SMA if selected
  if sma_50:
    plt.plot(df.index, df['50d SMA Real'], label='50-Day SMA (Real)', color='green')

  # Plot Predicted 50-day SMA if selected
  if sma_50 and '50d SMA Predicted' in df.columns:
    plt.plot(df.index, df['50d SMA Predicted'], label='50-Day SMA (Predicted)', color='green', linestyle='--')

  # Plot Real 200-day SMA if selected
  if sma_200:
    plt.plot(df.index, df['200d SMA Real'], label='200-Day SMA (Real)', color='blue')

  # Plot Predicted 200-day SMA if selected
  if sma_200 and '200d SMA Predicted' in df.columns:
    plt.plot(df.index, df['200d SMA Predicted'], label='200-Day SMA (Predicted)', color='blue', linestyle='--')

  # plt.title('%s Close Price Buy/Sell MACD Signals'%str(stock_name))
  plt.xlabel('Date')
  plt.xticks()
  plt.ylabel('%s Close Price, USD($)'%str(stock_name))
  plt.legend(loc='upper left')
  # plt.show()

  img = BytesIO()
  plt.savefig(img, format='png')
  img.seek(0)

  # Convert the image to Base64
  img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

  # Return the Base64 string as JSON response
  return {'plot': img_base64}

def best_peformance_stocks(predicted=False):
  threads = []
  lock = Lock()  # Create a lock for thread-safe operations on 'data'

  def get_plot_stock_performance(symbol):
    # end_date = datetime.today()
    # start_date = end_date - timedelta(days=num_days)

    stock_data = predictStock(symbol, 365, False) if predicted else STOCK_DATA[symbol]
    if stock_data.empty:
        return symbol, None, None

    start_price = stock_data['Close'].iloc[0]
    end_price = stock_data['Close'].iloc[-1]

    percentage_change = float(((end_price - start_price) / start_price) * 100)
    return symbol, percentage_change, stock_data

  performance_data = []
  stock_data_dict = {}

  def fetchData(symbol):
    symbol, performance, stock_data = get_plot_stock_performance(symbol)
    if isinstance(performance, (int, float)):  # Ensure it's a number
      # with lock:
        performance_data.append((symbol, performance))
        stock_data_dict[symbol] = stock_data  # Store stock data for plotting

  for symbol in list(STOCK_DATA.keys()):
    thread = Thread(target=fetchData, args=(symbol,))
    thread.start()
    threads.append(thread)

  for thread in threads:
    thread.join()

  # Sort and get top 5 performers
  performance_data = [x for x in performance_data if not math.isnan(x[1])]
  sorted_performance = sorted(performance_data, key=lambda x: x[1], reverse=True)
  top_5 = sorted_performance[:10]

  # Print the top 5 stocks
  for symbol, performance in top_5:
      print(f"{symbol}: {performance:.2f}%")

  return_list = []

  # Plot each of the top 5 stocks individually
  for symbol, performance in top_5:
    # stock_data = stock_data_dict[symbol]

    # plt.figure(figsize=(10, 5))
    # plt.plot(stock_data.index, stock_data['Close'], label=f"{symbol} ({performance:.2f}%)", color='blue')
    # plt.xlabel('Date')
    # plt.ylabel('Closing Price (USD)')
    # plt.title(f"{symbol} Stock Price Over {num_days} days")
    # plt.legend()
    # plt.grid()
    # plt.show()
    return_list.append({"plot": generate_chart(symbol, ["Predicted"] if predicted else [])["plot"], "ticker": symbol, "performance": performance})
  
  return_list = sorted(return_list, key=lambda x: x['performance'], reverse=True)
  for i in range(len(return_list)):
    return_list[i]['rank'] = (i + 1)

  # for v in return_list:
  #   print(v["performance"], v["ticker"])

  return return_list