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
    "Address": "123 Main St, City, Country",  # New field
    "Zip Code": "12345",  # New field
    "Country": "USA"  # New field
}

def capture_window(window_title):
    """Capture the browser window as an image."""
    app_window = Desktop(backend="uia").window(title_re=window_title)
    app_window.set_focus()
    rect = app_window.rectangle()
    img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
    return img, rect

def find_and_click_fields(img, rect, form_data):
    """Detect fields using OCR, click on them, and fill values."""
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    # Track the fields we've already filled
    filled_fields = set()

    for field, value in form_data.items():
        found = False  # Flag to check if we found the field
        for i, text in enumerate(ocr_data["text"]):
            if field.lower() in text.lower() and i not in filled_fields:  # Match field label
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

                filled_fields.add(i)  # Mark this field as filled
                found = True
                break  # Stop searching for the field once it's filled

        if not found:
            print(f"Could not find field: {field}")

def main():
    # Replace with the actual title of your browser window
    browser_window_title = "Sample Application Form Template"

    try:
        # Capture the browser window
        img, rect = capture_window(browser_window_title)

        # Process the image and fill fields
        find_and_click_fields(img, rect, form_data)

        print("Form filling completed.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
