# Google Dorking Automation Tool

A modular, extensible, and production-grade Python package to legally and ethically automate Google-dork queries. This tool allows for both deep, single-query research and large-scale reconnaissance using Google's standard search and the Custom Search Engine (CSE) API.

## Features

- **Dual Search Modes**: Switch between standard Google Search (`--google`) and the efficient Google CSE API (`--cse`).
- **Interactive Runner**: A beginner-friendly `runner.py` script that guides you through every step.
- **Automated Setup**: Simple `setup.sh` and `setup.bat` scripts to install all dependencies and browser binaries.
- **Flexible Input**: Provide a single dork with `--query` or run a batch of dorks from a pre-defined `--template`.
- **Built-in Dork Templates**: Comes with a library of dork templates for common use cases (e.g., finding log files, SQL errors). View them with `gda templates list`.
- **Multiple Output Formats**: Save your results in various formats:
    - CSV (`--output-csv`)
    - JSON-Lines (`--output-jsonl`)
    - Excel (`--output-excel`)
    - SQLite Database (`--output-sqlite`) with automatic deduplication.
- **Browser Automation**: Uses Playwright for robust, browser-based scraping that can handle modern web pages.
- **Attach to Existing Browser**: Use the `--attach` flag to connect to your own running instance of Chrome for manual CAPTCHA solving.

## Prerequisites

- **Python 3.10+**
- For the `--google` browser-based search, a compatible web browser (like Google Chrome) is needed for Playwright to drive. The setup script handles the installation of the necessary Playwright binaries.

## Installation

Getting started is easy. Just run the setup script for your operating system. This will create a local virtual environment, install all dependencies, and download the necessary browser binaries for Playwright.

**For Windows:**

Double-click and run the `setup.bat` file.

**For Linux / macOS:**

Open your terminal, make the script executable, and run it:

```bash
chmod +x setup.sh
./setup.sh
```

## Usage

After running the setup script, you can run the tool in two ways.

### 1. Interactive Runner (Recommended for Beginners)

This is the easiest way to get started. It will ask you questions and guide you through the process.

First, activate the virtual environment created by the setup script:

- **Windows**: `venv\Scripts\activate.bat`
- **Linux/macOS**: `source venv/bin/activate`

Then, run the interactive runner:

```bash
python runner.py
```

### 2. Direct CLI Usage

For advanced users, you can call the `gda` command directly from your activated virtual environment.

**List available dork templates:**
```bash
gda templates list
```

**Run a single query using the CSE API and save to Excel:**
```bash
gda search --query "intitle:\"index of\" \"/etc/passwd\"" --cse --output-excel results.xlsx
```

**Run all dorks from the `sqli_errors` template using a browser and save to SQLite:**
```bash
gda search --template sqli_errors --google --output-sqlite results.db
```

**Attach to your own running browser (started with `--remote-debugging-port=9222`) to solve CAPTCHAs manually:**
```bash
gda search --template exposed_panels --google --attach --output-csv results.csv
```

## Configuration

The tool uses a `config.yaml` file for configuration. You can edit this file to change default behaviors.

- **`browser`**: Settings for Playwright, such as running in `headless` mode.
- **`search.cse`**: Your **API Key** and **Search Engine ID (cx)** for the Google Custom Search API. You must get your own API key and update the `CSE_API_KEY` environment variable for the `--cse` mode to work.
- **`stealth`**: Settings for user agents, proxies, and delays (not yet fully implemented).

## Viewing Results

The tool can save results in four formats:
- **CSV / Excel**: Can be opened with any spreadsheet software.
- **JSON-Lines**: A text file where each line is a JSON object representing a search result.
- **SQLite**: A database file that you can explore with any SQLite browser.

## Legal & Ethical Disclaimer

This tool is intended for security professionals, researchers, and system administrators to find security vulnerabilities and assess the security posture of systems **they are authorized to test**.

**You must only use this tool on assets you own or have explicit, written permission to test.**

The developers of this tool are not responsible for any misuse or damage caused by this tool. Unauthorized scanning of systems is illegal. Use responsibly.
