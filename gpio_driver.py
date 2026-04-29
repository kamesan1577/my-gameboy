import time
import uinput
from gpiozero import Button

BUTTON_MAP = {
    17: uinput.KEY_UP,
    27: uinput.KEY_DOWN,
    22: uinput.KEY_RETURN,
    23: uinput.KEY_ESCAPE,
}

buttons = {pin: Button(pin) for pin in BUTTON_MAP}
device = uinput.Device(list(BUTTON_MAP.values()))

while True:
    for pin, key in BUTTON_MAP.items():
        device.emit(key, 1 if buttons[pin].is_pressed else 0)
    time.sleep(0.01)
