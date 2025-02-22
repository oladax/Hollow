import requests
import re
import urllib.parse
import threading
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# ASCII Banner
BANNER = """
▗▖ ▗▖ ▗▄▖ ▗▖   ▗▖    ▗▄▖ ▗▖ ▗▖
▐▌ ▐▌▐▌ ▐▌▐▌   ▐▌   ▐▌ ▐▌▐▌ ▐▌
▐▛▀▜▌▐▌ ▐▌▐▌   ▐▌   ▐▌ ▐▌▐▌ ▐▌
▐▌ ▐▌▝▚▄▞▘▐▙▄▄▖▐▙▄▄▖▝▚▄▞▘▐▙█▟▌
                                                     
This tool is intended for educational and security research purposes only.Unauthorized use against websites you don't own is illegal.
Made by Oladax - Bug Bounty Edition
"""

# Rotating User-Agents to bypass blocks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

# Function to make requests with retries


def fetch_url(url):
    headers = {
        "User-Agent": USER_AGENTS[threading.current_thread().ident % len(USER_AGENTS)]}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
    except requests.exceptions.RequestException:
        pass
    return ""

# Extract JavaScript files


def extract_js_files(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    js_files = set()

    for script in soup.find_all("script", src=True):
        js_url = script["src"]
        full_url = urllib.parse.urljoin(base_url, js_url)
        js_files.add(full_url)

    return js_files

# Function to find API endpoints using regex


def find_api_endpoints(content):
    api_patterns = [
        r'https?://[^\s"\']+',   # Full URLs
        r'[\w/-]+\.json',        # JSON endpoints
        r'[\w/-]+\.php',         # PHP endpoints
        r'[\w/-]+/api/[\w/-]+',  # Common /api/ paths
        r'[\w/-]+/v\d+/[\w/-]+'  # Versioned API (v1, v2)
    ]

    found_endpoints = set()
    for pattern in api_patterns:
        matches = re.findall(pattern, content)
        found_endpoints.update(matches)

    return found_endpoints

# Multi-threaded JavaScript scraping


def scrape_js(js_url, found_api):
    print(f"[*] Fetching JavaScript: {js_url}")
    js_content = fetch_url(js_url)
    found_api.update(find_api_endpoints(js_content))

# Function to fuzz API endpoints


def fuzz_api_endpoints(domain, wordlist="common_api_paths.txt"):
    print("[+] Fuzzing for hidden API endpoints...")
    found_fuzzed = set()
    base_url = f"https://{domain}"
    try:
        with open(wordlist, "r") as f:
            paths = [line.strip() for line in f]

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(
                fetch_url, f"{base_url}/{path}"): path for path in paths}
            for future in futures:
                if future.result():
                    found_fuzzed.add(f"{base_url}/{futures[future]}")
    except FileNotFoundError:
        print("[-] Wordlist file not found. Skipping fuzzing.")

    return found_fuzzed

# Main function


def scrape_api(domain):
    full_url = f"https://{domain}"
    print(f"[+] Fetching HTML from {full_url}...")
    html = fetch_url(full_url)
    if not html:
        print("[-] No HTML fetched. Exiting...")
        return

    found_api = find_api_endpoints(html)

    print("[+] Extracting JavaScript files...")
    js_files = extract_js_files(html, full_url)

    # Multi-threading for JavaScript scraping
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(scrape_js, js, found_api)
                   for js in js_files]
        for future in futures:
            future.result()

    # Fuzz for additional API endpoints
    fuzzed_endpoints = fuzz_api_endpoints(domain)
    found_api.update(fuzzed_endpoints)

    # Save results
    if found_api:
        print("\n[+] Found API Endpoints:")
        for api in found_api:
            print(api)

        with open("api_endpoints.txt", "w") as f:
            for api in sorted(found_api):  # Sorting for easy reading
                f.write(api + "\n")
        print("\n[+] Results saved to api_endpoints.txt")
    else:
        print("[-] No API endpoints found.")


# Run script
if __name__ == "__main__":
    print(BANNER)
    target_domain = input("Enter the target domain (e.g., example.com): ")
    scrape_api(target_domain)
