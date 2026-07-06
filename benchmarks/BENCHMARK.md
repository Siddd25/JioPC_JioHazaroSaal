# Benchmark Report

## Test Environment

| Item | Value |
|------|------|
| OS | Ubuntu 24.04 LTS |
| CPU | 4 vCPU @ 2.45 GHz |
| RAM | 8 GB |
| GPU | None |
| Python | 3.12 |
| Browser | Chromium (Playwright) |

---

# Methodology

Benchmarking was performed using the official challenge VM.

- Hyperfine was used to benchmark overall runtime.
- 3 warm-up runs.
- 30 benchmark runs.
- Same YAML configuration used for every run.
- No additional applications were running.
- Peak RAM and CPU were collected using the agent's built-in psutil resource monitor.
- Part B timings were extracted from structured JSON execution logs.

Command used:

```bash
hyperfine \
    --warmup 3 \
    --runs 30 \
    --export-json runtime.json \
    "python3 jiopc_agent.py --config jiopc-agent.yaml"
```

---

# Overall Performance

| Metric | Mean | p50 | p95 | Min | Max |
|--------|-----:|----:|----:|----:|----:|
| Runtime (s) | 126.21 | 124.20 | 137.07 | 122.58 | 138.48 |
| Peak RAM (MB) | 59.83 | 59.82 | 59.89 | 59.75 | 59.89 |
| Peak CPU (%) | 4.06 | 4.00 | 5.10 | 2.00 | 6.00 |

---

# Part B Overhead Analysis

Part B measures the execution overhead introduced by the native application validation component. The reported overhead includes:

- Application launch
- Process detection
- Window detection
- Five-second health verification
- CPU and memory sampling
- Graceful application termination
- Two-second cooldown before the next application

The cooldown ensures that all child processes terminate cleanly before the next benchmark begins, preventing interference between consecutive tests.

| Application | Mean Launch (ms) | p50 Launch (ms) | p95 Launch (ms) | Mean Overhead (s) | p50 Overhead (s) | p95 Overhead (s) |
|-------------|-----------------:|----------------:|----------------:|------------------:|-----------------:|-----------------:|
| Calculator | 541.52 | 542.07 | 558.36 | 8.66 | 8.66 | 8.72 |
| FeatherNotes | 538.42 | 538.05 | 545.68 | 8.73 | 8.73 | 8.79 |
| LibreOffice Calc | 730.47 | 566.06 | 1097.77 | 8.94 | 8.84 | 9.26 |
| LibreOffice Impress | 670.99 | 550.92 | 1088.28 | 8.87 | 8.79 | 9.22 |
| LibreOffice Math | 1042.49 | 1058.08 | 1073.15 | 9.20 | 9.19 | 9.27 |
| LibreOffice Writer | 1004.68 | 1075.14 | 1159.21 | 9.16 | 9.22 | 9.33 |
| Text Editor | 542.11 | 541.86 | 556.30 | 8.67 | 8.66 | 8.73 |
| Thunar | 540.21 | 541.43 | 549.14 | 8.70 | 8.69 | 8.78 |
| Audacious | 539.52 | 540.45 | 546.53 | 8.70 | 8.70 | 8.79 |
| mpv | 538.53 | 535.32 | 553.17 | 8.71 | 8.69 | 8.83 |

### Observations

- Lightweight native applications (Calculator, FeatherNotes, Audacious, mpv, Text Editor and Thunar) consistently launched in approximately **540 ms**.
- LibreOffice applications required significantly longer startup times (670–1040 ms) due to application initialization.
- Despite differences in startup latency, the overall validation overhead remained below **10 seconds per application**.
- The measured overhead is dominated by the intentional five-second health verification period and the two-second cooldown between tests, ensuring stable and isolated measurements.


---

# Observations

- Runtime remained consistent across all 30 executions.
- Peak memory usage remained below 60 MB throughout benchmarking.
- Peak CPU utilization remained below 6%.
- Lightweight applications consistently launched within approximately 550 ms.
- Larger LibreOffice applications required longer startup times, but overall test duration remained below 10 seconds.

---

# Reproducibility

The benchmark can be reproduced using:

```bash
hyperfine \
    --warmup 3 \
    --runs 30 \
    --export-json runtime.json \
    "python3 jiopc_agent.py --config jiopc-agent.yaml"
```

followed by

```bash
python benchmark.py
```

which generates the statistical summary and Part B benchmark tables.