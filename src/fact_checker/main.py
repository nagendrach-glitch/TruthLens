#!/usr/bin/env python
"""
main.py
CLI entry point for the TruthLens CrewAI crew.
Run via:  fact_checker  |  run_crew  |  python -m fact_checker.main
"""

import sys
import warnings

from fact_checker.crew import FactChecker

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# ── Default test inputs ───────────────────────────────────────────────────────
_DEFAULT_INPUTS = {
    "input_content": (
        "The Great Wall of China is visible from space with the naked eye."
    )
}


def run():
    """Run the crew with default test inputs."""
    try:
        FactChecker().crew().kickoff(inputs=_DEFAULT_INPUTS)
    except Exception as e:
        raise RuntimeError(f"An error occurred while running the crew: {e}") from e


def train():
    """Train the crew for a given number of iterations.

    Usage: crewai train <n_iterations> <output_filename>
    """
    if len(sys.argv) < 3:
        print("Usage: train <n_iterations> <filename>")
        sys.exit(1)
    try:
        FactChecker().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=_DEFAULT_INPUTS,
        )
    except Exception as e:
        raise RuntimeError(f"An error occurred while training the crew: {e}") from e


def replay():
    """Replay the crew execution from a specific task ID.

    Usage: crewai replay <task_id>
    """
    if len(sys.argv) < 2:
        print("Usage: replay <task_id>")
        sys.exit(1)
    try:
        FactChecker().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise RuntimeError(f"An error occurred while replaying the crew: {e}") from e


def test():
    """Test the crew and return evaluation results.

    Usage: crewai test <n_iterations> <eval_llm>
    """
    if len(sys.argv) < 3:
        print("Usage: test <n_iterations> <eval_llm>")
        sys.exit(1)
    try:
        FactChecker().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs=_DEFAULT_INPUTS,
        )
    except Exception as e:
        raise RuntimeError(f"An error occurred while testing the crew: {e}") from e
