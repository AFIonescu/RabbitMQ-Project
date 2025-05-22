import pathlib
import matplotlib.pyplot as plt

# ---------------- samples (ms) ----------------
lat_ms = [
    22.4, 24.0, 23.1, 25.8, 26.0,
    26.3, 24.9, 25.4, 27.3, 29.0
]

samples = list(range(1, len(lat_ms) + 1))
lat_min, lat_avg, lat_max = min(lat_ms), sum(lat_ms)/len(lat_ms), max(lat_ms)

# ---------------- figure ----------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))

# (1) individual samples
ax1.plot(samples, lat_ms, marker="o", linewidth=1)
ax1.axhline(lat_avg, linestyle="--", linewidth=1)
ax1.set_xlabel("Sample")
ax1.set_ylabel("Latency (ms)")
ax1.set_title("RTT per message")

# (2) min / avg / max bars
ax2.bar(["Min", "Avg", "Max"], [lat_min, lat_avg, lat_max])
for x, y in zip(["Min", "Avg", "Max"], [lat_min, lat_avg, lat_max]):
    ax2.text(x, y + 0.3, f"{y:.2f}", ha="center")
ax2.set_ylim(0, lat_max + 5)
ax2.set_ylabel("Latency (ms)")
ax2.set_title("Latency summary")

fig.tight_layout()

# ---------------- save ----------------
out_dir = pathlib.Path("docs/plots")
out_dir.mkdir(parents=True, exist_ok=True)
outfile = out_dir / "latency_distribution.png"
fig.savefig(outfile, dpi=150)

print(f"Plot saved to {outfile}")
