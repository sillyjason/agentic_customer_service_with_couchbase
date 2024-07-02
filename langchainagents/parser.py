import re
import json


def parse_message(input_message):
    # Step 1: Extract Message Type
    message_type_match = re.search(r"={33}\s(.+?)\s={33}", input_message)
    if message_type_match:
        message_type = message_type_match.group(1)
        is_tool_message = message_type == "Tool Message"
    else:
        return False, None, None

    # Step 2: Extract Function Name
    function_name = None
    
    function_name_match = re.search(r"Name:\s(.+?)\n", input_message)
    if function_name_match:
        function_name = function_name_match.group(1)
    else:
        return is_tool_message, None, None

    # Step 3: Extract JSON Content
    json_content_match = re.search(r"\n\n({.*})", input_message, re.DOTALL)
    if json_content_match:
        json_content = json_content_match.group(1)
        # Convert Python dictionary format to valid JSON format
        
        json_content = json_content.replace("'", '"').replace("None", "null").replace("False", "false").replace("True", "true")
        
        print(f'json_contenttt: {json_content}')
        
        try:
            json_data = json.loads(json_content)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return is_tool_message, function_name, None
        return is_tool_message, function_name, json_data
            
    return is_tool_message, function_name, None