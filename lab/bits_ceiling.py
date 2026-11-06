"""bits_ceiling.py: stage 1b's "too short" limits redone at higher rates of taste (D31). lab/bits_family.py's Wald table counts tastes at the bank's rate, 0.63 a second; a brain may eat more. Its own measure of unwired lives
gives 145 meals a life, and 181 in the best. Neither is a physical ceiling, since a brain could chase blocks, so a limit here is "too short at this rate", not for every brain. Also: seconds per doubling of a family, from the union estimate.

    .venv/bin/python lab/bits_ceiling.py"""
import math


def kl(e):
    return (1 - 2 * e) * math.log2((1 - e) / e)


def bhatt(e):
    return -math.log2(2 * math.sqrt(e * (1 - e)))


W = 0.9 * math.log2(0.95 / 0.05)  # Wald's bits for one pair at 5% error each way


def largest_lie(n):
    lo, hi = 0.001, 0.4999
    for _ in range(60):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if kl(m) * n > W else (lo, m)
    return lo


print(f"Wald: {W:.2f} bits for one pair at 5% error each way")
for rate, name in ((0.63, "the bank, 0.63 a s"), (1.45, "unwired mean, 1.45 a s"), (1.81, "unwired best life, 1.81 a s")):
    print(f"{name}: largest lie rate one pair can stand, disagreeing on every taste: " + ", ".join(f"{t} s {largest_lie(rate * t):.3f}" for t in (10, 30, 100)))
    print("   seconds for a rare disagreement: " + ", ".join(f"e {e} on {rho:.0%}: {W / kl(e) / rho / rate:.0f}" for e, rho in ((0.025, 0.01), (0.2, 0.05), (0.35, 0.2))))
print("\nUnion estimate, pairs disagreeing on half of tastes, 5% error, at the bank's rate in each world:")
for e, rate, name in ((0.025, 0.63, "plain"), (0.215, 0.60, "unreliable")):
    bps = 0.5 * bhatt(e) * rate
    print(f"{name}: {1 / bps:.1f} s per doubling of the family; N=7 {(math.log2(7) + math.log2(20)) / bps:.0f} s; N=1000 {(math.log2(1000) + math.log2(20)) / bps:.0f} s")
