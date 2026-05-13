#!/usr/bin/env python3
"""
Generador de imágenes sintéticas de prueba para AuthScore Demo.

Crea 7 imágenes placeholder (una por criterio Gucci) en la carpeta
./test_images/ con el naming correcto para el pipeline.

Estas imágenes son solo para verificar que el código corre end-to-end.
Para un test real de autenticación, reemplazalas con fotos reales
(ver FUENTES_IMAGENES.txt para saber dónde conseguirlas).

Uso:
    python generate_test_images.py
    python generate_test_images.py --folder ./mis_fotos   # carpeta custom
"""

import argparse
import pathlib
from PIL import Image, ImageDraw, ImageFont

# Definición de las imágenes a generar
IMAGES = [
    {
        "filename": "01_gg_canvas.jpg",
        "label": "Patrón GG Canvas",
        "description": "Tela con motivo GG repetido\nColor: beige / marrón\nAlineación y simetría del patrón",
        "bg_color": (210, 185, 145),
        "text_color": (80, 55, 30),
        "pattern": "gg",
    },
    {
        "filename": "02_herrajes.jpg",
        "label": "Herrajes / Hardware",
        "description": "Cierre dorado con grabado GUCCI\nAcabado metálico uniforme\nSin descascaramientos",
        "bg_color": (200, 175, 100),
        "text_color": (80, 60, 10),
        "pattern": "metal",
    },
    {
        "filename": "03_etiqueta.jpg",
        "label": "Etiqueta Interior",
        "description": "GUCCI\n123456\nMade in Italy",
        "bg_color": (240, 230, 210),
        "text_color": (30, 30, 30),
        "pattern": "label",
    },
    {
        "filename": "04_costuras.jpg",
        "label": "Costuras",
        "description": "Puntadas regulares y uniformes\nSin hilos sueltos\nTensión consistente",
        "bg_color": (185, 155, 120),
        "text_color": (60, 40, 20),
        "pattern": "stitch",
    },
    {
        "filename": "05_interior.jpg",
        "label": "Interior / Forro",
        "description": "Forro de microfibra suede\nColor uniforme\nBolsillos bien terminados",
        "bg_color": (220, 210, 195),
        "text_color": (50, 40, 30),
        "pattern": "interior",
    },
    {
        "filename": "06_cierre.jpg",
        "label": "Sistema de Cierre",
        "description": "Solapa / cremallera principal\nAlineación correcta\nAcabado de calidad",
        "bg_color": (195, 165, 130),
        "text_color": (60, 40, 20),
        "pattern": "closure",
    },
    {
        "filename": "07_challenge.jpg",
        "label": "Challenge Anti-Fraude",
        "description": "CÓDIGO DE SESIÓN: A3F7B2C1\n[Producto junto al papel con código]",
        "bg_color": (230, 230, 230),
        "text_color": (20, 20, 20),
        "pattern": "challenge",
    },
]


def draw_gg_pattern(draw, width, height, color):
    """Dibuja un patrón GG simplificado."""
    step = 60
    for x in range(0, width, step):
        for y in range(0, height, step):
            # Dos G entrelazadas simplificadas como elipses
            draw.ellipse([x+5, y+5, x+30, y+35], outline=color, width=3)
            draw.ellipse([x+20, y+5, x+45, y+35], outline=color, width=3)


def draw_stitch_pattern(draw, width, height, color):
    """Dibuja líneas de puntadas."""
    step = 20
    dash = 8
    gap = 4
    for y in range(20, height, step):
        x = 10
        while x < width - 10:
            draw.line([(x, y), (x + dash, y)], fill=color, width=2)
            x += dash + gap


def draw_metal_pattern(draw, width, height, color):
    """Dibuja un rectángulo metálico simulado con grabado."""
    cx, cy = width // 2, height // 2
    draw.rectangle([cx-80, cy-40, cx+80, cy+40], outline=color, width=4)
    draw.rectangle([cx-70, cy-30, cx+70, cy+30], outline=color, width=2)


