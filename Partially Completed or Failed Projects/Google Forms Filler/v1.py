import pyautogui
import pytesseract
import time
import difflib
from PIL import Image, ImageOps

# Optional: Set Tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ====================== CONFIGURATION ======================
FIELD_ANSWERS = {
    "name": "John Doe",
    "email": "john@example.com",
    "mobile": "9876543210",
    "location": "Pune"
}

SYNONYMS = {
    "full name": "name",
    "email address": "email",
    "current location": "location",
    "phone": "mobile",
    "contact number": "mobile",
    "mobile number": "mobile"
}

MAX_FIELDS = 15           # Max fields to scan
FIELD_HEIGHT = 70         # Height of each form field
DELAY_BETWEEN_FIELDS = 1  # Time between actions

# ====================== OCR + MATCHING ======================

def extract_label(region):
    img = pyautogui.screenshot(region=region)
    gray = ImageOps.grayscale(img)
    text = pytesseract.image_to_string(gray)
    return text.lower().strip()

def match_field(label_text):
    label_text = label_text.lower().strip()

    # Exact or close match to FIELD_ANSWERS
    direct_keys = list(FIELD_ANSWERS.keys())
    best_match = difflib.get_close_matches(label_text, direct_keys, n=1, cutoff=0.6)
    if best_match:
        return best_match[0]

    # Fallback to synonyms
    for key, val in SYNONYMS.items():
        if key in label_text:
            return val

    return None

# ====================== FORM FILLING ======================

def fill_google_form(top_left, bottom_right):
    x1, y1 = top_left
    x2, y2 = bottom_right
    width = x2 - x1
    current_y = y1

    print("\n📋 Starting OCR-based form filling...\n")

    for i in range(MAX_FIELDS):
        label_region = (x1, current_y - 40, width, 40)  # label above the input box
        label_text = extract_label(label_region)

        print(f"[Field {i+1}] Detected label: '{label_text}'")
        if "your answer" in label_text or label_text == "":
            print("→ Ignoring placeholder or empty label.")
        else:
            matched_key = match_field(label_text)
            if matched_key:
                value = FIELD_ANSWERS[matched_key]
                print(f"→ Matched with '{matched_key}' → Typing: {value}")
                pyautogui.click(x1 + 150, current_y + 30)
                time.sleep(0.5)
                pyautogui.write(value)
            else:
                print("→ No good match found. Skipping.")

        current_y += FIELD_HEIGHT + 10
        time.sleep(DELAY_BETWEEN_FIELDS)

    print("\n✅ Done! Please review the form and submit manually if needed.")

# ====================== MAIN DRIVER ======================

if __name__ == "__main__":
    print("🟢 Google Form Filler Activated!")
    print("Move your mouse to the TOP-LEFT of the form and press ENTER...")
    input()
    top_left = pyautogui.position()

    print("Now move mouse to the BOTTOM-RIGHT of the form and press ENTER...")
    input()
    bottom_right = pyautogui.position()

    fill_google_form(top_left, bottom_right)
