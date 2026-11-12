"""drive.py: drive the creature by hand, to feel a body's tuning (the user, 2026-11-11). "." pulses the left thruster (which turns the
creature right), "," the right one (turning it left); a press fires one pulse at once, and a key held longer than HOLD fires at REPEAT
pulses a second, on one clock shared by both keys, so both held drive straight (keys scanned each tick, not the keyboard's repeat). b switches the body between the muscle-like one (lab/sigmoid_body.py) and
world.py's; r a new world; Up / Down speed (real time by default); space pause; Esc quit.

    .venv/bin/python lab/drive.py [--seed 0] [--body sigmoid|world]

The panel shows each thruster's activation and thrust (the muscle-like body), the speed and turning, and the eyes: how strongly each
sees its colour now, with a flash at each eye pulse. Blocks: one colour a filled circle, the other a square (here nothing is food or
poison: this is for feeling the body)."""
import argparse
import math
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import pygame

import world
import sigmoid_body as SB
from units import TICK

ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--body", default="sigmoid")
a = ap.parse_args()

W, PANEL, H = 640, 600, 640
REPEAT = 50                                     # pulses a second while a key is held ...
HOLD = 0.15                                     # s: ... once it has been held this long
KEYS = {pygame.K_PERIOD: "left", pygame.K_COMMA: "right"}   # the right-hand key fires the left thruster, which turns the creature right
ORANGE, BLUE, YELLOW, GREY, WHITE, BLACK, SKY, GREEN = (230, 159, 0), (0, 114, 178), (240, 228, 66), (150, 150, 150), (235, 235, 235), (20, 20, 20), (86, 180, 233), (0, 158, 115)


def make_body(seed, kind):
    b = world.Body(np.random.default_rng(seed))
    if kind == "sigmoid":
        b.__class__ = SB.SigmoidBody
        b.act = {"left": 0.0, "right": 0.0}
    return b


def switch(b, kind):
    if kind == "sigmoid":
        b.__class__ = SB.SigmoidBody
        b.act = {"left": 0.0, "right": 0.0}
    else:
        b.__class__ = world.Body
    return b


def main():
    pygame.init()
    screen = pygame.display.set_mode((W + PANEL, H))
    pygame.display.set_caption("drive the creature: '.' turns right, ',' turns left, both straight")
    font, small, big = pygame.font.SysFont("dejavusans", 16), pygame.font.SysFont("dejavusans", 13), pygame.font.SysFont("dejavusans", 19, bold=True)
    clock = pygame.time.Clock()
    seed, kind = a.seed, a.body
    body = make_body(seed, kind)
    rng = np.random.default_rng(seed + 1)
    speed, paused, t = 1.0, False, 0.0
    flash = {c: 0 for c in world.COLOURS}
    glow = {"left": 0, "right": 0}
    pulses = {"left": 0, "right": 0}
    eaten = {c: 0 for c in world.COLOURS}
    trail = []
    queued = []
    down = {}                                           # thruster -> sim time its key went down
    next_clock = 0.0                                    # the shared repeat clock
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                return
            if e.type == pygame.KEYDOWN:
                if e.key in KEYS:
                    queued.append(KEYS[e.key])          # a press: one pulse at once
                    down[KEYS[e.key]] = t
                elif e.key == pygame.K_SPACE:
                    paused = not paused
                elif e.key == pygame.K_UP:
                    speed = min(8.0, speed * 2)
                elif e.key == pygame.K_DOWN:
                    speed = max(0.125, speed / 2)
                elif e.key == pygame.K_b:
                    kind = "world" if kind == "sigmoid" else "sigmoid"
                    body = switch(body, kind)
                elif e.key == pygame.K_r:
                    seed += 1
                    body = make_body(seed, kind)
                    trail, eaten = [], {c: 0 for c in world.COLOURS}
        pressed = pygame.key.get_pressed()
        for k, th in KEYS.items():
            if not pressed[k]:
                down.pop(th, None)
        if not paused:
            ticks = max(1, int(round(speed / 60 / TICK)))
            for i in range(ticks):
                if t >= next_clock:                     # the shared clock: every held key fires together
                    next_clock = t + 1.0 / REPEAT
                    for th, t0 in down.items():
                        if t - t0 >= HOLD:
                            queued.append(th)
                for th in queued:
                    body.fire(th)
                    glow[th] = 6
                    pulses[th] += 1
                queued = []
                for c in body.move():
                    eaten[c] += 1
                for c, v in body.sees().items():
                    if rng.random() < world.SENSE * v * TICK:
                        flash[c] = 8
                t += TICK
            trail.append(tuple(body.pos))
            trail = trail[-600:]
        draw(screen, body, kind, t, speed, paused, seed, glow, flash, pulses, eaten, trail, font, small, big)
        for d in (glow, flash):
            for k in d:
                d[k] = max(0, d[k] - 1)
        pygame.display.flip()
        clock.tick(60)


def px(p):
    x, y = p[0] % world.WORLD, p[1] % world.WORLD
    return int(x / world.WORLD * W), int((world.WORLD - y) / world.WORLD * W)


