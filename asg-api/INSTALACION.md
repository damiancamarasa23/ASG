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

```bash
git clone git@github.com:damiancamarasa23/ASG.git
cd ASG
git checkout poc
cd asg-api
```

---

## Paso 5 — Configurar variables de entorno

Copiar el archivo de configuración de ejemplo:

```bash
cp .env.example .env
```

Abrir el archivo `.env` recién creado con cualquier editor de texto. Su contenido es:

```env
# Vision backend: "ollama" (local) o "gemini" (producción)
BACKEND=ollama

# Ollama settings
OLLAMA_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llava:7b

# Gemini settings (solo necesario si BACKEND=gemini)
GEMINI_API_KEY=

# Storage
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=/tmp/asg_storage
API_BASE_URL=http://localhost:8000
```

### Variables que sí o sí hay que revisar

**`OLLAMA_URL`** — indica dónde está corriendo Ollama.

| Situación | Valor correcto |
|-----------|---------------|
| Ollama corre en tu Mac (lo más común) | `http://host.docker.internal:11434` |
| Ollama corre dentro de Docker Compose | `http://ollama:11434` |

En casi todos los casos usarás `http://host.docker.internal:11434`. Si al lanzar el análisis ves el error *"No se pudo conectar con Ollama"*, es que esta URL está mal.

**`OLLAMA_MODEL`** — modelo de visión a usar. Dejarlo en `llava:7b` a menos que hayas descargado otro modelo (ej: `moondream`).

### Variables opcionales

**`BACKEND`** — cambiar a `gemini` solo si querés usar la API de Google en lugar de Ollama local. En ese caso también completar `GEMINI_API_KEY`.

**`GEMINI_API_KEY`** — clave de la API de Google Gemini. Obtenerla gratis en [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey). Solo necesaria si `BACKEND=gemini`.

**`LOCAL_STORAGE_PATH`** — carpeta donde se guardan las imágenes subidas. El valor por defecto `/tmp/asg_storage` funciona en Mac y Linux. Podés cambiarlo a cualquier ruta, por ejemplo `/Users/tu_usuario/asg_storage`.

**`API_BASE_URL`** — URL base de la API. Dejar en `http://localhost:8000` para desarrollo local.

> **Importante:** el archivo `.env` nunca debe subirse a GitHub ya que puede contener claves privadas. Ya está excluido en el `.gitignore` del proyecto.

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

## Paso 8 — Verificar que todo funciona

```bash
curl http://localhost:8000/health
```

Respuesta esperada: `{"status": "ok"}`

---

## Interfaces disponibles

Una vez levantada la API, tenés tres interfaces:

| URL | Qué es |
|-----|--------|
| `http://localhost:8000/wizard` | **Wizard de autenticación** — subís fotos paso a paso y obtenés el score. Empezá por acá. |
| `http://localhost:8000/admin` | **Configuración de productos** — define qué fotos se piden por modelo de producto |
| `http://localhost:8000/docs` | **Documentación interactiva** de todos los endpoints de la API |

---

## Cómo hacer una autenticación (Wizard)

1. Abrir `http://localhost:8000/wizard`
2. Seleccionar marca y modelo del producto
3. Por cada foto requerida: seleccionar el archivo → el sistema valida calidad automáticamente → si pasa, continuar a la siguiente
4. Al subir la última foto, el análisis se lanza automáticamente
5. Esperar el resultado (puede tardar varios minutos con Ollama local)

> **Nota sobre tiempos con Ollama local:** el modelo `llava:7b` analiza las fotos de a una en la CPU. Cada foto tarda ~50 segundos, por lo que una sesión de 4-6 fotos puede tardar 4-6 minutos. Esto es esperable en desarrollo local.

---

## Configurar modelos de producto (Admin)

En `http://localhost:8000/admin` podés ver los modelos de producto cargados y activar o desactivar qué criterios (fotos) aplican a cada uno. Los cambios se guardan en `gucci/products.json` y se aplican inmediatamente sin reiniciar.

Para agregar un nuevo modelo, editar directamente el archivo `gucci/products.json`:

```json
"gucci_nuevo_modelo": {
  "name": "Nombre del modelo",
  "description": "Descripción breve",
  "criteria": ["gg_canvas", "herrajes", "etiqueta", "costuras"]
}
```

Los criterios disponibles son: `gg_canvas`, `herrajes`, `etiqueta`, `costuras`, `interior`, `cierre`, `challenge`.

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

### El wizard no carga o muestra error 500
Revisar los logs del container: `docker logs asg-api-api-1 --tail 30`

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
    ├── criteria.py          ← criterios y prompts de autenticación Gucci
    └── products.json        ← modelos de producto y criterios activos por modelo
```

---

*Para consultas técnicas o reportar problemas, contactar al equipo de desarrollo.*
