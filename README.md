# 🔍 Network Scanner

A lightweight Python-based network scanning tool that uses **nmap** under the hood. Built with a Tkinter GUI for desktop use, and easily adaptable to a CLI interface for headless/server environments.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [GUI Mode](#gui-mode)
  - [CLI Mode (No Display / Lab Environments)](#cli-mode-no-display--lab-environments)
- [Sample Output](#sample-output)
- [Project Structure](#project-structure)
- [Known Issues](#known-issues)
- [Legal Disclaimer](#legal-disclaimer)
- [License](#license)

---

## Overview

Network Scanner is a Python application that wraps the powerful `nmap` command-line tool inside a clean interface. Enter any IP address or hostname, click **Scan Network**, and get a fast port scan result in seconds.

---

## Features

- Fast port scanning using `nmap -F` (top 100 ports)
- Clean Tkinter GUI with input field and result display area
- Graceful error handling — the app never crashes on bad input or unreachable hosts
- CLI fallback for environments without a display server (servers, labs, WSL)

---

## Prerequisites

- Python 3.x
- `nmap` installed on the system
- `tkinter` (bundled with Python on most systems; separate install on Linux)
- `python-nmap` Python library (optional, for programmatic nmap access)

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/MukeshKumarCloud/Network-Scanner.git
cd network-scanner

# 2. Update package lists and install system dependencies
sudo apt update
sudo apt-get install nmap -y
sudo apt-get install python3-tk -y

# 3. Install Python dependencies
sudo pip install python-nmap
```

---

## Usage

### GUI Mode

Requires a display environment (desktop OS, X11 forwarding, etc.).

```bash
python network_scanner.py
```

1. Enter an IP address or hostname in the input field (e.g., `45.33.32.156` or `scanme.nmap.org`)
2. Click the **Scan Network** button
3. View results in the text area below

### CLI Mode (No Display / Lab Environments)

If your environment has no GUI (servers, cloud labs, WSL without X11), use the CLI version:

```python
import subprocess

def scan_network(ip_address):
    print(f"Scanning network: {ip_address}\n")
    try:
        output = subprocess.check_output(["nmap", "-F", ip_address])
        print(output.decode("utf-8"))
    except subprocess.CalledProcessError:
        print("An error occurred while scanning the network.")
    except FileNotFoundError:
        print("nmap is not installed. Run: sudo apt install nmap")

ip = input("Enter IP Address: ")
scan_network(ip)
```

---

## Sample Output

```
Scanning network: 45.33.32.156

Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-15 11:42 +0530
Nmap scan report for scanme.nmap.org (45.33.32.156)
Host is up (0.39s latency).
Not shown: 92 closed tcp ports (reset)
PORT    STATE    SERVICE
22/tcp  open     ssh
25/tcp  filtered smtp
80/tcp  open     http
135/tcp filtered msrpc
139/tcp filtered netbios-ssn
179/tcp filtered bgp
445/tcp filtered microsoft-ds
646/tcp filtered ldp

Nmap done: 1 IP address (1 host up) scanned in 8.77 seconds
```

---

## Project Structure

```
network-scanner/
│
├── network_scanner.py   # Main application (GUI version)
└── README.md            # Project documentation
```

---

## Known Issues

| Issue | Cause | Fix |
|---|---|---|
| `_tkinter.TclError: no display name and no $DISPLAY environment variable` | Running GUI in a headless environment (server/lab) | Use the CLI version instead |
| `nmap: command not found` | nmap not installed | Run `sudo apt-get install nmap -y` |
| `An error occurred while scanning the network.` | Invalid IP, unreachable host, or permission error | Verify IP and try with `sudo` |

---

## Legal Disclaimer

> ⚠️ **Only scan networks and IP addresses you own or have explicit written permission to scan.**
>
> Unauthorized port scanning may be **illegal** under laws such as the Computer Fraud and Abuse Act (USA), the IT Act (India), and similar legislation in other countries.
>
> For safe, legal practice, use the officially authorized target maintained by the Nmap project:
> - **Host:** `scanme.nmap.org`
> - **IP:** `45.33.32.156`
>
> Scanning your own machine (`127.0.0.1`) is always safe.

---

## License

This project is open source and available under the [MIT License](LICENSE).

