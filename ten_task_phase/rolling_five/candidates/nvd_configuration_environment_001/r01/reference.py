"""Candidate entry point for the single saved reference implementation."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[3] / "opportunities" / "nvd_configuration_environment" / "solve_reference.py"), run_name="__main__")
