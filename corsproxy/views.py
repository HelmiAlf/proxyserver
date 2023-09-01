from django.http import HttpResponse, JsonResponse
import requests
from bs4 import BeautifulSoup


def get_user_data(snackvideo_id):
	req = requests.get("https://m.snackvideo.com/user/@"+snackvideo_id)
	soup = BeautifulSoup(req.text)
	username = soup.css.select("div.username")[0].text
	img_src = soup.css.select(".profile .avatar img")[0]['src']
	bio = soup.css.select("div.desc")[0].text

	return username, img_src, bio



def index(request):
	# print(request.GET)
	if 'username' in request.GET.keys():

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

	else:
		return HttpResponse("use /?username=(snackvideo_id)")
