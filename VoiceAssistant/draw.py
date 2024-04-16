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


def draw_bbox_multi(img_path, elem_list, output_path):
    img = cv2.imread(img_path)
    count = 1
    for elem in elem_list:
        left, top = elem.bbox[0][0], elem.bbox[0][1]
        right, bottom = elem.bbox[1][0], elem.bbox[1][1]
        crop_image = img[top:bottom + 1, left:right+1]
        dark = is_dark_color(get_background_color(crop_image))
        text_color = (10, 10, 10) if dark else (255, 250, 250)
        bg_color = (255, 250, 250) if dark else (10, 10, 10)
        cv2.rectangle(img, (left, top), (right, bottom), bg_color, 2)
        label = str(count)
        img = ps.putBText(img, label, text_offset_x=left+5,
                          text_offset_y=top+5,
                          vspace=5, hspace=5, font_scale=0.5, thickness=1, background_RGB=bg_color,
                          text_RGB=text_color, alpha=0.3)
        count += 1
    cv2.imwrite(output_path, img)

elem_list = []
controller.traverse_tree("./xml/domtree.xml", elem_list, "clickable")
draw_bbox_multi("./screenshots/screen.png", elem_list, "./labeled/labeled.png")