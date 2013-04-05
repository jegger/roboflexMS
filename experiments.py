import json

data='[{"x":0, "y":1}]'
for i in json.loads(data):
    print i
