from django.http import HttpResponse, JsonResponse
import requests
from bs4 import BeautifulSoup
import json
import datetime
import re
from xendit import Xendit

def get_user_data(snackvideo_id):
	req = requests.get("https://m.snackvideo.com/user/@"+snackvideo_id)
	soup = BeautifulSoup(req.text)
	data = json.loads(soup.css.select("#Person")[0].text)
	username = data['name']
	img_src = data['image']
	bio = data['description']

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
			return_no_cors_response(data_response)

		except Exception as e:
			data_response = {
				"name": 'failed locating account',
				"img_src": 'https://cdn-icons-png.flaticon.com/512/4436/4436559.png',
				"bio": str(e)
				}
			return_no_cors_response(data_response)


	else:
		return HttpResponse("use /?username=(snackvideo_id)")


def return_no_cors_response(json_data):
	response = JsonResponse(json_data)
	response["Access-Control-Allow-Origin"] = "*"
	response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
	response["Access-Control-Max-Age"] = "1000"
	response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
	return response

def topup_form(request):
	# http://127.0.0.1:8000/topupform/?username=alpha_real&email=helmi.alf@gmail.com&name=Helmi%20Alfarel&paket_diamond=150%20diamond&kode_bank=BNI&diamond_amount=150&gross_profit=900000&admin_fee=5000

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
			diamond_amount = re.sub('[^0-9]', '', paket_diamond)
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

			xendit_call = send_api_to_xendit(transaction_id, kode_bank, name, expected_amount_paid, description)

			virtual_account = json.loads(str(xendit_call))

			return return_no_cors_response(virtual_account)
			

		else:
			return return_no_cors_response({'Error Message':"Wrong Message"})
	
	except Exception as e:
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


def doku_callback(request):
	if request.method =='POST':
		return JsonResponse(request.POST)

	else:
		return JsonResponse(request.GET)
	