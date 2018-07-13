import requests

url = "https://plex.tv/users/sign_in.json"

username = input("Plex username: ")
password = input("Plex password: ")

payload = "user%5Blogin%5D=" +  username + "&user%5Bpassword%5D=" + password
headers = {
    'x-plex-client-identifier': "plexapi",
    'x-plex-product': "plexapi",
    }

data = requests.request("POST", url, data=payload, headers=headers)
data = str(data.text)
token = data[(data.find("authToken")+12):((data.find("authToken")+12)+20)]
print(token)