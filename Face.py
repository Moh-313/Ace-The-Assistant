import pygame
import pygame.gfxdraw
import math
import random
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
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))

BG_COLORS = {
    'idle':      (155, 213, 200),
    'listening': (108, 190, 252),
    'thinking':  (208, 202, 108),
    'speaking':  (102, 218, 148),
    'happy':     (255, 210, 100),
}
BLACK = (22, 22, 22)
WHITE = (255, 255, 255)

def get_state():
    try:
        s = open(os.path.join(BASE_DIR, STATE_FILE)).read().strip()
        return s or 'idle'
    except Exception:
        return 'idle'

def lerp(a, b, t):
    return a + (b - a) * t

# ── Anti-aliased draw helpers ─────────────────────────────────

def aa_circle(surf, color, x, y, r):
    if r < 1:
        return
    pygame.gfxdraw.filled_circle(surf, int(x), int(y), int(r), color)
    pygame.gfxdraw.aacircle(surf, int(x), int(y), int(r), color)

def aa_ellipse(surf, color, x, y, rx, ry):
    if rx < 1 or ry < 1:
        return
    pygame.gfxdraw.filled_ellipse(surf, int(x), int(y), int(rx), int(ry), color)
    pygame.gfxdraw.aaellipse(surf, int(x), int(y), int(rx), int(ry), color)

def aa_arc(surf, color, cx, cy, rx, ry, a0, a1, thickness, steps=100):
    """Smooth thick arc drawn as a filled polygon."""
    hw = thickness / 2.0
    outer, inner = [], []
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps
        ca, sa = math.cos(a), math.sin(a)
        outer.append((cx + (rx + hw) * ca, cy + (ry + hw) * sa))
        inner.append((cx + (rx - hw) * ca, cy + (ry - hw) * sa))
    pts = [(int(p[0]), int(p[1])) for p in outer + list(reversed(inner))]
    if len(pts) >= 3:
        pygame.gfxdraw.filled_polygon(surf, pts, color)
        pygame.gfxdraw.aapolygon(surf, pts, color)

def aa_pill(surf, color, x1, y, x2, half_w):
    """Rounded horizontal line (pill shape)."""
    if x2 <= x1:
        x1, x2 = x2, x1
    hw = int(half_w)
    pygame.draw.rect(surf, color, (x1, y - hw, x2 - x1, hw * 2))
    aa_circle(surf, color, x1, y, hw)
    aa_circle(surf, color, x2, y, hw)

# ── Vignette (pre-built once at startup) ─────────────────────

def make_vignette(W, H, strength=70):
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    edge = int(min(W, H) * 0.22)
    for i in range(edge):
        t = ((edge - i) / edge) ** 2
        a = int(strength * t)
        if a <= 0:
            continue
        c = (0, 0, 0, a)
        pygame.draw.line(surf, c, (0, i),         (W, i))
        pygame.draw.line(surf, c, (0, H - 1 - i), (W, H - 1 - i))
        pygame.draw.line(surf, c, (i, 0),         (i, H))
        pygame.draw.line(surf, c, (W - 1 - i, 0), (W - 1 - i, H))
    return surf

# ── Main ─────────────────────────────────────────────────────

