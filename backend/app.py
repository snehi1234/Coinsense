from flask import Flask, request
from flaskext.mysql import MySQL
import requests, traceback
import datetime
from flask_cors import CORS
from flask_cors import cross_origin


app = Flask(__name__)
CORS(app, support_credentials=True)
# cors = CORS(app,origin="*")
# mysql = MySQL()

# app.secret_key = 'your secret key'
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'Maybelater9$'
# app.config['MYSQL_DB'] = 'db'

# mysql.init_app(app)


@app.route('/topCoins', methods=['POST'])
def top():
    #TODO:
    # choose the category name and crate a dictionary. d[category_name] = category_id
    #will pass category name from the UI, search in dict and pass category_id in params
    data = request.json
    print(data)
    num = int(data.get('num'))
    category_id = data.get('category')
    parameter = data.get('parameter') #total_volume, market_cap, circulating_supply, price_change_24h
    print(num, category_id, parameter)
    endpoint = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "per_page": num,
        "page": "1",
        "sparkline": "false" 
        ,"category": category_id
    }
    if parameter == "total_volume":
        params["order"] = "volume_desc"
    elif parameter == "market_cap":
        params["order"] = "market_cap_desc"
    elif parameter == "circulating_supply":
        params["order"] = "circulating_supply_desc"
    elif parameter == "price_change_24h":
        params["order"] = "price_change_24h_desc"

    try:
        response = requests.get(endpoint, params=params)
        data = response.json()
        return {
            'response_code': '200',
            'data': data[:min(num, len(data))]
        }
        
    except Exception as e:
        resp = {
            'response_code': "230",
            'response_message': traceback.print_exc(),
            'error': str(e)
        }

        return resp


@app.route('/graphs', methods=['POST'])
def graphs():
    try:
        data = request.json
        name = data.get('name')
        print(name)
        #extract coin id using coin name
        endpoint = 'https://api.coingecko.com/api/v3/coins/list'
        response = requests.get(endpoint)
        data = response.json()
        coins = {}
        for coin in data:
            coins[coin['name']] = coin['id']
        
        chart_data = []
        if name in coins:
            id_ = coins[name] 
            print(id_)
            #extract price information
            endpoint = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart'
            params = {
                'vs_currency': 'usd',
                'days': '80',
                'id': id_,
                'interval': 'daily'
            }
            response = requests.get(endpoint, params=params)
            data = response.json()
            prices = data['prices'][1:]
            
            for price in prices:
                datetime_obj = datetime.datetime.fromtimestamp(price[0]//1000)
                date_str = datetime_obj.strftime('%Y-%m-%d')
                chart_data.append({
                    'date': date_str,
                    'price': price[1]
                })

        resp = {
            'status_code': 200,
            'chart_data': chart_data
        }
        return resp 

    except Exception as e:
        resp = {
            'response_code': "230",
            'response_message': traceback.print_exc(),
            'error': str(e)
        }
        return resp


alertsList = []
@app.route('/createAlert', methods=['POST'])
@cross_origin(supports_credentials=True)
def createAlert():
    try:
        data = request.json
        coin = data.get('coin')
        price = data.get('price')
        email = data.get('email')
        print(coin, price, email)
        alertsList.append([coin, price, email])
        print(alertsList)
        # cur = mysql.connect().cursor()
        # cur.execute('INSERT INTO alertsTable VALUES (% s, % s)', (coin, price))
        # mysql.connection.commit()

        resp = {
            'status code' : 200
        }
        return resp
        # response = jsonify(message="Simple server is running")

        # # Enable Access-Control-Allow-Origin
        # return jsonify(message="POST request returned")
        # return response

    except Exception as e:
        resp = {
            'response_code': "230",
            'response_message': traceback.print_exc(),
            'error': str(e)
        }
        return resp

@app.route('/AllAlerts', methods=['GET'])
def AllAlerts():
    try:
        data = []
        for li in alertsList:
            temp_json = {
                "coin": li[0], "price": li[1], "email": li[2]
            }
            data.append(temp_json)
        print(data)
        resp = {
            "data": data, 
            "status_code": 200
        }
        return resp 

    except Exception as e:
        resp = {
            'response_code': "230",
            'response_message': traceback.print_exc(),
            'error': str(e)
        }
        return resp