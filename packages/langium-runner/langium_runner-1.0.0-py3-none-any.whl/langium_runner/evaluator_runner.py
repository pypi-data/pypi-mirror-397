import atexit
import json
import logging
import os
import select
import subprocess
import sys
from typing import Optional, Union

from .generated.langium_ai_tools import EvaluatorResultMsg

logging.basicConfig(level=logging.INFO)


class LangiumEvaluatorRunner:
    def __init__(self, timeout: int = 5) -> None:
        """
        Initialize the LangiumEvaluatorRunner.

        :param timeout: Timeout in seconds for waiting for process output. Default is 5 seconds.
        """
        self.timeout = timeout
        self.process: Optional[subprocess.Popen] = None
        self.start_process()

        # Ensure the process is terminated when the main process exits
        atexit.register(self.stop_process)

    def _is_process_healthy(self) -> bool:
        """Check if the current process is healthy and ready for communication."""
        return (
            self.process is not None
            and self.process.poll() is None
            and self.process.stdin is not None
            and self.process.stdout is not None
            and not self.process.stdin.closed
            and not self.process.stdout.closed
        )

    def is_node_installed(self) -> bool:
        """Check if Node.js is installed and available in the PATH."""
        try:
            subprocess.run(
                ["node", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            logging.error(f"Unexpected error while checking Node.js installation: {e}")
            return False

    def start_process(self) -> None:
        """Start the Node.js process."""
        # Clean up existing process if it exists
        if self.process is not None:
            self.stop_process()

        if not self.is_node_installed():
            logging.error("Node.js is not installed or not in PATH.")
            raise RuntimeError("Node.js is not installed or not in PATH.")

        script_path = os.path.join(os.path.dirname(__file__), "dist/bundle.cjs")
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found at path: {script_path}")

        try:
            self.process = subprocess.Popen(
                ["node", script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            logging.info("LangiumEvaluator process started.")

            # Verify the process started successfully
            if self.process.poll() is not None:
                raise RuntimeError("Process terminated immediately after startup")

        except Exception as e:
            logging.error(f"Failed to start LangiumEvaluator process: {e}")
            self.process = None
            raise

    def _convert_enum_format(self, obj: Union[dict, list]) -> None:
        """
        Convert TypeScript protobuf enum format to Python betterproto format.
        TypeScript protobuf-ts uses full enum names (e.g., "DIAGNOSTIC_SEVERITY_ERROR")
        while betterproto uses short names (e.g., "ERROR").
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "severity" and isinstance(value, str):
                    # Convert DiagnosticSeverity enum format
                    if value.startswith("DIAGNOSTIC_SEVERITY_"):
                        obj[key] = value.replace("DIAGNOSTIC_SEVERITY_", "")
                elif isinstance(value, (dict, list)):
                    self._convert_enum_format(value)
        elif isinstance(obj, list):
            for item in obj:
                self._convert_enum_format(item)

    def run_langium_evaluator(self, evaluation_input: str) -> EvaluatorResultMsg:
        """Send input to the Node.js process and retrieve the evaluation result."""
        if not self._is_process_healthy():
            logging.warning(
                "LangiumEvaluator process is not healthy. Restarting process."
            )
            self.start_process()

        # After start_process, we know self.process is not None and healthy
        process = self.process
        assert process is not None, "Process should be running after start_process"

        if not evaluation_input or not isinstance(evaluation_input, str):
            raise ValueError(
                "The 'evaluation_input' parameter must be a non-empty string."
            )

        try:
            # Write input to the process
            assert process.stdin is not None, "Process stdin should not be None"
            assert process.stdout is not None, "Process stdout should not be None"

            process.stdin.write(evaluation_input + "\n")
            process.stdin.flush()

            # Read output from the process
            ready, _, _ = select.select([process.stdout], [], [], self.timeout)
            if ready:
                output = process.stdout.readline().strip()
                logging.debug(f"Received output: {output}")
            else:
                raise TimeoutError(
                    "Timeout while waiting for LangiumEvaluator process output."
                )
            try:
                # Parse JSON and convert TypeScript enum format to Python format
                json_data: dict = json.loads(output)
                self._convert_enum_format(json_data)
                # mypy is not able to resolve the dynamically created from_dict method
                return EvaluatorResultMsg.from_dict(json_data)  # type: ignore[no-any-return]
            except json.JSONDecodeError as json_error:
                raise ValueError(
                    "Malformed JSON output received from LangiumEvaluator."
                ) from json_error
        except TimeoutError:
            logging.error(
                "Timeout occurred while communicating with LangiumEvaluator process"
            )
            raise
        except ValueError:
            logging.error("Invalid input or malformed JSON response")
            raise
        except Exception as e:
            logging.error(f"Unexpected error during evaluation: {e}")
            raise

    def stop_process(self) -> None:
        """Terminate the Node.js process."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                logging.info("LangiumEvaluator process terminated.")
            except subprocess.TimeoutExpired:
                logging.warning(
                    "LangiumEvaluator process did not terminate in time. Forcing termination."
                )
                self.process.kill()
            except Exception as e:
                logging.error(f"Error while terminating LangiumEvaluator process: {e}")
            finally:
                self.process = None


def run_langium_evaluator_cli() -> None:
    """CLI entry point for LangiumEvaluator."""

    if len(sys.argv) < 2:
        print("Usage: python evaluator_runner.py '<evaluation_input>'")
        sys.exit(1)

    evaluation_input = sys.argv[1]

    runner = LangiumEvaluatorRunner()
    try:
        result = runner.run_langium_evaluator(evaluation_input)
        print(json.dumps(result.to_dict(), indent=2))
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        runner.stop_process()


# Example usage
if __name__ == "__main__":
    runner = LangiumEvaluatorRunner(timeout=7)
    try:
        evaluation_input = "grammar LangiumExample { entry: Example; }"
        result = runner.run_langium_evaluator(evaluation_input)
        logging.info(f"Evaluation Result: {result.to_dict()}")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        runner.stop_process()