def draw(screen, body, kind, t, speed, paused, seed, glow, flash, pulses, eaten, trail, font, small, big):
    screen.fill(BLACK)
    pygame.draw.rect(screen, (35, 35, 35), (0, 0, W, W))
    r = max(3, int(world.BLOCK / world.WORLD * W))
    for i in range(len(body.xy)):
        x, y = px(body.xy[i])
        if body.kind[i] == 0:
            pygame.draw.circle(screen, ORANGE, (x, y), r)
        else:
            pygame.draw.rect(screen, BLUE, (x - r, y - r, 2 * r, 2 * r))
    for i in range(1, len(trail)):
        p0, p1 = px(trail[i - 1]), px(trail[i])
        if abs(p0[0] - p1[0]) < W / 2 and abs(p0[1] - p1[1]) < W / 2:
            pygame.draw.line(screen, (75, 75, 75), p0, p1, 1)
    c = px(body.pos)
    sc = W / world.WORLD
    f = body.forward()
    side = np.array([f[1], -f[0]])

    def rel(v):
        d = v - body.pos
        return int(c[0] + d[0] * sc), int(c[1] - d[1] * sc)
    mouth = body.pos + f * world.RADIUS
    for s in (-1, 1):
        a0 = mouth + side * s * world.EAT
        pygame.draw.line(screen, (90, 90, 60), rel(a0), rel(a0 + f * world.RANGE), 1)
    pygame.draw.circle(screen, WHITE, c, int(world.RADIUS * sc), 2)
    pygame.draw.line(screen, WHITE, c, rel(mouth), 2)
    for th, pos in zip(world.THRUSTERS, body.thrusters()):
        on = glow[th] or (kind == "sigmoid" and body.thrust(th) > 0.05)
        q = rel(pos)
        if on:
            pygame.draw.line(screen, YELLOW, q, rel(pos - f * world.RADIUS * 0.9), 5)
        pygame.draw.circle(screen, YELLOW if on else GREY, q, 5)
        screen.blit(small.render("." if th == "left" else ",", True, WHITE), (q[0] + 6, q[1] - 8))
    x0, y = W + 16, 12

    def text(s, colour=WHITE, f=font, dy=22):
        nonlocal y
        screen.blit(f.render(s, True, colour), (x0, y))
        y += dy
    text(f"t {t:6.1f} s   speed x{speed:g}{'   PAUSED' if paused else ''}   world {seed}")
    text("BODY: " + ("muscle-like thrusters (sigmoid)" if kind == "sigmoid" else "world.py's (a fixed kick a pulse)"), SKY, big, 30)
    text("'.' fires the left thruster (turns right), ',' the right (turns left); hold for a burst", GREY, small, 24)
    for th in world.THRUSTERS:
        text(f"{th} thruster ('{'.' if th == 'left' else ','}'): {pulses[th]} pulses", WHITE, font, 20)
        if kind == "sigmoid":
            act, thr = body.act[th], body.thrust(th)
            pygame.draw.rect(screen, (60, 60, 60), (x0 + 10, y, 300, 12))
            pygame.draw.rect(screen, SKY, (x0 + 10, y, int(300 * min(1.0, act / 5)), 12))
            screen.blit(small.render(f"activation {act:4.2f}", True, WHITE), (x0 + 320, y - 2))
            y += 16
            pygame.draw.rect(screen, (60, 60, 60), (x0 + 10, y, 300, 12))
            pygame.draw.rect(screen, YELLOW, (x0 + 10, y, int(300 * thr), 12))
            screen.blit(small.render(f"thrust {thr:4.0%}", True, WHITE), (x0 + 320, y - 2))
            y += 24
        else:
            y += 6
    v = float(body.speed @ f) * 1000
    text(f"forward speed {v:6.1f} mm/s    turning {math.degrees(body.spin):7.1f} deg/s", WHITE, font, 28)
    text("The eyes (each sees one colour, down the corridor ahead):", WHITE, font, 22)
    seen = body.sees()
    for col, colour, shape in (("red", ORANGE, "circles"), ("blue", BLUE, "squares")):
        pygame.draw.rect(screen, (60, 60, 60), (x0 + 10, y, 200, 12))
        pygame.draw.rect(screen, colour, (x0 + 10, y, int(200 * seen[col]), 12))
        if flash[col]:
            pygame.draw.circle(screen, WHITE, (x0 + 225, y + 6), 6)
        screen.blit(small.render(f"{shape}: {seen[col]:.2f}" + ("  pulse" if flash[col] else ""), True, WHITE), (x0 + 240, y - 2))
        y += 22
    text(f"eaten: {eaten['red']} circles, {eaten['blue']} squares", WHITE, font, 28)
    y = H - 90
    text("one pulse turns: muscle-like about 4 deg; world.py's about 23 deg", GREY, small, 18)
    text("keys: . turn right  , turn left  (hold: a burst at 50 a second; both: straight)   b body   r new world", GREY, small, 18)
    text("Up / Down speed   space pause   Esc quit", GREY, small, 18)


if __name__ == "__main__":
    main()
