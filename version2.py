import requests
import time

API_URL = "http://35.200.185.69:8000/v2/autocomplete?query={}&max_results=75"
ULTIMATE_NAMES = set()
MAX_CALLS_PER_MINUTE = 50  # API rate limit
DELAY = 60 / MAX_CALLS_PER_MINUTE  # Delay between requests

TOTAL_API_CALLS = 0  # Counter for total API calls

# Function to get the next character in sequence
def next_char(c):
    if c == '9':
        return 'a'  # After '9', start with 'a'
    elif c == 'z':
        return None  # Stop at 'z'
    else:
        return chr(ord(c) + 1)

def fetch_names(prefix, depth=1, max_depth=6):
    """Recursively fetch names by expanding the query lexicographically."""
    try:
        response = requests.get(API_URL.format(prefix))
        global TOTAL_API_CALLS
        TOTAL_API_CALLS += 1

        if response.status_code == 429:
            print(f"Rate limit exceeded. Waiting for 60 seconds... ({prefix})")
            time.sleep(60)
            return fetch_names(prefix, depth, max_depth)

        data = response.json()
        results = data.get("results", [])

        if not results:
            return  # Stop if no results found

        ULTIMATE_NAMES.update(results)
        time.sleep(DELAY)

        # Stop searching if fewer than 75 results are returned
        if len(results) < 75:
            return

        # Extract last word to determine next prefix
        last_word = results[-1]

        # Stop recursion if max depth is reached
        if depth >= max_depth:
            return

        # Iterate through next possible characters recursively
        char = last_word[depth] if len(last_word) > depth else None

        while char:
            new_query = last_word[:depth] + char  # Extend prefix lexicographically
            fetch_names(new_query, depth + 1, max_depth)
            char = next_char(char)  # Move to the next character

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Start extraction from all possible first characters
for char in "0123456789abcdefghijklmnopqrstuvwxyz":
    fetch_names(char)

print(f"Total unique words: {len(ULTIMATE_NAMES)}")
sorted(ULTIMATE_NAMES)
print(f"Total API calls: {TOTAL_API_CALLS}")
