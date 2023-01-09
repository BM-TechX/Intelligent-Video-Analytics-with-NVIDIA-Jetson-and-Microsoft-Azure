import json
def read_json():
    with open('config.json') as json_file:
        data = json.load(json_file)

        print(data["roi1"])

read_json()
