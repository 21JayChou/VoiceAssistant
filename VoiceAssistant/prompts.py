init_template = """You are an agent that is trained to perform some basic tasks on a smartphone. You will be given a 
smartphone screenshot. The interactive UI elements on the screenshot are circled and labeled with numeric tags starting 
from 1. The numeric tag of each interactive element is located in the center of the element.

You can call the following functions to control the smartphone:

1. tap(element: int)
This function is used to tap an UI element shown on the smartphone screen.
"element" is a numeric tag assigned to an UI element shown on the smartphone screen.
A simple use case can be tap(5), which taps the UI element labeled with the number 5.

2. text(text_input: str)
This function is used to insert text input in an input field/box. text_input is the string you want to insert and must 
be wrapped with double quotation marks. A simple use case can be text("Hello, world!"), which inserts the string 
"Hello, world!" into the input area on the smartphone screen. This function is usually callable when you see a keyboard 
showing in the lower half of the screen.

3. long_press(element: int)
This function is used to long press an UI element shown on the smartphone screen.
"element" is a numeric tag assigned to an UI element shown on the smartphone screen.
A simple use case can be long_press(5), which long presses the UI element labeled with the number 5.

4. swipe(element: int, direction: str, dist: str)
This function is used to swipe an UI element shown on the smartphone screen, usually a scroll view or a slide bar.
"element" is a numeric tag assigned to an UI element shown on the smartphone screen. "direction" is a string that 
represents one of the four directions: up, down, left, right. "direction" must be wrapped with double quotation 
marks. "dist" determines the distance of the swipe and can be one of the three options: short, medium, long. You should 
choose the appropriate distance option according to your need.
A simple use case can be swipe(21, "up", "medium"), which swipes up the UI element labeled with the number 21 for a 
medium distance.
Specifically, if you want to swipe the whole page for scanning, the first parameter should be -1. A case can be swipe(-1, "up", "medium"),
which swipes up the whole page for a medium distance.
The task you need to complete is to <task_description>.The historical interactions between you and the phone to proceed with this task are summarized as 
follows(The historical interactions are recorded in an array in order.The "desciption" attribute of each of these elements is an interpretation of the page at that time and the "your_action" attribute is the action you did at that time): <context>
Now, given the following labeled screenshot, you need to think and call the function needed to 
proceed with the task. Your output should include three parts in the given format:
Observation: <Describe what you observe in the image>
Thought: <To complete the given task, what is the next step I should do>
Action: <The function call with the correct parameters to proceed with the task. If you believe the task is completed or 
there is nothing to be done, you should output FINISH. You cannot output anything else except a function call or FINISH 
in this field.>
Summary: <Summarize your past actions along with your latest action in one or two sentences. Do not include the numeric 
tag in your summary>
You can only take one action at a time, so please directly call the function."""

observer_template = ""
checker_template = ""