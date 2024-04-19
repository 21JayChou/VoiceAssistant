import base64
import requests
import re

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_content(prompt, base64_image):
    content = [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            },
        ]
    return content

def inference_chat(chat, API_TOKEN):    
    api_url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }

    data = {
        "model": 'gpt-4-vision-preview',
        "messages": [],
        "max_tokens": 2048,
    }

    for role, content in chat:
        data["messages"].append({"role": role, "content": content})
    while 1:
        try:
            res = requests.post(api_url, headers=headers, json=data)
            res = res.json()['choices'][0]['message']['content']
            print(res)
        except:
            print("Network Error:")
        else:
            break
    
    return res

def parse_explore_rsp(rsp):
    try:
        observation = re.findall(r"Observation: (.*?)$", rsp, re.MULTILINE)[0]
        think = re.findall(r"Thought: (.*?)$", rsp, re.MULTILINE)[0]
        act = re.findall(r"Action: (.*?)$", rsp, re.MULTILINE)[0]
        last_act = re.findall(r"Summary: (.*?)$", rsp, re.MULTILINE)[0]
        # print_with_color("Observation:", "yellow")
        # print_with_color(observation, "magenta")
        # print_with_color("Thought:", "yellow")
        # print_with_color(think, "magenta")
        # print_with_color("Action:", "yellow")
        # print_with_color(act, "magenta")
        # print_with_color("Summary:", "yellow")
        # print_with_color(last_act, "magenta")
        if "FINISH" in act:
            return ["FINISH"]
        act_name = act.split("(")[0]
        if act_name == "tap":
            area = int(re.findall(r"tap\((.*?)\)", act)[0])
            return [act_name, area, last_act]
        elif act_name == "text":
            input_str = re.findall(r"text\((.*?)\)", act)[0][1:-1]
            return [act_name, input_str, last_act]
        elif act_name == "long_press":
            area = int(re.findall(r"long_press\((.*?)\)", act)[0])
            return [act_name, area, last_act]
        elif act_name == "swipe":
            params = re.findall(r"swipe\((.*?)\)", act)[0]
            area, swipe_dir, dist = params.split(",")
            area = int(area)
            swipe_dir = swipe_dir.strip()[1:-1]
            dist = dist.strip()[1:-1]
            return [act_name, area, swipe_dir, dist, last_act]
        else:
            # print_with_color(f"ERROR: Undefined act {act_name}!", "red")
            return ["ERROR"]
    except Exception as e:
        # print_with_color(f"ERROR: an exception occurs while parsing the model response: {e}", "red")
        # print_with_color(rsp, "red")
        return ["ERROR"]