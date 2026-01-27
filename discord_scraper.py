import os
import json
import re
import requests
from datetime import datetime

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
CHANNEL_ID = "1370076214986801332"  # Coconut Spawners prices channel

def fetch_latest_messages(limit=10):
    """Fetch the latest messages from the Discord channel."""
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN environment variable not set")
        return None
    
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"
    headers = {
        "Authorization": DISCORD_TOKEN,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    params = {"limit": limit}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Error fetching messages: {response.status_code}")
        print(response.text)
        return None
    
    return response.json()

def parse_spawner_prices(messages):
    """
    Parse spawner prices from messages.
    
    New format:
    - Skeleton: 2.2m
    - Iron Golem: 2.3m
    - Zombie 450k
    """
    data = {
        "buying": {},   # Prices when WE BUY (you sell to them)
    }
    
    # Remove custom Discord emojis for cleaner parsing
    emoji_pattern = re.compile(r'<a?:\w+:\d+>')
    
    # Pattern to match: "- Name: price" or "- Name price"
    # Handles both "Skeleton: 2.2m" and "Zombie 450k" formats
    price_pattern = re.compile(
        r'-\s*([A-Za-z\s]+?)[:.]?\s*([0-9.]+[kmb]?)\s*(?:\$|$)',
        re.IGNORECASE
    )
    
    for msg in messages:
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", "")
        author = msg.get("author", {}).get("username", "unknown")
        
        # Skip if not a price message
        if "spawner prices" not in content.lower():
            continue
        
        # Remove custom Discord emojis
        content_clean = emoji_pattern.sub('', content)
        
        print(f"Processing message from {author}:")
        
        for line in content_clean.split("\n"):
            match = price_pattern.search(line)
            if match:
                spawner_type = match.group(1).strip().title()
                price = match.group(2).strip().lower()
                
                # Skip empty or too short names
                if not spawner_type or len(spawner_type) < 2:
                    continue
                
                data["buying"][spawner_type] = {
                    "price": price,
                    "source_timestamp": timestamp,
                    "author": author
                }
                
                print(f"  Found: {spawner_type} = {price}")
    
    return data

def main():
    print("Fetching Discord messages...")
    messages = fetch_latest_messages(limit=10)
    
    if not messages:
        print("Failed to fetch messages")
        return
    
    print(f"Fetched {len(messages)} messages")
    
    # Parse prices
    prices = parse_spawner_prices(messages)
    
    # Count total prices found
    total_prices = sum(len(section) for section in prices.values())
    
    # Create output
    output = {
        "updated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "channel_id": CHANNEL_ID,
        "source": "Coconut Spawners",
        "total_prices": total_prices,
        "prices": prices,
        "raw_messages": [
            {
                "id": msg["id"],
                "content": msg.get("content", ""),
                "timestamp": msg.get("timestamp", ""),
                "author": msg.get("author", {}).get("username", "unknown")
            }
            for msg in messages
        ]
    }
    
    # Save to file
    with open("spawner_prices.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nDone! Found {total_prices} spawner prices")
    for section, items in prices.items():
        print(f"  {section.title()}: {len(items)} types")
    print("Saved to spawner_prices.json")

if __name__ == "__main__":
    main()
