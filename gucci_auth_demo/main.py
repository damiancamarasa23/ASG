#!/usr/bin/env python3
"""
AuthScore Demo — Autenticación de productos Gucci

Backends disponibles:
  gemini  → Google Gemini Vision API (producción, requiere API key)
  ollama  → Modelo local vía Ollama (desarrollo, sin límites ni costos)

Uso:
    # Con Gemini
    python main.py --api-key TU_KEY --folder ./fotos --backend gemini

    # Con Ollama (requiere: brew install ollama && ollama pull llava:7b && ollama serve)
    python main.py --folder ./fotos --backend ollama

Las fotos deben nombrarse así (soporta .jpg, .jpeg, .png, .webp):
    01_gg_canvas.jpg      — Patrón GG Canvas (frente del producto)
    02_herrajes.jpg       — Herrajes / cierres / argollas
    03_etiqueta.jpg       — Etiqueta interior con número serial
    04_costuras.jpg       — Detalle de costuras (lateral)
    05_interior.jpg       — Interior / forro del producto
    06_cierre.jpg         — Sistema de cierre / solapa principal
    07_challenge.jpg      — Foto con código de sesión (anti-fraude)
"""

import argparse
import pathlib
import sys
import time
import uuid

from criteria import GUCCI_CRITERIA
from analyzer import analyze_image, find_image_for_criterion
from report import CriterionResult, print_report


def parse_args():
    parser = argparse.ArgumentParser(
        description="AuthScore — Demo de autenticación de productos Gucci"
    )
    parser.add_argument(
        "--folder",
        required=True,
        type=pathlib.Path,
        help="Carpeta con las fotos del producto a analizar",
    )
    parser.add_argument(
        "--backend",
        choices=["gemini", "ollama"],
        default="gemini",
        help="Motor de análisis: 'gemini' (API remota) o 'ollama' (modelo local). Default: gemini",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API Key de Google Gemini (requerida solo con --backend gemini)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Modelo de Ollama a usar (default: llava:7b). Ej: --model moondream",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=5.0,
        help="Segundos de pausa entre requests (default: 5). Solo aplica a backend gemini.",
    )
    parser.add_argument(
        "--session-id",
        default=None,
        help="ID de sesión (opcional, se genera automáticamente si no se especifica)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Validaciones
    folder = args.folder.resolve()
    if not folder.exists() or not folder.is_dir():
        print(f"Error: la carpeta '{folder}' no existe.", file=sys.stderr)
        sys.exit(1)

    if args.backend == "gemini" and not args.api_key:
        print("Error: --api-key es requerido con --backend gemini.", file=sys.stderr)
        sys.exit(1)

    # Sobreescribir modelo de Ollama si se especificó
    if args.model:
        import analyzer
        analyzer.OLLAMA_MODEL = args.model

    session_id = args.session_id or str(uuid.uuid4())[:8].upper()

    print(f"\nAuthScore Demo — Backend: {args.backend.upper()}")
    print(f"Fotos en: {folder}")
    print(f"Sesión:   {session_id}")
    print(f"Criterios a evaluar: {len(GUCCI_CRITERIA)}")
    print()

    results = []

    for criterion in GUCCI_CRITERIA:
        image_path = find_image_for_criterion(folder, criterion["filename"])

        if image_path is None:
            print(f"  ⚫ [{criterion['label']}] — foto no encontrada, se omite")
            results.append(CriterionResult(
                key=criterion["key"],
                label=criterion["label"],
                weight=criterion["weight"],
                score=0,
                observaciones="Foto no proporcionada",
                image_found=False,
            ))
            continue

        print(f"  🔍 [{criterion['label']}] ({image_path.name})...", end=" ", flush=True)

        try:
            result = analyze_image(
                image_path,
                criterion["prompt"],
                api_key=args.api_key,
                backend=args.backend,
                delay=args.delay,
            )
            score = max(0, min(100, int(result.get("score", 0))))
            observaciones = result.get("observaciones", "Sin observaciones")
            print(f"Score: {score}/100")

            # Pausa entre requests (solo relevante para Gemini)
            if args.backend == "gemini":
                time.sleep(args.delay)

        except Exception as e:
            score = 0
            observaciones = f"Error al analizar: {e}"
            print(f"ERROR — {e}")

        results.append(CriterionResult(
            key=criterion["key"],
            label=criterion["label"],
            weight=criterion["weight"],
            score=score,
            observaciones=observaciones,
            image_found=True,
        ))

    print_report(results, session_id)


if __name__ == "__main__":
    main()
