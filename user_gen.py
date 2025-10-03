import requests, colorama, random, threading, sys, os, time, re
from colorama import init, Fore
from dhooks import Webhook, Embed

## CONFIG
sendtowebhook = True  ## (False, True) 
yourwebhook = "https://discord.com/api/webhooks/1423644290852327527/5bOkzssfT6NYFRQxdREjanFY21Cyj7KXx_Zr2sGbdvApRx-uxAps9fzCzlH_i3JP6C9S"
min = 5
max = 5
threads = 2  ## keep this at 1 if using webhook, otherwise you can increase
request_delay = 0.1  ## seconds between requests to reduce API issues
## END OF CONFIG

init()

# List of banned substrings (case-insensitive)
banned_words = [
    "FUC", "FUK", "ASS", "SEX", "DIK", "DIH", "KYS", "BAO", 
    "NIG", "SHT", "SHIT", "KKK", "HOE", "DCK", "DKS", "SLT", 
    "CUM", "SMN", "FCK", "FAG", "GAY", "PUS"
]

# File to store tried usernames
tried_file = "tried_usernames.txt"
tried = set()
# Counters
total_tried = 0
total_free = 0

# Load already tried usernames from file
if os.path.exists(tried_file):
    with open(tried_file, "r") as f:
        tried = set(line.strip().upper() for line in f.readlines())

def namegen():
    length = random.randint(min, max)
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join(random.choice(letters) for _ in range(length))

def is_valid_username(name):
    """Check if username contains banned words or specific patterns."""
    name_upper = name.upper()
    
    # Check banned words
    for word in banned_words:
        if word in name_upper:
            return False
    
    # Patterns to block:
    # P..RN
    # F..U..K
    # F..C..K
    # F..C
    patterns = [
        r'P.{0,2}R.{0,2}N',
        r'F.{0,2}U.{0,2}K',
        r'F.{0,2}C.{0,2}K',
        r'F.{0,2}C'
    ]
    
    for pat in patterns:
        if re.search(pat, name_upper):
            return False
    
    return True

if sendtowebhook:
    setwebhook = Webhook(url=yourwebhook)

def main():
    global total_tried, total_free
    try:
        while True:
            name = namegen().upper()
            
            # Skip usernames already tried
            if name in tried:
                continue

            # Skip usernames containing banned words or patterns
            if not is_valid_username(name):
                print(f'{Fore.RED}{name} contains banned words or patterns, skipping.')
                tried.add(name)
                with open(tried_file, "a") as f:
                    f.write(name + "\n")
                total_tried += 1
                continue

            # Check if username exists on Roblox
            try:
                r = requests.post("https://users.roblox.com/v1/usernames/users",
                                  json={"usernames": [name]})
                data = r.json()
            except requests.exceptions.RequestException as e:
                print(f'{Fore.RED}Network error for {name}: {e}')
                time.sleep(request_delay)  # small delay and retry next loop
                continue
            except Exception as e:
                print(f'{Fore.RED}Unexpected error for {name}: {e}')
                time.sleep(request_delay)
                continue

            # Mark this username as tried
            tried.add(name)
            with open(tried_file, "a") as f:
                f.write(name + "\n")
            total_tried += 1

            # Username is free
            if "data" in data and len(data["data"]) == 0:
                print(f'{Fore.GREEN}{name} Is Not Taken! (Tried: {total_tried}, Free: {total_free+1})')
                total_free += 1
                with open("usernames.txt", "a") as f:
                    f.write(name + "\n")

                if sendtowebhook:
                    embed = Embed(title='New Username Sniped!', color=0x00e3fd)
                    embed.add_field(name='Username', value=f'{name}')
                    embed.add_field(name='Register Here!', value=f'Here!')
                    setwebhook.execute(embed=embed)
            else:
                # Username is taken
                print(f'{Fore.RED}{name} is already taken. (Tried: {total_tried})')

            # Small delay to reduce API issues
            time.sleep(request_delay)

    except KeyboardInterrupt:
        print("\nStopped by user.")
        sys.exit(0)

for _ in range(threads):
    try:
        t = threading.Thread(target=main)
        t.start()
    except Exception as e:
        print(f'{Fore.RED}Thread error: {e}')
