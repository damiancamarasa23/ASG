# ASG — Authenticity Score Generator
## Memoria de proyecto para Claude

### Qué es este proyecto
API service B2B que permite validar si un producto de ropa de lujo de segunda mano es auténtico, mediante análisis visual por IA de fotografías del producto. Score probabilístico 0-100, desglosado por criterio. Primera vertical: **Gucci GG Canvas leather goods**.

### Estado actual (Junio 2026)
- ✅ Prototipo CLI funcional (`gucci_auth_demo/`)
- ✅ Soporte para dos backends: Gemini (producción) y Ollama local (desarrollo)
- ✅ Protocolo de 7 fotos con criterios y pesos definidos para Gucci
- ✅ Sistema de anti-fraude: challenge dinámico por sesión
- ✅ Parser de respuestas JSON robusto (greedy + fallback por regex)
- ✅ Redimensionado automático de imágenes (800px) para reducir tokens
- ✅ Backoff exponencial en rate limit
- ✅ README para GitHub
- 🔄 Pendiente: integración Ollama completa validada con fotos reales
- 🔄 Pendiente: agregar soporte para más marcas
- 🔄 Pendiente: API REST wrapper para integración B2B

### Estructura del repo
```
ASG/                          ← raíz del repo git (branch: poc)
├── README.md
├── CLAUDE.md                 ← este archivo
├── .gitignore
└── gucci_auth_demo/
    ├── main.py               ← CLI entry point
    ├── analyzer.py           ← backends Gemini + Ollama, image encoding
    ├── criteria.py           ← 7 criterios Gucci con prompts y pesos
    ├── report.py             ← formato del reporte en consola
    ├── generate_test_images.py
    ├── INSTRUCCIONES.txt
    ├── FUENTES_IMAGENES.txt
    ├── images_dani/          ← fotos de prueba reales (4 fotos Gucci)
    └── images_internet/      ← fotos de prueba de internet (6 fotos)
```

### Cómo correr el proyecto

```bash
cd ASG/gucci_auth_demo
source venv/bin/activate      # activar virtualenv (Python 3.9)

# Con Ollama local (desarrollo) — requiere: ollama serve en otra terminal
python3 main.py --folder ./images_dani --backend ollama

# Con Gemini (producción)
python3 main.py --api-key API_KEY --folder ./images_dani --backend gemini --delay 5

# Generar imágenes sintéticas para testear pipeline
python3 generate_test_images.py
```

### Criterios de autenticación Gucci (con pesos)
| # | Criterio | Peso |
|---|----------|------|
| 01 | Patrón GG Canvas | 20% |
| 02 | Herrajes / Hardware | 15% |
| 03 | Etiqueta interior + serial | 20% |
| 04 | Costuras | 15% |
| 05 | Interior / Forro | 15% |
| 06 | Sistema de cierre / solapa | 10% |
| 07 | Challenge anti-fraude | 5% |

### Modelo de negocio
- **B2B API** — marketplaces de reventa de lujo integran el API
- **Revenue**: pay-per-use (USD 0,80–2,50/verificación) + planes de volumen mensual
- **Mercado inicial**: LATAM + España
- **Documento de negocio**: `AuthScore_Modelo_de_Negocio.docx` en la carpeta raíz del proyecto
- **Google Doc compartido**: https://docs.google.com/document/d/1Ove-UZE_0Dch8h3gs3eWM6arJl5lzu0ErcAAs8m4JHY

### Decisiones técnicas tomadas
- **Gemini backend**: `gemini-2.0-flash-lite` via REST (no SDK), redimensionado a 800px
- **Ollama backend**: `llava:7b` por defecto, configurable con `--model moondream` si poca RAM
- **Python 3.9** (versión del sistema de Damian) — usar `Optional[X]` en vez de `X | None`
- **Virtualenv** en `gucci_auth_demo/venv/` (excluido del repo)
- **Rate limit**: backoff exponencial × 4 intentos, delay configurable con `--delay`

### Problemas conocidos y soluciones
- **Rate limit Gemini free tier**: reducir tamaño de imágenes + delay entre requests. Solución definitiva: habilitar billing en Google AI Studio.
- **JSON parsing**: LLaVA a veces retorna JSON con `}` dentro de strings → usar regex greedy `\{.*\}` en lugar de non-greedy.
- **Python 3.9**: no soporta `X | None` syntax → usar `from typing import Optional`.

### Próximos pasos sugeridos
1. Integrar Ollama y validar scores con `images_dani` (fotos reales Gucci)
2. Añadir soporte para más marcas (Prada, LV) en `criteria.py`
3. Construir API REST wrapper (FastAPI) para integración B2B
4. Definir estrategia de datos de entrenamiento para fine-tuning futuro
5. Explorar acuerdos con plataformas de reventa para piloto
