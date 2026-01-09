import os  # Essential to read your Portainer environment variables
import time
import requests
from bs4 import BeautifulSoup

# Config from Portainer Environment Variables
# These fallback to defaults if not set in your Portainer stack
NTFY_HOST = os.getenv("NTFY_HOST", "https://ntfy.knagie.dev")
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "steamdeck")
NTFY_PRIORITY = os.getenv("NTFY_PRIORITY", "default") # 1 (min) to 5 (max)
NTFY_TAGS = os.getenv("NTFY_TAGS", "bell")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))
URL = os.getenv("TARGET_URL", "https://store.steampowered.com/sale/steamdeckrefurbished")
SCOPE_KEYWORD = os.getenv("SCOPE_KEYWORD", "512GB OLED")
SEARCH_STRING = os.getenv("SEARCH_STRING", "Add to Cart")

def send_ntfy(message, tags=None, priority=None):
    """Sends a push notification via the ntfy API"""
    # Use function defaults if specific values aren't passed
    tags = tags or NTFY_TAGS
    priority = priority or NTFY_PRIORITY
    
    # Construct the full URL (e.g., https://ntfy.knagie.dev/steamdeck)
    full_url = f"{NTFY_HOST.rstrip('/')}/{NTFY_TOPIC}"
    
    try:
        response = requests.post(
            full_url,
            data=message.encode('utf-8'), # Encode for special characters/emojis
            headers={
                "Title": "Scraper Alert",
                "Priority": str(priority), # Priority level 1-5
                "Tags": tags              # Comma-separated emoji names
            },
            timeout=10
        )
        print(f"[{time.strftime('%H:%M:%S')}] Notified {NTFY_TOPIC}. Status: {response.status_code}")
    except Exception as e:
        print(f"Notification error: {e}")

def check_stock():
    """Scrapes the target page for the specific item and stock status"""
    print(f"[{time.strftime('%H:%M:%S')}] Checking {URL} for '{SCOPE_KEYWORD}'...")
    try:
        # Browser-like header to avoid being blocked by Steam
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the specific product block
        # We look for a container that mentions our SCOPE_KEYWORD (e.g. 512GB OLED)
        for box in soup.find_all(class_=lambda x: x and 'container' in x.lower()):
            content = box.get_text()
            if SCOPE_KEYWORD.lower() in content.lower():
                # Check if the specific trigger string is inside this box
                if SEARCH_STRING.lower() in content.lower():
                    return True
        return False
    except Exception as e:
        print(f"Scraper error: {e}")
    return False

if __name__ == "__main__":
    # Test notification to confirm connection on startup
    send_ntfy(f"Tracker started! Monitoring {SCOPE_KEYWORD} every {CHECK_INTERVAL}s", tags="rocket", priority=3)
    
    while True:
        if check_stock():
            send_ntfy(f"🚨 {SCOPE_KEYWORD} IN STOCK! 🚨", tags="tada,computer", priority=5)
            # Wait 1 hour after a hit to avoid notification fatigue
            time.sleep(3600) 
        else:
            time.sleep(CHECK_INTERVAL)
