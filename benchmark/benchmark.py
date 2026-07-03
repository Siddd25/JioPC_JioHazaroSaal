import json
import numpy as np
import pandas as pd
from pathlib import Path

# ----------------------------
# Configuration
# ----------------------------

LOG_DIR = Path.home() / ".local/share/jiopc/agent"
RUNTIME_JSON = "runtime.json"

# ----------------------------
# Overall metrics
# ----------------------------

runtime_values = []
ram_values = []
cpu_values = []

# ----------------------------
# Part B metrics
# ----------------------------

partb_rows = []

# ----------------------------
# Read hyperfine runtime
# ----------------------------

with open(RUNTIME_JSON) as f:
    runtime_json = json.load(f)

runtime_values = runtime_json["results"][0]["times"]

# ----------------------------
# Parse every log
# ----------------------------

for logfile in sorted(LOG_DIR.glob("test_run_*.log"))[:30]:

    with open(logfile) as f:

        for line in f:

            try:
                record = json.loads(line)

            except Exception:
                continue

            # ------------------------
            # Resource Usage
            # ------------------------

            if record.get("type") == "RESOURCE_USAGE":

                ram_values.append(
                    record["peak_agent_ram_mb"]
                )

                cpu_values.append(
                    record["peak_agent_cpu_percent"]
                )

            # ------------------------
            # Part B App Entry
            # ------------------------

            if record.get("component") == "B":

                if "app_name" not in record:
                    continue

                partb_rows.append({

                    "app": record["app_name"],

                    "launch_time_ms":
                        record.get(
                            "launch_time_ms",
                            np.nan
                        ),

                    "total_test_time_s":
                        record.get(
                            "total_test_time_s",
                            np.nan
                        ),

                    "rss_mb":
                        record.get(
                            "rss_mb",
                            np.nan
                        ),

                    "cpu":
                        record.get(
                            "cpu_percent",
                            np.nan
                        ),

                    "status":
                        record["status"]

                })

# ----------------------------
# Statistics helper
# ----------------------------

def stats(values):

    values = np.array(values)

    return {

        "mean":
            np.mean(values),

        "p50":
            np.percentile(values,50),

        "p95":
            np.percentile(values,95),

        "min":
            np.min(values),

        "max":
            np.max(values)

    }

# ----------------------------
# Overall statistics
# ----------------------------

print("\n========== OVERALL ==========\n")

overall = {

    "Runtime (s)" : stats(runtime_values),

    "Peak RAM (MB)" : stats(ram_values),

    "Peak CPU (%)" : stats(cpu_values)

}

for metric,data in overall.items():

    print(metric)

    for k,v in data.items():

        print(f"{k:8}: {v:.2f}")

    print()

# ----------------------------
# Part B statistics
# ----------------------------

df = pd.DataFrame(partb_rows)

summary_rows = []

for app in sorted(df["app"].unique()):

    temp = df[df["app"] == app]

    summary_rows.append({

        "Application":app,

        "Mean Launch(ms)":
            temp["launch_time_ms"].mean(),

        "P50 Launch(ms)":
            np.percentile(
                temp["launch_time_ms"].dropna(),
                50
            ),

        "P95 Launch(ms)":
            np.percentile(
                temp["launch_time_ms"].dropna(),
                95
            ),

        "Mean Total(s)":
            temp["total_test_time_s"].mean(),

        "P50 Total(s)":
            np.percentile(
                temp["total_test_time_s"].dropna(),
                50
            ),

        "P95 Total(s)":
            np.percentile(
                temp["total_test_time_s"].dropna(),
                95
            )

    })

summary = pd.DataFrame(summary_rows)

print("\n========== PART B ==========\n")

print(summary)

summary.to_csv(
    "partB_benchmark.csv",
    index=False
)

print("\nSaved partB_benchmark.csv")