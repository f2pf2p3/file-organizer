from pathlib import Path
import shutil
import os
import json


# =========================================================
# Configuration
# =========================================================

CONFIG_FILE = "config.txt"
HISTORY_FILE = "history.json"

# Stores only the files moved by the most recent organize operation.
last_action: list[tuple[Path, Path]] = []


# =========================================================
# Default automatic file categories
# =========================================================

# These rules are used by Auto Mode.
# Users can add or modify categories here if needed.
AUTO_CATEGORIES = {
    "img": [
        "jpg", "jpeg", "png", "gif", "webp", "bmp",
        "svg", "ico", "tiff", "tif"
    ],

    "video": [
        "mp4", "mkv", "avi", "mov", "wmv", "flv",
        "webm", "m4v"
    ],

    "audio": [
        "mp3", "wav", "flac", "aac", "ogg", "m4a"
    ],

    "document": [
        "txt", "doc", "docx", "odt", "rtf"
    ],

    "pdf": [
        "pdf"
    ],

    "spreadsheet": [
        "xls", "xlsx", "csv", "ods"
    ],

    "presentation": [
        "ppt", "pptx", "odp"
    ],

    "archive": [
        "zip", "rar", "7z", "tar", "gz"
    ],

    "code": [
        "py", "js", "ts", "java", "cpp", "c",
        "h", "hpp", "cs", "go", "rs", "php"
    ],

    "font": [
        "ttf", "otf", "woff", "woff2"
    ],

    "exe": [
        "exe"
    ],
}


# =========================================================
# Load configuration from config.txt
# =========================================================

