# Pull new variables from environment
# Priority: 1 (min) to 5 (max)
NTFY_PRIORITY = os.getenv("NTFY_PRIORITY", "default") 
NTFY_TAGS = os.getenv("NTFY_TAGS", "bell")

def send_ntfy(message, tags=None, priority=None):
    # Use function arguments if provided, otherwise use env variables
    tags = tags or NTFY_TAGS
    priority = priority or NTFY_PRIORITY
    
    full_url = f"{NTFY_HOST.rstrip('/')}/{NTFY_TOPIC}"
    
    try:
        response = requests.post(
            full_url,
            data=message.encode('utf-8'),
            headers={
                "Title": "Scraper Alert",
                "Priority": str(priority), # ntfy accepts numbers or names
                "Tags": tags
            },
            timeout=10
        )
        print(f"[{time.strftime('%H:%M:%S')}] Notification sent. Status: {response.status_code}")
    except Exception as e:
        print(f"Notification error: {e}")
        
