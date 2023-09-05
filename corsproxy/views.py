from django.http import HttpResponse, JsonResponse
import requests
from bs4 import BeautifulSoup
import json
import datetime
import re


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
	# http://127.0.0.1:8000/topupform/?username=alpha_real&email=helmi.alf@gmail.com&paket_diamond=150%20diamond&kode_bank=BCA&diamond_amount=150&gross_profit=900000&admin_fee=5000

	webhook_url = 'https://hook.us1.make.com/kpk9v3ee2l4ovynwoc5a8g142keat6tc'

	if 'username' in request.GET.keys():
		username = request.GET["username"]
		email = request.GET["email"]
		paket_diamond = request.GET["paket_diamond"]
		kode_bank = request.GET["kode_bank"]
		diamond_amount = request.GET["diamond_amount"]
		gross_profit = re.sub('[^0-9]', '', request.GET["gross_profit"])
		admin_fee = request.GET["admin_fee"]

		timestamp_clean = re.sub('[^a-zA-Z0-9]', '', str(datetime.datetime.now()))
		date_today = str(datetime.date.today())

		transaction_id = "TW_{}_{}".format(username, timestamp_clean)
		table = "Diamond Ordered"


		data = {
			'Table':table,
			'Transaction ID': transaction_id,
			'Snack Video ID': username,
			'Email': email,
			'Package': paket_diamond,
			'Diamond Amount': diamond_amount,
			'Gross Profit': gross_profit,
			'Admin Fee': admin_fee,
			'Bank': kode_bank,
			'Date': date_today,
			'Timestamp': timestamp_clean
		}

		print(data)

		req = requests.post(webhook_url, data=json.dumps(data), headers={'Content-type': 'application/json'})


		return HttpResponse(str(req))

	else:
		return HttpResponse("wrong format")