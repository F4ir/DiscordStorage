import os
import shutil
import requests
import subprocess
import time
import tempfile
import stat

# Define the current version
current_version = "v0.7"

# URL to check the latest version
version_url = "https://raw.githubusercontent.com/F4ir/DiscordStorage/main/version.version"

# URL of the GitHub repository to download
repo_url = "https://github.com/F4ir/DiscordStorage.git"
repo_name = "DiscordStorage"  # Name of the repository

def get_latest_version(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Error checking the latest version: {e}")
        return None

def make_folder_writable(directory, folder_name):
    folder_path = os.path.join(directory, folder_name)
    for root, dirs, files in os.walk(folder_path):
        for d in dirs:
            os.chmod(os.path.join(root, d), stat.S_IWRITE)
        for f in files:
            os.chmod(os.path.join(root, f), stat.S_IWRITE)
    os.chmod(folder_path, stat.S_IWRITE)

def hide_folder(directory, folder_name):
    folder_path = os.path.join(directory, folder_name)
    try:
        subprocess.run(["attrib", "+h", folder_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error hiding {folder_name} folder: {e}")

def clear_directory(directory):
    for item in os.listdir(directory):
        if item in ["downloads", "configs"]:
            continue
        item_path = os.path.join(directory, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            print(f"Failed to delete {item_path}. Reason: {e}")

def is_directory_empty(directory):
    for item in os.listdir(directory):
        if item not in ["downloads", "configs"]:
            return False
    return True

def clone_repository(repo_url, temp_directory):
    try:
        subprocess.run(["git", "clone", repo_url, temp_directory], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error cloning the repository: {e}")

def move_contents(src, dst):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

def main():
    # Get the current working directory
    current_directory = os.getcwd()

    # Check if .git folder exists
    git_folder = os.path.join(current_directory, ".git")

    # Get latest version from URL
    latest_version = get_latest_version(version_url)

    if latest_version is None:
        print("Could not determine the latest version.")
        return

    if current_version == latest_version:
        print("The version is up to date.")
        return

    print("Update detected.")
    print("")
    print("You need to have Git installed to update.")
    print("You can install Git at: https://git-scm.com/download/win")
    print("")
    choice = input("Do you want to update to the latest version? (Y/N): ").strip().lower()

    if choice != 'y':
        print("Update canceled.")
        return

    if os.path.exists(git_folder):
        print(".git folder exists. Making it writable.")
        make_folder_writable(current_directory, ".git")

        # Now delete the .git folder
        print("Deleting the .git folder.")
        try:
            shutil.rmtree(git_folder)
        except Exception as e:
            print(f"Failed to delete {git_folder}. Reason: {e}")
            return

    print(f"Updating from version {current_version} to {latest_version}.")

    # Clear the directory
    clear_directory(current_directory)

    # Wait until the directory is empty
    while not is_directory_empty(current_directory):
        time.sleep(0.5)

    # Clone the repository into a temporary directory
    with tempfile.TemporaryDirectory() as temp_directory:
        clone_repository(repo_url, temp_directory)

        # Move the contents of the temporary directory to the current directory
        move_contents(temp_directory, current_directory)

    # Hide the .git folder if it exists
    if os.path.exists(git_folder):
        hide_folder(current_directory, ".git")

    print("Update completed successfully.")

if __name__ == "__main__":
    main()
    input("Press Enter to close...")  # Keeps the command prompt open
