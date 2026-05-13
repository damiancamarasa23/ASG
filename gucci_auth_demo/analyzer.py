"""
Motor de análisis visual usando Gemini Vision API (vía REST).
No requiere SDK — usa solo `requests` de la stdlib de Python.
"""

import base64
import json
import pathlib
import re
import time
from typing import Optional
import requests


GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash-lite:generateContent"
)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _encode_image(image_path: pathlib.Path, max_px: int = 800) -> tuple[str, str]:
    """
    Devuelve (base64_data, mime_type) para una imagen.
    Redimensiona al lado más largo a max_px para reducir consumo de tokens
    y evitar rate limits en el tier gratuito de Gemini.
    """
    import io
    from PIL import Image

    img = Image.open(image_path)
    w, h = img.size
    if max(w, h) > max_px:
        scale = max_px / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=85)
    data = base64.b64encode(buf.getvalue()).decode("utf-8")
    return data, "image/jpeg"


def _parse_json_response(text: str) -> dict:
    """
    Extrae el JSON del texto devuelto por Gemini.
    Gemini a veces devuelve el JSON dentro de bloques ```json ```.
    """
    # Intentar extraer de bloque de código
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)

    # Intentar encontrar el primer objeto JSON en el texto
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Fallback: intentar parsear el texto completo
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return {"score": 0, "observaciones": f"Error al parsear respuesta: {text[:100]}"}


def analyze_image(image_path: pathlib.Path, prompt: str, api_key: str,
                  delay: float = 5.0, max_retries: int = 4) -> dict:
    """
    Envía una imagen a Gemini Vision con el prompt dado.
    Devuelve {"score": int, "observaciones": str}.

    En caso de rate limit (429) usa backoff exponencial:
      intento 1 → espera delay * 2
      intento 2 → espera delay * 4
      intento 3 → espera delay * 8
      ...
    """
    img_data, mime_type = _encode_image(image_path)

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": img_data,
                        }
                    },
                    {"text": prompt},
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 256,
        },
    }

    for attempt in range(max_retries):
        response = requests.post(
            GEMINI_URL,
            params={"key": api_key},
            json=payload,
            timeout=30,
        )

        if response.status_code == 429:
            wait = delay * (2 ** (attempt + 1))   # backoff exponencial
            print(f"rate limit, esperando {int(wait)}s...", end=" ", flush=True)
            time.sleep(wait)
            continue

        if response.status_code != 200:
            return {
                "score": 0,
                "observaciones": f"Error API {response.status_code}: {response.text[:200]}",
            }

        data = response.json()
        try:
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return _parse_json_response(raw_text)
        except (KeyError, IndexError) as e:
            return {"score": 0, "observaciones": f"Error procesando respuesta: {e}"}

    return {"score": 0, "observaciones": f"Rate limit persistente tras {max_retries} intentos. Probá --delay más alto."}


def find_image_for_criterion(folder: pathlib.Path, filename_base: str) -> Optional[pathlib.Path]:
    """
    Busca en `folder` un archivo que empiece con `filename_base`
    y tenga una extensión de imagen soportada.
    """
    for ext in SUPPORTED_EXTENSIONS:
        candidate = folder / f"{filename_base}{ext}"
        if candidate.exists():
            return candidate
    return None
