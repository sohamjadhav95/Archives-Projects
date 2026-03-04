from pywinauto import Desktop
from PIL import ImageGrab, ImageEnhance
import pytesseract
import pyautogui
import time
from collections import defaultdict

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Define form data fields
form_data = {
    "First Name": "John Doe",
    "Last Name": "Harrington",
    "E-mail": "johndoe@example.com",
    "Phone": "1234567890",
    "Address": "123 Main St, City",
    "Zip Code": "12345",
    "City": "San Francisco",
    "State": "CA",
    "Country": "USA"
}

def enhance_image(img):
    """Enhance the image to improve OCR detection."""
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)  # Increase contrast
    img = img.convert("L")  # Convert to grayscale
    return img

def capture_window(window_title):
    """Capture the browser window as an image."""
    app_window = Desktop(backend="uia").window(title_re=window_title)
    app_window.set_focus()
    rect = app_window.rectangle()
    img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
    img = enhance_image(img)
    return img, rect

def find_and_fill_visible_fields(img, rect, fields_to_fill):
    """Fill visible fields from the current viewport."""
    custom_config = r'--oem 3 --psm 6'
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=custom_config)
    fields_filled = []

    # Group words by proximity
    word_boxes = defaultdict(list)
    for i, word in enumerate(ocr_data["text"]):
        if word.strip():
            word_boxes[word.strip().lower()].append(
                (ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i])
            )

    for field, value in list(fields_to_fill.items()):
        field_parts = field.lower().split()
        matches = []

        # Match field parts in proximity
        for part in field_parts:
            if part in word_boxes:
                matches.extend(word_boxes[part])

        if matches:
            # Calculate average bounding box
            avg_x = sum([match[0] + match[2] // 2 for match in matches]) // len(matches)
            avg_y = sum([match[1] + match[3] // 2 for match in matches]) // len(matches)

            abs_x = rect.left + avg_x
            abs_y = rect.top + avg_y

            try:
                # Click on the detected field and fill its value
                pyautogui.click(abs_x, abs_y)
                time.sleep(0.5)
                pyautogui.typewrite(value, interval=0.1)
                print(f"Filled '{field}' with '{value}'")
                fields_to_fill.pop(field)  # Remove filled field from data
                fields_filled.append(field)
                return fields_filled  # Return immediately to re-capture the viewport
            except Exception as e:
                print(f"Failed to fill '{field}': {e}")
    return fields_filled

def scroll_page(direction="down", amount=500):
    """Scroll the page to bring fields into view."""
    pyautogui.scroll(amount if direction == "up" else -amount)
    print(f"Scrolled {direction}.")

def main():
    browser_window_title = "Application Form"  # Replace with your actual window title
    scroll_attempts = 0
    max_scroll_attempts = 10  # Avoid infinite scrolling

    try:
        while form_data:
            img, rect = capture_window(browser_window_title)

            while True:
                filled_fields = find_and_fill_visible_fields(img, rect, form_data)
                if filled_fields:
                    img, rect = capture_window(browser_window_title)
                else:
                    break

            if not form_data:  # Exit if all fields are filled
                break

            if scroll_attempts < max_scroll_attempts:
                print("No more fields in current viewport. Scrolling...")
                scroll_page("down")
                scroll_attempts += 1
                time.sleep(1)
            else:
                print("Maximum scroll attempts reached. Exiting.")
                break

        print("Form filling completed. Remaining fields:", form_data)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
