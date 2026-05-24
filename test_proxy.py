import http.client
import json

conn = http.client.HTTPConnection("localhost", 8082)
payload = json.dumps({
    "model": "claude-3-5-sonnet-20240620",
    "max_tokens": 10,
    "messages": [{"role": "user", "content": "Hi"}]
})
headers = {
    'Content-Type': 'application/json',
    'x-api-key': 'freecc'
}
conn.request("POST", "/v1/messages", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
