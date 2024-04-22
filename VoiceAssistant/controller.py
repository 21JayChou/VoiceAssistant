import os
import time
import xml.etree.ElementTree as ET
import subprocess

MIN_DIS = 30


class AndroidElement:
    def __init__(self, uid, bbox):
        self.uid = uid
        self.bbox = bbox


def get_domtree(save_path):
    save_path = os.path.join("./xml", save_path).replace("\\", "/")
    print(save_path)
    os.system(f"adb shell uiautomator dump /sdcard/uidump.xml")
    os.system(f"adb pull /sdcard/uidump.xml {save_path}")
    time.sleep(2)
    return save_path


def get_screenshot(save_path):
    save_path = os.path.join("./screenshots", save_path).replace("\\", "/")
    os.system(f"adb shell screencap -p /sdcard/screen.png")
    os.system(f"adb pull /sdcard/screen.png {save_path}")
    return save_path


def get_id_from_element(elem):
    bounds = elem.attrib["bounds"][1:-1].split("][")
    x1, y1 = map(int, bounds[0].split(","))
    # if y1 == 0:
    #     y1 = 140
    # if y1 == 2199:
    #     y1 = 2339
    x2, y2 = map(int, bounds[1].split(","))
    # if y2 == 0:
    #     y2 = 140
    # if y2 == 2199:
    #     y2 = 2339
    elem_w, elem_h = x2 - x1, y2 - y1
    if "resource-id" in elem.attrib and elem.attrib["resource-id"]:
        elem_id = elem.attrib["resource-id"].replace(":", ".").replace("/", "_")
    else:
        elem_id = f"{elem.attrib['class']}_{elem_w}_{elem_h}"
    if "content-desc" in elem.attrib and elem.attrib["content-desc"] and len(elem.attrib["content-desc"]) < 20:
        content_desc = elem.attrib['content-desc'].replace("/", "_").replace(" ", "").replace(":", "_")
        elem_id += f"_{content_desc}"
    return elem_id


def traverse_tree(xml_path, elem_list, text_list, content_list):
    path = []
    for event, elem in ET.iterparse(xml_path, ['start', 'end']):
        if event == 'start':
            path.append(elem)
            if "clickable" in elem.attrib and elem.attrib["clickable"] == "true" or \
                    "long-clickable" in elem.attrib and elem.attrib["long-clickable"] == "true":
                parent_prefix = ""
                if len(path) > 1:
                    parent_prefix = get_id_from_element(path[-2])
                bounds = elem.attrib["bounds"][1:-1].split("][")
                x1, y1 = map(int, bounds[0].split(","))
                x2, y2 = map(int, bounds[1].split(","))
                if x1 == x2 or y1 == y2:
                    continue
                center = (x1 + x2) // 2, (y1 + y2) // 2
                elem_id = get_id_from_element(elem)
                if parent_prefix:
                    elem_id = parent_prefix + "_" + elem_id
                elem_id += f"_{elem.attrib['index']}"
                # close = False
                # for e in elem_list:
                #     bbox = e.bbox
                #     center_ = (bbox[0][0] + bbox[1][0]) // 2, (bbox[0][1] + bbox[1][1]) // 2
                #     dist = (abs(center[0] - center_[0]) ** 2 + abs(center[1] - center_[1]) ** 2) ** 0.5
                #     if dist <= MIN_DIS:
                #         close = True
                #         break
                elem_list.append(AndroidElement(elem_id, ((x1, y1), (x2, y2))))
                if "text" in elem.attrib:
                    text_list.append(elem.attrib["text"])
                else:
                    text_list.append("")
                if "content-desc" in elem.attrib:
                    content_list.append(elem.attrib["content-desc"])
                else:
                    content_list.append("")


        if event == 'end':
            path.pop()
        i = 1


def merge_list(clickable_list, focusable_list):
    elem_list = clickable_list.copy()
    for elem in focusable_list:
        bbox = elem.bbox
        center = (bbox[0][0] + bbox[1][0]) // 2, (bbox[0][1] + bbox[1][1]) // 2
        close = False
        for e in clickable_list:
            bbox = e.bbox
            center_ = (bbox[0][0] + bbox[1][0]) // 2, (bbox[0][1] + bbox[1][1]) // 2
            dist = (abs(center[0] - center_[0]) ** 2 + abs(center[1] - center_[1]) ** 2) ** 0.5
            if dist <= MIN_DIS:
                close = True
                break
        if not close:
            elem_list.append(elem)
    return elem_list


def tap(x, y):
    try:
        os.system(f"adb  shell input tap {x} {y}")
    except:
        print("tap error!")
    time.sleep(2)

def back():
    try:
        os.system("adb  shell input keyevent KEYCODE_BACK")
    except:
        print("back error!")
    time.sleep(2)

def text(input_str):
    input_str = input_str.replace(" ", "%s")
    input_str = input_str.replace("'", "")
    try:
        os.system(f"adb shell am broadcast -a ADB_INPUT_TEXT --es msg '{input_str}'")
    except:
        print("text error!")
    time.sleep(2)

def long_press(self, x, y, duration=1000):
    try:
        os.system(f"adb shell input swipe {x} {y} {x} {y} {duration}")
    except:
        print("long press error!")
    time.sleep(2)

def swipe(x, y, direction, width,dist="medium"):
    unit_dist = int(width / 10)
    if dist == "long":
        unit_dist *= 3
    elif dist == "medium":
        unit_dist *= 2
    if direction == "up":
        offset = 0, -2 * unit_dist
    elif direction == "down":
        offset = 0, 2 * unit_dist
    elif direction == "left":
        offset = -1 * unit_dist, 0
    elif direction == "right":
        offset = unit_dist, 0
    else:
        return "ERROR"
    duration = 100
    try:
        os.system(f"adb shell input swipe {x} {y} {x+offset[0]} {y+offset[1]} {duration}")
    except:
        print("swipe error!")
    time.sleep(2)


def get_device_size():
    adb_command = f"adb shell wm size"
    result = subprocess.run(adb_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result = result.stdout.strip()
    return map(int, result.split(": ")[2].split("x"))

if __name__ == "__main__":
    swipe(540,1200,"up",1080)
