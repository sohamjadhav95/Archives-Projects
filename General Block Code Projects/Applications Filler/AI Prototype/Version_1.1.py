import paddleocr
from transformers import pipeline
import pyautogui
import time
from PIL import ImageGrab, ImageEnhance

# PaddleOCR setup
ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang='en')

# NLP classifier setup
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Predefined form data
form_data = {
    "First Name": "John Doe",
    "Last Name": "Harrington",
    "E-mail": "johndoe@example.com",
    "Phone": "1234567890",
    "Address": "123 Main St, City, Country",
    "Zip Code": "12345",
    "City": "San Francisco",
    "State": "CA",
    "Country": "USA",
}

# Enhance image for OCR
def enhance_image(img):
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)  # Increase contrast
    img = img.convert("L")  # Convert to grayscale
    return img

# Capture form window
def capture_form_window(window_title):
    try:
        rect = pyautogui.getWindowsWithTitle(window_title)[0].box
        img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
        return enhance_image(img), rect
    except IndexError:
        print("Window not found!")
        return None, None

# Detect fields using PaddleOCR
def detect_fields(img):
    results = ocr.ocr(img, cls=True)
    detected_texts = [(line[1][0], line[0]) for line in results[0]]  # (text, box)
    return detected_texts

# Classify fields with NLP
def classify_field(detected_text, field_options):
    result = classifier(detected_text, field_options)
    return result['labels'][0] if result['scores'][0] > 0.5 else None

# Fill fields
def fill_fields(detected_fields, rect):
    for text, box in detected_fields:
        matched_field = classify_field(text, list(form_data.keys()))
        if matched_field and matched_field in form_data:
            center_x = int((box[0][0] + box[2][0]) / 2) + rect.left
            center_y = int((box[0][1] + box[2][1]) / 2) + rect.top
            try:
                pyautogui.click(center_x, center_y)
                time.sleep(0.5)
                pyautogui.typewrite(form_data[matched_field], interval=0.1)
                print(f"Filled '{matched_field}' with '{form_data[matched_field]}'")
                form_data.pop(matched_field)  # Remove filled field
            except Exception as e:
                print(f"Error filling '{matched_field}': {e}")

# Main function
def main():
    window_title = "Sample Application Form Template"  # Update with actual window title
    img, rect = capture_form_window(window_title)
    if img is None or rect is None:
        return

    detected_fields = detect_fields(img)
    fill_fields(detected_fields, rect)

    print("Form filling completed!")

if __name__ == "__main__":
    main()
