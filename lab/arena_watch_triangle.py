"""arena_watch.py: watch the arena live (arena.py). Each robot a triangle, its mouth disc red and lettered M, its tail disc
blue and lettered T (colour never the only cue); its belly as a bar and number; a line from mouth to tail it is biting.
Every robot's eyes' rays (key E: every robot's, one robot's, none; Tab: the next robot), each drawn to where it
stops, bright with a ring there if it met a disc, faint if it saw nothing out to the eyes' range; the chosen robot's four sensors' strengths printed below.

    python arena_watch.py [seed] [--n 10] [--kinds told,tracker] [--record DIR --seconds S]
    (space: pause; up/down: speed; E: rays; Tab: next robot; Esc: quit)"""
import argparse
import time
import math
import os
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
from arena import Arena, BELLY, HIT, LEFT, R, TOUCH
import world as W
from units import TICK

SIDE = 760
RED, BLUE = (213, 94, 0), (0, 114, 178)                 # Okabe-Ito vermilion and blue
HIT_RAY, MISS_RAY = (200, 200, 200), (46, 48, 54)      # a ray that met a disc; one that saw nothing


def rays(A, r, angles):
    """Watching only: each of robot r's rays in one eye, as arena._fan casts it: (end point, distance, kind or -1)."""
    others = [d for o in A.robots if o is not r for d in o.discs()]
    xy = np.array([c for c, _ in others])
    kind = np.array([k for _, k in others])
    h = r.body.head()
    out = []
    for a in angles:
        u = np.array([math.cos(r.body.heading + a), math.sin(r.body.heading + a)])
        dv = W.Body.wrap(xy - h)
        t = dv @ u
        e2 = (dv * dv).sum(1) - t * t
        ok = (t > -R) & (e2 < R * R)
        d = np.where(ok, np.maximum(0.0, t - np.sqrt(np.maximum(R * R - e2, 0.0))), W.RANGE)
        b = int(np.argmin(d))
        best, k = (d[b], int(kind[b])) if d[b] < W.RANGE else (W.RANGE, -1)
        out.append((h + best * u, best, k))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seed", nargs="?", type=int, default=0)
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--kinds", default="told,tracker", help="each robot's brain in turn: B, told, tracker, grow")
    ap.add_argument("--grow", default="", help="the grower's settings, e.g. \"knob=1 w0=0\" (grow_escape.py)")
    ap.add_argument("--record")
    ap.add_argument("--seconds", type=float, default=60.0)
    a = ap.parse_args()
    if "grow" in a.kinds.split(","):
        import grow_escape                              # (registers the escape grower as the kind "grow")
        grow_escape.GROW.update({k: float(v) for k, v in (x.split("=") for x in a.grow.split())})
    if a.record:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    global pygame
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((SIDE, SIDE + 84))
    font = pygame.font.SysFont(None, 18)
    big = pygame.font.SysFont(None, 22)
    A = Arena(a.seed, a.n, tuple(a.kinds.split(",")))
    per, paused, frame = 3, False, 0
    got, mark, t0 = 0.0, time.time(), 0.0              # the speed actually reached (the arena may not keep up)
    show, pick = 2, 0                                   # rays: 2 all, 1 one robot's, 0 none

    sc = SIDE / W.WORLD
    clock = pygame.time.Clock()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    paused = not paused
                elif e.key == pygame.K_UP:
                    per = min(per * 2, 4096)                # (4096 a frame: about 1200 x asked)
                elif e.key == pygame.K_DOWN:
                    per = max(per / 2, 1 / 32)
                elif e.key == pygame.K_e:
                    show = (show - 1) % 3
                elif e.key == pygame.K_TAB:
                    pick += 1
        if not paused:
            frame_n = getattr(main, "n", 0) + 1
            main.n = frame_n
            if per >= 1:
                for _ in range(int(per)):
                    A.step()
            elif frame_n % int(round(1 / per)) == 0:
                A.step()
        screen.fill((24, 26, 30))
        def at(r, c):                                   # a point of robot r, drawn beside its centre (not across the wrap)
            p = r.body.pos % W.WORLD + W.Body.wrap(c - r.body.pos)
            return int(p[0] * sc), int(p[1] * sc)

        chosen = A.robots[pick % len(A.robots)]
        sensed = {}
        for r in A.robots:
            if show == 0 or (show == 1 and r is not chosen):
                continue
            hx, hy = at(r, r.body.head())
            for eye, angles in (("left", LEFT), ("right", -LEFT)):
                strength = [0.0, 0.0]
                for end, dist, k in rays(A, r, angles):
                    p = at(r, end)
                    pygame.draw.line(screen, HIT_RAY if k >= 0 else MISS_RAY, (hx, hy), p, 1)
                    if k >= 0:
                        pygame.draw.circle(screen, HIT_RAY, p, 3, 1)
                        strength[k] += HIT / (1 + (dist / W.REACH) ** 2)
                if r is chosen:
                    sensed[eye] = [min(v, 1.0) for v in strength]
        for r in A.robots:
            pts = [at(r, c) for c in r.body.corners()]
            pygame.draw.polygon(screen, (255, 255, 255) if r is chosen and show == 1 else (200, 200, 200), pts,
                                2 if r is chosen and show == 1 else 1)
            for (c, k) in r.discs():
                x, y = at(r, c)
                pygame.draw.circle(screen, RED if k == 0 else BLUE, (x, y), max(3, int(R * sc)))
                screen.blit(font.render("M" if k == 0 else "T", True, (255, 255, 255)), (x - 4, y - 6))
            hx, hy = at(r, r.body.head())
            for o in A.robots:
                if o is not r and np.hypot(*W.Body.wrap(r.body.head() - o.tail())) < TOUCH:
                    tx, ty = at(r, o.tail())
                    pygame.draw.line(screen, (240, 228, 66), (hx, hy), (tx, ty), 3)
            x, y = pts[0]
            w = int(30 * max(r.belly, 0) / BELLY)
            pygame.draw.rect(screen, (230, 159, 0), (x - 15, y - 18, w, 4))
            right = "right" if r.brain.food == r.sensor[("blue", "left")] // 2 else "wrong"
            label = f"grow:{getattr(r.brain, 'kept', '-')}" if r.kind == "grow" else r.kind   # (the response it rates best)
            if hasattr(r.brain, "knobs"):               # the knob recruit: each motor's share of full rate, noise aside
                label += f" {r.brain.knobs[0]:.1f}/{r.brain.knobs[1]:.1f}"
            hurt = " OUCH" if getattr(r.brain, "hurting", False) else ""
            screen.blit(font.render(f"{label} {r.belly:.1f}{hurt}", True, (220, 220, 220)), (x - 15, y - 32))
        pygame.draw.rect(screen, (10, 10, 12), (0, SIDE, SIDE, 84))
        screen.blit(big.render(f"t {A.t:6.1f} s   alive {len(A.robots)}   died {len(A.dead)}   "
                               f"speed {per * 30 * TICK:.3g} x asked, {got:.3g} x got {'(paused)' if paused else ''}   (right/wrong: blue tails food?)",
                               True, (230, 230, 230)), (8, SIDE + 8))
        if sensed:
            txt = "   ".join(f"{eye} eye: mouths {v[0]:.2f}, tails {v[1]:.2f}" for eye, v in sensed.items())
            screen.blit(big.render(f"chosen ({chosen.kind}, outlined)  {txt}", True, (230, 230, 230)), (8, SIDE + 32))
        screen.blit(big.render("M mouth, T tail, yellow: bite, bar: belly; "
                               "space, up/down, E, Tab", True, (180, 180, 180)), (8, SIDE + 56))
        if a.record:
            pygame.image.save(screen, os.path.join(a.record, f"{frame:06d}.png"))
            frame += 1
            if A.t >= a.seconds:
                return
        else:
            pygame.display.flip()
            clock.tick(30)
            if time.time() - mark > 1.0:
                got, mark, t0 = (A.t - t0) / (time.time() - mark), time.time(), A.t


if __name__ == "__main__":
    main()
