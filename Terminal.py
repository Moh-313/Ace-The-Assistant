import tkinter as tk
import os
import subprocess

try:
    from gpiozero import Button as GPIOButton
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
CMD_FILE  = os.path.join(BASE_DIR, "ace_command.txt")
LANG_FILE = os.path.join(BASE_DIR, "ace_lang.txt")

BTN_UP      = 27   # physical 13-14
BTN_DOWN    = 10   # physical 19-20
BTN_LEFT    = 5    # physical 29-30
BTN_RIGHT   = 3    # physical 5-6  (has hardware pull-up)
BTN_CONFIRM = 13   # physical 33-34

MENU = [
    ("ACM Info",      "acm_info"),
    ("Language: EN",  "lang"),
    ("Start Ace",     "start"),
    ("Stop Ace",      "stop"),
    ("Quit",          "quit"),
]

BG     = "#0a0a0a"
FG_DIM = "#555555"
FG_SEL = "#00aaff"
FG_OUT = "#00ccff"
FONT   = ("Courier", 13)

root = tk.Tk()
root.configure(bg=BG)
root.attributes("-topmost", True)
root.overrideredirect(True)
root.geometry("220x230+0+0")

selected  = 0
lang      = "EN"
ace_procs = []
with open(LANG_FILE, "w") as f:
    f.write("en")

tk.Label(root, text="ACE MENU", fg=FG_SEL, bg=BG,
         font=("Courier", 13, "bold")).pack(pady=(10, 4))
tk.Label(root, text="─" * 18, fg="#222", bg=BG, font=FONT).pack()

labels = []
for label, _ in MENU:
    lbl = tk.Label(root, text="", fg=FG_DIM, bg=BG, font=FONT, anchor="w", padx=12)
    lbl.pack(fill="x", pady=2)
    labels.append(lbl)

output = tk.Label(root, text="", fg=FG_OUT, bg=BG,
                  font=("Courier", 10), wraplength=200, anchor="w", padx=12)
output.pack(fill="x", pady=(4, 0))

def refresh():
    for i, (label, _) in enumerate(MENU):
        text = label if i != 1 else f"Language: {lang}"
        if i == selected:
            labels[i].config(text=f"▶ {text}", fg=FG_SEL)
        else:
            labels[i].config(text=f"  {text}", fg=FG_DIM)

def go_up():
    global selected
    selected = (selected - 1) % len(MENU)
    refresh()

def go_down():
    global selected
    selected = (selected + 1) % len(MENU)
    refresh()

def confirm():
    global lang
    _, cmd = MENU[selected]

    if cmd == "lang":
        lang = "AR" if lang == "EN" else "EN"
        with open(LANG_FILE, "w") as f:
            f.write(lang.lower())
        output.config(text=f"▶ Language: {lang}")
        refresh()

    elif cmd == "start":
        env = os.environ.copy()
        env["DISPLAY"] = ":0"
        ace_procs.clear()
        ace_procs.append(subprocess.Popen(["python", os.path.join(BASE_DIR, "Face.py")], env=env, start_new_session=True))
        ace_procs.append(subprocess.Popen(["python", os.path.join(BASE_DIR, "Ace.py")], start_new_session=True))
        output.config(text="▶ Ace started!")

    elif cmd == "stop":
        for p in ace_procs:
            try:
                p.kill()
            except Exception:
                pass
        ace_procs.clear()
        os.system("pkill -f Face.py; pkill -f Ace.py")
        output.config(text="▶ Ace stopped.")

    elif cmd == "quit":
        root.destroy()
        os._exit(0)

    else:
        label, _ = MENU[selected]
        output.config(text=f"▶ {label}...")
        with open(CMD_FILE, "w") as f:
            f.write(cmd)

refresh()

if GPIO_AVAILABLE:
    try:
        btn_up      = GPIOButton(BTN_UP,     pull_up=True, bounce_time=0.05)
        btn_down    = GPIOButton(BTN_DOWN,   pull_up=True, bounce_time=0.05)
        btn_confirm = GPIOButton(BTN_CONFIRM, pull_up=True, bounce_time=0.05)
        prev = {"up": False, "down": False, "confirm": False}

        def poll_buttons():
            u, d, c = btn_up.is_pressed, btn_down.is_pressed, btn_confirm.is_pressed
            if u and not prev["up"]:      go_up()
            if d and not prev["down"]:    go_down()
            if c and not prev["confirm"]: confirm()
            prev["up"], prev["down"], prev["confirm"] = u, d, c
            root.after(50, poll_buttons)

        poll_buttons()
        print("GPIO ready.")
    except Exception as e:
        print(f"GPIO setup failed: {e} — keyboard active instead")
        GPIO_AVAILABLE = False

if not GPIO_AVAILABLE:
    root.bind("<w>", lambda e: go_up())
    root.bind("<s>", lambda e: go_down())
    root.bind("<Return>", lambda e: confirm())

root.mainloop()
