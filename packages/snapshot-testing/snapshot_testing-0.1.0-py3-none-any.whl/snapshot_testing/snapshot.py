import logging
import os
import pathlib
from collections.abc import Callable
from inspect import getsource
from typing import Concatenate, ParamSpec, TypeVar

from pytest import (
    CaptureFixture,
    FixtureRequest,
    LogCaptureFixture,
    WarningsRecorder,
)

FuncParams = ParamSpec("FuncParams")
FuncReturns = TypeVar("FuncReturns")
FuncSignature = Callable[FuncParams, FuncReturns]
DecoratedSignature = Callable[
    Concatenate[
        LogCaptureFixture,
        CaptureFixture,
        WarningsRecorder,
        FixtureRequest,
        FuncParams,
    ],
    FuncReturns,
]


def snapshot(func: FuncSignature) -> DecoratedSignature:
    """
    Creates a snapshot test decorator that captures stdout, stderr, logs,
    and warnings during the execution of the decorated test function. The
    captured output is saved to a file named after the test function with a
    `.captured` extension. On subsequent runs, the output is compared to the
    previously saved output, and an error is raised if there are any
    differences.

    Args:
         func: The test function to be decorated.

    Returns:
        A wrapped function that captures and compares test outputs.
    """

    def wrapper(
        caplog: LogCaptureFixture,
        capsys: CaptureFixture[str],
        recwarn: WarningsRecorder,
        request: FixtureRequest,
        *args: FuncParams.args,
        **kwargs: FuncParams.kwargs,
    ):
        # Set up logging capture
        caplog.set_level(logging.DEBUG)

        # Get the node path from pytest request
        node_path = request.node.nodeid
        # Extract directory and test name from node path
        # Format: path/to/test_file.py::test_function
        if "::" in node_path:
            file_part, test_part = node_path.rsplit("::", 1)
            # Remove .py extension and convert to directory structure
            file_part = file_part.replace(".py", "")
            # Replace path separators with directory separators
            dir_structure = file_part.replace("/", os.sep)
        else:
            dir_structure = node_path.replace(".py", "").replace("/", os.sep)
            test_part = func.__name__

        # Create base output directory structure
        base_output_dir = os.path.join("snapshots", dir_structure)
        pathlib.Path(base_output_dir).mkdir(exist_ok=True, parents=True)

        # Use test function name with .captured extension
        test_filename = f"{test_part}.captured"
        filepath = os.path.join(base_output_dir, test_filename)

        result = func(*args, **kwargs)

        # Capture all output after test execution
        captured_stdout = capsys.readouterr()

        current_output = "RESOURCE:\n"
        current_output += getsource(func) + "\n\n"

        if captured_stdout.out:
            current_output += "STDOUT:\n"
            current_output += captured_stdout.out
            current_output += "\n"

        if captured_stdout.err:
            current_output += "STDERR:\n"
            current_output += captured_stdout.err
            current_output += "\n"

        if caplog.text:
            current_output += "LOGS:\n"
            current_output += caplog.text
            current_output += "\n"

        if recwarn:
            current_output += "WARNINGS:\n"
            for warning in recwarn:
                current_output += (
                    f"{warning.filename}:{warning.lineno}: {warning.message}\n"
                )
            current_output += "\n"

        # Compare with previous output if file exists
        previous_output = ""
        if pathlib.Path(filepath).exists():
            with pathlib.Path(filepath).open(encoding="utf-8") as f:
                previous_output = f.read()

        # Always write current output to file (overwrite existing)
        with pathlib.Path(filepath).open("w", encoding="utf-8") as f:
            f.write(current_output)

        # Check for differences and raise error if content changed
        if previous_output != current_output:
            error_msg = f"""
Output changed for {func.__name__}!

=== EXPECTED OUTPUT ===
{previous_output}

=== ACTUAL OUTPUT ===
{current_output}

Test output file: {filepath}
"""
            raise AssertionError(error_msg)
        if not previous_output:
            print(f"First run for {func.__name__} - baseline captured")
        else:
            print(f"Output unchanged for {func.__name__}")

        print(f"Test output captured to: {filepath}")
        return result

    return wrapper
