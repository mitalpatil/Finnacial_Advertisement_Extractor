import cv2
import pytesseract
import numpy as np
import uuid

def extract_text_blocks(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    ret, thresh1 = cv2.threshold(blur, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)

    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
    dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)
    contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    structured_results = []
    for cnt in sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[1]):
        x, y, w, h = cv2.boundingRect(cnt)
        cropped = gray[y:y + h, x:x + w]
        _, block_thresh = cv2.threshold(cropped, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text = pytesseract.image_to_string(block_thresh, lang='eng').strip()
        if text:
            structured_results.append({
                "block_id": str(uuid.uuid4()),
                "coordinates": [int(x), int(y), int(w), int(h)],
                "text": text
            })
    return structured_results, img
