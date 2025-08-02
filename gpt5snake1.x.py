import os
import pygame as pg
import random
import numpy as np
import sys

# ---- PS2 SNAKE – Universal Beep, CRT Vibes ----
GRID, TILE = 16, 28
W, H = GRID * TILE, GRID * TILE
FPS = 60

# Colors: Washed-out PS2 palette
BG     = (54, 60, 96)
GRID_C = (68, 72, 128)
SNAKE  = (212, 208, 176)
HEAD   = (240, 244, 120)
FOOD   = (255, 136, 64)
SHADOW = (40, 36, 64, 68)
TXT    = (208, 224, 236)

# --- Pygame Init ---
os.environ["SDL_VIDEODRIVER"] = "windows" if sys.platform == "win32" else "x11"
pg.init()
pg.mixer.quit()
pg.mixer.init(frequency=22050, size=-16, channels=1, buffer=128)
screen = pg.display.set_mode((W, H))
pg.display.set_caption("PS2 SNAKE – OG Vibes")
font = pg.font.SysFont("monaco", 36, bold=True)
clock = pg.time.Clock()

# --- Universal PS2 Beep (Mono/Stereo Safe) ---
def beep(freq=410, ms=150, vol=0.22, pan=0.0):
    """
    freq = Hz, ms = duration, vol = volume (0.0 - 1.0), pan=-1(left) to 1(right)
    Handles mono or stereo mixer auto-magically.
    """
    rate, size, chans = pg.mixer.get_init()
    n = int(rate * ms / 1000)
    t = np.linspace(0, ms/1000, n, False)
    base = np.sin(2 * np.pi * freq * t) * vol
    crunchy = np.sign(base) * (0.19 + 0.81 * base)
    wave = (base * 0.72 + crunchy * 0.22 + np.random.uniform(-0.09,0.09,n)*0.15)
    audio = np.int16(wave * 32767)
    if chans == 2:
        # Simple stereo pan law
        left = audio * ((1 - pan) / 2)
        right = audio * ((1 + pan) / 2)
        audio = np.column_stack((left.astype(np.int16), right.astype(np.int16)))
    sound = pg.sndarray.make_sound(audio)
    sound.play(maxtime=ms)

# --- Game State ---
snake = [(GRID//2, GRID//2)]
dx, dy = 0, -1
food = (random.randint(0, GRID-1), random.randint(0, GRID-1))
score = 0
game_over = False
dir_buf = []
timer = 0

def draw_crt():
    for y in range(0, H, 3):
        pg.draw.line(screen, (34,32,44), (0,y), (W,y), 1)
    overlay = pg.Surface((W,H), pg.SRCALPHA)
    overlay.fill((40,30,90,12))
    screen.blit(overlay, (0,0), special_flags=pg.BLEND_RGBA_ADD)

def draw_shadow(rect, amt=6):
    surf = pg.Surface((rect[2]+amt*2, rect[3]+amt*2), pg.SRCALPHA)
    pg.draw.ellipse(surf, SHADOW, (0,0,rect[2]+amt*2, rect[3]+amt*2))
    screen.blit(surf, (rect[0]-amt, rect[1]-amt//2))

def draw():
    screen.fill(BG)
    for x in range(0, W, TILE):
        pg.draw.line(screen, GRID_C, (x,0), (x,H), 1)
    for y in range(0, H, TILE):
        pg.draw.line(screen, GRID_C, (0,y), (W,y), 1)
    # Food + shadow
    f_rect = (food[0]*TILE+7, food[1]*TILE+7, TILE-14, TILE-14)
    draw_shadow(f_rect, 7)
    pg.draw.rect(screen, FOOD, f_rect, border_radius=8)
    # Snake + shadows
    for i, (x,y) in enumerate(snake):
        rect = (x*TILE+2, y*TILE+2, TILE-4, TILE-4)
        if i == 0:
            draw_shadow(rect, 9)
            pg.draw.rect(screen, HEAD, rect, border_radius=6)
        else:
            draw_shadow(rect, 6)
            pg.draw.rect(screen, SNAKE, rect, border_radius=6)
    # Score
    txt = font.render(f"SCORE: {score}", True, TXT)
    screen.blit(txt, (14, H-44))
    draw_crt()
    if game_over:
        msg = font.render("GAME OVER  (R to Retry)", True, (255,120,120))
        screen.blit(msg, (W//2-msg.get_width()//2, H//2-36))

# --- Main Loop ---
while True:
    clock.tick(FPS)
    timer += 1
    for e in pg.event.get():
        if e.type == pg.QUIT:
            sys.exit()
        if e.type == pg.KEYDOWN:
            if not game_over:
                if e.key == pg.K_UP and dy != 1: dir_buf.append((0, -1))
                if e.key == pg.K_DOWN and dy != -1: dir_buf.append((0, 1))
                if e.key == pg.K_LEFT and dx != 1: dir_buf.append((-1, 0))
                if e.key == pg.K_RIGHT and dx != -1: dir_buf.append((1, 0))
            if game_over and e.key == pg.K_r:
                snake = [(GRID//2, GRID//2)]
                dx, dy = 0, -1
                food = (random.randint(0, GRID-1), random.randint(0, GRID-1))
                score = 0
                game_over = False
                dir_buf.clear()
                continue
    if not game_over and timer % (FPS//9) == 0:
        if dir_buf:
            dx, dy = dir_buf.pop(0)
        head = ((snake[0][0]+dx)%GRID, (snake[0][1]+dy)%GRID)
        if head in snake:
            game_over = True
        else:
            snake.insert(0, head)
            if head == food:
                score += 1
                beep()  # Only beep when eating!
                while True:
                    nf = (random.randint(0, GRID-1), random.randint(0, GRID-1))
                    if nf not in snake:
                        food = nf
                        break
            else:
                snake.pop()
    draw()
    pg.display.flip()
