from rich import print


def load_web_app_data() -> str:
    file_path = "webAppData.txt"
    try:
        with open(file_path, "r") as file:
            data = file.read().strip()
            if not data:
                print("Error: No data found in the file.")
                exit(1)
            return data
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        exit(1)
