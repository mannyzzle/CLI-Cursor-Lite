import os
import subprocess

def run_python_file(working_directory, file_path):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

        if not abs_file_path.startswith(abs_working_dir):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.exists(abs_file_path):
            return f'Error: File "{file_path}" not found.'

        if not abs_file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'

        result = subprocess.run(
            ["python", abs_file_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=abs_working_dir
        )

        output = []
        if result.stdout:
            output.append("STDOUT:\n" + result.stdout.strip())
        if result.stderr:
            output.append("STDERR:\n" + result.stderr.strip())
        if result.returncode != 0:
            output.append(f"Process exited with code {result.returncode}")

        return "\n".join(output) if output else "No output produced."

    except subprocess.TimeoutExpired:
        return f"Error: Execution of \"{file_path}\" timed out after 30 seconds."
    except Exception as e:
        return f"Error: executing Python file: {e}"
