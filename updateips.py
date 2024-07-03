import json
import os
from dotenv import load_dotenv

load_dotenv()

APP_NODE_HOSTNAME = os.getenv("APP_NODE_HOSTNAME")

# Replace "YOUR_IP_ADDRESS" in the JSON file
def update_json_file(file_path):
    file_path = os.path.join('static', 'eventing', file_path)
    with open(file_path, 'r+') as file:
        data = json.load(file)
        data_as_str = json.dumps(data)
        data_as_str = data_as_str.replace("YOUR_IP_ADDRESS", APP_NODE_HOSTNAME)
        data = json.loads(data_as_str)
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

update_json_file('process_message.json')
update_json_file('process_refund_ticket.json')

print(f"Updated Eventing JSON files with IP address: {APP_NODE_HOSTNAME}")