"""watch_play.py: the playing brain live (D48): a quiet spell in which nothing tastes of anything, then food and poison from a moment
the brain isn't told; a lopsided body (each thruster a half to twice). The brain plays random rhythms until play's best guess of each
motor's effect clearly beats its rival (bored when certain), or until the first taste; a motor still in doubt hands its rival to taste.

    .venv/bin/python lab/watch_play.py [--seed 92001] [--arm partners:beats:certainmover] [--speed 8] [--record FILE.mp4]

Keys, as creature.py's live view: space pause, Up / Down speed, r a new life (next seed), Esc quit. Watching only: nothing here feeds back to the brain.
Colours (Okabe-Ito) always paired with a shape: food a filled circle, poison a square with a cross; a thruster firing a flame with its
motor's number."""
import argparse
import math
import os
import subprocess
import sys
import tempfile
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np

import stage3_random as R

ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int, default=92001)
ap.add_argument("--arm", default="partners:beats:certainmover")
ap.add_argument("--speed", type=float, default=8.0)
ap.add_argument("--record")
ap.add_argument("--seconds", type=float, default=900.0)
a = ap.parse_args()

R._init(0.0025, False)
import play3 as P3
import play4  # noqa: F401  (sets play3's world: the quiet spell, then the challenge)
import play2 as P2
from stage2_lang.sim import WLife

if a.record:
    os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

W = 600                                         # px: the arena (the world's 60 mm torus)
PANEL = 560
H = 640
ORANGE, BLUE, YELLOW, GREY, WHITE, BLACK = (230, 159, 0), (0, 114, 178), (240, 228, 66), (150, 150, 150), (235, 235, 235), (20, 20, 20)
SKY, GREEN, VERM = (86, 180, 233), (0, 158, 115), (213, 94, 0)
FPS = 30


def new_life(seed):
    lf = P3.make(a.arm, seed, ("red", "blue")[seed % 2])
    k = {lf.wire_m[th]: g for th, g in ((0, lf.v_a), (1, lf.v_b))}
    return lf, math.log(k[1] / k[0]), k


def main():
    pygame.init()
    screen = pygame.display.set_mode((W + PANEL, H))
    pygame.display.set_caption("the playing brain: play first, the challenge later")
    font, small, big = pygame.font.SysFont("dejavusans", 16), pygame.font.SysFont("dejavusans", 13), pygame.font.SysFont("dejavusans", 19, bold=True)
    clock = pygame.time.Clock()
    seed = a.seed
    lf, right, kk = new_life(seed)
    speed, paused = a.speed, False
    fire_glow = {0: 0, 1: 0}
    frames = tempfile.mkdtemp() if a.record else None
    nframe = 0
    trail = []
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_q)):
                pygame.quit()
                return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    paused = not paused
                elif e.key in (pygame.K_UP, pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    speed = min(64.0, speed * 2)
                elif e.key in (pygame.K_DOWN, pygame.K_MINUS, pygame.K_KP_MINUS):
                    speed = max(0.25, speed / 2)
                elif e.key in (pygame.K_r, pygame.K_n):
                    seed += 1
                    lf, right, kk = new_life(seed)
                    trail = []
        if not paused:
            n = max(1, int(round(speed / FPS / lf.dt)))
            for _ in range(n):
                lf.step()
                for m, _at in getattr(lf.brain, "beats", None) or []:
                    fire_glow[m] = 4
                if lf.t * lf.dt >= a.seconds:
                    break
            trail.append(tuple(lf.body.pos))
            trail = trail[-400:]
        t = lf.t * lf.dt
        b = lf.brain
        draw(screen, lf, b, t, right, kk, fire_glow, trail, speed, paused, seed, font, small, big)
        for m in fire_glow:
            fire_glow[m] = max(0, fire_glow[m] - 1)
        pygame.display.flip()
        if frames:
            pygame.image.save(screen, os.path.join(frames, f"f{nframe:05d}.png"))
            nframe += 1
            if t >= a.seconds:
                subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(frames, "f%05d.png"),
                                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "28", a.record], check=True)
                print("written", a.record)
                return
        else:
            clock.tick(FPS)


