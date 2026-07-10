import pygame
import os
import sys
import time

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
STATE_FILE  = os.path.join(BASE_DIR, "ace_state.txt")

ANIM_FPS    = 16
BLINK_PAUSE = 3.5   # seconds between blinks
LOOK_PAUSE  = 4.0   # seconds between looks

STATE_FOLDERS = {
    "idle":      "blink",
    "listening": "blink",
    "thinking":  "look",
    "speaking":  "happy",
}

pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h
screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
pygame.display.set_caption("Ace")
clock = pygame.time.Clock()

screen.fill((0, 0, 0))
font = pygame.font.SysFont("Arial", 32)
screen.blit(font.render("Loading...", True, (180, 180, 180)), (W // 2 - 60, H // 2 - 16))
pygame.display.flip()

def load_folder(folder_name):
    folder = os.path.join(BASE_DIR, folder_name)
    files  = sorted(f for f in os.listdir(folder) if f.lower().endswith('.png'))
    result = []
    for f in files:
        img    = pygame.image.load(os.path.join(folder, f)).convert()
        iw, ih = img.get_size()
        scale  = min(W / iw, H / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        scaled = pygame.transform.smoothscale(img, (nw, nh))
        surf   = pygame.Surface((W, H))
        surf.blit(scaled, ((W - nw) // 2, (H - nh) // 2))
        result.append(surf)
    print(f"  {folder_name}: {len(result)} frames")
    return result

anims = {}
for folder in set(STATE_FOLDERS.values()):
    anims[folder] = load_folder(folder)

print("Ready.")

def get_state():
    try:
        with open(STATE_FILE, "r") as f:
            s = f.read().strip()
        return s if s in STATE_FOLDERS else "idle"
    except Exception:
        return "idle"

def get_folder(state):
    return STATE_FOLDERS.get(state, "blink")

# --- animation state ---
cur_folder  = get_folder(get_state())
frame_idx   = 0
frame_time  = 0.0
# cooldown before next blink/look (start with a natural delay)
cooldown    = 1.5
playing     = False   # True while mid-blink or mid-look
last_poll   = 0.0
last_state  = ""

FRAME_DUR = 1.0 / ANIM_FPS

while True:
    dt = min(clock.tick(60) / 1000.0, 0.05)

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()

    # Poll state every 100ms
    now = time.time()
    if now - last_poll > 0.1:
        new_state  = get_state()
        new_folder = get_folder(new_state)
        if new_folder != cur_folder:
            cur_folder = new_folder
            frame_idx  = 0
            frame_time = 0.0
            playing    = False
            cooldown   = 1.0   # brief pause before first cycle on new state
        last_state = new_state
        last_poll  = now

    frames = anims[cur_folder]

    if cur_folder in ("blink", "look"):
        pause = BLINK_PAUSE if cur_folder == "blink" else LOOK_PAUSE

        if playing:
            frame_time += dt
            if frame_time >= FRAME_DUR:
                frame_time -= FRAME_DUR
                frame_idx  += 1
                if frame_idx >= len(frames):
                    # cycle done — reset to frame 0 and wait
                    frame_idx = 0
                    playing   = False
                    cooldown  = pause
        else:
            cooldown -= dt
            if cooldown <= 0:
                playing    = True
                frame_time = 0.0

    elif cur_folder == "happy":
        # play to last frame then hold
        if frame_idx < len(frames) - 1:
            frame_time += dt
            if frame_time >= FRAME_DUR:
                frame_time -= FRAME_DUR
                frame_idx  += 1

    screen.blit(frames[frame_idx], (0, 0))
    pygame.display.flip()
