# =========================
# IMPORTS
# =========================
import os
import pytesseract
import cv2
import numpy as np
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI

# =========================
# LOAD ENV
# =========================
load_dotenv()

api_key = os.getenv("API_KEY")
endpoint = os.getenv("ENDPOINT")
model_name = os.getenv("MODEL_NAME")

if not api_key or not endpoint:
    raise ValueError("❌ API KEY ou ENDPOINT manquant")

# =========================
# MISTRAL CLIENT
# =========================
client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

# =========================
# TESSERACT PATH
# =========================
pytesseract.pytesseract.tesseract_cmd = r"D:\tesseractOCR\tesseract.exe"

# =========================
# IMAGE PATH
# =========================
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def resolve_image_path(path):
    path = os.path.normpath(path)
    if os.path.isabs(path):
        return path

    candidates = [
        os.path.normpath(os.path.join(PROJECT_ROOT, path)),
        os.path.normpath(os.path.join(os.path.dirname(__file__), path)),
    ]

    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate

    return candidates[0]


image_path = resolve_image_path(
    os.getenv(
        "IMAGE_PATH",
        r"screenshotsaa\Historique des notifications_20260316_121951.png",
    )
)

print("📌 Image:", image_path)

# =========================
# PREPROCESS IMAGE
# =========================
def preprocess_image(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"❌ Image introuvable: {path}")

    try:
        pil_rgb = Image.open(path).convert("RGB")
        img = cv2.cvtColor(np.array(pil_rgb), cv2.COLOR_RGB2BGR)
    except Exception as e:
        raise FileNotFoundError(f"❌ Image illisible: {path} | Détail: {e}")

    img = cv2.resize(img, None, fx=1.2, fy=1.2)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

    return gray

# =========================
# OCR (TESSERACT)
# =========================
def extract_text(path):
    img = preprocess_image(path)
    pil_img = Image.fromarray(img)

    text = pytesseract.image_to_string(pil_img)

    # nettoyage simple
    lines = text.split("\n")
    cleaned = [l.strip() for l in lines if len(l.strip()) > 2]

    return " ".join(cleaned)

# =========================
# MISTRAL SUMMARY
# =========================
def summarize(text):
    if not text.strip():
        return "❌ Aucun texte détecté"

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": f"Résume ce texte en une  ligne en français:\n{text[:800]}"
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

# =========================
# PIPELINE
# =========================
text = extract_text(image_path)
summary = summarize(text)

# =========================
# OUTPUT
# =========================
print("\n================ CLEAN TEXT ================\n")
print(text)

print("\n================ SUMMARY ================\n")
print(summary)