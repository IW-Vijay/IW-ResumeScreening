import requests

response = requests.get(
    "http://localhost:3000/api/v1/chatmessage/84f06a5d-b268-4ee8-adfc-c008273087e7",
    headers={"Authorization":"Bearer aW8IQI_KyF0m9JmoNeQww8Pmj_2bg5ydT-maQATinvg"},
)
data = response.text

print(data)