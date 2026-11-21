# D178 addendum 1 — observation windows (2026-11-20, written after bench.py, before any stage-1 scoring)

From [bench.json](bench.json) (32 seeds x 2 sensors per substrate, single body-size pulses into rested units, 1 ms):
first-spike latency of non-oscillating units p50 / p99 = 2.5 / 9.4 ms (biology), 2.1 / 6.1 ms (silicon).
Second pulse of a pair responds 0-18% at 5-20 ms gaps, 79-88% at 50 ms: recovery takes about 20-50 ms.
Frozen windows: a sensor spike is pulse-locked if it starts within W = 10 ms after one of its sensor's pulses (>= p99
in both substrates); a motor spike is sensor-linked if within 10 ms after either sensor's spike (synapse filter
1.25 ms plus the same latency bound). Recovery window for stage 2: 50 ms. These are measured from the circuit,
not from the body's pulse length; they are association windows, not causal attributions (omission gives causality).
Unit classes seen on the bench (sensor units, 64 per substrate; own firing > 1/s "oscillating", response < 10% "dead",
>= 90% "reliable"): biology 14 reliable, 15 partial, 11 dead, 24 oscillating; silicon 37 / 3 / 14 / 10.
