import pyautogui
import pandas as pd
import random
import subprocess
import time
import os

from multithread_search_10_19 import main_2

# 10-19

# ===============================
# User Configuration
# ===============================

browser_paths = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\39a55e8d68262d97\Personal - Edge.lnk",
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\8eff091da6ff8c78\Soham Jadhav Microsoft - Edge.lnk",
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\c5c722f79d0ebcef\Personal 4 - Edge.lnk",
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\a6b9223a5642fdac\Personal 5 - Edge.lnk",
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\11e375aa989b5c43\Personal 6 - Edge.lnk",
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\24ec6ed44eebbe42\Personal 7 - Edge.lnk",
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\93b6394480321fad\Personal 8 - Edge.lnk"
]

csv_path = r"E:\Projects\Archives\Real Completed Projects\Browser Search Automation Script\general_search_queries_1000.csv"

num_loops = 14  # searches per browser
wait_time = 3  # seconds between searches

# ===============================
# Functions
# ===============================

def get_random_query(df):
    """Select a random search query from CSV."""
    return random.choice(df.iloc[:, 0].dropna().tolist())

def open_all_browsers():
    """Open all browser shortcuts."""
    for path in browser_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Browser shortcut not found: {path}")
        subprocess.Popen([path], shell=True)
        time.sleep(3)  # give browser time to open

def perform_cycled_searches():
    """Perform searches cycling through browsers using Alt+Tab."""
    df = pd.read_csv(csv_path)
    total_browsers = len(browser_paths)

    # Start from the last opened browser
    for search_round in range(num_loops):
        print(f"\n--- Search Round {search_round + 1} ---")
        for i in range(total_browsers):
            query = get_random_query(df)
            print(f"[Browser {total_browsers - i}] Searching for: {query}")

            # Focus search bar
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.5)
            pyautogui.typewrite(query)
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(wait_time)

            # Switch to next browser
            if i < total_browsers - 1:  # skip Alt+Tab after last browser
                # Press Alt+Tab 4 times while keeping Alt held down
                pyautogui.keyDown('alt')
                for _ in range(len(browser_paths)-1):
                    pyautogui.press('tab')
                pyautogui.keyUp('alt')
                time.sleep(1)  # wait for window to focus
                # wait for window to focus

# ===============================
# Main Logic
# ===============================

def main():
    print("Opening all browsers...")
    open_all_browsers()
    time.sleep(2)  # extra wait to ensure all browsers are fully loaded

    # --- Prime the Alt+Tab cycle ---
    print("Priming Alt+Tab cycle...")
    pyautogui.keyDown('alt')
    for _ in range(len(browser_paths)-1):  # press Tab n times while holding Alt
        pyautogui.press('tab')
    pyautogui.keyUp('alt')
    time.sleep(1)  # wait for window to focus

    print(f"\nStarting cycled searches: {num_loops} searches per browser\n")
    perform_cycled_searches()
    print("\n✅ All browser searches completed.")

    # ----------------------------------------------
    #   NEW PART: Close all browsers using Ctrl+W
    # ----------------------------------------------
    print("\nClosing all browser tabs...")

    for _ in range(len(browser_paths)):    # number of browsers opened
        pyautogui.hotkey('ctrl', 'w')      # close current tab
        time.sleep(0.5)                     # small delay for stable closing

    print("✅ All browser tabs closed.")
    
    main_2()


if __name__ == "__main__":
    main()