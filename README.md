# HOLLOW

## 🔥 About
Hollow is a Python-based tool for discovering API endpoints on a target website. It:
- Scrapes JavaScript files and HTML for API endpoints.
- Uses regex patterns to extract API calls.
- Performs fuzzing to brute-force hidden API paths.
- Saves all discovered endpoints to a text file.

### 🚀 Features
- Multi-threaded scraping for fast performance.
- Rotating User-Agents to evade basic bot detection.
- Automatic API endpoint extraction from JS files.
- Fuzzing integration with a customizable wordlist.
- Saves results for easy reference.

## 🛠 Installation
```bash
git clone https://github.com/oladax/Hollow.git
cd Hollow
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
pip install -r requirements.txt

