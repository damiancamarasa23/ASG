# ASG API — Guía de Instalación y Primeros Pasos

**Versión:** 0.1.0 — Entorno de Desarrollo Local  
**Requisitos previos:** macOS o Linux, conexión a internet

---

## ¿Qué es esto?

El proyecto ASG (Authenticity Score Generator) es una API que analiza fotos de productos de lujo y devuelve un score de autenticidad usando inteligencia artificial visual.

Esta guía cubre la instalación completa del entorno de desarrollo local, donde la API corre en Docker y el modelo de visión corre en Ollama (en tu propia máquina, sin costos ni límites de API).

---

## Herramientas necesarias

| Herramienta | Para qué sirve | Cómo instalar |
|-------------|---------------|---------------|
| **Docker Desktop** | Corre la API en un contenedor aislado | Ver Paso 1 |
| **Ollama** | Corre el modelo de visión localmente | Ver Paso 2 |

---

## Paso 1 — Instalar Docker Desktop

Docker es la plataforma que permite correr la API sin instalar Python ni dependencias manualmente en tu máquina.

### macOS

1. Ir a [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Descargar **Docker Desktop for Mac** (elegir Apple Silicon si tenés Mac con chip M1/M2/M3, o Intel si es Mac más antiguo)
3. Abrir el archivo `.dmg` descargado y arrastrar Docker a la carpeta Aplicaciones
4. Abrir Docker Desktop desde Aplicaciones
5. Completar el setup inicial (puede pedir contraseña de administrador)
6. Verificar que funciona: abrir una terminal y ejecutar:

```bash
docker --version
```

Debe mostrar algo como: `Docker version 25.0.3`

### Linux (Ubuntu/Debian)

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar para aplicar el grupo
```

---

## Paso 2 — Instalar Ollama

Ollama es el servidor que corre el modelo de visión artificial (llava:7b) en tu propia computadora.

### macOS

```bash
brew install ollama
```

> Si no tenés Homebrew instalado, primero ejecutar:
> ```bash
> /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
> ```

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Verificar instalación

```bash
ollama --version
```

---

## Paso 3 — Descargar el modelo de visión

Este comando descarga el modelo `llava:7b` (~4.7 GB). Solo es necesario hacerlo una vez.

```bash
ollama pull llava:7b
```

La descarga puede tardar entre 5 y 20 minutos según la velocidad de internet. Cuando termine, verás el modelo listado con:

```bash
ollama list
```

---

## Paso 4 — Obtener el código

Si tenés acceso al repositorio:

```bash
git clone <url-del-repositorio>
cd asg-api
```

Si recibiste el código como archivo ZIP:

1. Descomprimir el archivo
2. Abrir una terminal en la carpeta `asg-api`

---

## Paso 5 — Configurar variables de entorno

Copiar el archivo de configuración de ejemplo:

```bash
cp .env.example .env
```

El archivo `.env` ya viene preconfigurado para desarrollo local. No es necesario modificar nada para empezar.

> Para usar Gemini en lugar de Ollama (modo producción), editar `.env` y completar:
> ```
> BACKEND=gemini
> GEMINI_API_KEY=tu_api_key_aqui
> ```

---

## Paso 6 — Levantar el servidor Ollama

Antes de iniciar la API, Ollama debe estar corriendo. Ejecutar en una terminal (dejarla abierta):

```bash
ollama serve
```

Verificar que responde:

```bash
curl http://localhost:11434/api/tags
```

Debe mostrar el modelo `llava:7b` en la lista.

---

## Paso 7 — Levantar la API

En una terminal nueva (con Docker Desktop abierto):

```bash
cd asg-api
docker-compose up --no-deps api
```

Cuando veas esta línea en el log, la API está lista:

```
INFO:     Application startup complete.
```

### Verificar que funciona

```bash
curl http://localhost:8000/health
```

Respuesta esperada:

```json
{"status": "ok"}
```

---

## Paso 8 — Explorar la API

La API incluye documentación interactiva automática. Abrir en el navegador:

```
http://localhost:8000/docs
```

Desde ahí podés ver todos los endpoints disponibles, sus parámetros y probarlos directamente sin escribir código.

---

## Flujo completo de uso

El flujo para analizar un producto tiene 5 pasos:

```
1. Crear sesión          POST /create_session/
2. Obtener URL de subida POST /get_upload_url/       (una vez por foto)
3. Subir foto            PUT  <url_obtenida>          (una vez por foto)
4. Confirmar subida      POST /confirm_upload/        (una vez por foto)
5. Lanzar análisis       POST /generate_scoring/
6. Consultar resultado   GET  /scoring_status/{id}    (polling cada 3s)
```

### Ejemplo paso a paso con curl

**1. Crear sesión:**
```bash
curl -X POST http://localhost:8000/create_session/ \
  -H "Content-Type: application/json" \
  -d '{"consumer_platform_id": "mi_plataforma", "user_id": "usuario_001", "brand": "gucci"}'
```
Respuesta:
```json
{"session_id": "A3F9B21C", "status": "created", "created_at": "..."}
```

**2. Obtener URL para subir una foto:**
```bash
curl -X POST http://localhost:8000/get_upload_url/ \
  -H "Content-Type: application/json" \
  -d '{"session_id": "A3F9B21C", "filename": "01_gg_canvas.jpg"}'
```
Respuesta:
```json
{"upload_url": "http://localhost:8000/internal/upload/A3F9B21C/01_gg_canvas.jpg", "filename": "01_gg_canvas.jpg"}
```

**3. Subir la foto:**
```bash
curl -X PUT http://localhost:8000/internal/upload/A3F9B21C/01_gg_canvas.jpg \
  --data-binary @/ruta/a/tu/foto.jpg
```

**4. Confirmar subida:**
```bash
curl -X POST http://localhost:8000/confirm_upload/ \
  -H "Content-Type: application/json" \
  -d '{"session_id": "A3F9B21C", "filename": "01_gg_canvas.jpg"}'
```

**5. Lanzar análisis** (después de subir todas las fotos):
```bash
curl -X POST http://localhost:8000/generate_scoring/ \
  -H "Content-Type: application/json" \
  -d '{"session_id": "A3F9B21C"}'
```
Respuesta inmediata:
```json
{"session_id": "A3F9B21C", "status": "pending"}
```

**6. Consultar resultado** (repetir hasta que `status` sea `completed`):
```bash
curl http://localhost:8000/scoring_status/A3F9B21C
```
Respuesta cuando termina:
```json
{
  "session_id": "A3F9B21C",
  "status": "completed",
  "final_score": 84,
  "criteria": [
    {"key": "gg_canvas", "label": "Patrón GG Canvas", "score": 87, "weight": 0.20, "image_found": true, "observaciones": "..."},
    ...
  ]
}
```

---

## Fotos requeridas

El sistema evalúa hasta 7 fotos por producto. Nombrarlas exactamente así:

| Archivo | Qué fotografiar |
|---------|----------------|
| `01_gg_canvas.jpg` | Patrón GG Canvas (frente del producto) |
| `02_herrajes.jpg` | Herrajes, cierres y argollas (primer plano) |
| `03_etiqueta.jpg` | Etiqueta interior con número serial |
| `04_costuras.jpg` | Detalle de costuras (vista lateral) |
| `05_interior.jpg` | Interior / forro del producto |
| `06_cierre.jpg` | Sistema de cierre principal |
| `07_challenge.jpg` | Foto anti-fraude: producto junto a código de sesión escrito en papel |

Formatos aceptados: `.jpg`, `.jpeg`, `.png`, `.webp`

> No es obligatorio subir todas las fotos. El score se recalcula sobre las fotos disponibles.

---

## Detener el servidor

```bash
# En la terminal donde corre docker-compose, presionar Ctrl+C
# O desde otra terminal:
docker-compose down
```

---

## Solución de problemas frecuentes

### "Cannot connect to Docker daemon"
Docker Desktop no está abierto. Abrirlo desde Aplicaciones y esperar a que el ícono de la ballena aparezca en la barra de menú.

### "No se pudo conectar con Ollama"
Ollama no está corriendo. Ejecutar `ollama serve` en una terminal.

### El scoring queda en estado `pending` indefinidamente
El modelo `llava:7b` no está descargado. Verificar con `ollama list` y si no aparece, correr `ollama pull llava:7b`.

### Puerto 8000 ocupado
Otro proceso usa ese puerto. Cambiar en `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"   # cambia el 8000 del lado izquierdo
```
Y usar `http://localhost:8001` en lugar de `http://localhost:8000`.

---

## Estructura del proyecto

```
asg-api/
├── docker-compose.yml       ← levanta todo con un comando
├── Dockerfile               ← imagen de la API
├── .env                     ← configuración local (no compartir)
├── .env.example             ← plantilla de configuración
├── requirements.txt         ← dependencias Python
│
├── app/
│   ├── main.py              ← entrada de la aplicación
│   ├── config.py            ← variables de entorno
│   ├── dependencies.py      ← inyección de dependencias
│   ├── api/                 ← endpoints HTTP
│   ├── services/            ← lógica de negocio
│   ├── clients/             ← conexión a Ollama / Gemini / Storage
│   ├── models/              ← estructuras de datos
│   └── repositories/        ← persistencia (JSON local → DynamoDB en producción)
│
└── gucci/
    └── criteria.py          ← criterios y prompts de autenticación Gucci
```

---

*Para consultas técnicas o reportar problemas, contactar al equipo de desarrollo.*