def main():
    print("Preparing display…")
    vignette = make_vignette(W, H)
    print("Ready.")

    state     = 'idle'
    bg        = list(map(float, BG_COLORS['idle']))
    t         = 0.0
    last_read = 0.0

    blink       = 1.0
    blink_phase = 0
    blink_cd    = 2.0 + random.random() * 2.5

    mouth_open  = 0.0
    mouth_curve = 0.8
    pupil_dx    = 0.0
    pupil_dy    = 0.0
    eye_size    = 1.0
    talk_t      = 0.0

    while True:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        t += dt

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

        now = time.time()
        if now - last_read > 0.1:
            state     = get_state()
            last_read = now

        # Background colour lerp
        tgt = BG_COLORS.get(state, BG_COLORS['idle'])
        for i in range(3):
            bg[i] = lerp(bg[i], tgt[i], min(1.0, dt * 4))
        bg_col = tuple(int(x) for x in bg)

        # Blink
        blink_cd -= dt
        if blink_phase == 0 and blink_cd <= 0:
            blink_phase = 1
            blink_cd    = 2.5 + random.random() * 3.5
        if blink_phase == 1:
            blink = max(0.0, blink - dt * 16)
            if blink == 0.0:
                blink_phase = 2
        elif blink_phase == 2:
            blink = min(1.0, blink + dt * 10)
            if blink == 1.0:
                blink_phase = 0
        if state == 'listening':
            blink = min(1.0, blink + dt * 8)

        # Per-state targets
        t_mo = 0.0; t_mc = 0.78; t_pdx = 0.0; t_pdy = 0.0; t_es = 1.0

        if state == 'happy':
            t_mc = 1.0
        elif state == 'listening':
            t_mo = 0.18; t_mc = 0.0; t_es = 1.1
        elif state == 'thinking':
            t_pdx = -0.3; t_pdy = -0.25; t_mc = 0.0
        elif state == 'speaking':
            talk_t += dt * 9
            t_mo = (abs(math.sin(talk_t * 0.71)) * 0.55
                  + abs(math.sin(talk_t * 1.29)) * 0.28
                  + 0.08)
            t_mc = 0.15

        sp          = min(1.0, dt * 10)
        mouth_open  = lerp(mouth_open,  t_mo,  sp * 1.5)
        mouth_curve = lerp(mouth_curve, t_mc,  sp * 0.65)
        pupil_dx    = lerp(pupil_dx,    t_pdx, sp)
        pupil_dy    = lerp(pupil_dy,    t_pdy, sp)
        eye_size    = lerp(eye_size,    t_es,  sp * 0.7)

        # ── Draw ─────────────────────────────────────────────
        screen.fill(bg_col)

        cx, cy = W // 2, H // 2
        R  = min(W, H)
        lw = max(4, int(R * 0.011))

        er      = int(R * 0.056 * eye_size)
        eox     = int(W * 0.135)
        eye_y   = cy - int(H * 0.09)
        mw      = int(W * 0.19)
        mouth_y = cy + int(H * 0.15)

        # Eyes
        for side in [-1, 1]:
            ex = cx + side * eox
            ey = eye_y

            aa_circle(screen, BLACK, ex, ey, er)

            # Eyelid cover (bg colour rectangle clipped to circle area)
            if blink < 0.999:
                cv = int(er * (1 - blink)) + 1
                pygame.draw.rect(screen, bg_col,
                    (ex - er - 2, ey - er - 2,    er * 2 + 4, cv + 1))
                pygame.draw.rect(screen, bg_col,
                    (ex - er - 2, ey + int(er * blink) - 1, er * 2 + 4, cv + 2))

            # White highlight
            if blink > 0.25:
                hx = ex + int(pupil_dx * er * 0.5) - int(er * 0.24)
                hy = ey + int(pupil_dy * er * 0.5) - int(er * 0.22)
                aa_circle(screen, WHITE, hx, hy, max(2, int(er * 0.27)))

        # Mouth
        if mouth_open > 0.04:
            oh = max(4, int(mouth_open * R * 0.1))
            aa_ellipse(screen, BLACK, cx, mouth_y, mw // 2, oh // 2)
        else:
            if mouth_curve > 0.02:
                ry = max(3, int(mouth_curve * mw * 0.38))
                aa_arc(screen, BLACK, cx, mouth_y, mw // 2, ry, 0, math.pi, lw)
            else:
                shift = int(math.sin(t * 1.8) * mw * 0.08) if state == 'thinking' else 0
                aa_pill(screen, BLACK,
                        cx - mw // 3 + shift, mouth_y,
                        cx + mw // 3 + shift, lw // 2)

        screen.blit(vignette, (0, 0))
        pygame.display.flip()

if __name__ == '__main__':
    main()
