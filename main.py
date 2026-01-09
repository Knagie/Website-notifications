import os
import time
import requests
from bs4 import BeautifulSoup

# Configurable via Portainer Environment Variables
URL = os.getenv("TARGET_URL", "https://store.steampowered.com/sale/steamdeckrefurbished")
SEARCH_STRING = os.getenv("SEARCH_STRING", "Add to Cart")
# The "scope" allows you to target a specific part of the page (e.g., '512GB OLED')
SCOPE_KEYWORD = os.getenv("SCOPE_KEYWORD", "512GB OLED") 
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "my_generic_alerts")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))

def send_ntfy(message):
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={
                "Title": "Scraper Alert!",
                "Priority": "5",
                "Tags": "bell,monitor"
            })
    except Exception as e:
        print(f"Notification failed: {e}")

def check_site():
    print(f"[{time.strftime('%H:%M:%S')}] Checking {URL} for '{SEARCH_STRING}'...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Generic Logic: Find the block of text containing our SCOPE_KEYWORD
        # and then check if our SEARCH_STRING is inside it.
        results = soup.find_all(string=lambda t: SCOPE_KEYWORD in t if t else False)
        
        for r in results:
            # Look at the parent container of the keyword to see if 'Add to Cart' is nearby
            parent_text = r.find_parent().get_text() if r.find_parent() else ""
            if SEARCH_STRING.lower() in parent_text.lower():
                return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Send a test message on startup so you know it's working
    send_ntfy(f"Scraper started for {URL}")
    
    while True:
        if check_site():
            send_ntfy(f"MATCH FOUND: {SEARCH_STRING} detected on {URL}")
        time.sleep(CHECK_INTERVAL)
