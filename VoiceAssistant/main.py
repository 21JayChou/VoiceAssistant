import controller
import draw
import api
import prompts
import re

MAX_ROUND = 15
API_TOKEN = "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"
if __name__ == "__main__":
    roundcount = 0
    last_act = "None"
    width, height = controller.get_device_size()
    while roundcount < MAX_ROUND:
        roundcount += 1
        screenshot_path = controller.get_screenshot(f"screen_{roundcount}.png")
        xml_path = controller.get_domtree(f"domtree_{roundcount}.xml")
        clickable_list = []
        focusable_list = []
        controller.traverse_tree(xml_path, clickable_list, "clickable")
        draw.draw_bbox_multi(f"./screenshots/screen_{roundcount}.png", clickable_list, f"./labeled/labeled_{roundcount}.png")
        base64_image = api.encode_image(f"./labeled/labeled_{roundcount}.png")
        prompt = re.sub(r"<task_description>", "查看最近十五日天气情况，并概括写在笔记中", prompts.init_template)
        prompt = re.sub(r"<last_act>", last_act, prompt)
        content = [
            {
                "type": "text",
                # "text":"This is a screenshot of a mobile phone where all the interactive elements have been framed, and the number of the element is marked in the upper left corner of each box. Now I want you to click on the \"Share\" button on this page, please give the number of the element you are going to click on, your answer only needs to give the number."
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            },
            # {
            #     "type":"text",
            #     "text":"hello"
            # }
        ]
        chat = []
        chat.append(["user",content])
        rsp = api.inference_chat(chat,API_TOKEN)
        res = api.parse_explore_rsp(rsp)
        act_name = res[0]
        last_act = res[-1]
        res = res[1:-1]
        if act_name == "FINISH":
            print("Task finished successfully!")
            break
        if act_name == "ERROR":
            print("Task finished unsuccessfully!")
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