def make_image(spec: dict, size=(800, 600)) -> Image.Image:
    width, height = size
    img = Image.new("RGB", size, spec["bg_color"])
    draw = ImageDraw.Draw(img)

    # Patrón de fondo
    if spec["pattern"] == "gg":
        draw_gg_pattern(draw, width, height, spec["text_color"])
    elif spec["pattern"] == "stitch":
        draw_stitch_pattern(draw, width, height, spec["text_color"])
    elif spec["pattern"] == "metal":
        draw_metal_pattern(draw, width, height, spec["text_color"])

    # Panel semitransparente para el texto
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rectangle([20, 20, width - 20, 200], fill=(255, 255, 255, 180))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Texto: etiqueta principal
    try:
        font_big   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_mono  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 22)
    except OSError:
        font_big = font_small = font_mono = ImageFont.load_default()

    draw.text((40, 35), f"[TEST] {spec['label']}", font=font_big, fill=spec["text_color"])
    draw.text((40, 80), spec["description"], font=font_small, fill=(50, 50, 50))

    # Watermark
    draw.text((width - 200, height - 30), "AuthScore Demo — SYNTHETIC",
              font=font_small, fill=(180, 180, 180))

    # Para la etiqueta, simular texto de etiqueta Gucci real
    if spec["pattern"] == "label":
        cx, cy = width // 2, height // 2 + 40
        draw.rectangle([cx-120, cy-60, cx+120, cy+80], fill=(245, 235, 215), outline=(150,130,100), width=2)
        try:
            font_gucci = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            font_serial = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 20)
        except OSError:
            font_gucci = font_serial = ImageFont.load_default()
        draw.text((cx - 65, cy - 50), "GUCCI", font=font_gucci, fill=(30, 30, 30))
        draw.text((cx - 40, cy), "123456", font=font_serial, fill=(60, 60, 60))
        draw.text((cx - 55, cy + 30), "Made in Italy", font=font_serial, fill=(60, 60, 60))

    # Para el challenge, simular papel con código
    if spec["pattern"] == "challenge":
        cx, cy = width // 2, height // 2 + 40
        draw.rectangle([cx-150, cy-50, cx+150, cy+60], fill=(255, 255, 240), outline=(100, 100, 100), width=2)
        try:
            font_code = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 36)
        except OSError:
            font_code = ImageFont.load_default()
        draw.text((cx - 100, cy - 20), "A3F7B2C1", font=font_code, fill=(20, 20, 20))
        try:
            font_label2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except OSError:
            font_label2 = ImageFont.load_default()
        draw.text((cx - 80, cy + 30), "Código de sesión", font=font_label2, fill=(100, 100, 100))

    return img


def main():
    parser = argparse.ArgumentParser(description="Genera imágenes de prueba para AuthScore Demo")
    parser.add_argument("--folder", default="./test_images", type=pathlib.Path,
                        help="Carpeta de destino (default: ./test_images)")
    args = parser.parse_args()

    folder = args.folder
    folder.mkdir(parents=True, exist_ok=True)

    print(f"\nGenerando imágenes de prueba en: {folder.resolve()}\n")

    for spec in IMAGES:
        img = make_image(spec)
        path = folder / spec["filename"]
        img.save(path, "JPEG", quality=90)
        print(f"  ✓ {spec['filename']}  ({spec['label']})")

    print(f"\n✅ {len(IMAGES)} imágenes generadas correctamente.")
    print(f"\nPara correr el demo con estas imágenes:")
    print(f"  python main.py --api-key TU_GEMINI_KEY --folder {folder}")
    print()
    print("⚠️  Recordá que estas son imágenes SINTÉTICAS.")
    print("   El análisis de Gemini les dará scores bajos porque no son fotos reales.")
    print("   Son útiles solo para verificar que el pipeline corre sin errores.")
    print("   Ver FUENTES_IMAGENES.txt para obtener fotos reales de prueba.\n")


if __name__ == "__main__":
    main()
