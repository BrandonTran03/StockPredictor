from flask import Flask, jsonify, request
from flask_cors import CORS  # Import the CORS package
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import time
import schedule
import threading
from datetime import datetime
import yfinance as yf
from stock_functions import get_stock_data, generate_chart, topFiveCorrelationsForStock, topFiveCorrelations, best_peformance_stocks
import json

app = Flask(__name__)

# Enable CORS for all origins (or you can specify a specific origin)
CORS(app)

# ----------------------------------------------------------- #
STOCK_DATA = {}
STORED_DATA = {"TopCorrelated": {}, "BestPerformance_Current": {}, "BestPerformance_Predicted": {}}
TOP_CORRELATIONS = []

# Function to update the dictionary at midnight
def update_dicts():
    global STOCK_DATA, STORED_DATA, TOP_CORRELATIONS
    print(f"Updating dictionary at {datetime.now()}")
    STOCK_DATA = get_stock_data()
    STORED_DATA["BestPerformance_Current"] = best_peformance_stocks()
    STORED_DATA["BestPerformance_Predicted"] = best_peformance_stocks(predicted=True)
    TOP_CORRELATIONS = topFiveCorrelations()

# Schedule the update every day at 12 AM
schedule.every().day.at("00:00").do(update_dicts)
update_dicts()

# Function to run the scheduler in a separate thread
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# ----------------------------------------------------------- #

@app.route('/plot', methods=['GET'])
def plot():
    params_str = request.args.get('params')

    if not params_str:
        return jsonify({"error": "No parameters provided."})
    
    try:
        params = json.loads(params_str)
    except ValueError:
        return jsonify({"error": "Invalid JSON format for parameters."})
    
    stock_name = params.get("stock", None)
    if stock_name is None:
        return jsonify({"error": "No stock provided."})
    
    selected_items = params.get("selected_items", [])

    return jsonify(generate_chart(stock_name, selected_items))

@app.route('/tickers', methods=['GET'])
def tickers():
    ticker_list = []
    for key in STOCK_DATA.keys():
        ticker_list.append(key)
    return jsonify({'tickers': ticker_list})

@app.route('/top5correlated', methods=['GET'])
def top5correlated():
    params_str = request.args.get('params')

    if not params_str:
        return jsonify({"error": "No parameters provided."})
    
    try:
        params = json.loads(params_str)
    except ValueError:
        return jsonify({"error": "Invalid JSON format for parameters."})
    
    stock_name = params.get("stock", None)
    if stock_name is None:
        return jsonify({"error": "No stock provided."})

    return topFiveCorrelationsForStock(stock_name)

@app.route('/topcorrelated', methods=['GET'])
def topcorrelated():
    return jsonify(TOP_CORRELATIONS)

@app.route('/topStocks', methods=['GET'])
def topStocks():
    return jsonify(STORED_DATA["BestPerformance_Current"])

@app.route('/topStocksPredicted', methods=['GET'])
def topStocksPredicted():
    return jsonify(STORED_DATA["BestPerformance_Predicted"])

if __name__ == '__main__':
    app.run(debug=False, port=5000)