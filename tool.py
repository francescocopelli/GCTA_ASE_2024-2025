import os

EXCLUDED_DIRS = {".git", ".postman", ".vent", ".vscode"}

def convert_crlf_to_lf(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()

        # Sostituzione CRLF con LF
        new_content = content.replace(b'\r\n', b'\n')

        with open(file_path, 'wb') as f:
            f.write(new_content)

        print(f"[SUCCESS] Converted CRLF to LF for: {file_path}")
    except Exception as e:
        print(f"[ERROR] there was an error during convertion of {file_path}: {e}")

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        # Rimuovi le directory escluse
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            if file.endswith(".sh"):  # Considera solo i file con estensione .sh
                file_path = os.path.join(root, file)
                convert_crlf_to_lf(file_path)

current_directory = os.getcwd()
process_directory(current_directory)