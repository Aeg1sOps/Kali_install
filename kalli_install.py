#!/usr/bin/env python3
import subprocess
import os

def main():
    logo = r"""
    █████████                     ████             ███████                     
  ███▒▒▒▒▒███                   ▒▒███           ███▒▒▒▒▒███                   
 ▒███    ▒███   ██████   ███████ ▒███   █████  ███     ▒▒███ ████████   █████ 
 ▒███████████  ███▒▒███ ███▒▒███ ▒███  ███▒▒  ▒███      ▒███▒▒███▒▒███ ███▒▒  
 ▒███▒▒▒▒▒███ ▒███████ ▒███ ▒███ ▒███ ▒▒█████ ▒███      ▒███ ▒███ ▒███▒▒█████ 
 ▒███    ▒███ ▒███▒▒▒  ▒███ ▒███ ▒███  ▒▒▒▒███▒▒███     ███  ▒███ ▒███ ▒▒▒▒███
 █████   █████▒▒██████ ▒▒███████ █████ ██████  ▒▒▒███████▒   ▒███████  ██████ 
▒▒▒▒▒   ▒▒▒▒▒  ▒▒▒▒▒▒   ▒▒▒▒▒███▒▒▒▒▒ ▒▒▒▒▒▒     ▒▒▒▒▒▒▒     ▒███▒▒▒  ▒▒▒▒▒▒  
                        ███ ▒███                             ▒███             
                       ▒▒██████                              █████            
                        ▒▒▒▒▒▒                              ▒▒▒▒▒             
                                                                             
"""                                                                         
    print(logo)

if __name__ == "__main__":
    main()


def run_cmd(command):
    """Run a shell command and print errors if any """
    try:
        print(f"\n[+] Running: {command}")
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Error while executing: {e}")

def system_update():
    """Update and upgrade the system before installations."""
    print("\n=== Updating and Upgrading System Packages ===")
    run_cmd("sudo apt-get update -y")
    run_cmd("sudo apt-get upgrade -y")

def install_chrome():
    print("\n=== Installing Google Chrome ===")
    run_cmd("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb")
    run_cmd("sudo apt install -y /tmp/chrome.deb")
    # Cleanup
    run_cmd("rm -f /tmp/chrome.deb")

def install_vscode():
    print("\n=== Installing Visual Studio Code ===")
    run_cmd("wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/microsoft.gpg")
    run_cmd("sudo install -o root -g root -m 644 /tmp/microsoft.gpg /etc/apt/trusted.gpg.d/")
    run_cmd('sudo sh -c \'echo "deb [arch=amd64] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list\'')
    run_cmd("sudo apt update && sudo apt install -y code")
    # Cleanup
    run_cmd("rm -f /tmp/microsoft.gpg")
    run_cmd("sudo rm -f /etc/apt/sources.list.d/vscode.list")

def install_tor():
    print("\n=== Installing Tor Browser ===")
    run_cmd("sudo apt update && sudo apt install -y tor torbrowser-launcher")

if __name__ == "__main__":
    print("=== Kali Linux Installation Script ===")
    system_update()
    install_chrome()
    install_vscode()
    install_tor()
    print("\n✅ Installation completed successfully! Sources and temp files have been cleaned up.")

