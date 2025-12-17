import subprocess, json
from ipykernel.kernelspec import install as install_ipykernel
from pathlib import Path
import sys, os

from colorama import init, Fore, Style
init()

def get_venv_for_cwd():
    """
    Find any poetry virtual environments that may match the current working directory.
    Args: None
    Returns: 
    matching_folders (list): List of folder names that match the current working directlory.
    """
    # Get the current working directory name
    cwd_name = os.path.basename(os.getcwd())
    
    # Path to Poetry virtualenvs cache
    poetry_cache_path = os.path.expanduser("~/.cache/pypoetry/virtualenvs")
    
    # Check if the directory exists
    if not os.path.exists(poetry_cache_path):
        print("Poetry virtualenvs directory not found. You may need to reinstall the virtual environment.")
    else:
        # Search for folders containing the current directory name
        matching_folders = [
            folder for folder in os.listdir(poetry_cache_path)
            if cwd_name in folder and os.path.isdir(os.path.join(poetry_cache_path, folder))
        ]
    return matching_folders
    
def install_kernel(kernel_name):
    """
    Installs JupyterLab kernel using installed virtual environment.
    Args: 
    kernel_name (str): Name of kernel to be installed.
    Returns: None
    """    
    display_name = "ipyk_" + kernel_name
    # Installs a kernelspec for the current Python environment
    venv_path = subprocess.run(["poetry", "env", "info", "-p"], capture_output=True, text=True).stdout[:-1]
    print("Virtual environment path: ", venv_path)

    py = venv_path + "/bin/python"
    cmd = [py, "-m", "ipykernel", "install", "--user", "--name", kernel_name, "--display-name", display_name]
    rc, out, err = run(cmd)
    msg = ""
    if rc != 0:
        msg = (
            "Failed to register ipykernel.\n"
            f"Command: {subprocess.list2cmdline(cmd)}\n"
            f"STDOUT:\n{out}\nSTDERR:\n{err}"
        )
    
    else:
        msg = (
            f"Kernel installed.\n"
            f"  Name:         {kernel_name}\n"
            f"  Display name: {display_name}\n"
            f"  Python:       {py}\n"
            f"Tip: In JupyterLab, choose Kernel → Change Kernel → '{kernel_name}'."
        )
        print(msg)

def confirm_overwrite(path: Path) -> bool:
    """
    Give uiser option to overwrite existing folder if it exists.
    Args:
    path (path): Folder path
    Returns:
    Boolean: True or False
    """
    if not path.exists():
        return True  # Nothing to overwrite

    while True:
        resp = input(Fore.YELLOW + f"File '{path}' already exists. Overwrite? [y/n]: ").strip().lower()
        if resp in ("n", "no", ""):
            print("Not overwriting." + Style.RESET_ALL)
            return False
        else:
            print("Overwriting." + Style.RESET_ALL)
            os.remove(path)
            return True

def run(cmd_list):
    """
    Helper to run a command and capture output
    Args:
    cmd_list (list): List of command parts to be run.
    Returns:
    str: Errorcode or command result.
    """
    try:
        proc = subprocess.run(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError as e:
        return 127, "", str(e)
    except Exception as e:
        return 1, "", str(e)

def install_venv():
    """
    Install poetry virtual environment and specified packacges.
    Args: None.
    Returns: None.
    """
    # Install poetry
    subprocess.run(["pip", "install", "poetry"], check=True)
    
    # Initialize poetry in the current directory
    if confirm_overwrite(Path('pyproject.toml')):
        subprocess.run(["poetry", "init", "--python", ">=3.12,<4.0", "--no-interaction"], check=True)
    
    # Add dependencies - required packages
    subprocess.run(["poetry", "add", "ipykernel"], check=True)
    
    # Add dependencies - common packages
    subprocess.run(["poetry", "add", "pandas"], check=True)
    subprocess.run(["poetry", "add", "pandasql"], check=True)
    subprocess.run(["poetry", "add", "numpy"], check=True)
    subprocess.run(["poetry", "add", "pytest"], check=True)
    subprocess.run(["poetry", "add", "toml"], check=True)
    subprocess.run(["poetry", "add", "pydbtools"], check=True)
    subprocess.run(["poetry", "add", "xlsxwriter"], check=True)
    subprocess.run(["poetry", "add", "fsspec"], check=True)
    subprocess.run(["poetry", "add", "s3fs"], check=True)
    subprocess.run(["poetry", "add", "openpyxl"], check=True)

    # Install pamo-utilities
    subprocess.run(["poetry", "add", "git+https://github.com/ministryofjustice/pamo-utilities.git"], check=True)
    # Install pamo-report-builder
    subprocess.run(["poetry", "add", "git+https://github.com/ministryofjustice/pamo-report-builder.git"], check=True)
    
    install_jupyter_kernel()

def install_jupyter_kernel():
    """
    Install a Jupyter kernel for the poetry virtual environment.
    Args: None.
    Returns: None.
    """
    
    # Install kernel for use by Jupyter notebooks
    print(Fore.GREEN + "\nAdding Jupyter kernel...")
    cwd = Path.cwd().resolve().name
    install_kernel("pvenv_" + cwd)
    print(Style.RESET_ALL)

def initiate_pvenv_setup():
    """
    Check if a virtual environment already exists for this working directory.
    Args: None.
    Returns: None.
    """
    # Present the user with a numbered list of found folders, or reinstall option.
    matching_folders = get_venv_for_cwd()
    if matching_folders:
        print(Fore.YELLOW + "Found the following matching virtual environment folders:" + Style.RESET_ALL)
        for i, folder in enumerate(matching_folders, start=1):
            print(f"{i}. {folder}")
        print("0. Reinstall the virtual environment")
    
        # Prompt user for selection
        choice = input("Select a virtual environment folder by number or enter 0 to reinstall: ")
        try:
            choice = int(choice)
            if choice == 0:
                print("You chose to reinstall the virtual environment.")
                # Reinstall virtual environment
                install_venv()
    
            elif 1 <= choice <= len(matching_folders):
                selected_folder = matching_folders[choice - 1]
                print(f"You selected: {selected_folder}")
                # Activate the virtual environment for the working folder
                install_jupyter_kernel()
         
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a valid number.")
    else:
        print(Fore.YELLOW + "No matching virtualenv folders found. Installing the virtual environment." + Style.RESET_ALL)
        install_venv()

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    # Ensure folder name is appropriate and has no spaces or special characters in it other than hypen or underscore.
    initiate_pvenv_setup()

    # Provide tip for user on how to activate the virtual environment
    venv_path = subprocess.run(["poetry", "env", "info", "-p"], capture_output=True, text=True).stdout[:-1]
    print(Fore.YELLOW + "\nActivate the virtual environment by running the command below:\n")
    print("source " + venv_path + "/bin/activate\n\n")  
    print("To subsequently deactivate the environment run the command: \n")
    print("deactivate\n")
    print(Style.RESET_ALL)
    






