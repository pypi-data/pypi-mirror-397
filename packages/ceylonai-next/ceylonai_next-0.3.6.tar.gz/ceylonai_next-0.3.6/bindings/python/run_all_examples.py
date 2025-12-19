import os
import sys
import subprocess
import time
from pathlib import Path

# Configuration
EXAMPLES_DIR = Path("examples")
REPORT_FILE = "examples_report.md"
TIMEOUT_SECONDS = 30
# Use uv run to ensure we use the correct virtual environment with ceylonai_next installed
VENV_PYTHON_COMMAND = ["uv", "run", "python"]


def main():
    print(f"Running examples from: {EXAMPLES_DIR.absolute()}")
    example_files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith(".py")]
    example_files.sort()

    results = []

    for filename in example_files:
        filepath = EXAMPLES_DIR / filename
        print(f"Running {filename}...")

        start_time = time.time()
        status = "UNKNOWN"
        output = ""
        error_msg = ""

        try:
            # We run the example with the SAME python executable script is running with
            # We set PYTHONPATH to include current dir so examples can import ceylonai_next if needed
            # (though venv should handle it, explicit is safer if run from here)
            env = os.environ.copy()
            # env['PYTHONPATH'] = os.getcwd() # Might not be needed if installed in venv
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"

            # Run the process
            # We use cwd=EXAMPLES_DIR so the examples run relative to where they are
            result = subprocess.run(
                VENV_PYTHON_COMMAND + [filename],
                cwd=EXAMPLES_DIR,
                capture_output=True,
                encoding="utf-8",
                timeout=TIMEOUT_SECONDS,
                env=env,
            )

            duration = time.time() - start_time
            output = result.stdout + "\n" + result.stderr

            if result.returncode == 0:
                status = "PASS"
            else:
                status = "FAIL"
                error_msg = f"Exit code: {result.returncode}"

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            status = "TIMEOUT"
            error_msg = f"Timed out after {TIMEOUT_SECONDS}s"
            # We can't easily capture output from timed out process with subprocess.run
            # but sometimes it's possible. subprocess.run doesn't return stdout on timeout exception easily in older python
            # In 3.7+ TimeoutExpired has `stdout` and `stderr` attributes if captured.
            output = "Timeout - output truncated"

        except Exception as e:
            duration = time.time() - start_time
            status = "ERROR"
            error_msg = str(e)
            output = str(e)

        print(f"  Result: {status} ({duration:.2f}s)")

        results.append(
            {
                "filename": filename,
                "status": status,
                "duration": duration,
                "error": error_msg,
                "output": output,
            }
        )

    # Generate Report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# Python Examples Execution Report\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Examples:** {len(results)}\n\n")

        # Summary Table
        f.write("| Example | Status | Duration | Error |\n")
        f.write("|---------|--------|----------|-------|\n")
        for res in results:
            icon = (
                "✅"
                if res["status"] == "PASS"
                else "❌"
                if res["status"] == "FAIL"
                else "⏱️"
            )
            f.write(
                f"| {res['filename']} | {icon} {res['status']} | {res['duration']:.2f}s | {res['error']} |\n"
            )

        f.write("\n\n## Detailed Output\n")
        for res in results:
            if res["status"] != "PASS":
                f.write(f"\n### {res['filename']} ({res['status']})\n")
                f.write("```\n")
                # Limit output size using simple slicing if too long
                out_content = res["output"]
                if len(out_content) > 2000:
                    out_content = (
                        out_content[:1000]
                        + "\n... [truncated] ...\n"
                        + out_content[-1000:]
                    )
                f.write(out_content)
                f.write("\n```\n")

    print(f"Report generated: {REPORT_FILE}")


if __name__ == "__main__":
    main()
