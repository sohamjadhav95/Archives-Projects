
from pywinauto import Desktop
from PIL import ImageGrab
import pytesseract
import pyautogui
import time

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Define form data fields
form_data = {
    "Name": "John Doe",
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

def find_and_click_field(img, rect, field, value):
    """Detect a single field using OCR, click on it, and fill the value."""
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    for i, text in enumerate(ocr_data["text"]):
        if field.lower() in text.lower():  # Match field label
            x, y, w, h = (ocr_data["left"][i], ocr_data["top"][i],
                          ocr_data["width"][i], ocr_data["height"][i])

            # Convert bounding box coordinates to screen coordinates
            abs_x = rect.left + x + w // 2
            abs_y = rect.top + y + h // 2

            # Simulate click on the detected field
            pyautogui.click(abs_x, abs_y)
            time.sleep(0.5)

            # Type the corresponding value
            pyautogui.typewrite(value, interval=0.1)
            print(f"Filled '{field}' with '{value}'")
            return True  # Field filled successfully
    return False  # Field not found

def scroll_page(direction, amount=500):
    """Scroll the page to bring fields into view."""
    pyautogui.scroll(amount if direction == "up" else -amount)

def main():
    # Replace with the actual title of your browser window
    browser_window_title = "Sample Application Form Template"

    try:
        # Capture the browser window
        while form_data:
            img, rect = capture_window(browser_window_title)
            
            # Attempt to find and fill each field in the form
            for field, value in list(form_data.items()):
                success = find_and_click_field(img, rect, field, value)
                if success:
                    # Remove field from the data after filling
                    form_data.pop(field)
                else:
                    print(f"Field '{field}' not found. Scrolling...")
                    # Scroll down to look for the next field
                    scroll_page("down")
                    time.sleep(1)  # Allow page to adjust
                    break  # Break to re-capture window after scrolling

        print("Form filling completed.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
