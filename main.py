import os
import time
import requests
from bs4 import BeautifulSoup

# Config from Portainer Environment Variables
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "default_topic")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))
URL = os.getenv("TARGET_URL", "https://store.steampowered.com/sale/steamdeckrefurbished")

def send_ntfy(message, tags="bell", priority="default"):
    try:
        requests.post(f"https://{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={
                "Title": "Steam Deck Tracker",
                "Priority": priority,
                "Tags": tags
            })
    except Exception as e:
        print(f"Notification error: {e}")

def check_stock():
    print(f"[{time.strftime('%H:%M:%S')}] Checking stock for 512GB OLED...")
    try:
        # Steam sometimes blocks simple scripts; we use a browser-like header
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # We look for all product containers on the page
        # Steam usually uses 'sale_item_container' or similar classes for these boxes
        containers = soup.find_all(class_=lambda x: x and 'container' in x.lower())
        
        for box in containers:
            content = box.get_text()
            # Ensure we are looking at the 512 GB OLED box specifically
            if "512 GB" in content and "OLED" in content:
                if "Add to cart" in content or "In Stock" in content:
                    return True
                else:
                    print("Found 512GB OLED section, but it is still 'Out of stock'.")
                    return False
        
        # Backup: If classes changed, check the whole page text as a fallback
        if "512 GB OLED" in soup.text and "Add to cart" in soup.text:
             return True

    except Exception as e:
        print(f"Scraper error: {e}")
    return False

if __name__ == "__main__":
    # Test notification so you know the Docker container started correctly
    send_ntfy(f"Tracker started! Monitoring {URL} every {CHECK_INTERVAL}s", tags="rocket", priority="3")
    
    while True:
        if check_stock():
            send_ntfy("🚨 512GB OLED REFURB IN STOCK! 🚨", tags="tada,computer", priority="5")
            # If found, check less frequently to avoid spamming your phone
            time.sleep(3600) 
        else:
            time.sleep(CHECK_INTERVAL)
