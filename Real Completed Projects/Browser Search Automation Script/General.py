import subprocess
import pyautogui
import time
import pyperclip

# Path to Microsoft Edge shortcut (.lnk)
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Base URL pattern
base_url = "https://rewards.bing.com/redeem/0008850000"

# Launch Microsoft Edge once
subprocess.Popen([edge_path])
time.sleep(5)  # wait for Edge to open completely

for i in range(51, 101):  # 01 to 50
    link = f"{base_url}{i:02d}"
    print(f"Opening: {link}")

    # Copy link to clipboard
    pyperclip.copy(link)
    time.sleep(1)

    # Focus search bar (Ctrl + L)
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(1)

    # Paste link and open
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')

    # Wait 5 seconds before next link
