import pyautogui
import pandas as pd
import random
import subprocess
import time
import os

# ===============================
# User Configuration Section
# ===============================

# Path to your browser shortcut (.lnk)
browser_path = r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\fc826efa601c039b\Personal 11 - Edge.lnk"

# Path to CSV file containing search queries
csv_path = r"E:\Projects\General Projects\General-Projects\Real Completed Projects\Browser Search Automation Script\general_search_queries_1000.csv"  # Update this path

# Number of loops (how many searches to perform)
num_loops = 5

# Wait time between searches (in seconds)
wait_time = 7

# ===============================
# Script Logic
# ===============================

def open_browser():
    """Opens browser using provided shortcut path."""
    if not os.path.exists(browser_path):
        raise FileNotFoundError(f"Browser shortcut not found: {browser_path}")
    subprocess.Popen([browser_path], shell=True)
    time.sleep(3)  # give time to open

def get_random_query():
    """Selects a random search query from CSV file."""
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError("CSV file is empty or invalid.")
    query = random.choice(df.iloc[:, 0].dropna().tolist())
    return query

def perform_search(query):
    """Performs the search automation."""
    # Focus on search bar
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.5)

    # Type the query
    pyautogui.typewrite(query)
    time.sleep(0.5)

    # Press Enter to search
    pyautogui.press('enter')
    time.sleep(wait_time)

def main():
    open_browser()
    print(f"Running automation for {num_loops} searches with {wait_time}s delay each...\n")

    for i in range(num_loops):
        query = get_random_query()
        print(f"[{i+1}] Searching for: {query}")
        perform_search(query)
        time.sleep(1)

    print("\n✅ Automation complete.")

if __name__ == "__main__":
    main()
