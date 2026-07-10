from gpiozero import Button
import time

PINS = {"Up": 17, "Down": 27, "Left": 10, "Right": 13, "Confirm": 22}

buttons = {name: Button(pin, pull_up=True) for name, pin in PINS.items()}

print("Press each button — you should see its name printed. Ctrl+C to stop.")
while True:
    for name, btn in buttons.items():
        if btn.is_pressed:
            print(f"{name} pressed (GPIO {PINS[name]})")
    time.sleep(0.05)
