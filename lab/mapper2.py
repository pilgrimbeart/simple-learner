"""mapper2.py SEEDS k=v ...: the mapping rung with a proper sensor model. Each colour has an occupancy grid (0.5 mm
cells, probabilities). Each tick, along an eye's corridor (bins of 0.5 mm along it, each the cells across it), the
map gives each bin's chance of holding a block; the eye sees the nearest: so the chance that the nearest is in bin i
is p_i x the product of (1 - p_j) before it, or none at all. The pulses n weigh these (Poisson, at the rate a block
that far gives; a little background), and each bin becomes: the chance its block is the nearest, plus, if the nearest
is before it, its old chance (hidden). Cells across a bin move together; eating empties the cells at the mouth; the
grid relaxes to the prior over relax s (blocks eaten reappear elsewhere). Told its pose and which colour is food;
steers as omni.py to the likeliest near food with no likely poison on its path; else scans, and runs straight now
and then."""
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
LAM = world.SENSE * TICK / (1 + (ALONG / world.REACH) ** 2)
P0 = world.BLOCKS / N ** 2


class Mapper2(Omni):
    def __init__(self, lf, poison, food_sensor, bg=0.002, want=0.4, avoid=0.3, scan=12.0, bored=2.0, roam=0.5,
                 relax=30.0, **p):
        super().__init__(lf, poison, **p)
        self.food_sensor, self.bg, self.want, self.avoid = food_sensor, bg, want, avoid
        self.scan, self.bored, self.roam, self.relax = scan, bored, roam, relax
        self.g = {s: np.full((N, N), P0) for s in (0, 1)}
        self.n, self.phase, self.idle = [0, 0], 0.0, 0.0
        yy, xx = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
        self.cx, self.cy = (xx + 0.5) * CELL, (yy + 0.5) * CELL

    def stimulate(self, sensor, at):
        self.n[sensor] += 1

    @staticmethod
    def blur(g, r=2):
        """The expected number of blocks within r cells (a block's own size): the map judged block by block."""
        out = np.zeros_like(g)
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                out += np.roll(np.roll(g, dy, 0), dx, 1)
        return out

    def taste(self, value, at):
        b = self.lf.body
        h = b.head()
        d = np.hypot(b.wrap(self.cx - h[0]), b.wrap(self.cy - h[1]))
        for s in (0, 1):
            self.g[s][d < world.EAT + world.BLOCK] = 1e-4

    def look(self):
        b = self.lf.body
        h, f = b.head(), b.forward()
        r = np.array([f[1], -f[0]])
        pts = h[None, None, :] + ALONG[:, None, None] * f + ACROSS[None, :, None] * r
        ij = (np.floor(pts / CELL).astype(int)) % N
        iy, ix = ij[..., 1], ij[..., 0]
        for s in (0, 1):
            g, n = self.g[s], self.n[s]
            pc = g[iy, ix]                                   # (along, across)
            pb = 1 - np.prod(1 - pc, axis=1)                 # each bin's chance of a block
            before = np.concatenate([[1.0], np.cumprod(1 - pb)[:-1]])
            prior = np.append(pb * before, np.prod(1 - pb))  # nearest in bin i, or none
            lam = np.append(LAM, 0.0) + self.bg
            like = np.exp(n * np.log(lam) - lam)
            w = prior * like
            w /= w.sum()
            nearer = np.concatenate([[0.0], np.cumsum(w[:-1])[:-1]])   # the nearest lies before bin i
            pb2 = np.clip(w[:-1] + pb * nearer, 1e-6, 1 - 1e-6)
            up = pb2 > pb
            k = np.where(up, (1 - pb2) / np.maximum(1 - pb, 1e-9), pb2 / np.maximum(pb, 1e-9))[:, None]
            g[iy, ix] = np.where(up[:, None], 1 - (1 - pc) * k, pc * k)
        self.n = [0, 0]

    def step(self):
        b, lf = self.lf.body, self.lf
        self.look()
        a = TICK / self.relax
        for s in (0, 1):
            self.g[s] += (P0 - self.g[s]) * a
        food, bad = (self.blur(self.g[s]) for s in (self.food_sensor, 1 - self.food_sensor))   # a block's chance
                                                                                                  # near each cell
        h = b.head()
        dx, dy = b.wrap(self.cx - h[0]), b.wrap(self.cy - h[1])
        dist = np.hypot(dx, dy)
        score = np.where(food > self.want, food - dist / 5e-3, -1e9)
        for _ in range(4):
            i = np.unravel_index(np.argmax(score), score.shape)
            if score[i] < -1e8:
                break
            d = np.array([dx[i], dy[i]]); L = dist[i]
            u = d / max(L, 1e-9)
            along = dx * u[0] + dy * u[1]
            side = np.abs(dx * u[1] - dy * u[0])
            if np.any((bad > self.avoid) & (along > 0) & (along < L) & (side < self.clear)):
                score[i] = -1e9
                continue
            self.idle = 0.0
            e = (math.atan2(d[1], d[0]) - b.heading - b.spin / world.DRAG + math.pi) % (2 * math.pi) - math.pi
            if abs(e) > self.tol:
                return [lf.motor["right" if e > 0 else "left"]]
            v = b.speed @ b.forward()
            return [lf.motor["left"], lf.motor["right"]] if v < min(self.vmax, self.k * L) else []
        self.idle += TICK
        if self.idle > self.bored:
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
    lf.brain = Mapper2(lf, poison, lf.sensor[next(c for c in lf.sensor if c != poison)], **p)
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
            print(show(f"mapper2 {p}", summary(L)), flush=True)
