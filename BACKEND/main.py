import json
import requests
from flask import Flask, request, jsonify, session, make_response
from datetime import date, timedelta
from flask_cors import CORS
import random
from models import get_user, get_user_stocks
from sqlalchemy.pool import NullPool
import oracledb
from sqlalchemy import create_engine, text

with open("secrets.txt") as file: #the API key is hidden
    API_KEY = file.read()

app = Flask(__name__)

CORS(app, supports_credentials=True, resources={r"/*": {}})
app.config['SECRET_KEY'] = 'JNCIZPHAUKJIOLZ5' #random secret key to ensure log in works
app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['SESSION_COOKIE_SECURE'] = True

un = 'MYBACKEND' #database credentials
pw = 'AaZZ0r_cle#1'
dsn = '(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-madrid-1.oraclecloud.com))(connect_data=(service_name=gc1ee84d2900e16_capstone_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'

pool = oracledb.create_pool(user=un, password=pw, dsn=dsn) #implementing Oracle db

engine = create_engine("oracle+oracledb://", creator=pool.acquire, poolclass=NullPool, future=True, echo=True) #execution of SQL commands

def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response


def obtain_user_list(user_id):
    #this function performs a SQL query to obtain the user's stock list
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
    return random.randint(50, 500)  #generates a random number between 50 and 500

def get_user_stocks(user_id):
    user_id = int(user_id)  #ensure user_id is an integer
    stocks_list = []
    with pool.acquire() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT SYMBOL, QUANTITY FROM STOCKS WHERE user_id = :user_id", {"user_id": user_id})
            for stock_row in cursor:
                stocks_list.append({'symbol': stock_row[0], 'quantity': stock_row[1]})
    return stocks_list

    
@app.route("/api/portfolio")
def retrieve_portfolio():
    total_value_of_portfolio = 0
    user_id = 1  
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

            portfolio_response["stocks"][stock_symbol] = {
                "num_stocks": num_stocks,
                "last_close": closing_price
            }

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
            #logs the full API response for debugging
            return jsonify({"error": "Expected data not found in API response", "api_response": data}), 500

        daily_data = data["Time Series (Daily)"] #this is for displaying day by day
        return jsonify({"symbol": stock_symbol, "values_daily": daily_data}) 

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve data: {str(e)}", "exception_details": str(e)}), 500

    
@app.route("/api/portfolio/update_user", methods=['POST'])
def update_user():
    try:
        data = request.json
        user_id = data.get("user_id", 1) # 1 is for setting default values
        symbol = data.get("symbol")
        quantity = data.get("quantity")

        if symbol is None or quantity is None:
            raise ValueError("Both 'symbol' and 'quantity' must be provided.")

        with engine.begin() as connection: #according with the latest version on Flask
            #if quantity is zero, delete the stock; otherwise, update or insert.
            if quantity == 0:
                #deletes operation
                delete_stmt = text("DELETE FROM STOCKS WHERE user_id = :user_id AND symbol = :symbol")
                connection.execute(delete_stmt, {"user_id":user_id, "symbol":symbol})
            else:
                #check if the stock exists
                select_stmt = text("SELECT quantity FROM STOCKS WHERE user_id = :user_id AND symbol = :symbol")
                stock = connection.execute(select_stmt, {"user_id":user_id, "symbol":symbol}).fetchone()
                if stock:
                    #updates operation
                    update_stmt = text("UPDATE STOCKS SET quantity = :quantity WHERE user_id = :user_id AND symbol = :symbol")
                    connection.execute(update_stmt, {"quantity":quantity, "user_id":user_id, "symbol":symbol})
                else:
                    #inserts operation
                    insert_stmt = text("INSERT INTO STOCKS (user_id, symbol, quantity) VALUES (:user_id, :symbol, :quantity)")
                    connection.execute(insert_stmt, {"user_id":user_id, "symbol":symbol, "quantity":quantity})

        return jsonify({"message": "Stocks updated successfully"}), 200

    except Exception as e:
        print("Error:", e)  #log the error for debugging purposes
        return jsonify({"error": f"Failed to update stocks: {str(e)}"}), 500


@app.route('/api/historical_prices/<stock_symbol>')
def get_historical_prices(stock_symbol):
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={stock_symbol}&outputsize=compact&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()

        #extract the last 30 days of data
        time_series = data.get('Time Series (Daily)', {})
        last_30_days = list(time_series.items())[:30]
        prices = [{date: info['4. close']} for date, info in last_30_days]

        return jsonify(prices), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch historical prices: {str(e)}"}), 500

@app.route('/login', methods=['POST']) #connection with the front end, cookie had to be removed since it was causing erros in many areas once implemented
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')

    with engine.connect() as connection:
        user = connection.execute(
            text("SELECT * FROM USERS WHERE username = :username AND password = :password"),
            {"username": username, "password": password}
        ).fetchone()

        if user:
            # User found, return success message with status code 200
            response = jsonify({"message": "Logged in successfully"})
            return response, 200
        else:
            # User not found, return error message with status code 401
            response = jsonify({"error": "Invalid username or password"})
            return response, 401
    


@app.route('/logout')#removed from front end return statement as unsolvable errors were found multiple times
def logout():
    session.pop('user', None)
    return jsonify({"message": "Logged out successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001, use_reloader=False) 
