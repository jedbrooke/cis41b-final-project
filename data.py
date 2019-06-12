import requests
import json
url = 'https://api.imgur.com/3/gallery/search?q=cats'
headers = {
  'Authorization': 'Client-ID b8edaa81221fa46'
}
response = requests.request('GET', url, headers = headers, allow_redirects=False)
#print(response.text)

data = json.loads(response.text)

print(len(data["data"]))

for post in data["data"]:
	for image in post["images"]:
		print(image["link"])