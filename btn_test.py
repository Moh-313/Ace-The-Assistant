from gpiozero import Button
import time

# Test all your physical pin pairs
PINS = {
    "Physical 5-6":   3,
    "Physical 13-14": 27,
    "Physical 19-20": 10,
    "Physical 29-30": 5,
    "Physical 33-34": 13,
}

buttons = {}
for name, pin in PINS.items():
    try:
        buttons[name] = Button(pin, pull_up=True)
        print(f"OK: {name} -> GPIO {pin}")
    except Exception as e:
        print(f"FAIL: {name} -> GPIO {pin} ({e})")

print("\nPress each button one at a time:")
while True:
    for name, btn in buttons.items():
        if btn.is_pressed:
            print(f"  PRESSED: {name} (GPIO {PINS[name]})")
    time.sleep(0.05)
