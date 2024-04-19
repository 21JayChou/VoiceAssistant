import os
import re

last_act = {}
last_act["user"] = "user"
context = []
context.append(last_act)
context.append(last_act)
prompt = "<last_act>"
prompt = re.sub(r"<last_act>", str(context), prompt)
print(prompt)