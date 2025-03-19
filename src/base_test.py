import subprocess
import sys


def run_test():
    process = subprocess.Popen(["uvicorn", "main:app"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)

    try:
        _, _ = process.communicate(timeout=7)
        print(f"Exit code: {process.returncode}")

        if process.returncode != 0:
            sys.exit(1)

    except subprocess.TimeoutExpired:

        print("Success")
        process.kill()

        process.communicate()
        sys.exit(0)


if __name__ == "__main__":
    run_test()
