import os

MAX_CHARS = 10000

def get_file_content(working_directory, file_path):
    try:
        abs_path = os.path.abspath(os.path.join(working_directory, file_path))
        base_path = os.path.abspath(working_directory)

        # Guardrail: check if file is within working directory
        if not abs_path.startswith(base_path):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # Check if it's a valid file
        if not os.path.isfile(abs_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(abs_path, "r") as f:
            content = f.read()

        if len(content) > MAX_CHARS:
            return content[:MAX_CHARS] + f'\n[...File "{file_path}" truncated at 10000 characters]'

        return content

    except Exception as e:
        return f"Error: {str(e)}"
