"""This script imports all tests written in tests/ and execute them using unittest"""

import argparse
import logging
import unittest

logger = logging.getLogger(__package__)


def run_tests(log_lvl="WARNING", file_name=None, unittest_verbosity=0):
    # Set teacher logging level

    logger.setLevel(log_lvl)

    # Discover all tests in a directory or in the specified file
    if file_name is None:
        pattern = "test_*.py"
    else:
        pattern = file_name

    # Run the test suite
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir="src/trame_tests",  # directory to start discovery
        pattern=pattern,  # pattern for test files
        top_level_dir=".",  # top-level directory of project
    )

    runner = unittest.TextTestRunner(verbosity=unittest_verbosity)
    runner.run(suite)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import and execute all tests from tests/ using unittest"
    )
    parser.add_argument("--log-lvl", default="WARNING", help="Log level (default: WARNING)")
    parser.add_argument("--verbosity", type=int, default=0, help="unittest verbosity (default: 0)")

    args = parser.parse_args()

    run_tests(args.log_lvl, None, args.verbosity)
