from django.http import HttpResponse, JsonResponse
import requests
from bs4 import BeautifulSoup
import json


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
