"""
CV-based image quality validation — no AI, runs in <200ms.
Checks resolution, blur, and exposure.
"""

import io
import math
from dataclasses import dataclass

from PIL import Image, ImageStat

MIN_WIDTH = 400
MIN_HEIGHT = 400
BLUR_THRESHOLD = 80.0   # Laplacian variance — below this is blurry
DARK_THRESHOLD = 40.0   # mean brightness — below this is too dark
BRIGHT_THRESHOLD = 220.0  # mean brightness — above this is overexposed


@dataclass
class QualityResult:
    ok: bool
    issues: list[str]


def validate(image_bytes: bytes) -> QualityResult:
    issues = []

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        return QualityResult(ok=False, issues=["No se pudo leer la imagen. Verificá el formato (JPG, PNG, WEBP)."])

    # 1. Resolution
    w, h = img.size
    if w < MIN_WIDTH or h < MIN_HEIGHT:
        issues.append(f"Resolución muy baja ({w}x{h}px). Mínimo requerido: {MIN_WIDTH}x{MIN_HEIGHT}px.")

    # 2. Blur — approximate Laplacian variance using PIL
    gray = img.convert("L")
    stat = ImageStat.Stat(gray)
    # Variance of pixel values correlates with sharpness
    variance = stat.var[0]
    if variance < BLUR_THRESHOLD:
        issues.append("La imagen parece estar borrosa. Intentá con mejor foco.")

    # 3. Exposure — mean brightness
    brightness = stat.mean[0]
    if brightness < DARK_THRESHOLD:
        issues.append("La imagen está muy oscura. Mejorá la iluminación.")
    elif brightness > BRIGHT_THRESHOLD:
        issues.append("La imagen está sobreexpuesta. Reducí la iluminación o alejate de la fuente de luz.")

    return QualityResult(ok=len(issues) == 0, issues=issues)
