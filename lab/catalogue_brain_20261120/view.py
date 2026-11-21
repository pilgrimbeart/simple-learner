"""D180 live viewer: registers the lab brain in-process (no production registry edit) and runs creature.watch.

  view.py SEED [--version N]        a live window (poison colour by creature.watch's own rule: COLOURS[seed % 2])

The brain's panel shows E0, E1, P0, P1, X0, X1, M0, M1 over the last ticks, each labelled (colour never the only cue).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

from brain import CatalogueBrain                     # noqa: E402

ROWS = [("E0", 0), ("E1", 1), ("P0", 2), ("P1", 3), ("X0", 6), ("X1", 7), ("M0", 8), ("M1", 9)]
TRACE = 490


class Watched(CatalogueBrain):
    def built(self):
        return True

    def stage(self):
        return "waiting"

    def draw(self, screen, side, font, sensors, motors, lit):
        import pygame
        h = side // len(ROWS)
        hist = self.rows[-TRACE:]
        for i, (label, col) in enumerate(ROWS):
            top = i * h
            pygame.draw.rect(screen, (30, 30, 30), (0, top + 4, side, h - 8))
            mid = top + h // 2
            pts = [(x * side // TRACE, mid - int(v[col] / 0.9 * (h // 2 - 6))) for x, v in enumerate(hist)]
            if len(pts) > 1:
                pygame.draw.lines(screen, (86, 180, 233), False, pts, 1)
            pygame.draw.line(screen, (90, 90, 90), (0, mid), (side, mid), 1)
            extra = ""
            if label.startswith("P"):
                extra = f"  {sensors[int(label[1])]}"
            if label.startswith("M"):
                extra = f"  -> {motors[int(label[1])]} thruster"
            screen.blit(font.render(label + extra, True, (255, 255, 255), (60, 60, 60)), (6, top + 8))


def main():
    import creature
    seed = int(sys.argv[1])
    v = int(sys.argv[sys.argv.index("--version") + 1]) if "--version" in sys.argv else 1
    spec = None
    if v != 1:
        import importlib
        spec = importlib.import_module(f"design_v{v}").graph
    name = f"catalogue-v{v}"
    dict.__setitem__(creature.BRAINS, name, lambda s: Watched(s, spec=spec))
    creature.watch(seed=seed, brain=name)


if __name__ == "__main__":
    main()
