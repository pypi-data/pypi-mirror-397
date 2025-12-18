import json
import os
from glob import glob
from pathlib import Path

import numpy as np
import pandas as pd

from bella_companion.backend import (
    avg_CI_width_from_summaries,
    coverage_from_summaries,
    mae_from_summaries,
    mean_ess_per_hour_from_summaries,
)
from bella_companion.simulations.scenarios import SCENARIOS

METRICS_FILENAME = "sim-metrics.json"


def metrics():
    base_summaries_dir = Path(os.environ["BELLA_SUMMARIES_DIR"])
    estimates: dict[str, dict[str, dict[str, dict[str, float]]]] = {}
    mean_ess_per_hour = {}
    for name, scenario in SCENARIOS.items():
        summaries_dir = base_summaries_dir / name
        models_summaries = {
            Path(summary).stem: pd.read_csv(summary)  # pyright: ignore
            for summary in glob(str(summaries_dir / "*.csv"))
        }
        estimates[name] = {
            target: {
                model: {
                    "MAE": mae_from_summaries(summaries, true_values),
                    "coverage": coverage_from_summaries(summaries, true_values),
                    "avg_CI_width": avg_CI_width_from_summaries(
                        summaries, list(true_values)
                    ),
                }
                for model, summaries in models_summaries.items()
            }
            for target, true_values in scenario.targets.items()
        }
        if len(scenario.targets) > 1:
            estimates[name]["mean"] = {
                model: {
                    metric: np.mean(
                        [estimates[name][t][model][metric] for t in scenario.targets],
                        dtype=float,
                    )
                    for metric in ["MAE", "coverage", "avg_CI_width"]
                }
                for model in models_summaries
            }
        mean_ess_per_hour[name] = {
            model: mean_ess_per_hour_from_summaries(
                summaries, [target for v in scenario.targets.values() for target in v]
            )
            for model, summaries in models_summaries.items()
        }

    with open(base_summaries_dir / METRICS_FILENAME, "w") as f:
        json.dump({"estimates": estimates, "mean_ess_per_hour": mean_ess_per_hour}, f)
