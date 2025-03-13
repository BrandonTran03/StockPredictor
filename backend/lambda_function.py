from datetime import datetime
import json
import pymongo
import yfinance as yf
import ssl
import certifi
ca = certifi.where()
import requests
from bs4 import BeautifulSoup
import time
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="yfinance")
warnings.filterwarnings("ignore", category=UserWarning, module="pandas")

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

def lambda_handler(event, context):
    client = pymongo.MongoClient("mongodb+srv://Brandon_Tran07:Roblox89@stockpredictor.wjef4.mongodb.net/?retryWrites=true&w=majority&appName=StockPredictor", tlsCAFile=ca)
    # db = client["StockDatabase"]
    db = client["stocks_database"]  # Create or use an existing database

    # Collection for daily stock prices
    prices_collection = db["StockPrices"]

    # Clear the StockPrices collection
    prices_collection.delete_many({})  # Removes all documents in the collection

    start = time.time()

    stock_data = yf.download(
            tickers = get_sp500_symbols(),
            period = '2y',
            interval = '1d',
            threads = True,
        )

    print(stock_data)

    # print('It took', time.time()-start, 'seconds.')

    stock_data.index.name = "Date"  # Ensure index has a name
    stock_data.columns.names = ["Price", "Ticker"]  # Set column names
    STOCK_DATA = {ticker: stock_data.xs(ticker, axis=1, level=1) for ticker in stock_data.columns.levels[1]}

    # count = 10
    # for _, stock_df in STOCK_DATA.items():
    #     stock_df.loc[:, 'pct'] = stock_df['Close'].pct_change()

    #     count -= 1
    #     if count == 0:
    #        break

    # operations = []
    
    # count = 50
    # for symbol,data in STOCK_DATA.items():
    #     # print(symbol)
    #     # Store stock price data
    #     for index, row in data.iterrows():
    #         # start = time.time()
    #         stock_data_ = {
    #             "Symbol": symbol,
    #             "Date": index.strftime("%Y-%m-%d"),
    #             "Open": row["Open"],  # Use iloc[0] to get the value
    #             "High": row["High"],
    #             "Low": row["Low"],
    #             "Close": row["Close"],
    #             "Volume": row["Volume"],  # Ensure to use iloc[0]
    #             # "pct": row["pct"]
    #         }
    #         operations.append(
    #             pymongo.UpdateOne(
    #                 {"Symbol": symbol, "Date": stock_data_["Date"]},  # Filter
    #                 {"$set": stock_data_},  # Update action
    #                 upsert=True
    #             )
    #         )
    #         # prices_collection.update_one(
    #         #     {"Symbol": symbol, "Date": stock_data_["Date"]},
    #         #     {"$set": stock_data_},
    #         #     upsert=True
    #         # )
    #         # print('It took', stock_data_["Date"], stock_data_["Symbol"], time.time()-start, 'seconds.')
    #     print(f"Finished {symbol}")
        
    #     # if operations:
    #     #     prices_collection.bulk_write(operations)
    #     #     print(f'Finished processing {symbol}')
    #     #     operations.clear()  # Clear operations after each symbol

    #     count -= 1
    #     if count == 0:
    #        break
    
    # if operations:
    #    prices_collection.bulk_write(operations)

    # Loop through each stock ticker and insert data into MongoDB
    # for ticker, df in STOCK_DATA.items():
    #     # Convert the DataFrame to a list of dictionaries
    #     records = df.reset_index().to_dict(orient="records")  # Reset index to include Date as a field

    #     # Insert the data into MongoDB under the corresponding ticker collection
    #     collection = db[ticker]  # Each ticker will have its own collection
    #     collection.insert_many(records)
    #     print(f"Inserted {len(records)} records for {ticker} into MongoDB.")
    
    print("Sent to MongoDB")
    print('It took', time.time()-start, 'seconds.')

    return {
        'statusCode': 200,
        'body': json.dumps('Stock Prices Updated Successfully!')
    }

# Mock event and context for local testing
mock_event = {}  # You can add mock event data if necessary
mock_context = {}  # You can add mock context data if necessary

# Call the lambda_handler manually
# print(lambda_handler(mock_event, mock_context))

# tickers = ["NVDA", "AVB", "EQR"]
# for i in tickers:
#     end_date = datetime.now()
#     start_date = end_date.replace(year=end_date.year - 3)

#     END_DATE = end_date.strftime('%Y-%m-%d')
#     START_DATE = start_date.strftime('%Y-%m-%d')
#     data = yf.download(i, start=START_DATE, end=END_DATE)

#     print(data)


# dat = yf.Ticker("MSFT")
# historical = dat.history(period='5y')

# print(historical)

# lambda_handler(mock_event, mock_context)