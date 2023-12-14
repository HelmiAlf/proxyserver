from bs4 import BeautifulSoup
from django.http import HttpResponse, JsonResponse
from xendit import Xendit
import base64
import datetime
import hashlib
import hmac
import json
import random
import re
import requests
import html


def get_user_data(snackvideo_id):
	req = requests.get("https://m.snackvideo.com/user/@"+snackvideo_id)
	# print(req.text)
	soup = BeautifulSoup(req.text)
	data = json.loads(html.unescape(soup.find(id="Person").text))
	username = data['mainEntity']['name']
	img_src = data['mainEntity']['image']
	bio = data['mainEntity']['description']

	return username, img_src, bio





def index(request):
	# print(request.GET)
	if 'username' in request.GET.keys():
		try:
			username, img_src, bio = get_user_data(request.GET["username"])

			data_response = {
				"name": username,
				"img_src": img_src,
				"bio": bio
				}
			return return_no_cors_response(data_response)

		except Exception as e:
			data_response = {
				"name": 'failed locating account',
				"img_src": 'https://cdn-icons-png.flaticon.com/512/4436/4436559.png',
				"bio": str(e)
				}
			return return_no_cors_response(data_response)


	else:
		return HttpResponse("use /?username=(snackvideo_id)")


def return_no_cors_response(json_data):
	response = HttpResponse(json.dumps(json_data), content_type='application/json')
	response["Access-Control-Allow-Origin"] = "*"
	response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
	response["Access-Control-Max-Age"] = "1000"
	response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
	return response

def topup_form(request):
	# http://127.0.0.1:8000/topupform/?username=alpha_real&email=helmi.alf@gmail.com&name=Helmi%20Alfarel&paket_diamond=150%20diamond&kode_bank=BNI&diamond_amount=150&gross_profit=900000&admin_fee=5000
	# https://proxyserver-helmialf.vercel.app/topupform/?username=AAA&email=helmi.alf@gmail.com&name=tests&paket_diamond=%2710.000&kode_bank=BNI&gross_profit=Rp. 1.580.000&admin_fee=4000

	webhook_url = 'https://hook.us1.make.com/kpk9v3ee2l4ovynwoc5a8g142keat6tc'

	try:

		if 'username' in request.GET.keys():
			if 'testing' in request.GET["username"].lower():
				return tes_topup_function()

			username = request.GET["username"]
			email = request.GET["email"]
			name = re.sub('[^a-zA-Z]', '', request.GET["name"])
			paket_diamond = request.GET["paket_diamond"]
			kode_bank = request.GET["kode_bank"].upper()
			diamond_amount = request.GET["diamond_amount"]
			gross_profit = re.sub('[^0-9]', '', request.GET["gross_profit"])
			admin_fee = request.GET["admin_fee"]


			timestamp_clean = re.sub('[^a-zA-Z0-9]', '', str(datetime.datetime.now()))[:14]
			date_today = str(datetime.date.today())

			transaction_id = "TW_{}_{}".format(username, timestamp_clean)
			expected_amount_paid = int(gross_profit)+int(admin_fee)
			expiration_date = str(datetime.datetime.today() + datetime.timedelta(days=1))


			data = {
				'Table':"Diamond Ordered",
				'Transaction ID': transaction_id,
				'Snack Video ID': username,
				'Email': email,
				'Name' : name,
				'Package': paket_diamond,
				'Diamond Amount': diamond_amount,
				'Gross Profit': gross_profit,
				'Admin Fee': admin_fee,
				'Bank': kode_bank,
				'Date': date_today,
				'Timestamp': timestamp_clean
			}

			# print(data)

			req = requests.post(webhook_url, data=json.dumps(data), headers={'Content-type': 'application/json'})

			doku_call = doku_get_payment_url(transaction_id, expected_amount_paid)
			return return_no_cors_response(doku_call)
			

		else:
			return return_no_cors_response({'Error Message':"Wrong Message"})
	
	except Exception as e:
		print(e)
		return return_no_cors_response({'Error Message':e})


