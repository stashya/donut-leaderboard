import requests
import json
import time

API_KEY = "41c9e4c6c3b44e38a06ce3e72ba3f7a5"
BASE_URL = "https://api.donutsmp.net/v1/leaderboards"

# All leaderboard types
LEADERBOARD_TYPES = [
    "money",
    "kills", 
    "deaths",
    "mobskilled",
    "brokenblocks",
    "placedblocks",
    "playtime",
    "sell",
    "shards",
    "shop"
]

# For money, we still fetch all 22 pages for the full top 1000
MONEY_PAGES = 22

def fetch_leaderboard_page(leaderboard_type, page):
    """Fetch a single page of a leaderboard."""
    response = requests.get(
        f"{BASE_URL}/{leaderboard_type}/{page}",
        headers={
            "accept": "application/json",
            "Authorization": API_KEY
        }
    )
    
    if response.status_code != 200:
        print(f"Error fetching {leaderboard_type} page {page}: {response.status_code}")
        return []
    
    data = response.json()
    return data.get("result", [])

def fetch_money_leaderboard():
    """Fetch full money leaderboard (top 1000)."""
    all_players = []
    
    for page in range(1, MONEY_PAGES + 1):
        print(f"Fetching money page {page}/{MONEY_PAGES}...")
        players = fetch_leaderboard_page("money", page)
        all_players.extend(players)
        time.sleep(0.5)
    
    return all_players

def fetch_top_10(leaderboard_type):
    """Fetch only the top 10 of a leaderboard (first page, limited)."""
    print(f"Fetching top 10 for {leaderboard_type}...")
    players = fetch_leaderboard_page(leaderboard_type, 1)
    # First page has ~46 players, we only need top 10
    return players[:10]

def main():
    # Fetch money leaderboard (full top 1000)
    money_players = fetch_money_leaderboard()
    
    # Build combined leaderboards structure
    all_leaderboards = {
        "money": money_players  # Full list for money
    }
    
    # Fetch top 10 for all other leaderboard types
    for lb_type in LEADERBOARD_TYPES:
        if lb_type == "money":
            continue  # Already fetched
        
        top_10 = fetch_top_10(lb_type)
        all_leaderboards[lb_type] = top_10
        time.sleep(0.5)  # Be nice to the API
    
    # Create combined output
    output = {
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "leaderboards": all_leaderboards
    }
    
    # Save combined leaderboards file (will be encrypted by encrypt.py)
    with open("all_leaderboards.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nDone!")
    print(f"Money leaderboard: {len(money_players)} players")
    for lb_type in LEADERBOARD_TYPES:
        if lb_type != "money":
            print(f"{lb_type}: {len(all_leaderboards[lb_type])} players (top 10)")

if __name__ == "__main__":
    main()
