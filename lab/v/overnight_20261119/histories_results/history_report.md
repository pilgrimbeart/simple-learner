# Task D — fixed development schedules

Histories 80/80, settings 1920/1920; elapsed 1020.2 s; refinement passed (max knob change 7.84e-06).
Ten reused, deliberately selected component draws (the two failures and the lowest eight labels) × eight new schedules. Not a population sample; not fresh components; not new event families. Observer settings computed from a fixed trajectory and scored on isolated old cases; not closed-loop lives or online learning.

## Draws whose every old case passes (of 80 histories), by observation mode and window

| window | raw | 0.15 | 1.0 | 3.8585074308112732 |
|---|---|---|---|---|
| first_100s_last_third | 23/80 | 19/80 | 19/80 | 19/80 |
| full_100s | 38/80 | 51/80 | 51/80 | 51/80 |
| last_third_1000s | 56/80 | 70/80 | 70/80 | 70/80 |
| full_1000s | 55/80 | 71/80 | 72/80 | 72/80 |
| prefix_666.6666666666666s | 57/80 | 72/80 | 72/80 | 72/80 |
| prefix_833.3333333333334s | 54/80 | 72/80 | 72/80 | 72/80 |

## By component seed (all-pass count of 8 schedules), tau 0.15 s

| seed | first_100s_last_third | full_100s | last_third_1000s | full_1000s | prefix_666.6666666666666s | prefix_833.3333333333334s |
|---|---|---|---|---|---|---|
| 2026112200 | 4/8 | 5/8 | 8/8 | 8/8 | 8/8 | 8/8 |
| 2026112201 | 2/8 | 6/8 | 8/8 | 8/8 | 8/8 | 8/8 |
| 2026112202 | 2/8 | 6/8 | 8/8 | 8/8 | 8/8 | 8/8 |
| 2026112203 | 2/8 | 6/8 | 8/8 | 8/8 | 8/8 | 8/8 |
| 2026112204 | 2/8 | 5/8 | 7/8 | 7/8 | 8/8 | 8/8 |
| 2026112205 | 0/8 | 6/8 | 8/8 | 8/8 | 8/8 | 8/8 |
| 2026112206 | 1/8 | 7/8 | 8/8 | 8/8 | 8/8 | 8/8 |
| 2026112207 | 3/8 | 6/8 | 8/8 | 8/8 | 8/8 | 8/8 |
| 2026112215 | 0/8 | 0/8 | 0/8 | 0/8 | 0/8 | 0/8 |
| 2026112227 | 3/8 | 4/8 | 7/8 | 8/8 | 8/8 | 8/8 |

## By evidence (simultaneous events in the window: 0, 1, 2+), tau 0.15 s

| window | 0 | 1 | 2+ |
|---|---|---|---|
| first_100s_last_third | 0/58 | 18/21 | 1/1 |
| full_100s | 1/24 | 36/39 | 14/17 |
| last_third_1000s | 0/2 | 3/4 | 67/74 |
| full_1000s | 0/0 | 0/1 | 71/79 |
| prefix_666.6666666666666s | 0/0 | 2/2 | 70/78 |
| prefix_833.3333333333334s | 0/0 | 1/1 | 71/79 |

Every setting, failed case and denominator is in `settings.jsonl` / `case_scores.jsonl`; full tables by seed, mode, window and evidence in `history_summary.json`.
