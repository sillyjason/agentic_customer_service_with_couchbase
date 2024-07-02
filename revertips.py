import json
import requests
import os

# 1. Find public ipv4 address
response = requests.get('https://api.ipify.org?format=json')
IP_ADDRESS = response.json()['ip']

print(f'Your public IP address is: {IP_ADDRESS}')

# 2. Replace "YOUR_IP_ADDRESS" in the JSON file
def revert_json_file(file_path):
    file_path = os.path.join('static', 'events', file_path)
    with open(file_path, 'r+') as file:
        data = json.load(file)
        data_as_str = json.dumps(data)
        data_as_str = data_as_str.replace(IP_ADDRESS, "YOUR_IP_ADDRESS")
        data = json.loads(data_as_str)
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

revert_json_file('message_response_processing.json')
revert_json_file('process_message.json')
revert_json_file('process_refund_ticket.json')