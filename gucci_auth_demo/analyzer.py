"""
Motor de análisis visual — soporta dos backends:
  - gemini:  Google Gemini Vision API (producción)
  - ollama:  modelo local vía Ollama (desarrollo, sin límites ni costos)
"""

import base64
import io
import json
import pathlib
import re
import time
from typing import Optional
import requests
from PIL import Image


# ── Configuración de backends ──────────────────────────────────────────────────

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash-lite:generateContent"
)

OLLAMA_URL  = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llava:7b"   # cambiar a "moondream" si tenés poca RAM

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _encode_image(image_path: pathlib.Path, max_px: int = 800) -> str:
    """
    Devuelve la imagen como string base64 (JPEG, redimensionada a max_px).
    Reducir el tamaño baja el consumo de tokens en APIs remotas y acelera
    la inferencia local.
    """
    img = Image.open(image_path)
    w, h = img.size
    if max(w, h) > max_px:
        scale = max_px / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _parse_json_response(text: str) -> dict:
    """
    Extrae el JSON del texto devuelto por el modelo.
    Usa match greedy ({.*}) para capturar el objeto completo aunque
    el texto de observaciones contenga llaves internas.
    """
    # 1. Bloque ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 2. Primer objeto JSON completo (greedy: del primer { al último })
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # 3. Texto completo
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # 4. Extraer score numérico del texto como fallback
    score_match = re.search(r'"score"\s*:\s*(\d+)', text)
    obs_match   = re.search(r'"observaciones"\s*:\s*"([^"]+)"', text)
    if score_match:
        return {
            "score": int(score_match.group(1)),
            "observaciones": obs_match.group(1) if obs_match else "Respuesta parcial del modelo.",
        }

    return {"score": 0, "observaciones": f"No se pudo parsear respuesta: {text[:120]}"}


# ── Backend: Gemini ────────────────────────────────────────────────────────────

def _analyze_gemini(img_b64: str, prompt: str, api_key: str,
                    delay: float, max_retries: int) -> dict:
    payload = {
        "contents": [{
            "parts": [
                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}},
                {"text": prompt},
            ]
        }],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 256},
    }

    for attempt in range(max_retries):
        response = requests.post(
            GEMINI_URL,
            params={"key": api_key},
            json=payload,
            timeout=30,
        )

        if response.status_code == 429:
            wait = delay * (2 ** (attempt + 1))
            print(f"rate limit, esperando {int(wait)}s...", end=" ", flush=True)
            time.sleep(wait)
            continue

        if response.status_code != 200:
            return {"score": 0, "observaciones": f"Error API {response.status_code}: {response.text[:200]}"}

        try:
            raw = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return _parse_json_response(raw)
        except (KeyError, IndexError) as e:
            return {"score": 0, "observaciones": f"Error procesando respuesta: {e}"}

    return {"score": 0, "observaciones": f"Rate limit persistente tras {max_retries} intentos. Probá --delay más alto."}


# ── Backend: Ollama ────────────────────────────────────────────────────────────

def _analyze_ollama(img_b64: str, prompt: str) -> dict:
    payload = {
        "model":  OLLAMA_MODEL,
        "prompt": prompt,
        "images": [img_b64],
        "stream": False,
        "options": {"temperature": 0.1},
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    except requests.exceptions.ConnectionError:
        return {
            "score": 0,
            "observaciones": (
                "No se pudo conectar con Ollama. "
                "Asegurate de que esté corriendo: ollama serve"
            ),
        }

    if response.status_code != 200:
        return {"score": 0, "observaciones": f"Error Ollama {response.status_code}: {response.text[:200]}"}

    try:
        raw = response.json().get("response", "")
        return _parse_json_response(raw)
    except Exception as e:
        return {"score": 0, "observaciones": f"Error procesando respuesta de Ollama: {e}"}


# ── Interfaz pública ───────────────────────────────────────────────────────────

def analyze_image(image_path: pathlib.Path, prompt: str,
                  api_key: Optional[str] = None,
                  backend: str = "gemini",
                  delay: float = 5.0,
                  max_retries: int = 4) -> dict:
    """
    Analiza una imagen contra un criterio de autenticidad.

    backend="gemini"  → usa Google Gemini Vision (requiere api_key)
    backend="ollama"  → usa modelo local vía Ollama (requiere ollama serve)
    """
    img_b64 = _encode_image(image_path)

    if backend == "ollama":
        return _analyze_ollama(img_b64, prompt)
    else:
        if not api_key:
            return {"score": 0, "observaciones": "Se requiere --api-key para el backend gemini."}
        return _analyze_gemini(img_b64, prompt, api_key, delay, max_retries)


def find_image_for_criterion(folder: pathlib.Path, filename_base: str) -> Optional[pathlib.Path]:
    """Busca la imagen correspondiente a un criterio en la carpeta dada."""
    for ext in SUPPORTED_EXTENSIONS:
        candidate = folder / f"{filename_base}{ext}"
        if candidate.exists():
            return candidate
    return None
