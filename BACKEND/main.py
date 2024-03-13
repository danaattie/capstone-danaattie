import json
import requests
from flask import Flask, request, jsonify
from datetime import date, timedelta
from flask_cors import CORS
import random

# Load the environment variables from the .env file
with open("secrets.txt") as file:
    API_KEY = file.read()

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

#Flask routes under /api/ will accept requests from http://example.com
#read the user database and store in a dictionary:
with open("user_database.json", 'r') as db:
        db_dict = json.load(db)

def obtain_user_list(user_id):
    #this function returns the list of symbols for a specific user
    try:
        return db_dict[user_id]
    except KeyError:
        print("User not found in database.")


def get_previous_weekday():
    #this function retrieves the last weekday date to use it in the api call. Return has format "YYYY-MM-DD"
    today = date.today()
    if today.weekday()==0:  #if today is monday
        delta = timedelta(days=3)
    elif today.weekday()==6: #if today is sunday:
        delta = timedelta(days=2)
    else:   #any other day of the week
        delta = timedelta(days=1)
    return (today-delta).strftime("%Y-%m-%d")

def get_stock_quantity(stock_symbol):
    return random.randint(50, 500)  # Generates a random number between 50 and 500

@app.route("/api/portfolio")
def retrieve_portfolio():
    total_value_of_portfolio = 0
    user_id = "user1"  # This should be dynamically modified based on your application's logic
    portfolio_response = {"username": user_id, "stocks": {}}
    
    portfolio_stocks = obtain_user_list(user_id=user_id)  #obtain stock list for the user

    for stock_symbol in portfolio_stocks:
        try:
            request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock_symbol}&apikey={API_KEY}"
            response = requests.get(request_url)
            stock_data = response.json()
            last_closing_price = stock_data["Time Series (Daily)"][get_previous_weekday()]["4. close"]
            num_stocks = portfolio_stocks[stock_symbol]
            closing_price = float(last_closing_price)

            #update individual stock info
            portfolio_response["stocks"][stock_symbol] = {
                "num_stocks": num_stocks,
                "last_close": closing_price
            }

            # Update total portfolio value
            total_value_of_portfolio += num_stocks * closing_price

        except Exception as e:
            #handling errors in data retrieval
            portfolio_response["stocks"][stock_symbol] = {"error": f"Data retrieval failed: {e}"}

    #add total portfolio value to the response
    portfolio_response["total_port_val"] = total_value_of_portfolio
    return jsonify(portfolio_response)

@app.route("/api/portfolio/<stock_symbol>")
def retrieve_stock_data(stock_symbol):
    try:
        api_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock_symbol}&apikey={API_KEY}"
        response = requests.get(api_url)

        if response.status_code != 200:
            return jsonify({"error": f"API request failed with status code {response.status_code}", "details": response.text}), response.status_code

        data = response.json()

        if "Time Series (Daily)" not in data:
            #Llog the full API response for debugging
            return jsonify({"error": "Expected data not found in API response", "api_response": data}), 500

        daily_data = data["Time Series (Daily)"] #this is for displaying day by day
        return jsonify({"symbol": stock_symbol, "values_daily": daily_data}) 

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve data: {str(e)}", "exception_details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)