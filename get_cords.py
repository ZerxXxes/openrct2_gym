import subprocess
import time

def get_mouse_position():
    try:
        output = subprocess.check_output(['xdotool', 'getmouselocation']).decode()
        x = int(output.split()[0].split(':')[1])
        y = int(output.split()[1].split(':')[1])
        return x, y
    except subprocess.CalledProcessError:
        print("Error: Unable to get mouse position. Make sure xdotool is installed.")
        return None

# Test the function
print("Move your mouse. Position will be printed every second.")
for _ in range(10000):
    position = get_mouse_position()
    if position:
        print(f"Mouse position: {position}")
    time.sleep(1)