def px(p):
    """World (m, a torus of side lf_world) to the arena's pixels, y upward."""
    x, y = p[0] % lf_world, p[1] % lf_world
    return int(x / lf_world * W), int((lf_world - y) / lf_world * W)


def draw(screen, lf, b, t, right, kk, glow, trail, speed, paused, seed, font, small, big):
    global lf_world
    lf_world = lf.WORLD
    screen.fill(BLACK)
    pygame.draw.rect(screen, (35, 35, 35), (0, 0, W, W))
    body = lf.body
    poison = lf.first                                   # the colour that is poison this life (at the challenge)
    food_on = t >= lf.v_q
    # blocks
    for i in range(len(body.xy)):
        if not body.alive[i]:
            continue
        x, y = px(body.xy[i])
        r = max(3, int(lf.BLOCK / lf.WORLD * W))
        colour = VERM if body.kind[i] == 0 else BLUE
        bad = ("red", "blue")[body.kind[i]] == poison
        if not food_on:
            pygame.draw.circle(screen, colour, (x, y), r, 2) if not bad else pygame.draw.rect(screen, colour, (x - r, y - r, 2 * r, 2 * r), 2)
        elif bad:
            pygame.draw.rect(screen, colour, (x - r, y - r, 2 * r, 2 * r))
            pygame.draw.line(screen, BLACK, (x - r, y - r), (x + r, y + r), 2)
            pygame.draw.line(screen, BLACK, (x - r, y + r), (x + r, y - r), 2)
        else:
            pygame.draw.circle(screen, colour, (x, y), r)
    # trail
    for i in range(1, len(trail)):
        p0, p1 = px(trail[i - 1]), px(trail[i])
        if abs(p0[0] - p1[0]) < W / 2 and abs(p0[1] - p1[1]) < W / 2:
            pygame.draw.line(screen, (70, 70, 70), p0, p1, 1)
    # the creature
    h = body.heading
    f = np.array([math.cos(h), math.sin(h)])
    side = np.array([f[1], -f[0]])
    c = px(body.pos)
    scale = W / lf.WORLD

    def rel(v):                                         # a point of the creature, drawn from its own centre (no wrap across the arena)
        d = v - body.pos
        return int(c[0] + d[0] * scale), int(c[1] - d[1] * scale)
    rad = int(lf.RADIUS * scale)
    mouth = body.pos + f * lf.RADIUS
    for s in (-1, 1):                                   # the eyes' corridor
        a0 = mouth + side * s * lf.EAT
        pygame.draw.line(screen, (90, 90, 60), rel(a0), rel(a0 + f * lf.RANGE), 1)
    pygame.draw.circle(screen, WHITE, c, rad, 2)
    pygame.draw.line(screen, WHITE, c, rel(mouth), 2)
    for th, ang in ((0, 2 * math.pi / 3), (1, -2 * math.pi / 3)):
        m = lf.wire_m[th]
        pos = body.pos + lf.RADIUS * np.array([math.cos(h + ang), math.sin(h + ang)])
        q = rel(pos)
        if glow[m]:
            pygame.draw.line(screen, YELLOW, q, rel(pos - f * lf.RADIUS * 0.9), 5)
        pygame.draw.circle(screen, YELLOW if glow[m] else GREY, q, 4)
        screen.blit(small.render(str(m), True, WHITE), (q[0] + 5, q[1] - 7))
    # the panel
    x0, y = W + 16, 12

    def text(s, colour=WHITE, f=font, dy=22):
        nonlocal y
        screen.blit(f.render(s, True, colour), (x0, y))
        y += dy
    text(f"t = {t:6.1f} s    speed x{speed:g}{'   PAUSED' if paused else ''}    life {seed}", f=font)
    if food_on:
        text(f"WORLD: food and poison since {lf.v_q:.0f} s", ORANGE, big, 28)
    else:
        text("WORLD: quiet (nothing tastes of anything)", GREY, big, 28)
    text("(the brain isn't told when food will begin)", GREY, small, 24)
    if b.playing:
        u = P2.UNITS[b.cur] if b.cur is not None else None
        text(f"BRAIN: PLAYING ({t:.0f} s so far)", SKY, big, 26)
        if u:
            P, D, Rt, w, v = u
            text(f"unit {b.cur}: a {P:.1f} s rhythm, {Rt:.0f} beats/s", SKY, small, 18)
            text(f"  part 1: motor 0 x{w[0]:.2f}, motor 1 x{w[1]:.2f};  part 2: x{v[0]:.2f}, x{v[1]:.2f}", SKY, small, 26)
    elif b.trials:
        text("BRAIN: TASTE TRIES PLAY'S GUESSES", ORANGE, big, 26)
        text(f"trying balance {b.trials[0]:+.2f}; {len(b.trials) - 1} left; tallies so far: "
             + ", ".join(f"{k:+.2f}: {v:+.0f}" for k, v in b.tally.items()), ORANGE, small, 26)
    else:
        text("BRAIN: FORAGING", GREEN, big, 26)
        text(f"play ended at {b.play_end:.0f} s" + (" (bored: sure)" if b.play_end and b.play_end < lf.v_q - 1 else " (food came)"),
             GREEN, small, 26)
    # each motor's record
    text("What play has learned, each motor's own record:", WHITE, font, 24)
    lN = getattr(b, "_lN", None)
    for m in (0, 1):
        true_beats = 2 * math.pi / (lf.TURN / lf.DRAG * kk[m])
        if lN and lN[m] is not None:
            best, riv, mg = lN[m]
            text(f" motor {m}: a turn every {math.exp(best):.1f} beats (rival {math.exp(riv):.1f}); true {true_beats:.1f}", WHITE, small, 18)
            frac = max(0.0, min(1.0, mg / (2 * P3.SURE)))
            pygame.draw.rect(screen, (60, 60, 60), (x0 + 12, y, 300, 12))
            pygame.draw.rect(screen, GREEN if mg >= P3.SURE else SKY, (x0 + 12, y, int(300 * frac), 12))
            pygame.draw.line(screen, WHITE, (x0 + 162, y - 3), (x0 + 162, y + 15), 2)
            screen.blit(small.render(f"certainty {mg:.1f}  (sure at {P3.SURE:g}, the white line)", True, WHITE), (x0 + 12, y + 14))
            y += 36
        else:
            text(f" motor {m}: no record yet (no run of this motor alone)", GREY, small, 22)
    y += 4
    g = b.forager.p
    knob = math.log(g["g0"] / g["g1"]) if g.get("g1") else 0.0
    text("The balance knob (log of motor 0's rate over motor 1's):", WHITE, font, 22)
    text(f"  now {knob:+.2f}    right for this body {right:+.2f}   ({'off by %.2f' % abs(knob - right)})", YELLOW if abs(knob - right) < .2 else WHITE, font, 28)
    # the score since the challenge began
    if food_on:
        lo = lf.v_q / lf.dt
        good = sum(am for tt, bad, am in lf.scored if tt >= lo and not bad)
        badm = sum(am for tt, bad, am in lf.scored if tt >= lo and bad)
        text(f"Since food began: {good:.0f} food, {badm:.0f} poison", WHITE, font, 22)
    y = H - 70
    text("food: filled circle;  poison: square with a cross;  hollow: before food begins", GREY, small, 18)
    text("thruster firing: yellow flame, with the motor it is wired to", GREY, small, 18)
    text("keys (as creature.py): space pause, Up / Down speed, r next life, Esc quit", GREY, small, 18)


lf_world = 0.06
if __name__ == "__main__":
    main()
