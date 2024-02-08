import unittest
import json
from unittest.mock import patch, MagicMock
from app import app, process_receipt
import redis
from flask import Request 

class TestProcessReceiptAPI(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_process_receipt_empty_json(self):
        response = self.app.post('/receipts/process', json={})
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'receipt received empty')

    def test_process_receipt_invalid_data_types(self):
        invalid_data = {
            'retailer': 123,
            'purchaseDate': '2022-01-01',
            'total': '35.35',
            'items': []
        }
        response = self.app.post('/receipts/process', json=invalid_data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Invalid data types in receipt data')

    @patch('app.redis_client')
    @patch('app.uuid')
    def test_process_receipt_new_receipt(self, mock_uuid, mock_redis_client):
        mock_uuid.uuid4.return_value = '1234-5678'
        mock_redis_client.hexists.return_value = False

        receipt_data = {
            "retailer": "Target",
            "purchaseDate": "2023-03-04",
            "purchaseTime": "13:01",
            "items": [
                {
                "shortDescription": "Mountain Dew 12PK",
                "price": "6.49"
                },{
                "shortDescription": "Emils Cheese Pizza",
                "price": "12.25"
                },{
                "shortDescription": "Knorr Creamy Chicken",
                "price": "1.26"
                },{
                "shortDescription": "Doritos Nacho Cheese",
                "price": "3.35"
                },{
                "shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ",
                "price": "12.00"
                }
            ],
            "total": "35.35"
        }
        response = self.app.post('/receipts/process', json=receipt_data)
        data = json.loads(response.data.decode())
        ##Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], '1234-5678')


    @patch('app.redis_client', side_effect=redis.ConnectionError)
    def test_process_receipt_redis_connection_error(self,mock_redis_client):
        receipt_data = {
            'retailer': 'Target',
            'purchaseDate': '2022-01-01',
            'total': '35.35',
            'items': []
        }
        response = self.app.post('/receipts/process', json=receipt_data)
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 500)
        
    @patch('app.redis_client')
    def test_check_receipt_invalid_receipt_id(self, mock_redis_client):
        # Configure mock Redis client
        mock_redis_instance = mock_redis_client.return_value
        mock_redis_instance.get.return_value = None
        # Call the Flask route with an invalid receipt ID
        response = app.test_client().get('/receipts/123-568/points')
        data = response.get_json()

        # Assertions
        self.assertEqual(response.status_code, 500)
        self.assertEqual(data['error'],'badly formed hexadecimal UUID string')

    @patch('app.redis.client')
    def test_check_receipt_points(self, mock_redis_client):
        mock_redis_instance = mock_redis_client.return_value
        # with receipt_id processed from receipt_json given.Note replace receipt uuid with generated receipt id
        response = app.test_client().get('/receipts/e9b0a673-12fc-417e-bb7f-c56f2b441d88/points')
        data = response.get_json()
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['points'], 109)  # Assuming the total is a round dollar amount with no cents
    
    
if __name__ == '__main__':
    unittest.main()
