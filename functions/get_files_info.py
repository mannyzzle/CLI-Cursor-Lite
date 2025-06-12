import os

def get_files_info(working_directory, directory=None):
    try:
        target_dir = os.path.abspath(os.path.join(working_directory, directory or "."))
        base_dir = os.path.abspath(working_directory)

        if not target_dir.startswith(base_dir):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        entries = []
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            is_dir = os.path.isdir(item_path)
            try:
                file_size = os.path.getsize(item_path)
                entries.append(f'- {item}: file_size={file_size} bytes, is_dir={is_dir}')
            except Exception as e:
                entries.append(f'- {item}: Error reading file size: {str(e)}')

        return "\n".join(entries)

    except Exception as e:
        return f'Error: {str(e)}'


