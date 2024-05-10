import os
import re
import ast
import xml.etree.ElementTree as ET


def replace_unicode_escapes(text):
    def replace(match):
        code_point = match.group(1)
        return chr(int(code_point, 16))

    # 替换Unicode转义序列
    text = re.sub(r'([\u0000-\u00FF])', replace, text)
    text = re.sub(r'([\uFF00-\uFFFF])', replace, text)
    # 替换\xa0
    text = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), text)

    return text
print('\u00b7')