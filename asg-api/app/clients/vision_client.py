"""
Vision clients — abstraction over Ollama (local) and Gemini (production).
Adapted from gucci_auth_demo/analyzer.py.
"""

import base64
import io
import json
import re
import time
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from PIL import Image


class VisionClient(ABC):
    @abstractmethod
    def analyze(self, image_path: Path, prompt: str) -> dict:
        pass

    def _encode_image(self, image_path: Path, max_px: int = 800) -> str:
        img = Image.open(image_path)
        w, h = img.size
        if max(w, h) > max_px:
            scale = max_px / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def _parse_json_response(self, text: str) -> dict:
        match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        score_match = re.search(r'"score"\s*:\s*(\d+)', text)
        obs_match = re.search(r'"observaciones"\s*:\s*"([^"]+)"', text)
        if score_match:
            return {
                "score": int(score_match.group(1)),
                "observaciones": obs_match.group(1) if obs_match else "Respuesta parcial.",
            }

        return {"score": 0, "observaciones": f"No se pudo parsear: {text[:120]}"}


class OllamaClient(VisionClient):
    def __init__(self, base_url: str, model: str):
        self.url = f"{base_url}/api/generate"
        self.model = model

    def analyze(self, image_path: Path, prompt: str) -> dict:
        img_b64 = self._encode_image(image_path)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [img_b64],
            "stream": False,
            "options": {"temperature": 0.1},
        }
        try:
            response = requests.post(self.url, json=payload, timeout=120)
        except requests.exceptions.ConnectionError:
            return {
                "score": 0,
                "observaciones": "No se pudo conectar con Ollama. Verificá que esté corriendo: ollama serve",
            }

        if response.status_code != 200:
            return {"score": 0, "observaciones": f"Error Ollama {response.status_code}: {response.text[:200]}"}

        raw = response.json().get("response", "")
        return self._parse_json_response(raw)


class GeminiClient(VisionClient):
    URL = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.0-flash-lite:generateContent"
    )

    def __init__(self, api_key: str, delay: float = 5.0, max_retries: int = 4):
        self.api_key = api_key
        self.delay = delay
        self.max_retries = max_retries

    def analyze(self, image_path: Path, prompt: str) -> dict:
        img_b64 = self._encode_image(image_path)
        payload = {
            "contents": [{"parts": [
                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}},
                {"text": prompt},
            ]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 256},
        }

        for attempt in range(self.max_retries):
            response = requests.post(
                self.URL,
                params={"key": self.api_key},
                json=payload,
                timeout=30,
            )
            if response.status_code == 429:
                wait = self.delay * (2 ** (attempt + 1))
                time.sleep(wait)
                continue
            if response.status_code != 200:
                return {"score": 0, "observaciones": f"Error API {response.status_code}: {response.text[:200]}"}
            try:
                raw = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                return self._parse_json_response(raw)
            except (KeyError, IndexError) as e:
                return {"score": 0, "observaciones": f"Error procesando respuesta: {e}"}

        return {"score": 0, "observaciones": f"Rate limit persistente tras {self.max_retries} intentos."}
