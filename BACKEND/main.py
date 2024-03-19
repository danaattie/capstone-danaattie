import json
import requests
from flask import Flask, request, jsonify
from datetime import date, timedelta
from flask_cors import CORS
import random
from models import get_user, get_user_stocks
from sqlalchemy.pool import NullPool
import oracledb
from sqlalchemy import create_engine, text

# Load the environment variables from the .env file
with open("secrets.txt") as file:
    API_KEY = file.read()

un = 'MYBACKEND'
pw = 'AaZZ0r_cle#1'
dsn = '(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-madrid-1.oraclecloud.com))(connect_data=(service_name=gc1ee84d2900e16_capstone_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'

pool = oracledb.create_pool(user=un, password=pw,dsn=dsn)

engine = create_engine("oracle+oracledb://", creator=pool.acquire, poolclass=NullPool, future=True, echo=True)

app = Flask(__name__)
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
CORS(app)

def obtain_user_list(user_id):
    # This function now performs a SQL query to obtain the user's stock list
    stocks_list = []
    with pool.acquire() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT symbol, quantity FROM Stocks WHERE user_id = :user_id", [user_id])
            for stock_row in cursor:
                stocks_list.append({stock_row[0]: stock_row[1]})
    return stocks_list

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

def get_user_stocks(user_id):
    user_id = int(user_id)  # Ensure user_id is an integer
    stocks_list = []
    with pool.acquire() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT SYMBOL, QUANTITY FROM STOCKS WHERE user_id = :user_id", {"user_id": user_id})
            for stock_row in cursor:
                stocks_list.append({'symbol': stock_row[0], 'quantity': stock_row[1]})
    return stocks_list

    
@app.route("/api/portfolio", methods=['GET'])
def retrieve_portfolio():
    total_value_of_portfolio = 0
    user_id = 1  # Assuming this is just a placeholder
    portfolio_response = {"username": user_id, "stocks": {}}
    
    portfolio_stocks = get_user_stocks(user_id)

    for stock in portfolio_stocks:
        stock_symbol = stock['symbol']
        num_stocks = stock['quantity']
        try:
            request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock_symbol}&apikey={API_KEY}"
            response = requests.get(request_url)
            stock_data = response.json()
            last_closing_price = stock_data["Time Series (Daily)"][get_previous_weekday()]["4. close"]
            closing_price = float(last_closing_price)

            # Update individual stock info
            portfolio_response["stocks"][stock_symbol] = {
                "num_stocks": num_stocks,
                "last_close": closing_price
            }

            # Update total portfolio value
            total_value_of_portfolio += num_stocks * closing_price

        except Exception as e:
            # Handling errors in data retrieval
            portfolio_response["stocks"][stock_symbol] = {"error": f"Data retrieval failed: {e}"}

    # Add total portfolio value to the response
    portfolio_response["total_port_val"] = total_value_of_portfolio
    return jsonify(portfolio_response)


@app.route("/api/portfolio/<stock_symbol>", methods=['GET']) 
def retrieve_stock_data(stock_symbol):
    try:
        api_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock_symbol}&apikey={API_KEY}"
        response = requests.get(api_url)

        if response.status_code != 200:
            return jsonify({"error": f"API request failed with status code {response.status_code}", "details": response.text}), response.status_code

        data = response.json()

        if "Time Series (Daily)" not in data:
            #Log the full API response for debugging
            return jsonify({"error": "Expected data not found in API response", "api_response": data}), 500

        daily_data = data["Time Series (Daily)"] #this is for displaying day by day
        return jsonify({"symbol": stock_symbol, "values_daily": daily_data}) 

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve data: {str(e)}", "exception_details": str(e)}), 500


@app.route("/api/portfolio/update_user", methods=['POST'])
def update_user():
    try:
        data = request.json
        print("Received data:", data)  # Log the incoming payload for debugging
        user_id = data.get("user_id", 1)  # In production, use session or token for user_id
        symbol = data.get("symbol")
        quantity = data.get("quantity")

        if symbol is None or quantity is None:
            raise ValueError("Both 'symbol' and 'quantity' must be provided.")

        with engine.begin() as connection:
            # If quantity is zero, delete the stock; otherwise, update or insert.
            if quantity == 0:
                delete_result = connection.execute(
                    text("DELETE FROM STOCKS WHERE user_id = :user_id AND symbol = :symbol"),
                    {"user_id": user_id, "symbol": symbol}
                )
                print(f"Deleted {delete_result.rowcount} rows for user {user_id} and symbol {symbol}")  # Log deletion
            else:
                # Check if the stock exists
                result = connection.execute(
                    text("SELECT quantity FROM STOCKS WHERE user_id = :user_id AND symbol = :symbol FOR UPDATE"),
                    {"user_id": user_id, "symbol": symbol}
                )
                stock = result.fetchone()
                if stock:
                    # Update the existing stock quantity
                    update_result = connection.execute(
                        text("UPDATE STOCKS SET quantity = :quantity WHERE user_id = :user_id AND symbol = :symbol"),
                        {"user_id": user_id, "symbol": symbol, "quantity": quantity}
                    )
                    print(f"Updated quantity to {quantity} for user {user_id} and symbol {symbol}")  # Log update
                else:
                    # Insert a new stock record
                    insert_result = connection.execute(
                        text("INSERT INTO STOCKS (user_id, symbol, quantity) VALUES (:user_id, :symbol, :quantity)"),
                        {"user_id": user_id, "symbol": symbol, "quantity": quantity}
                    )
                    print(f"Inserted new stock for user {user_id} with symbol {symbol} and quantity {quantity}")  # Log insert

        # Fetch the current portfolio to ensure front end gets the updated data
        updated_stocks = connection.execute(
            text("SELECT * FROM STOCKS WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).fetchall()
        print(f"Current stocks after update: {updated_stocks}")  # Log the current state of the portfolio

        return jsonify({"message": "Stocks updated successfully", "updated_stocks": updated_stocks}), 200

    except Exception as e:
        print("Error:", e)  # Log the error for debugging
        return jsonify({"error": f"Failed to update stocks: {str(e)}"}), 500


@app.route('/api/historical_prices/<stock_symbol>', methods=['GET'])
def get_historical_prices(stock_symbol):
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={stock_symbol}&outputsize=compact&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()

        #extract just the last 30 days of data
        time_series = data.get('Time Series (Daily)', {})
        last_30_days = list(time_series.items())[:30]
        prices = [{date: info['4. close']} for date, info in last_30_days]

        return jsonify(prices), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch historical prices: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001, use_reloader=False) 
