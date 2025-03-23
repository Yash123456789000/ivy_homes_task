# It will approximately take 25 min 17 sec to extract all names of version 1
import requests
import time

API_URL = "http://35.200.185.69:8000/v1/autocomplete?query={}&max_results=50"
ULTIMATE_NAMES = set()  # set to store all names
MAX_CALLS_PER_MINUTE = 100  # API rate limit
DELAY = 60 / MAX_CALLS_PER_MINUTE  # Delay between requests

TOTAL_API_CALLS = 0  # Counter for total API calls

def fetch_names(prefix, depth=1, max_depth=6):     # max_depth will set maximum depth upto which position of letter, code will check different permutations
    """Recursively fetch names by expanding query lexicographically."""
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
            return  # No more results, stop searching at this depth

        ULTIMATE_NAMES.update(results)
        time.sleep(DELAY)

        if len(results) < 50:
            return  # No further words exist beyond this point

        # Extract the last result to determine the next prefix
        last_word = results[-1]

        # If we've reached max depth, stop recursion
        if depth >= max_depth:
            return

        x=last_word[depth]

        # Iterate through next possible letters recursively
        while x <= 'z':
            new_query = last_word[:depth] + x  # Extend prefix lexicographically
            x = chr(ord(x) + 1)  # Move to next letter
            fetch_names(new_query, depth + 1, max_depth)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Run extraction starting from each letter
for letter in "abcdefghijklmnopqrstuvwxyz":
    fetch_names(letter)

print(f"Total unique words: {len(ULTIMATE_NAMES)}")
sorted(ULTIMATE_NAMES)
print(f"Total API calls: {TOTAL_API_CALLS}")
