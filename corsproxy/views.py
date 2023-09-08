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

			response = JsonResponse({
				"name": username,
				"img_src": img_src,
				"bio": bio
				})
			response["Access-Control-Allow-Origin"] = "*"
			response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
			response["Access-Control-Max-Age"] = "1000"
			response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
			return response
		except Exception as e:
			response = JsonResponse({
				"name": 'failed locating account',
				"img_src": 'https://cdn-icons-png.flaticon.com/512/4436/4436559.png',
				"bio": str(e)
				})
			response["Access-Control-Allow-Origin"] = "*"
			response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
			response["Access-Control-Max-Age"] = "1000"
			response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
			return response


	else:
		return HttpResponse("use /?username=(snackvideo_id)")


def topup_form(request):
	# http://127.0.0.1:8000/topupform/?username=alpha_real&email=helmi.alf@gmail.com&name=Helmi%20Alfarel&paket_diamond=150%20diamond&kode_bank=BNI&diamond_amount=150&gross_profit=900000&admin_fee=5000

	webhook_url = 'https://hook.us1.make.com/kpk9v3ee2l4ovynwoc5a8g142keat6tc'

	if 'username' in request.GET.keys():
		username = request.GET["username"]
		email = request.GET["email"]
		name = request.GET["name"]
		paket_diamond = request.GET["paket_diamond"]
		kode_bank = request.GET["kode_bank"].upper()
		diamond_amount = re.sub('[^0-9]', '', paket_diamond)
		gross_profit = re.sub('[^0-9]', '', request.GET["gross_profit"])
		admin_fee = request.GET["admin_fee"]


		timestamp_clean = re.sub('[^a-zA-Z0-9]', '', str(datetime.datetime.now()))[:14]
		date_today = str(datetime.date.today())

		transaction_id = "TW_{}_{}".format(username, timestamp_clean)
		expected_amount_paid = int(gross_profit)+int(admin_fee)
		description = "Pembelian {} Diamond dari Twee Reseller".format(diamond_amount)


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

		response = JsonResponse(virtual_account)
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
		return response

	else:
		return HttpResponse("wrong format")

def send_api_to_xendit(external_id, bank_code, name, expected_amount, description):
	
	api_key = "xnd_production_WSn672EAXFr0apQijn98HRaovteNiX9rpeJHyOdGFPpwIqCNdapTs6NhxGBkkp7"
	xendit_instance = Xendit(api_key=api_key)
	VirtualAccount = xendit_instance.VirtualAccount

	virtual_account = VirtualAccount.create(
		external_id=external_id,
		bank_code=bank_code,
		name=name,
		is_single_use=True, 
		is_closed=True, 
		expected_amount=50000
	)

	print(virtual_account)
	return virtual_account


# if __name__ == '__main__':
# 	send_api_to_xendit('a','a','a','a','a','a')
