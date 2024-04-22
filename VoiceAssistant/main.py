import controller
import draw
import api
import prompts
import re

MAX_ROUND = 15
API_TOKEN = "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"
if __name__ == "__main__":
    roundcount = 0
    last_step = {}
    context = []
    width, height = controller.get_device_size()
    task = "将当前页面文章分享给微信好友：宝子"
    while roundcount < MAX_ROUND:
        roundcount += 1
        screenshot_path = controller.get_screenshot(f"screen_{roundcount}.png")
        xml_path = controller.get_domtree(f"domtree_{roundcount}.xml")
        clickable_list = []
        focusable_list = []
        text_list = []
        content_list = []
        controller.traverse_tree(xml_path, clickable_list, text_list, content_list)

        draw.draw_bbox_multi(f"./screenshots/screen_{roundcount}.png", clickable_list, f"./labeled/labeled_{roundcount}.png")
        base64_image = api.encode_image(f"./labeled/labeled_{roundcount}.png")
        # observer
        prompt = re.sub(r"<task_description>", task, prompts.observer_template)
        prompt = re.sub(r"<text_list>", str(text_list), prompt)
        prompt = re.sub(r"<content_list>", str(content_list),prompt)
        prompt = re.sub(r"<context>", str(context), prompt)
        # prompt = re.sub(r"<context>", context, prompt)
        content = api.generate_content(prompt, base64_image)
        chat = []
        chat.append(["user",content])
        print("Observer:")
        rsp = api.inference_chat(chat,API_TOKEN)
        page_description = rsp
        last_step["description"] =  page_description
        # checker
        prompt = re.sub(r"<task_description>", task, prompts.checker_template)
        prompt = re.sub(r"<context>", str(context), prompt)
        content = api.generate_content(prompt, base64_image)
        chat = []
        chat.append(["user",content])
        print("Checker:")
        rsp = api.inference_chat(chat,API_TOKEN)
        if rsp == 'FINISH':
            print("Task finished successfully!")
            break
        # executor
        prompt = re.sub(r"<task_description>", task, prompts.executor_template)
        prompt = re.sub(r"<context>", str(context), prompt)
        prompt = re.sub(r"<page_description>",  page_description, prompt)
        prompt = re.sub(r"<text_list>", str(text_list), prompt)
        prompt = re.sub(r"<content_list>", str(content_list),prompt)
        content = api.generate_content(prompt, base64_image)
        chat = []
        chat.append(["user", content])
        print("Executor:")
        rsp = api.inference_chat(chat,API_TOKEN)
        res = api.parse_explore_rsp(rsp)
        act_name = res[0]
        last_step["your_action"] = res[-1]
        context.append(last_step)
        res = res[1:-1]
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
