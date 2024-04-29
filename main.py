import subprocess
import sys
import os
import re

def install_requirements(requirements_file):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("Requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error: Failed to install requirements.")
        print(e)

def run_script():
    # Check if Python 3.11 is installed
    if sys.version_info >= (3, 11):
        # If installed, run the script in src folder
        requirements_file = "requirements.txt"  # Change this to the path of your requirements.txt file
        install_requirements(requirements_file)
        subprocess.run([sys.executable, os.path.join("src", "bharat_dns_server.py")])
    else:
        print("Python 3.11 is not installed. Installing...")

        # Determine the appropriate installation command based on the operating system
        if sys.platform == "darwin":  # macOS
            install_command = "brew install python@3.11"
        elif sys.platform == "win32":  # Windows
            install_command = "choco install python --version=3.11"
        elif sys.platform.startswith("linux"):  # Linux
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    os_info = f.read()
                if "ubuntu" in os_info.lower():
                    install_command = "sudo apt update && sudo apt install python3.11"
                elif "fedora" in os_info.lower():
                    install_command = "sudo dnf install python3.11"
                elif "centos" in os_info.lower() or "rhel" in os_info.lower():
                    install_command = "sudo yum install python3.11"
                else:
                    print("Unsupported Linux distribution. Please install Python 3.11 manually.")
                    return
            else:
                print("Unknown Linux distribution. Please install Python 3.11 manually.")
                return
        else:
            print("Unsupported operating system. Please install Python 3.11 manually.")
            return

        # Run the installation command
        subprocess.run(install_command, shell=True)
        print("Python 3.11 installed successfully. Running the script...")
        # Now, Python 3.11 should be installed, so run the script
        subprocess.run([sys.executable, os.path.join("src", "harat_dns_server.py")])

if __name__ == "__main__":
    run_script()