def send_api_to_xendit(external_id, bank_code, name, expected_amount, description, expiration_date):
	
	api_key = "xnd_production_WSn672EAXFr0apQijn98HRaovteNiX9rpeJHyOdGFPpwIqCNdapTs6NhxGBkkp7"
	xendit_instance = Xendit(api_key=api_key)
	VirtualAccount = xendit_instance.VirtualAccount

	virtual_account = VirtualAccount.create(
		external_id=external_id,
		bank_code=bank_code,
		name=name,
		is_single_use=True, 
		is_closed=True, 
		expected_amount=expected_amount,
		expiration_date=expiration_date
	)

	print(virtual_account)
	return virtual_account

def tes_topup_function():
	data = {"owner_id": "60ff6cf2dd93806c99a10ca5", "external_id": "TW_AAA_20230909234945", "account_number": "8808487689553918", "bank_code": "BNI", "merchant_code": "8808", "name": "XDT-tests", "is_closed": true, "expected_amount": 1584000, "is_single_use": true, "status": "PENDING", "currency": "IDR", "country": "ID", "expiration_date": "2054-09-09T17:00:00.000Z", "id": "64fd049a3dd020347dba3cfe"}
	return return_no_cors_response(data)

# Start Doku Gateway
def generateDigest(jsonBody):  
    return base64.b64encode(hashlib.sha256(jsonBody.encode('utf-8')).digest()).decode("utf-8")

def generateSignature(clientId, requestId, requestTimestamp, requestTarget, digest, secret):
    componentSignature = "Client-Id:" + clientId
    componentSignature += "\n"
    componentSignature += "Request-Id:" + requestId
    componentSignature += "\n"
    componentSignature += "Request-Timestamp:" + requestTimestamp
    componentSignature += "\n"
    componentSignature += "Request-Target:" + requestTarget
    # If body not send when access API with HTTP method GET/DELETE
    if digest:  
        componentSignature += "\n"
        componentSignature += "Digest:" + digest
     
    message = bytes(componentSignature, 'utf-8')
    secret = bytes(secret, 'utf-8')
 
    # Calculate HMAC-SHA256 base64 from all the components above
    signature = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest()).decode("utf-8")

    # Prepend encoded result with algorithm info HMACSHA256=
    return "HMACSHA256="+signature 

def doku_get_payment_url(external_id, expected_amount):
	client_id = "BRN-0216-1695707074316" # Sudah Ganti dengan yg asli
	secret_key = "SK-HiqxeU7rpRKAVxvNZqjk" # Sudah Ganti dengan yg asli
	endpoint = "https://api.doku.com/checkout/v1/payment" # Sudah Ganti dengan yg asli

	request_id = external_id
	request_timestamp = str(datetime.datetime.now(datetime.timezone.utc).isoformat()[:19]+"Z")
	invoice_number = external_id

	body = {
	    "order": {
	        "amount": expected_amount,
	        "invoice_number": invoice_number
	    },
	    "payment": {
	        "payment_due_date": 60,
	        "payment_method_types": [
	          "VIRTUAL_ACCOUNT_BCA",
	          "VIRTUAL_ACCOUNT_BANK_MANDIRI",
	          "VIRTUAL_ACCOUNT_BANK_SYARIAH_MANDIRI",
	          "VIRTUAL_ACCOUNT_DOKU",
	          "VIRTUAL_ACCOUNT_BRI",
	          "VIRTUAL_ACCOUNT_BNI",
	          "VIRTUAL_ACCOUNT_BANK_PERMATA",
	          "VIRTUAL_ACCOUNT_BANK_CIMB",
	          "VIRTUAL_ACCOUNT_BANK_DANAMON",
	          ]
	    }
	}

	jsonBody = json.dumps(body)
	digest = generateDigest(jsonBody)

	headerSignature = generateSignature(client_id, request_id, request_timestamp, "/checkout/v1/payment", digest, secret_key)

	headers = {
	  "Client-Id": client_id,
	  "Request-Id": request_id,
	  "Request-Timestamp": request_timestamp,
	  "Signature": headerSignature
	}

	response = requests.post(endpoint, headers=headers, json=body)
	return response.json()
