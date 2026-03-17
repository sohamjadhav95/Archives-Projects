import pyautogui
import time
import pyperclip

# List of 10 filenames for the loop
filenames = [
"6_10.pdf",
"11_15.pdf",
"16_20.pdf",
"21_25.pdf",
"26_30.pdf",
"31_35.pdf",
"36_40.pdf",
"41_45.pdf",
"46_50.pdf",
"51_55.pdf",
"56_60.pdf",
"61_65.pdf",
"66_70.pdf",
"71_75.pdf",
"76_80.pdf",
"81_85.pdf",
"86_90.pdf",
"91_95.pdf",
"96_100.pdf",
"101_105.pdf",
"106_110.pdf",
"111_115.pdf",
"116_120.pdf",
"121_125.pdf",
"126_130.pdf",
"131_135.pdf",
"136_140.pdf",
"141_145.pdf",
"146_150.pdf",
"151_155.pdf",
"156_160.pdf",
"161_165.pdf",
"166_170.pdf",
"171_175.pdf",
"176_180.pdf",
"181_185.pdf",
"186_190.pdf",
"191_195.pdf",
"196_200.pdf",
"201_205.pdf",
"206_210.pdf",
"211_215.pdf",
"216_220.pdf",
"221_225.pdf",
"226_230.pdf",
"231_235.pdf",
"236_240.pdf",
"241_245.pdf",
"246_250.pdf",
"251_255.pdf",
"256_260.pdf",
"261_265.pdf",
"266_270.pdf",
"271_275.pdf",
"276_280.pdf",
"281_285.pdf",
"286_290.pdf",
"291_295.pdf",
"296_300.pdf",
"301_305.pdf",
"306_310.pdf",
"311_315.pdf",
"316_320.pdf",
"321_324.pdf",
]

# Step 1: Go to Gemini and Doc.
print("Starting automation... Opening Gemini.")

pyautogui.hotkey('alt', 'tab')
time.sleep(1)
pyautogui.press('win')
time.sleep(1)
doc_link = "https://docs.google.com/document/d/1dghUAmfetqbK2wMXlqdTnCEjcmIERKrJGNaNq3qCA9A/edit?usp=sharing"
pyperclip.copy(doc_link)
pyautogui.hotkey('ctrl', 'v')
pyautogui.press('enter')
time.sleep(1)
pyautogui.hotkey('alt', 'tab')
time.sleep(1)

# Wait for the application to open
time.sleep(2)

# Step 6: repeat steps 2 to 5 again. for 10 times.
for filename in filenames:
    print(f"Executing loop for filename: {filename}")
    
    # Step 2: Type prompt that I'll enter in code (Directly start typing not any key pressing or anything).
    # --- ENTER YOUR PROMPT HERE ---
    prompt_text = """OCR Task: Marathi Layout Reconstruction
Objective: Convert the scanned Marathi PDF page into a Markdown table that mirrors the original layout with 100% character fidelity.

1. Structural Rules [Follow these Instructions carefully]
Two-Column Table: Use a table with Topic / Title (Left) and Details (Right).
Row Fidelity: Every row on the PDF page must correspond to exactly one row in the table. Do not merge rows.
Nested Tables (IMPORTANT): If a table exists within a section or column, create a Separate standalone table at that specific position to maintaining above and below content intact.
Lists & Breaks: Preserve numbered lists (1., 2., 3.) and bullet points. Use <br> for line breaks within a single cell.
2. Content & Formatting
Character Accuracy: Preserve every Marathi character exactly. Do NOT translate, paraphrase, or correct grammar.
Visual Hierarchy:
Use bold text for headings and labels.
Use Markdown headers (###) for major section titles to reflect visual scale.
Exclusions/Inclusions:
IGNORE headers: "S.P Publication" and "LAST HOUR REVISION".
INCLUDE page numbers at the bottom in this format: [Page XX].
3. Handling Illegible Text
High Confidence: If partially unreadable but contextually certain, use: [RECONSTRUCTED: word].
Low Confidence: If illegible, use: [UNCLEAR TEXT]. Do not guess.
4. Output Constraints
Output ONLY the reconstructed table.
No introductory text, explanations, or commentary.
Name this chat session using the document's filename.
OUTPUT MUST IN CANVAS ONLY"""
    
    # Use pyperclip to handle Unicode (Marathi) and multi-line strings without breaking the automation
    pyperclip.copy(prompt_text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1.0)
    
    # Step 3: press tab key only once, then hit enter, press tab again, hit enter, then type the filename only one at a time
    pyautogui.press('tab')
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    pyautogui.press('tab')
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(1) # Wait a moment just in case a file dialog or menu opens
    
    # Type the filename
    pyautogui.write(filename, interval=0.05)
    time.sleep(0.5)
    pyautogui.press('enter')
    
    # Step 4: wait 5 seconds then press tab twice, then enter, then press tab twice, enter, press tab 4 times, then enter.
    time.sleep(6)
    
    pyautogui.press('tab')
    pyautogui.press('tab')
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    pyautogui.press('tab')
    pyautogui.press('tab')
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    time.sleep(0.5)
    pyautogui.press('enter')

    # Wait till response is generated
    print("Waiting for response to generate...")
    time.sleep(40)

    # Step 5: Select and Paste in Document

    width, height = pyautogui.size()
    pyautogui.click(width * 0.75, height * 0.5)
    time.sleep(0.5)
    pyautogui.click(width * 0.75, height * 0.5)
    time.sleep(1.0)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.5)
    pyautogui.hotkey('alt', 'tab')
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')
    
    # Step 6: Return to Gemini
    pyautogui.hotkey('alt', 'tab')
    time.sleep(1.0)
    
    # Step 7: Open new chat
    pyautogui.hotkey('ctrl', 'shift', 'o')
    
    # Small wait before starting the next loop iteration
    time.sleep(2)

print("Automation finished!")
