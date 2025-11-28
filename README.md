Obsidian Local Brain: Private RAG & Active Recall Agent

Turn your passive notes into an active study partner. A fully local, privacy-first automation pipeline that connects your Obsidian Vault to a local LLM (Llama 3.2 Vision) via Docker.

The Concept

As a Cybersecurity student, I take hundreds of notes (Penetration Testing, Network Forensics, etc.). However, taking notes is passive. Remembering them is active.

I built this tool to automate Spaced Repetition and Active Recall without sending my private data to the cloud.

How it works:

Productivity Analysis: The script scans my vault daily to check how many words I wrote (Productivity Score).

Weighted Selection: It selects 3 notes from "Today" and 2 notes from "Last Month" to force spaced repetition.

Local RAG: It feeds these notes into a local Dockerized LLM (Ollama).

Exam Generation: The AI acts as a strict examiner, generating a Markdown-formatted quiz with Hidden Answers and Backlinks to the original source.

Feedback Loop: If I tag a question as #missed, the system detects my weakness and re-tests me on that topic later.


 Features

100% Privacy: No API keys, no data leaves the localhost.

Multimodal Ready: Supports extracting text from images using Llama 3.2 Vision.

Dynamic Difficulty:

High Activity Day (>500 words): Generates a "Deep Work" exam (10 questions).

Low Activity Day: Generates a "Maintenance" quiz (5 questions).

Interactive UI: Uses Obsidian Callouts and Collapsible Admonitions for a clean "App-like" experience inside Markdown.


Setup Guide

1. Prerequisites

Docker Desktop (WSL2 Backend enabled for Windows).

NVIDIA GPU (Recommended for inference speed).

Python 3.10+

2. Infrastructure Setup (Docker)

We use Docker to isolate the AI environment. Run this to spin up the brain:

# Run Ollama with GPU Passthrough
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name obsidian-brain ollama/ollama

# Download the Model
docker exec -it obsidian-brain ollama run llama3.2-vision



3. Installation

Clone the repository and install dependencies:

git clone [https://github.com/YOUR_USERNAME/Obsidian-Local-Brain.git](https://github.com/YOUR_USERNAME/Obsidian-Local-Brain.git)
cd Obsidian-Local-Brain
pip install -r requirements.txt



4. Configuration

Open daily_brain.py and update the VAULT_PATH variable to point to your local Obsidian folder:

# daily_brain.py
VAULT_PATH = r"C:\Users\YourName\Documents\Obsidian Vault"



5. Automation

Windows: Use Task Scheduler to run python daily_brain.py daily at 06:00 AM.

Linux/Mac: Use crontab -e -> 0 6 * * * /usr/bin/python3 /path/to/daily_brain.py.

📸 Output Example

The script generates a file like Daily Quiz - 2025-11-28.md inside your vault:

<img width="730" height="880" alt="image" src="https://github.com/user-attachments/assets/3016d192-f8de-4918-ab9b-f40c08d365db" />


Security Note

This project was built with SecOps principles:

Docker container isolation.

No external API calls (Air-gap compatible).

Sanitized inputs to prevent prompt injection from malicious notes.

Contributing

Feel free to fork this project and add features like "PDF Parsing" or "Anki Integration"!
