import json
import requests
from flask import Flask, request, jsonify
from datetime import date, timedelta
from flask_cors import CORS

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

def obtain_last_weekday():
    #this function retrieves the last weekday date to use it in the api call. Return has format "YYYY-MM-DD"
    today = date.today()
    if today.weekday()==0:  #if today is monday
        delta = timedelta(days=3)
    elif today.weekday()==6: #if today is sunday:
        delta = timedelta(days=2)
    else:   #any other day of the week
        delta = timedelta(days=1)
    return (today-delta).strftime("%Y-%m-%d")

@app.route("/api/portfolio")
def get_portfolio():
    portfolio_total_value = 0
    userId = "user2" #change for different users
    list_price_values = {}    #This dictionary will store the stock and last closing price like "STOCK":"123.45"
    user_portfolio = obtain_user_list(user_id=userId)
    stock_length = len(user_portfolio)
    print(stock_length)
    for stock in user_portfolio:
        #make the requests to the API and return the last closing value:
        try:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&apikey={API_KEY}"
            print(url)
            r = requests.get(url)
            data = r.json()
        except:
            data={"error accessing api"}
        #I only want the last closing value, so:
        try:
            lcv = data["Time Series (Daily)"][obtain_last_weekday()]["4. close"]  #i know that there is the last closing value
        except:
            lcv={"error in data"}
        list_price_values[stock] = lcv
        stock_total_value = float(lcv) * stock_length
        portfolio_total_value += stock_total_value
    print(portfolio_total_value)
    return jsonify(list_price_values)

@app.route("/api/portfolio/<stock>")
def obtain_stock_value(stock):
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&apikey={API_KEY}"
        r = requests.get(url)
        data = r.json()
        series = data['Time Series (Daily)']
        #we will use the last 30 days:
        start_date = (date.today()-timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = date.today().strftime("%Y-%m-%d")
        filtered_data = {date: details for date, details in series.items() if start_date <= date <= end_date}   #this is from Percy's code
        previous_stock={}
        previous_stock["symbol"]=stock
        previous_stock["values_daily"]=filtered_data
        return jsonify(previous_stock)
    except:
        return "error accessing api"

if __name__ == "__main__":
    app.run(debug = True)