def load_config(config_path: Path) -> dict[str, list[str]]:
    """Load folder rules from config.txt."""

    config: dict[str, list[str]] = {}

    try:
        with open(
            config_path,
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:
                line = line.strip()

                # Ignore empty lines and comments.
                if not line or line.startswith("#"):
                    continue

                # Ignore invalid configuration lines.
                if "=" not in line:
                    continue

                key, value = line.split("=", 1)

                key = key.strip()
                value = value.strip()

                # Convert extensions into normalized values.
                extensions = [
                    ext.strip().lower().lstrip(".")
                    for ext in value.split(",")
                    if ext.strip()
                ]

                if extensions:
                    config[key] = extensions

    except OSError as error:
        print(
            f"[ERROR] Cannot read config file: {error}"
        )

    return config


# =========================================================
# History Management
# =========================================================

def save_history(script_directory: Path) -> None:
    """
    Save the most recent organize operation to history.json.

    The history contains:
        original = original file location
        current  = current file location
    """

    history_path = script_directory / HISTORY_FILE

    data = [
        {
            "original": str(original_path),
            "current": str(current_path)
        }
        for original_path, current_path in last_action
    ]

    try:
        with open(
            history_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    except OSError as error:
        print(
            f"[ERROR] Cannot save history: {error}"
        )


def load_history(script_directory: Path) -> None:
    """
    Load the most recent organize operation
    from history.json.
    """

    global last_action

    history_path = script_directory / HISTORY_FILE

    # No history file means there is nothing to revert.
    if not history_path.exists():
        last_action = []
        return

    try:
        with open(
            history_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        last_action = []

        # Validate and restore history entries.
        for item in data:

            if not isinstance(item, dict):
                continue

            if "original" not in item:
                continue

            if "current" not in item:
                continue

            original_path = Path(
                item["original"]
            )

            current_path = Path(
                item["current"]
            )

            last_action.append(
                (original_path, current_path)
            )

    except (
        OSError,
        json.JSONDecodeError,
        KeyError,
        TypeError
    ) as error:

        print(
            f"[WARNING] Cannot load history.json: {error}"
        )

        last_action = []


def clear_history(script_directory: Path) -> None:
    """
    Delete history.json when there is no
    remaining action to revert.
    """

    history_path = script_directory / HISTORY_FILE

    try:

        if history_path.exists():
            history_path.unlink()

    except OSError as error:

        print(
            f"[ERROR] Cannot clear history: {error}"
        )


# =========================================================
# Create a folder
# =========================================================

def create_folder(
    base_directory: Path,
    folder_name: str
) -> Path:
    """
    Create one folder inside the target directory.

    Returns the folder path.
    """

    folder_path = base_directory / folder_name

    folder_path.mkdir(
        parents=True,
        exist_ok=True
    )

    return folder_path


# =========================================================
# Create multiple folders
# =========================================================

def create_folders(
    base_directory: Path,
    config: dict[str, list[str]]
) -> None:
    """
    Create all folders defined by the configuration.

    This function is available for cases where the user
    wants every configured folder to exist.
    """

    for folder_name in config:

        folder_path = create_folder(
            base_directory,
            folder_name
        )

        print(
            f"[CREATE] {folder_path}"
        )


# =========================================================
# Find the category of a file
# =========================================================

def find_target_folder(
    extension: str,
    config: dict[str, list[str]]
) -> str | None:
    """
    Find which folder should contain a file extension.
    """

    extension = (
        extension
        .lower()
        .lstrip(".")
    )

    for folder_name, extensions in config.items():

        if extension in extensions:
            return folder_name

    return None


# =========================================================
# Organize files
# =========================================================

def organize_files(
    target_directory: Path,
    config: dict[str, list[str]],
    script_directory: Path
) -> None:
    """
    Move files into folders according to the configuration.

    Only the most recent organize operation can be reverted.
    """

    global last_action

    # Start a new history for the new organize operation.
    last_action = []

    try:
        entries = list(
            target_directory.iterdir()
        )

    except OSError as error:

        print(
            f"[ERROR] Cannot access directory:\n"
            f"{target_directory}\n"
            f"{error}"
        )

        return

    moved_count = 0
    skipped_count = 0

    for file_path in entries:

        # Ignore directories.
        if not file_path.is_file():
            continue

        # Get the file extension.
        extension = (
            file_path.suffix
            .lower()
            .lstrip(".")
        )

        # Ignore files without extensions.
        if not extension:

            print(
                f"[SKIP] {file_path.name} "
                f"- no extension"
            )

            skipped_count += 1
            continue

        # Find the destination folder.
        target_folder = find_target_folder(
            extension,
            config
        )

        # Unknown extensions are skipped.
        if target_folder is None:

            print(
                f"[SKIP] {file_path.name} "
                f"- unknown extension"
            )

            skipped_count += 1
            continue

        # Create the destination folder only when needed.
        destination_folder = create_folder(
            target_directory,
            target_folder
        )

        destination_file = (
            destination_folder / file_path.name
        )

        # Never overwrite an existing file.
        if destination_file.exists():

            print(
                f"[SKIP] {file_path.name} "
                f"- destination already exists"
            )

            skipped_count += 1
            continue

        try:

            # Save original and destination paths.
            original_path = file_path
            new_path = destination_file

            # Move the file.
            shutil.move(
                str(original_path),
                str(new_path)
            )

            # Remember this move for Revert.
            last_action.append(
                (original_path, new_path)
            )

            print(
                f"[MOVE] {file_path.name} "
                f"-> {target_folder}/"
            )

            moved_count += 1

        except OSError as error:

            print(
                f"[ERROR] Cannot move "
                f"{file_path.name}: {error}"
            )

    print()
    print(f"Moved: {moved_count}")
    print(f"Skipped: {skipped_count}")

    # Save the latest operation to disk.
    if last_action:

        save_history(
            script_directory
        )

    else:

        # Remove old history if nothing was moved.
        clear_history(
            script_directory
        )


# =========================================================
# Revert Last Action
# =========================================================

def revert_last_action(
    script_directory: Path
) -> None:
    """
    Revert only the most recent organize operation.

    Successfully reverted files are removed from the history.
    Failed files remain available for another revert attempt.
    """

    global last_action

    # Load history from disk.
    # This allows Revert to work after restarting the program.
    load_history(
        script_directory
    )

    if not last_action:

        print(
            "[ERROR] Nothing to revert."
        )

        return

    print()
    print(
        "Reverting last action..."
    )
    print()

    reverted_count = 0
    failed_count = 0

    remaining_actions = []

    # Reverse the list so files are restored
    # in the opposite order from the move operation.
    for original_path, current_path in reversed(
        last_action
    ):

        # Current file no longer exists.
        if not current_path.exists():

            print(
                f"[SKIP] File not found: "
                f"{current_path.name}"
            )

            failed_count += 1

            remaining_actions.append(
                (original_path, current_path)
            )

            continue

        # Original location already contains a file.
        if original_path.exists():

            print(
                f"[SKIP] Original file already exists: "
                f"{original_path.name}"
            )

            failed_count += 1

            remaining_actions.append(
                (original_path, current_path)
            )

            continue

        try:

            # Move the file back to its original location.
            shutil.move(
                str(current_path),
                str(original_path)
            )

            print(
                f"[REVERT] {current_path.name}"
                f" <- {original_path.parent}"
            )

            reverted_count += 1

        except OSError as error:

            print(
                f"[ERROR] Cannot revert "
                f"{current_path.name}: {error}"
            )

            failed_count += 1

            # Keep failed action for another attempt.
            remaining_actions.append(
                (original_path, current_path)
            )

    # Keep only failed actions.
    last_action = remaining_actions

    # Update history on disk.
    if last_action:

        save_history(
            script_directory
        )

    else:

        clear_history(
            script_directory
        )

    print()
    print(f"Reverted: {reverted_count}")
    print(f"Failed: {failed_count}")


# =========================================================
# Get Common Windows Directories
# =========================================================

def get_common_directories() -> dict[str, Path]:
    """
    Get common directories for the current Windows user.

    Only directories that actually exist are returned.
    """

    home = Path.home()

    directories = {
        "Desktop": home / "Desktop",
        "Documents": home / "Documents",
        "Downloads": home / "Downloads",
        "Pictures": home / "Pictures",
        "Music": home / "Music",
        "Videos": home / "Videos",
        "Favorites": home / "Favorites",
        "Contacts": home / "Contacts",
        "Links": home / "Links",
        "Saved Games": home / "Saved Games",
        "Searches": home / "Searches",
    }

    # Only return directories that actually exist.
    return {
        name: path
        for name, path in directories.items()
        if path.is_dir()
    }


# =========================================================
# Resolve Directory
# =========================================================

def resolve_directory(
    path: str
) -> Path:
    """
    Convert user input into an absolute directory path.

    Supported examples:

        Downloads
        Desktop
        Documents
        %USERPROFILE%\\Downloads
        C:\\Users\\Username\\Downloads
        ../Downloads
        ~/Downloads
    """

    # Remove spaces and surrounding quotes.
    path = (
        path
        .strip()
        .strip('"')
        .strip("'")
    )

    if not path:
        return Path()

    # Allow common folder names.
    common_directories = (
        get_common_directories()
    )

    for name, directory in (
        common_directories.items()
    ):

        if path.lower() == name.lower():
            return directory.resolve()

    # Expand Windows environment variables.
    path = os.path.expandvars(path)

    # Expand ~ and resolve relative paths.
    return (
        Path(path)
        .expanduser()
        .resolve()
    )


# =========================================================
# Ask User for Target Directory
# =========================================================

def ask_for_directory() -> Path | None:
    """
    Display common directories and allow the user
    to select one or enter a custom path.
    """

    directories = (
        get_common_directories()
    )

    print()
    print(
        "Available directories:"
    )
    print()

    # Convert dictionary to a list for numbered options.
    items = list(
        directories.items()
    )

    for index, (name, path) in enumerate(
        items,
        start=1
    ):

        print(
            f"  {index}. {name}"
        )

        print(
            f"     {path}"
        )

        print()

    # Add Custom Path after common directories.
    custom_option = (
        len(items) + 1
    )

    print(
        f"  {custom_option}. Custom Path"
    )

    print()

    print(
        "-" * 55
    )

    choice = input(
        f"Select directory [1-{custom_option}]: "
    ).strip()

    # -----------------------------------------------------
    # Custom path
    # -----------------------------------------------------

    if choice == str(custom_option):

        custom_path = input(
            "\nEnter directory path: "
        ).strip()

        if not custom_path:

            print(
                "[ERROR] Directory cannot be empty."
            )

            return None

        try:

            target_directory = (
                resolve_directory(
                    custom_path
                )
            )

        except (
            OSError,
            RuntimeError
        ) as error:

            print(
                f"[ERROR] Cannot resolve path: "
                f"{error}"
            )

            return None

    # -----------------------------------------------------
    # Selected common directory
    # -----------------------------------------------------

    else:

        try:

            index = (
                int(choice) - 1
            )

            if (
                index < 0
                or index >= len(items)
            ):

                print(
                    "[ERROR] Invalid directory selection."
                )

                return None

            target_directory = (
                items[index][1].resolve()
            )

        except ValueError:

            print(
                "[ERROR] Please enter a valid number."
            )

            return None

    # -----------------------------------------------------
    # Validate directory
    # -----------------------------------------------------

    if not target_directory.exists():

        print(
            f"[ERROR] Directory does not exist:\n"
            f"{target_directory}"
        )

        return None

    if not target_directory.is_dir():

        print(
            f"[ERROR] Path is not a directory:\n"
            f"{target_directory}"
        )

        return None

    print()
    print(
        f"Selected: {target_directory}"
    )

    # Ask for confirmation before using the selected directory.
    while True:

        confirmation = input(
            "\nConfirm this directory? [Y/N]: "
        ).strip().lower()

        if confirmation in (
            "y",
            "yes"
        ):

            return target_directory

        if confirmation in (
            "n",
            "no"
        ):

            print(
                "[CANCELLED] "
                "Directory selection cancelled."
            )

            return None

        print(
            "[ERROR] Please enter Y or N."
        )


# =========================================================
# Config Mode
# =========================================================

def config_mode(
    script_directory: Path
) -> None:
    """
    Organize files using config.txt.

    The current user's home directory is detected automatically.
    """

    config_path = (
        script_directory / CONFIG_FILE
    )

    config = load_config(
        config_path
    )

    if not config:

        print(
            "[ERROR] No valid rules found "
            "in config.txt."
        )

        return

    # Detect the current user's home directory automatically.
    target_directory = (
        Path.home() / "Downloads"
    )

    if not target_directory.exists():

        print(
            f"[ERROR] Target directory not found: "
            f"{target_directory}"
        )

        return

    print()
    print(
        f"Username: {Path.home().name}"
    )

    print(
        f"Target directory: "
        f"{target_directory}"
    )

    print()

    organize_files(
        target_directory,
        config,
        script_directory
    )


# =========================================================
# Auto Mode
# =========================================================

def auto_mode(
    script_directory: Path
) -> None:
    """
    Automatically organize files using AUTO_CATEGORIES.

    Only categories that actually contain files are created.
    """

    target_directory = (
        ask_for_directory()
    )

    if target_directory is None:
        return

    print()
    print(
        f"Target directory: "
        f"{target_directory}"
    )

    print()
    print(
        "Scanning files..."
    )

    # Find only categories that actually have files.
    found_categories = set()

    try:

        entries = list(
            target_directory.iterdir()
        )

    except OSError as error:

        print(
            f"[ERROR] Cannot access directory:\n"
            f"{target_directory}\n"
            f"{error}"
        )

        return

    for file_path in entries:

        if not file_path.is_file():
            continue

        extension = (
            file_path.suffix
            .lower()
            .lstrip(".")
        )

        if not extension:
            continue

        category = find_target_folder(
            extension,
            AUTO_CATEGORIES
        )

        if category:
            found_categories.add(
                category
            )

    print()

    if not found_categories:

        print(
            "No recognized files found."
        )

        return

    print(
        "Folders that will be created:"
    )

    for category in sorted(
        found_categories
    ):

        print(
            f"  - {category}/"
        )

    print()

    # organize_files() creates the folders
    # only when files actually need to be moved.
    organize_files(
        target_directory,
        AUTO_CATEGORIES,
        script_directory
    )


# =========================================================
# Terminal UI
# =========================================================

def clear_terminal() -> None:
    """
    Clear the terminal screen.

    Works on Windows and Unix-like terminals.
    """

    if os.name == "nt":

        os.system("cls")

    else:

        os.system("clear")


def print_header() -> None:
    """
    Display the main application header.
    """

    print(
        "=" * 55
    )

    print(
        "                 FILE ORGANIZER"
    )

    print(
        "=" * 55
    )


def wait_for_enter() -> None:
    """
    Wait for the user before returning to the main menu.
    """

    input(
        "\nPress Enter to return to the menu..."
    )


# =========================================================
# Main Menu
# =========================================================

def main() -> None:
    """
    Main application loop.

    The program keeps running until the user selects Exit.
    """

    # Get the directory containing this Python script.
    script_directory = (
        Path(__file__).resolve().parent
    )

    while True:

        # Clear the previous screen before showing the menu.
        clear_terminal()

        print_header()

        print()

        print(
            "  1. Config Mode"
        )

        print(
            "  2. Auto Mode"
        )

        print(
            "  3. Revert Last Action"
        )

        print(
            "  4. Exit"
        )

        print()

        print(
            "-" * 55
        )

        choice = input(
            "  Select option [1-4]: "
        ).strip()

        # -------------------------------------------------
        # Config Mode
        # -------------------------------------------------

        if choice == "1":

            clear_terminal()

            print_header()

            print()

            print(
                "  [ CONFIG MODE ]"
            )

            print()

            config_mode(
                script_directory
            )

            wait_for_enter()

        # -------------------------------------------------
        # Auto Mode
        # -------------------------------------------------

        elif choice == "2":

            clear_terminal()

            print_header()

            print()

            print(
                "  [ AUTO MODE ]"
            )

            print()

            auto_mode(
                script_directory
            )

            wait_for_enter()

        # -------------------------------------------------
        # Revert Last Action
        # -------------------------------------------------

        elif choice == "3":

            clear_terminal()

            print_header()

            print()

            print(
                "  [ REVERT LAST ACTION ]"
            )

            print()

            revert_last_action(
                script_directory
            )

            wait_for_enter()

        # -------------------------------------------------
        # Exit
        # -------------------------------------------------

        elif choice == "4":

            clear_terminal()

            print_header()

            print()

            print(
                "  Goodbye."
            )

            print()

            break

        # -------------------------------------------------
        # Invalid option
        # -------------------------------------------------

        else:

            print()

            print(
                "  [ERROR] Invalid option."
            )

            print(
                "  Please select 1, 2, 3, or 4."
            )

            wait_for_enter()


# =========================================================
# Program Entry Point
# =========================================================

if __name__ == "__main__":
    main()