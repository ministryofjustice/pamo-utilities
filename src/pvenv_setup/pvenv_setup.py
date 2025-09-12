import subprocess
from ipykernel.kernelspec import install as install_ipykernel
from pathlib import Path
import sys

def install_kernel(kernel_name):
    
    # Installs a kernelspec for the current Python environment
    install_ipykernel(
        user=True,
        display_name=kernel_name,
        # prefix=None, env=None  # optional: use if you need a custom install location or env vars
    )
    
    print(f"Kernel '{kernel_name}' installed successfully via API.")


def confirm_overwrite(path: Path) -> bool:
    if not path.exists():
        return True  # Nothing to overwrite

    while True:
        resp = input(f"File '{path}' already exists. Overwrite? [y/N]: ").strip().lower()
        if resp in ("y", "yes"):
            return True
        if resp in ("n", "no", ""):
            print("Not overwriting.")
            return False
        print("Please enter 'y' or 'n'.")

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
# Install pamo-utilities
subprocess.run([sys.executable, "-m", "pip", "install", "git+https://github.com/ministryofjustice/pamo-utilities.git"], check=True)

# Activate the virtual environment
print("\nActivating virtual environment...")
subprocess.run(["poetry", "env", "activate"], check=True)

# Check working in virtual environment
subprocess.run(["poetry", "env", "info"], check=True)

# Install kernel for use by Jupyter notebooks
print("\nAdding Jupyter kernel...")
cwd = Path.cwd().resolve().name
install_kernel("pvenv_" + cwd)
