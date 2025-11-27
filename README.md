# 🌊 RawTorrent: Pure Python BitTorrent Engine

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Dependencies](https://img.shields.io/badge/Dependencies-None-green?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)

A fully functional BitTorrent client built entirely from scratch using **only the Python Standard Library**. 

There are no `pip install bencode` or `pip install twisted` shortcuts here. This project implements the BitTorrent Protocol Specification (BEP 0003) manually, handling raw binary data, socket networking, and cryptographic hashing.

It serves as a deep-dive educational implementation of P2P networking concepts.

---

## 🚀 Key Features

*   **Zero External Dependencies:** The core engine uses only `socket`, `struct`, `urllib`, `hashlib`, etc.
*   **Custom Bencode Parser:** A recursive descent parser for decoding `.torrent` files and Tracker responses.
*   **Tracker Communication:** HTTP GET implementation to negotiate with Trackers.
*   **Binary Peer Protocol:** Handles the TCP Handshake and length-prefixed message stream (Bitfield, Choke, Unchoke, Have).
*   **Dockerized:** Runs anywhere with a single command.

---

## 🛠 Architecture

The project is split into modular components:

1.  **`bencoding.py`**: Handles the serialization and deserialization of the Bencode format (Integers, Strings, Lists, Dictionaries).
2.  **`tracker.py`**: Manages URL generation, HTTP requests, and parsing binary peer lists (Compact Mode).
3.  **`client.py`**: A TCP client class that manages individual peer connections, handshakes, and message loops.
4.  **`main.py`**: The orchestrator that ties the components together.

---

## 🔮 Roadmap: The Discord Bot Interface

The next phase of this project is to integrate the Core Engine into a Discord Bot. This will allow users to control the client and visualize the P2P process via chat commands.

*   **Objective:** A "Proof of Concept" demo where users can trigger the download of specific test files (e.g., Debian ISOs).
*   **Status:** *In Development*
*   **Interaction:** Users will be able to see real-time logs of the Handshake and Piece requests in a Discord channel.

---

## 📦 How to Run

### Option 1: Docker (Recommended)
Ensure your environment is clean and isolated.

```bash
# 1. Build the image
docker build -t raw-torrent .
# 2. Run the client
docker run --rm raw-torrent
````

### Option 2: Local Python 
Requires Python 3.9+.
```bash
# Clone the repo
git clone https://github.com/kernelbits/Python-Torrent-Client.git

# Navigate to directory
cd python-torrent

# Run the client
python main.py
```
---

### 📚 Technical Concepts Covered
This project explores several low-level engineering concepts:
  *   **Recursive Parsing:** converting nested binary structures into Python objects.
  *   **Endianness:** Handling Big-Endian vs Little-Endian integers (struct library).
  *   **Socket Programming:** Managing raw TCP connections, timeouts, and data buffering.
  *   **Cryptographic Hashing:** Generating SHA-1 Info Hashes for swarm identification.
  *   **Binary Protocols:** Parsing length-prefixed messaging streams.

---
### ⚠️ Disclaimer
This project is for educational purposes only. It is designed to work with legal, open-source torrent files (like Linux distributions). The Discord bot integration is restricted to specific test files to demonstrate the functionality of the engine.








