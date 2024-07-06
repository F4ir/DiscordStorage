import os
import shutil
import requests
import subprocess
import time

# Define the current version
current_version = "v0.5"

# URL to check the latest version
version_url = "https://raw.githubusercontent.com/F4ir/DiscordStorage-Updater/main/version"

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

def make_folder_visible(directory, folder_name):
    try:
        subprocess.run(["attrib", "-h", os.path.join(directory, folder_name)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error making {folder_name} visible: {e}")

def wait_for_git_deletion(directory):
    while os.path.exists(os.path.join(directory, ".git")):
        print(".git folder still exists. Please delete it manually.")
        time.sleep(2)

def clear_directory(directory):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            print(f"Failed to delete {item_path}. Reason: {e}")

def is_directory_empty(directory):
    return len(os.listdir(directory)) == 0

def clone_repository(repo_url, directory):
    try:
        subprocess.run(["git", "clone", repo_url, directory], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error cloning the repository: {e}")

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
    choice = input("Do you want to update to the latest version? (Y/N): ").strip().lower()

    if choice != 'y':
        print("Update canceled.")
        return

    if os.path.exists(git_folder):
        print(".git folder exists. Making it visible.")
        make_folder_visible(current_directory, ".git")
        print("You need to have git installed to update, you can install it at: https://git-scm.com/download/win")
        input("Press any key to continue...")

        print("Please delete the .git folder manually.")
        wait_for_git_deletion(current_directory)

    print(f"Updating from version {current_version} to {latest_version}.")

    # Clear the directory
    clear_directory(current_directory)

    # Wait until the directory is empty
    while not is_directory_empty(current_directory):
        time.sleep(0.5)

    # Clone the repository into the current directory
    clone_repository(repo_url, current_directory)

    print("Update completed successfully.")

if __name__ == "__main__":
    main()
    input("Press Enter to close...")  # Keeps the command prompt open
