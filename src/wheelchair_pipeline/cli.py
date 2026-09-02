"""Command-line interface for the public reference pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from .synthetic import write_synthetic_trial
from .workflow import PipelineConfig, run_pipeline


def _build_config(args: argparse.Namespace) -> PipelineConfig:
    phases = None
    if args.propulsion is not None or args.recovery is not None:
        if args.propulsion is None or args.recovery is None:
            raise SystemExit("--propulsion and --recovery must be supplied together.")
        phases = (("propulsion", *args.propulsion), ("recovery", *args.recovery))
    return PipelineConfig(
        angle_key=args.angle_key,
        mode=args.mode,
        cutoff_hz=args.cutoff_hz,
        filter_order=args.filter_order,
        neutral_window=tuple(args.neutral_window),
        analysis_window=tuple(args.analysis_window) if args.analysis_window else None,
        pair_base=args.pair_base,
        direct_column=args.direct_column,
        phases=phases,
        phase_points=args.phase_points,
    )


def _add_run_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--angle-key", default="hombro_fe")
    parser.add_argument("--mode", choices=("axis_offset", "direct_resultant"), default="axis_offset")
    parser.add_argument("--pair-base", default=None)
    parser.add_argument("--direct-column", default=None)
    parser.add_argument("--cutoff-hz", type=float, default=6.0)
    parser.add_argument("--filter-order", type=int, default=4)
    parser.add_argument("--neutral-window", nargs=2, type=float, default=(0.2, 1.0), metavar=("START", "END"))
    parser.add_argument("--analysis-window", nargs=2, type=float, default=None, metavar=("START", "END"))
    parser.add_argument("--propulsion", nargs=2, type=float, default=None, metavar=("START", "END"))
    parser.add_argument("--recovery", nargs=2, type=float, default=None, metavar=("START", "END"))
    parser.add_argument("--phase-points", type=int, default=100)
    parser.add_argument("--no-plot", action="store_true")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Wheelchair IMU angular profiling public pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="process an exported signal CSV")
    _add_run_arguments(run_parser)

    demo_parser = subparsers.add_parser("generate-demo", help="write and process a deterministic synthetic trial")
    demo_parser.add_argument("--input", required=True, type=Path)
    demo_parser.add_argument("--output", required=True, type=Path)

    args = parser.parse_args(argv)
    if args.command == "generate-demo":
        write_synthetic_trial(args.input)
        config = PipelineConfig(
            angle_key="hombro_fe",
            neutral_window=(0.2, 1.0),
            phases=(("propulsion", 0.0, 2.0), ("recovery", 2.0, 3.99)),
        )
        result = run_pipeline(args.input, args.output, config)
    else:
        result = run_pipeline(args.input, args.output, _build_config(args), write_plot=not args.no_plot)
    print(f"Processed {result.samples} samples at {result.sampling_hz:.3f} Hz; axis={result.axis_used}")
    print(f"Outputs: {result.output_dir}")
    return 0
