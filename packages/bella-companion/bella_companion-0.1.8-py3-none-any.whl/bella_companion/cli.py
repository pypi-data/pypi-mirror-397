import argparse
import os
from pathlib import Path

import matplotlib.pyplot as plt
from dotenv import load_dotenv

from bella_companion.eucovid import plot_all as plot_eucovid
from bella_companion.eucovid import (
    run as run_eucovid,
)
from bella_companion.platyrrhine import summarize as summarize_platyrrhine
from bella_companion.simulations import (
    generate,
    metrics,
    plot_epi_multitype,
    plot_epi_skyline,
    plot_fbd_2traits,
    plot_fbd_no_traits,
    plot_scenarios,
)
from bella_companion.simulations import plot_all as plot_all_simulations
from bella_companion.simulations import run as run_simulations
from bella_companion.simulations import summarize as summarize_simulations


def main():
    load_dotenv(Path(os.getcwd()) / ".env")
    os.environ["BELLA_RUN_BEAST_CMD"] = " ".join(
        [
            "java",
            os.getenv("JAVA_OPTIONS", ""),
            f"-jar {Path(__file__).parent / 'BELLA.jar'}",
            f"-version_file {Path(__file__).parent / 'version.xml'}",
            "-overwrite",
            "-statefile /tmp/state",
        ]
    )
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["xtick.labelsize"] = 20
    plt.rcParams["ytick.labelsize"] = 20
    plt.rcParams["font.size"] = 20
    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["lines.linewidth"] = 4

    parser = argparse.ArgumentParser(
        prog="bella",
        description="Companion tool with experiments and evaluation for Bayesian Evolutionary Layered Learning Architectures (BELLA) BEAST2 package.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ------------------
    # Simulation dataset
    # ------------------

    sim_parser = subparsers.add_parser("sim", help="Simulation workflows")
    sim_subparsers = sim_parser.add_subparsers(dest="subcommand", required=True)

    sim_subparsers.add_parser(
        "generate", help="Generate synthetic simulation datasets."
    ).set_defaults(func=generate)

    sim_subparsers.add_parser(
        "run", help="Run BEAST2 analyses on simulation datasets."
    ).set_defaults(func=run_simulations)

    sim_subparsers.add_parser(
        "summarize", help="Summarize BEAST2 log outputs for simulations."
    ).set_defaults(func=summarize_simulations)

    sim_subparsers.add_parser(
        "metrics", help="Compute and print metrics from simulation results."
    ).set_defaults(func=metrics)

    sim_plot_parser = sim_subparsers.add_parser(
        "plot", help="Generate plots and figures from simulation results."
    )
    sim_plot_subparsers = sim_plot_parser.add_subparsers(
        dest="subcommand", required=True
    )

    sim_plot_subparsers.add_parser(
        "all", help="Generate plots and figures from simulation results."
    ).set_defaults(func=plot_all_simulations)

    sim_plot_subparsers.add_parser(
        "epi-multitype", help="Generate plots for the epi-multitype scenario."
    ).set_defaults(func=plot_epi_multitype)

    sim_plot_subparsers.add_parser(
        "epi-skyline", help="Generate plots for the epi-skyline scenarios."
    ).set_defaults(func=plot_epi_skyline)

    sim_plot_subparsers.add_parser(
        "fbd-2traits", help="Generate plots for the fbd-2traits scenario."
    ).set_defaults(func=plot_fbd_2traits)

    sim_plot_subparsers.add_parser(
        "fbd-no-traits", help="Generate plots for the fbd-no-traits scenarios."
    ).set_defaults(func=plot_fbd_no_traits)

    sim_plot_subparsers.add_parser(
        "scenarios", help="Generate scenario overview plots."
    ).set_defaults(func=plot_scenarios)

    # -------------------
    # Platyrrhine dataset
    # -------------------

    platyrrhine_parser = subparsers.add_parser(
        "platyrrhine", help="Empirical platyrrhine datasets workflows"
    )
    platyrrhine_subparser = platyrrhine_parser.add_subparsers(
        dest="subcommand", required=True
    )

    # platyrrhine_subparser.add_parser(
    #    "run", help="Run BEAST2 analyses on empirical platyrrhine datasets."
    # ).set_defaults(func=run_platyrrhine)

    platyrrhine_subparser.add_parser(
        "summarize",
        help="Summarize BEAST2 log outputs for empirical platyrrhine datasets.",
    ).set_defaults(func=summarize_platyrrhine)

    # platyrrhine_subparser.add_parser(
    #    "figures", help="Generate plots and figures from empirical platyrrhine results."
    # ).set_defaults(func=plot_platyrrhine_results)

    # ---------------
    # EUCOVID dataset
    # ---------------

    eucovid_parser = subparsers.add_parser(
        "eucovid", help="Empirical eucovid workflows"
    )
    eucovid_subparsers = eucovid_parser.add_subparsers(dest="subcommand", required=True)

    eucovid_subparsers.add_parser(
        "run", help="Run BEAST2 analyses on empirical eucovid datasets."
    ).set_defaults(func=run_eucovid)

    eucovid_subparsers.add_parser(
        "plot", help="Generate plots and figures from empirical eucovid results."
    ).set_defaults(func=plot_eucovid)

    args = parser.parse_args()
    args.func()
