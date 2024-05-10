import controller
import draw
import api
from prompts import executor_template, observer1_template, observer2_template, planner_template
import re
import ast
from similar import find_best

MAX_ROUND = 15
API_TOKEN = "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"
cols = 0
rows = 0

def area_to_xy(area, subarea):
    area -= 1
    row, col = area // cols, area % cols
    x_0, y_0 = col * (width // cols), row * (height // rows)
    if subarea == "top-left":
        x, y = x_0 + (width // cols) // 4, y_0 + (height // rows) // 4
    elif subarea == "top":
        x, y = x_0 + (width // cols) // 2, y_0 + (height // rows) // 4
    elif subarea == "top-right":
        x, y = x_0 + (width // cols) * 3 // 4, y_0 + (height // rows) // 4
    elif subarea == "left":
        x, y = x_0 + (width // cols) // 4, y_0 + (height // rows) // 2
    elif subarea == "right":
        x, y = x_0 + (width // cols) * 3 // 4, y_0 + (height // rows) // 2
    elif subarea == "bottom-left":
        x, y = x_0 + (width // cols) // 4, y_0 + (height // rows) * 3 // 4
    elif subarea == "bottom":
        x, y = x_0 + (width // cols) // 2, y_0 + (height // rows) * 3 // 4
    elif subarea == "bottom-right":
        x, y = x_0 + (width // cols) * 3 // 4, y_0 + (height // rows) * 3 // 4
    else:
        x, y = x_0 + (width // cols) // 2, y_0 + (height // rows) // 2
    return x, y

if __name__ == "__main__":
    roundcount = 0
    last_step = {}
    context = {}
    width, height = controller.get_device_size()
    task = "步行导航至复旦大学江湾校区"
    while roundcount < MAX_ROUND:
        roundcount += 1
        screenshot_path = controller.get_screenshot(f"screen_{roundcount}.png")
        xml_path = controller.get_domtree(f"domtree_{roundcount}.xml")
        clickable_list = []
        text_function_dict = {}
        controller.traverse_tree(xml_path, clickable_list,text_function_dict)
        draw.draw_bbox_multi(f"./screenshots/screen_{roundcount}.png", clickable_list, f"./labeled/labeled_{roundcount}.png")
        i = 1 + find_best(f"./screenshots/screen_{roundcount}.png")
        base64_image = api.encode_image(f"./labeled/labeled_{roundcount}.png")
        similar_image = api.encode_image(f"./knowledge/labeled/{i}.png")
        print(f"similar image:{i}")
        knowledge_content = ast.literal_eval(open(f"./knowledge/describe/{i}.txt", "r", encoding='utf-8').read())

        # observer1
        prompt = observer1_template
        print("\nObserver1:")
        rsp = api.inference_chat(prompt, API_TOKEN, base64_image)
        page_description = rsp
        # observer2

        prompt = re.sub(r"<text_function_dict>", str(text_function_dict), observer2_template)
        prompt = re.sub(r"<knowledge_content>", str(knowledge_content), prompt)
        print("\nObserver2:")
        rsp = api.inference_chat(prompt, API_TOKEN, base64_image, similar_image)
        text_function_dict = rsp
        page_description += "\nText&Function Dict:" + rsp

        # planner
        prompt = re.sub(r"<task_description>", task, planner_template)
        prompt = re.sub(r"<page_description>", page_description, prompt)
        prompt = re.sub(r"<context>", str(context), prompt)
        print("\nPlanner:")
        rsp = api.inference_chat(prompt, API_TOKEN, base64_image)
        summary = re.findall(r"Summary: (.*?)$", rsp, re.MULTILINE)[0]
        status = re.findall(r"Status: (.*?)$", rsp, re.MULTILINE)[0]
        plan = re.findall(r"Plan: (.*?)$", rsp, re.MULTILINE)[0]
        if status == "FINISH":
            print("Task Finished!")
            break

        # executor
        prompt = re.sub(r"<task_description>", task, executor_template)
        prompt = re.sub(r"<text_function_dict>", text_function_dict, prompt)
        prompt = re.sub(r"<history>", summary, prompt)
        prompt = re.sub(r"<plan>", plan, prompt)
        # print("\nExecutorPrompt:")
        # print(prompt)
        print("\nExecutor:")
        rsp = api.inference_chat(prompt, API_TOKEN, base64_image)
        res = api.parse_explore_rsp(rsp)
        act_name = res[0]
        context["step"+str(roundcount)] = res[-1]
        res = res[1:-1]

        if act_name == "FINISH":
            print("Task Completed!")
            break
        if act_name == "tap":
            area = res[0]
            index = int(area)-1
            center_x = (clickable_list[index].bbox[0][0] + clickable_list[index].bbox[1][0])//2
            center_y = (clickable_list[index].bbox[0][1] + clickable_list[index].bbox[1][1])//2
            controller.tap(center_x, center_y)
        elif act_name == "text":
            input_str = res[0]
            controller.text(input_str)
        elif act_name == "long_press":
            area = res[0]
            index = int(area) - 1
            center_x = (clickable_list[index].bbox[0][0] + clickable_list[index].bbox[1][0]) // 2
            center_y = (clickable_list[index].bbox[0][1] + clickable_list[index].bbox[1][1]) // 2
            controller.long_press(center_x, center_y)
        elif act_name == "swipe":
            area, swipe_dir, dist = res
            if int(area) != -1:
                index = int(area) - 1
                center_x = (clickable_list[index].bbox[0][0] + clickable_list[index].bbox[1][0]) // 2
                center_y = (clickable_list[index].bbox[0][1] + clickable_list[index].bbox[1][1]) // 2
            else:
                center_x = width/2
                center_y = height/2
            controller.swipe(center_x, center_y, swipe_dir, width, dist)
        elif act_name == "back":
            controller.back()
        elif act_name == "home":
            controller.home()
