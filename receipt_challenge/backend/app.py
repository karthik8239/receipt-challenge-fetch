from flask import Flask, request, jsonify
from flask_cors import CORS , cross_origin
from datetime import datetime
import redis
import json
import uuid
import hashlib
import json
import math
import datetime

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


##modify to redis while pushing
redis_client = redis.Redis(host='redis', port=6379, db=0)


##Helper Function to calculate the total number of points accumulated as per the given rules
##takes receipt_data as argument and returns total points
def calculate_points(receipt_data):
     points = 0
     ##getting the details of the receipt from receipt data
     retailer = receipt_data.get('retailer','')
     purchase_date = receipt_data.get('purchaseDate','')
     total = float(receipt_data.get('total','0'))
     items = receipt_data.get('items',[])
     purchase_time = receipt_data.get('purchaseTime','')
    
    ##calculations for the points according to each case mentioned
     count = sum(1 for char in retailer if char.isalnum())
     points = points + count
     if(total.is_integer()):
        points = points + 50

     if(total % 0.25 == 0):
        points = points + 25

     points = points + (len(items) // 2) * 5

     for item in items:
        if(len(item.get('shortDescription', '').strip()) % 3 == 0):
            price = float(item.get('price',0))
            points = points + math.ceil(price * 0.2)

     if(int(purchase_date.split("-")[-1]) % 2 == 1):
        points = points + 6

     if(purchase_time >= '14.00' and purchase_time < '16.00'):
        points = points + 10

     return points

def validate_receipt_data_types(receipt_data):
   ##Handling the logic in a try-catch block
    try:
        #Validate the retailer in receipt
        if not isinstance(receipt_data.get('retailer'), str):
            return False

        #Validate purchaseDate
        purchase_date_str = receipt_data.get('purchaseDate')
        if not purchase_date_str or not isinstance(purchase_date_str, str):
            return False
        datetime.datetime.strptime(purchase_date_str, '%Y-%m-%d')

        # Validate purchaseTime (optional)
        purchase_time_str = receipt_data.get('purchaseTime')
        if purchase_time_str and not isinstance(purchase_time_str, str):
            return False

        # Validate items list in the receipt
        items = receipt_data.get('items', [])
        if not isinstance(items, list):
            return False
        for item in items:
            if not isinstance(item.get('shortDescription'), str):
                return False
            if not isinstance(item.get('price'), str):
                return False
            try:
                float(item.get('price'))
            except ValueError:
                return False

        # Validate total
        total_str = receipt_data.get('total')
        if not total_str or not isinstance(total_str, str):
            return False
        float(total_str)

        return True

    except (ValueError, TypeError, KeyError):
        return False


##function to process the receipts and returns the json containing uuid for the receipt
@app.route('/receipts/process' , methods = ['POST'])
def process_receipt():
    ##try-catch block to handle the code
    try:
     receipt_data = request.get_json()
     ##validating the input json for empty
     if receipt_data is None or len(receipt_data) == 0:
        return jsonify({'error':'receipt received empty'}) , 400
    
     if not validate_receipt_data_types(receipt_data):
        return jsonify({'error':'Invalid data types in receipt data'}) , 400

     receipt_data_str = json.dumps(receipt_data)
     ##check if the receipts exsists in the redis db. 
     if redis_client.hexists('receipts', receipt_data_str):
        receipt_id = redis_client.hget('receipts', receipt_data_str).decode()

    ##generating receipt id and storing in the redis db
     else:
      receipt_id = str(uuid.uuid4())
      redis_client.set(receipt_id, receipt_data_str)
      redis_client.hset('receipts', receipt_data_str, receipt_id)

    ##framing the json with a response.
     response_data = {'id':receipt_id}
     return jsonify(response_data) , 200

    except redis.ConnectionError:
        return jsonify({'error':'Error connecting to the database server'}) , 500
    
    except json.JSONDecodeError:
        return jsonify({'error':'Error decoding JSON data from database server'}) , 500
        
     ##return the exception with the error information and HTTP code
    except Exception as e:
        return jsonify({'error' : str(e)}) ,500

##function to get the receipt by receipt id and calculate points return it as json
@app.route('/receipts/<string:receipt_id>/points',methods = ['GET'])
def check_receipt(receipt_id):
    #try-catch block to handle the logic 
    try:
    ##validating the input receipt_id
     if(not isinstance(receipt_id,str) or not uuid.UUID(str(receipt_id))):
        return jsonify({'error':'given receipt id does not match format'})
     receipt_data_str = redis_client.get(receipt_id)
     ##checking if there is any receipt id present in the database
     if receipt_data_str is None:
        return jsonify({'error':'given receipt_id does not exist'}) ,400

     receipt_data = json.loads(receipt_data_str)
     ##calling the helper function to get the total number of points
     total_points = calculate_points(receipt_data)
     response_data = {'points' : total_points}
     return jsonify(response_data) , 200

    except redis.ConnectionError:
        return jsonify({'error':'Error connecting to the database server'}) , 500
    
    except json.JSONDecodeError:
        return jsonify({'error':'Error decoding JSON data from database server'}) , 500

    ##returning the exception with error information and HTTP code
    except Exception as e:
        return jsonify({'error': str(e)}) , 500

##handling CORS from API side 
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

##Main method to invoke the function
if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 8001)