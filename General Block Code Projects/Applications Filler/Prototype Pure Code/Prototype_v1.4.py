from pywinauto import Desktop
from PIL import ImageGrab
import pytesseract
import pyautogui
import time

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Define form data fields
form_data = {
    "First": "John Doe",
    "Last Name": "Harrington",
    "E-mail": "johndoe@example.com",
    "Phone": "1234567890",
    "Address": "123 Main St, City, Country",
    "Zip Code": "12345",
    "Country": "USA"
}

def capture_window(window_title):
    """Capture the browser window as an image."""
    app_window = Desktop(backend="uia").window(title_re=window_title)
    app_window.set_focus()
    rect = app_window.rectangle()
    img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
    return img, rect

def find_and_fill_visible_fields(img, rect, fields_to_fill):
    """Fill visible fields from the current viewport."""
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    fields_filled = []

    for i, text in enumerate(ocr_data["text"]):
        if text.strip():  # Ignore empty text
            detected_field = text.strip().lower()
            # Match detected fields with form_data keys (case-insensitive)
            for field, value in list(fields_to_fill.items()):
                if field.lower() in detected_field:
                    x, y, w, h = (ocr_data["left"][i], ocr_data["top"][i],
                                  ocr_data["width"][i], ocr_data["height"][i])

                    # Convert bounding box coordinates to screen coordinates
                    abs_x = rect.left + x + w // 2
                    abs_y = rect.top + y + h // 2

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
    # Replace with the actual title of your browser window
    browser_window_title = "Web Form Example"
    scroll_attempts = 0
    max_scroll_attempts = 10  # Avoid infinite scrolling

    try:
        while form_data:
            img, rect = capture_window(browser_window_title)
            
            while True:
                # Attempt to fill a single visible field and re-capture
                filled_fields = find_and_fill_visible_fields(img, rect, form_data)
                if filled_fields:
                    # Re-capture the window after filling a field
                    img, rect = capture_window(browser_window_title)
                else:
                    break  # No fields filled, exit loop to scroll

            if not form_data:  # Check if all fields are filled
                break

            if scroll_attempts < max_scroll_attempts:
                print("No more fields in current viewport. Scrolling...")
                scroll_page("down")
                scroll_attempts += 1
                time.sleep(1)  # Allow the page to adjust
            else:
                print("Maximum scroll attempts reached. Exiting.")
                break

        print("Form filling completed. Remaining fields:", form_data)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
