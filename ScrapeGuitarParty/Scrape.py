import requests

# letters = [chr(ord('a') + i) for i in range(26)]


r = requests.get("http://api.guitarparty.com/v2/songs/?query=bubbi")

print(r.json)   