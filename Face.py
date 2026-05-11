import pygame
import sys
import os
import time

pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
pygame.display.set_caption("Ace")
clock = pygame.time.Clock()

STATE_FILE = "ace_state.txt"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_image(filename):
    path = os.path.join(BASE_DIR, filename)
    img = pygame.image.load(path).convert()
    return pygame.transform.scale(img, (W, H))

img_idle     = load_image("ACE Idle.png")
img_speaking = load_image("ACE Speaking.png")

def get_state():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                return f.read().strip()
    except Exception:
        pass
    return "idle"

def main():
    state = "idle"
    last_read = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

        now = time.time()
        if now - last_read > 0.1:
            state = get_state()
            last_read = now

        screen.blit(img_speaking if state == "speaking" else img_idle, (0, 0))
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
