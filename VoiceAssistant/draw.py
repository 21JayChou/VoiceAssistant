import cv2
import numpy as np
import pyshine as ps
import controller


def get_background_color(img):
    # 将图像转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 计算直方图
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

    # 获取直方图中灰度值最大的索引（即背景色）
    background_color_index = np.argmax(hist)

    # 将灰度值转换为RGB颜色
    background_color = (background_color_index, background_color_index, background_color_index)

    return background_color


def is_dark_color(rgb_color, threshold=0):
    # 计算灰度值
    gray = np.dot(rgb_color, [0.2989, 0.587, 0.114])
    # 判断灰度值是否小于阈值
    return gray < threshold


def draw_bbox_multi(img_path, elem_list, output_path, specific=[]):
    img = cv2.imread(img_path)
    count = 1
    for i, elem in enumerate(elem_list):
        if len(specific) and i not in specific:
            continue
        left, top = elem.bbox[0][0], elem.bbox[0][1]
        right, bottom = elem.bbox[1][0], elem.bbox[1][1]
        crop_image = img[top:bottom + 1, left:right+1]
        # dark = is_dark_color(get_background_color(crop_image))
        dark = False
        text_color = (10, 10, 10) if dark else (255, 250, 250)
        bg_color = (255, 250, 250) if dark else (10, 10, 10)
        cv2.rectangle(img, (left, top), (right, bottom), bg_color, 2)
        label = str(count)
        if not len(specific):
            img = ps.putBText(img, label, text_offset_x=left+5,
                          text_offset_y=top+5,
                          vspace=5, hspace=5, font_scale=0.5, thickness=1, background_RGB=bg_color,
                          text_RGB=text_color, alpha=0.3)
        count += 1
    cv2.imwrite(output_path, img)

def draw_grid(img_path, output_path):
    def get_unit_len(n):
        for i in range(1, n + 1):
            if n % i == 0 and 120 <= i <= 180:
                return i
        return -1

    image = cv2.imread(img_path)
    height, width, _ = image.shape
    color = (255, 116, 113)
    unit_height = get_unit_len(height)
    if unit_height < 0:
        unit_height = 120
    unit_width = get_unit_len(width)
    if unit_width < 0:
        unit_width = 120
    thick = int(unit_width // 50)
    rows = height // unit_height
    cols = width // unit_width
    for i in range(rows):
        for j in range(cols):
            label = i * cols + j + 1
            left = int(j * unit_width)
            top = int(i * unit_height)
            right = int((j + 1) * unit_width)
            bottom = int((i + 1) * unit_height)
            cv2.rectangle(image, (left, top), (right, bottom), color, thick // 2)
            cv2.putText(image, str(label), (left + int(unit_width * 0.05) + 3, top + int(unit_height * 0.3) + 3), 0,
                        int(0.01 * unit_width), (0, 0, 0), thick)
            cv2.putText(image, str(label), (left + int(unit_width * 0.05), top + int(unit_height * 0.3)), 0,
                        int(0.01 * unit_width), color, thick)
    cv2.imwrite(output_path, image)
    return rows, cols


if __name__ == "__main__":
    img_path = controller.get_screenshot("screen.png")
    xml_path = controller.get_domtree(f"domtree.xml")
    clickable_list = []
    text_function_dic = {}
    controller.traverse_tree(xml_path, clickable_list, text_function_dic)
    draw_bbox_multi(img_path, clickable_list, f"./labeled/labeled.png")
    print(str(text_function_dic))