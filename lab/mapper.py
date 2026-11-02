"""mapper.py k=v ...: the mapping rung (QUESTIONS.md): legal inputs only (each eye's pulses, the taste), told its own
pose (perfect path integration) and which colour is food, so that it measures what a map is worth. Each colour has
an evidence grid (0.5 mm cells, log-odds): each tick the cells along an eye's corridor gain n log(lam(d) / bg) -
lam(d) for n pulses, where lam(d) is what a block d away would give (lose lam(d) when n = 0); eating clears the cells
at the mouth. It steers (as omni.py) to the likeliest food that is near, with no likely poison on its straight path,
and scans (one thruster) when its map shows nothing worth going to."""
import sys, math, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import world
from omni import Omni
from units import TICK

CELL = 0.5e-3
N = int(round(world.WORLD / CELL))
ALONG = np.arange(0.25e-3, world.RANGE, CELL)
ACROSS = np.arange(-world.EAT - world.BLOCK + CELL / 2, world.EAT + world.BLOCK, CELL)
LAM = world.SENSE * TICK / (1 + (ALONG / world.REACH) ** 2)  # pulses a tick from a block d away


class Mapper(Omni):
    def __init__(self, lf, poison, food_sensor, bg=0.01, prior=-4.0, top=6.0, want=1.0, scan=12.0, bored=2.0,
                 roam=0.5, **p):
        super().__init__(lf, poison, **p)
        self.food_sensor, self.bg, self.top, self.want, self.scan = food_sensor, bg, top, want, scan
        self.g = {s: np.full((N, N), prior) for s in (0, 1)}
        self.n = [0, 0]
        self.phase = 0.0
        self.bored, self.roam, self.idle = bored, roam, 0.0
        yy, xx = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
        self.cx, self.cy = (xx + 0.5) * CELL, (yy + 0.5) * CELL

    def stimulate(self, sensor, at):
        self.n[sensor] += 1

    def taste(self, value, at):
        b = self.lf.body
        h = b.head()
        for s in (0, 1):
            d = np.hypot(b.wrap(self.cx - h[0]), b.wrap(self.cy - h[1]))
            self.g[s][d < world.EAT + world.BLOCK] = -self.top

    def cells(self):
        b = self.lf.body
        h, f = b.head(), b.forward()
        r = np.array([f[1], -f[0]])
        pts = h[None, None, :] + ALONG[:, None, None] * f + ACROSS[None, :, None] * r
        ij = (np.floor(pts / CELL).astype(int)) % N
        return ij[..., 1], ij[..., 0]                    # rows (y), cols (x), shape (along, across)

    def step(self):
        b, lf = self.lf.body, self.lf
        iy, ix = self.cells()
        for s in (0, 1):
            n = self.n[s]
            ev = (n * np.log(LAM / self.bg) - (LAM - self.bg)) if n else -LAM
            g = self.g[s]
            g[iy, ix] = np.clip(g[iy, ix] + ev[:, None], -self.top, self.top)
        self.n = [0, 0]
        food, bad = self.g[self.food_sensor], self.g[1 - self.food_sensor]
        h = b.head()
        dx, dy = b.wrap(self.cx - h[0]), b.wrap(self.cy - h[1])
        dist = np.hypot(dx, dy)
        score = np.where(food > self.want, food - dist / 2e-3, -1e9)
        out = []
        for _ in range(4):                               # the likeliest near food with no likely poison on the way
            i = np.unravel_index(np.argmax(score), score.shape)
            if score[i] < -1e8:
                break
            d = np.array([dx[i], dy[i]]); L = dist[i]
            u = d / max(L, 1e-9)
            along = dx * u[0] + dy * u[1]
            side = np.abs(dx * u[1] - dy * u[0])
            if np.any((bad > self.want) & (along > 0) & (along < L) & (side < self.clear)):
                score[i] = -1e9
                continue
            self.idle = 0.0
            e = (math.atan2(d[1], d[0]) - b.heading - b.spin / world.DRAG + math.pi) % (2 * math.pi) - math.pi
            if abs(e) > self.tol:
                return [lf.motor["right" if e > 0 else "left"]]
            v = b.speed @ b.forward()
            return [lf.motor["left"], lf.motor["right"]] if v < min(self.vmax, self.k * L) else []
        self.idle += TICK                                # nothing worth going to: scan, and now and then run
        if self.idle > self.bored:                       # straight (moving, so that its rays cross: ranging)
            if self.idle > self.bored + self.roam:
                self.idle = 0.0
            return [lf.motor["left"], lf.motor["right"]] if b.speed @ b.forward() < self.vmax else []
        self.phase += self.scan * TICK
        k = int(self.phase); self.phase -= k
        return [lf.motor["left"]] * k


def life(job):
    from creature import Life
    from minimal.spec import Lived, SPAN, thirds
    p, seed, poison = job
    lf = Life(seed, poison, brain=lambda s: None)
    good = lf.sensor[next(c for c in lf.sensor if c != poison)]
    lf.brain = Mapper(lf, poison, good, **p)
    while lf.t < 10000:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, 10000, poison))
    l.power, l.firings = 0.0, SPAN * len(lf.firings) / 100.0
    return l


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    from minimal.spec import summary
    from discrete.poison import show
    seeds = range(50000, 50000 + int(sys.argv[1]))
    with ProcessPoolExecutor(4) as ex:
        for a in sys.argv[2:]:
            p = {k: float(v) for k, v in (x.split("=") for x in a.split(",") if x)}
            L = list(ex.map(life, [(p, s, c) for s in seeds for c in ("red", "blue")]))
            print(show(f"mapper {p}", summary(L)), flush=True)
