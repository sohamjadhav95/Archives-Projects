import pyautogui
import pandas as pd
import random
import subprocess
import time
import os

# 10-19

# ===============================
# User Configuration
# ===============================

browser_paths = [
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\6fd4453e751a8ed5\Personal 9 - Edge.lnk",
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\d88e12aebbc32f3a\Personal 10 - Edge.lnk",
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\b29c39003909df6c\Personal 11 - Edge.lnk",
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\5c66e90f7d07e83\Personal 12 - Edge.lnk",
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\f9a412ea02f8effb\Personal 13 - Edge.lnk",
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\4efe457acc214e14\Personal 14 - Edge.lnk",
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\2d8045b7076d0f57\Personal 15 - Edge.lnk",
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\4bd8396aaec5a274\Personal 17 - Edge.lnk",
    r"C:\Users\soham\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts\fc826efa601c039b\Personal 18 - Edge.lnk"
]

csv_path = r"E:\Projects\Archives-Projects\Real Completed Projects\Browser Search Automation Script\general_search_queries_1000.csv"

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

def main_2():
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


if __name__ == "__main__":
    main_2()
