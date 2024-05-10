import os
import re
import time
import xml.etree.ElementTree as ET
import subprocess

MIN_DIS = 30


class AndroidElement:
    def __init__(self, bbox):
        self.bbox = bbox
        self.text = ""


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


def none_children_clickable(root:ET.Element):
    for child in root:
        if child.attrib["clickable"] == "true":
            return False
        if not none_children_clickable(child):
            return False
    return True

def converge_text(root:ET.Element, android_element:AndroidElement, pre = None):
    if root.attrib['text'] != "" and root.attrib['text'] != pre:
        android_element.text += root.attrib['text'] + ','
        pre = root.attrib['text']
    if root.attrib['content-desc'] != "" and root.attrib['content-desc'] != pre:
        android_element.text += root.attrib['content-desc'] + ','
        pre = root.attrib['content-desc']

    for child in root:
        converge_text(child, android_element, pre)

def traverse_root(root:ET.Element, elem_list=[]):
    for child in root:
        flag = child.attrib['class'] == "android.widget.FrameLayout"
        if flag and child.attrib["clickable"] == "true" and none_children_clickable(child) or (not flag and child.attrib["clickable"] == "true"):
            bounds = child.attrib["bounds"][1:-1].split("][")
            x1, y1 = map(int, bounds[0].split(","))
            x2, y2 = map(int, bounds[1].split(","))
            if x1 != x2 and y1 != y2:
                android_element = AndroidElement(((x1, y1), (x2, y2)))
                converge_text(child, android_element)
                android_element.text = android_element.text[:-1]
                elem_list.append(android_element)
        traverse_root(child, elem_list)

def traverse_tree(xml_path, elem_list=[], text_function_dic={}):
    root = ET.ElementTree(file=xml_path).getroot()
    traverse_root(root, elem_list)
    for i, elem in enumerate(elem_list):
        # elem.text =  elem.text.replace('\xa0', ' ').replace('\ue608', ' ').replace('\u200b', "")
        elem.text = replace_unicode_escapes(elem.text)
        text_function_dic[str(i+1)] = {'text': elem.text, 'function': ""}


def replace_unicode_escapes(text):
    def replace(match):
        code_point = match.group(1)
        return chr(int(code_point, 16))


    # 替换Unicode转义序列
    text = re.sub(r'\\u([0-9a-fA-F]{4})', replace, text)
    # 替换\xa0
    text = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), text)

    return text

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

def home():
    try:
        os.system("adb  shell input keyevent KEYCODE_HOME")
    except:
        print("home error!")
    time.sleep(2)

def text(input_str):
    input_str = input_str.replace(" ", "%s")
    input_str = input_str.replace("'", "")
    try:
        os.system(f"adb shell am broadcast -a ADB_INPUT_TEXT --es msg '{input_str}'")
    except:
        print("text error!")
    time.sleep(2)

def long_press(x, y, duration=1000):
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

def swipe_precise(start, end, duration=400):
    start_x, start_y = start
    end_x, end_y = end
    try:
        os.system(f"adb shell input swipe { start_x} {start_y} {end_x} {end_y} {duration}")
    except:
        print("swipe error!")
    time.sleep(2)


def get_device_size():
    adb_command = f"adb shell wm size"
    result = subprocess.run(adb_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result = result.stdout.strip()
    return map(int, result.split(": ")[2].split("x"))

if __name__ == "__main__":
    elem_list = []
    text_function_dict = {}
    traverse_tree('./xml/domtree_2.xml',elem_list, text_function_dict)
    print(str(text_function_dict))
