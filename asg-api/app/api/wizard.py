import json
import pathlib

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

PRODUCTS_PATH = pathlib.Path(__file__).parent.parent.parent / "gucci" / "products.json"
CRITERIA_PATH = pathlib.Path(__file__).parent.parent.parent / "gucci" / "criteria.py"

router = APIRouter(tags=["wizard"])

CRITERIA_META = {
    "gg_canvas":  {"label": "Patrón GG Canvas",              "hint": "Fotografiá el frente del producto mostrando el patrón completo."},
    "herrajes":   {"label": "Herrajes / Hardware",            "hint": "Primer plano de cierres, argollas o hebillas metálicas."},
    "etiqueta":   {"label": "Etiqueta Interior",              "hint": "Fotografiá la etiqueta interior con el número serial visible."},
    "costuras":   {"label": "Costuras",                       "hint": "Detalle lateral de las costuras, bien iluminado."},
    "interior":   {"label": "Interior / Forro",               "hint": "Abrí el producto y fotografiá el interior completo."},
    "cierre":     {"label": "Sistema de Cierre / Solapa",     "hint": "Fotografiá el mecanismo de cierre principal."},
    "challenge":  {"label": "Challenge Anti-Fraude",          "hint": "Producto junto a un papel con el código de sesión escrito a mano."},
}


@router.get("/wizard", response_class=HTMLResponse)
def wizard_page():
    products = json.loads(PRODUCTS_PATH.read_text())
    products_json = json.dumps(products)
    criteria_json = json.dumps(CRITERIA_META)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ASG — Autenticación de Producto</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0f4f8; color: #1a1a2e; min-height: 100vh; display: flex; flex-direction: column; }}

    .header {{
      background: #1a1a2e; color: white;
      padding: 20px 40px;
      display: flex; align-items: center; gap: 16px;
    }}
    .header h1 {{ font-size: 18px; font-weight: 600; }}
    .header .step-indicator {{ margin-left: auto; font-size: 13px; color: #8892a4; }}

    .progress-bar {{ height: 3px; background: #e8edf2; }}
    .progress-fill {{ height: 100%; background: #0f3460; transition: width 0.4s ease; }}

    .container {{ flex: 1; display: flex; align-items: center; justify-content: center; padding: 40px 20px; }}

    .card {{
      background: white; border-radius: 16px;
      box-shadow: 0 4px 24px rgba(0,0,0,0.10);
      width: 100%; max-width: 520px;
      overflow: hidden;
    }}

    .card-body {{ padding: 40px; }}
    .screen {{ display: none; }}
    .screen.active {{ display: block; }}

    h2 {{ font-size: 22px; font-weight: 700; margin-bottom: 8px; }}
    .subtitle {{ font-size: 14px; color: #6b7a8d; margin-bottom: 28px; line-height: 1.5; }}

    label {{ display: block; font-size: 13px; font-weight: 600; color: #1a1a2e; margin-bottom: 6px; }}

    select, input[type="text"] {{
      width: 100%; padding: 12px 14px;
      border: 1.5px solid #dde3ea; border-radius: 8px;
      font-size: 14px; color: #1a1a2e;
      background: white; outline: none;
      transition: border-color 0.2s;
    }}
    select:focus, input[type="text"]:focus {{ border-color: #0f3460; }}

    .field {{ margin-bottom: 20px; }}

    /* Upload area */
    .upload-area {{
      border: 2px dashed #dde3ea; border-radius: 12px;
      padding: 40px 20px; text-align: center;
      cursor: pointer; transition: all 0.2s;
      position: relative; margin-bottom: 16px;
    }}
    .upload-area:hover {{ border-color: #0f3460; background: #f8fafc; }}
    .upload-area.has-file {{ border-color: #0f3460; background: #f0f6ff; border-style: solid; }}
    .upload-area.error {{ border-color: #e74c3c; background: #fff5f5; }}
    .upload-icon {{ font-size: 32px; margin-bottom: 10px; }}
    .upload-text {{ font-size: 14px; color: #6b7a8d; }}
    .upload-text strong {{ color: #0f3460; }}
    .upload-area input[type="file"] {{ position: absolute; inset: 0; opacity: 0; cursor: pointer; }}
    .file-name {{ font-size: 13px; color: #0f3460; font-weight: 600; margin-top: 6px; }}

    .preview-img {{ width: 100%; max-height: 200px; object-fit: cover; border-radius: 8px; margin-bottom: 16px; display: none; }}

    /* Hint box */
    .hint {{
      background: #f0f6ff; border-left: 3px solid #0f3460;
      border-radius: 0 8px 8px 0; padding: 12px 16px;
      font-size: 13px; color: #0f3460; margin-bottom: 20px; line-height: 1.5;
    }}

    /* Validation feedback */
    .quality-feedback {{
      border-radius: 8px; padding: 12px 16px;
      font-size: 13px; margin-bottom: 16px; display: none;
    }}
    .quality-feedback.ok {{ background: #eafaf1; color: #1e8449; border: 1px solid #a9dfbf; }}
    .quality-feedback.fail {{ background: #fff5f5; color: #c0392b; border: 1px solid #f5b7b1; }}
    .quality-feedback ul {{ margin-top: 6px; padding-left: 16px; }}
    .quality-feedback li {{ margin-top: 4px; }}

    /* Buttons */
    .btn {{
      width: 100%; padding: 14px;
      border: none; border-radius: 10px;
      font-size: 15px; font-weight: 600;
      cursor: pointer; transition: all 0.2s;
    }}
    .btn-primary {{ background: #0f3460; color: white; }}
    .btn-primary:hover {{ background: #1a4a7a; }}
    .btn-primary:disabled {{ background: #8892a4; cursor: not-allowed; }}
    .btn-secondary {{ background: #f0f4f8; color: #6b7a8d; margin-top: 10px; }}
    .btn-secondary:hover {{ background: #e0e8f0; }}
    .btn-danger {{ background: #fff0f0; color: #c0392b; margin-top: 10px; }}
    .btn-danger:hover {{ background: #ffe0e0; }}

    /* Progress dots */
    .dots {{ display: flex; gap: 8px; justify-content: center; margin-bottom: 28px; }}
    .dot {{ width: 8px; height: 8px; border-radius: 50%; background: #dde3ea; transition: all 0.3s; }}
    .dot.active {{ background: #0f3460; transform: scale(1.3); }}
    .dot.done {{ background: #a9dfbf; }}

    /* Scoring screen */
    .score-circle {{
      width: 140px; height: 140px; border-radius: 50%;
      border: 8px solid #0f3460;
      display: flex; align-items: center; justify-content: center;
      flex-direction: column; margin: 0 auto 28px;
    }}
    .score-number {{ font-size: 42px; font-weight: 800; color: #0f3460; line-height: 1; }}
    .score-label {{ font-size: 12px; color: #6b7a8d; margin-top: 2px; }}

    .spinning {{ border-color: #dde3ea; border-top-color: #0f3460; animation: spin 1s linear infinite; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}

    .criteria-list {{ margin-top: 20px; }}
    .criterion-row {{
      display: flex; align-items: flex-start; gap: 12px;
      padding: 12px 0; border-bottom: 1px solid #f0f4f8;
      font-size: 13px;
    }}
    .criterion-row:last-child {{ border-bottom: none; }}
    .c-label {{ flex: 1; font-weight: 600; color: #1a1a2e; }}
    .c-obs {{ flex: 2; color: #6b7a8d; line-height: 1.4; }}
    .c-score {{ font-weight: 700; color: #0f3460; min-width: 40px; text-align: right; }}

    .verdict {{
      text-align: center; padding: 12px 20px;
      border-radius: 8px; font-weight: 600; font-size: 15px;
      margin-bottom: 20px;
    }}
    .verdict.high {{ background: #eafaf1; color: #1e8449; }}
    .verdict.medium {{ background: #fef9e7; color: #d68910; }}
    .verdict.low {{ background: #fff5f5; color: #c0392b; }}
  </style>
</head>
<body>

<div class="header">
  <div>
    <h1>ASG — Autenticación de Producto</h1>
  </div>
  <span class="step-indicator" id="step-indicator"></span>
</div>
<div class="progress-bar"><div class="progress-fill" id="progress-fill" style="width:0%"></div></div>

<div class="container">
  <div class="card">
    <div class="card-body">

      <!-- SCREEN 1: Select brand/product -->
      <div class="screen active" id="screen-select">
        <h2>Nueva autenticación</h2>
        <p class="subtitle">Seleccioná la marca y el modelo del producto a analizar.</p>

        <div class="field">
          <label>Marca</label>
          <select id="brand-select">
            <option value="gucci">Gucci</option>
          </select>
        </div>

        <div class="field">
          <label>Modelo</label>
          <select id="product-select"></select>
        </div>

        <div class="field">
          <label>ID de usuario (opcional)</label>
          <input type="text" id="user-id" placeholder="Ej: user_001">
        </div>

        <button class="btn btn-primary" onclick="startSession()">Comenzar →</button>
      </div>

      <!-- SCREEN N: Upload photo -->
      <div class="screen" id="screen-upload">
        <div class="dots" id="dots"></div>
        <h2 id="upload-title"></h2>
        <p class="subtitle" id="upload-subtitle">Subí una foto clara y bien iluminada.</p>
        <div class="hint" id="upload-hint"></div>

        <img class="preview-img" id="preview-img">

        <div class="upload-area" id="upload-area" onclick="document.getElementById('file-input').click()">
          <div class="upload-icon">📷</div>
          <div class="upload-text">
            <strong>Hacé clic para seleccionar</strong><br>o arrastrá la foto aquí
          </div>
          <div class="file-name" id="file-name"></div>
          <input type="file" id="file-input" accept="image/*" onchange="onFileSelected(event)">
        </div>

        <div class="quality-feedback" id="quality-feedback"></div>

        <button class="btn btn-primary" id="btn-next" onclick="uploadAndNext()" disabled>
          Validar y continuar →
        </button>
        <button class="btn btn-danger" onclick="cancelProcess()">Cancelar proceso</button>
      </div>

      <!-- SCREEN: Scoring in progress / result -->
      <div class="screen" id="screen-scoring">
        <div style="text-align:center; margin-bottom: 24px;">
          <div class="score-circle spinning" id="score-circle" style="margin-bottom: 16px;">
            <div class="score-number" id="score-number">···</div>
            <div class="score-label" id="score-label">analizando</div>
          </div>
          <h2 id="scoring-title">Analizando imágenes</h2>
          <p class="subtitle" id="scoring-subtitle">Esto puede tardar unos minutos. No cierres esta ventana.</p>
        </div>

        <div class="verdict" id="verdict" style="display:none"></div>
        <div class="criteria-list" id="criteria-list"></div>

        <button class="btn btn-primary" id="btn-restart" style="display:none; margin-top:24px;" onclick="restart()">
          Nueva autenticación
        </button>
      </div>

    </div>
  </div>
</div>

<script>
const PRODUCTS = {products_json};
const CRITERIA_META = {criteria_json};

let sessionId = null;
let activeCriteria = [];
let currentStep = 0;
let selectedFile = null;

// ── Init ──────────────────────────────────────────────────────────────────────

function populateProducts() {{
  const sel = document.getElementById('product-select');
  sel.innerHTML = '';
  for (const [id, p] of Object.entries(PRODUCTS)) {{
    const opt = document.createElement('option');
    opt.value = id;
    opt.textContent = p.name;
    sel.appendChild(opt);
  }}
}}

populateProducts();

// ── Screen helpers ────────────────────────────────────────────────────────────

function showScreen(id) {{
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}}

function setProgress(current, total) {{
  const pct = total === 0 ? 0 : Math.round((current / total) * 100);
  document.getElementById('progress-fill').style.width = pct + '%';
  document.getElementById('step-indicator').textContent =
    total > 0 ? `Foto ${{current}} de ${{total}}` : '';
}}

function renderDots(total, current) {{
  const container = document.getElementById('dots');
  container.innerHTML = '';
  for (let i = 0; i < total; i++) {{
    const d = document.createElement('div');
    d.className = 'dot' + (i < current ? ' done' : '') + (i === current ? ' active' : '');
    container.appendChild(d);
  }}
}}

// ── Step 1: Start session ─────────────────────────────────────────────────────

async function startSession() {{
  const productId = document.getElementById('product-select').value;
  const userId = document.getElementById('user-id').value || 'anonymous';

  const res = await fetch('/create_session/', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{ consumer_platform_id: 'wizard', user_id: userId, brand: 'gucci' }})
  }});
  const data = await res.json();
  sessionId = data.session_id;

  activeCriteria = PRODUCTS[productId].criteria;
  currentStep = 0;
  showUploadScreen();
}}

// ── Step N: Upload photo ──────────────────────────────────────────────────────

function showUploadScreen() {{
  const key = activeCriteria[currentStep];
  const meta = CRITERIA_META[key];
  const total = activeCriteria.length;

  document.getElementById('upload-title').textContent = meta.label;
  document.getElementById('upload-hint').textContent = meta.hint;
  document.getElementById('quality-feedback').style.display = 'none';
  document.getElementById('file-name').textContent = '';
  document.getElementById('preview-img').style.display = 'none';
  document.getElementById('btn-next').disabled = true;
  document.getElementById('upload-area').className = 'upload-area';
  document.getElementById('file-input').value = '';
  selectedFile = null;

  renderDots(total, currentStep);
  setProgress(currentStep + 1, total);
  showScreen('screen-upload');
}}

function onFileSelected(event) {{
  const file = event.target.files[0];
  if (!file) return;
  selectedFile = file;
  document.getElementById('file-name').textContent = file.name;
  document.getElementById('upload-area').classList.add('has-file');
  document.getElementById('btn-next').disabled = false;
  document.getElementById('quality-feedback').style.display = 'none';

  const reader = new FileReader();
  reader.onload = e => {{
    const img = document.getElementById('preview-img');
    img.src = e.target.result;
    img.style.display = 'block';
  }};
  reader.readAsDataURL(file);
}}

async function uploadAndNext() {{
  if (!selectedFile) return;

  const btn = document.getElementById('btn-next');
  btn.disabled = true;
  btn.textContent = 'Validando...';

  // 1. Validate quality
  const qualityRes = await fetch('/validate_image_quality/', {{
    method: 'POST',
    body: selectedFile
  }});
  const quality = await qualityRes.json();
  const feedback = document.getElementById('quality-feedback');

  if (!quality.ok) {{
    feedback.className = 'quality-feedback fail';
    feedback.innerHTML = '<strong>La foto no cumple los requisitos mínimos:</strong><ul>' +
      quality.issues.map(i => `<li>${{i}}</li>`).join('') + '</ul>';
    feedback.style.display = 'block';
    document.getElementById('upload-area').classList.add('error');
    btn.disabled = false;
    btn.textContent = 'Validar y continuar →';
    return;
  }}

  feedback.className = 'quality-feedback ok';
  feedback.innerHTML = '✓ Foto válida';
  feedback.style.display = 'block';
  btn.textContent = 'Subiendo...';

  // 2. Get upload URL
  const key = activeCriteria[currentStep];
  const filename = `${{String(currentStep + 1).padStart(2,'0')}}_${{key}}.jpg`;

  const urlRes = await fetch('/get_upload_url/', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{ session_id: sessionId, filename }})
  }});
  const {{ upload_url }} = await urlRes.json();

  // 3. Upload image
  await fetch(upload_url, {{ method: 'PUT', body: selectedFile }});

  // 4. Confirm upload
  await fetch('/confirm_upload/', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{ session_id: sessionId, filename }})
  }});

  btn.textContent = 'Validar y continuar →';
  currentStep++;

  if (currentStep < activeCriteria.length) {{
    showUploadScreen();
  }} else {{
    startScoring();
  }}
}}

// ── Final: Scoring ────────────────────────────────────────────────────────────

async function startScoring() {{
  const productId = document.getElementById('product-select').value;
  showScreen('screen-scoring');
  setProgress(activeCriteria.length, activeCriteria.length);
  document.getElementById('step-indicator').textContent = 'Analizando...';

  await fetch('/generate_scoring/', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{ session_id: sessionId, product_id: productId }})
  }});

  pollStatus();
}}

async function pollStatus() {{
  const res = await fetch(`/scoring_status/${{sessionId}}`);
  const data = await res.json();

  if (data.status === 'processing' || data.status === 'pending') {{
    setTimeout(pollStatus, 3000);
    return;
  }}

  if (data.status === 'failed') {{
    document.getElementById('scoring-title').textContent = 'Error en el análisis';
    document.getElementById('scoring-subtitle').textContent = data.error || 'Ocurrió un error inesperado.';
    document.getElementById('score-circle').classList.remove('spinning');
    document.getElementById('btn-restart').style.display = 'block';
    document.getElementById('step-indicator').textContent = '';
    return;
  }}

  // Completed
  const score = data.final_score;
  const circle = document.getElementById('score-circle');
  circle.classList.remove('spinning');
  document.getElementById('score-number').textContent = score;
  document.getElementById('score-label').textContent = '/ 100';
  document.getElementById('scoring-title').textContent = 'Análisis completado';
  document.getElementById('scoring-subtitle').textContent = `Sesión: ${{sessionId}}`;
  document.getElementById('step-indicator').textContent = '';

  const verdict = document.getElementById('verdict');
  verdict.style.display = 'block';
  if (score >= 75) {{
    verdict.className = 'verdict high';
    verdict.textContent = '✓ Alta probabilidad de autenticidad';
  }} else if (score >= 50) {{
    verdict.className = 'verdict medium';
    verdict.textContent = '⚠ Probabilidad media — revisar observaciones';
  }} else {{
    verdict.className = 'verdict low';
    verdict.textContent = '✗ Baja probabilidad de autenticidad';
  }}

  const list = document.getElementById('criteria-list');
  list.innerHTML = (data.criteria || []).map(c => `
    <div class="criterion-row">
      <div class="c-label">${{c.label}}</div>
      <div class="c-obs">${{c.observaciones}}</div>
      <div class="c-score">${{c.score}}</div>
    </div>
  `).join('');

  document.getElementById('btn-restart').style.display = 'block';
}}

// ── Cancel / Restart ──────────────────────────────────────────────────────────

function cancelProcess() {{
  if (!confirm('¿Cancelar el proceso? Se perderán las fotos cargadas.')) return;
  restart();
}}

function restart() {{
  sessionId = null;
  activeCriteria = [];
  currentStep = 0;
  selectedFile = null;
  setProgress(0, 0);
  document.getElementById('step-indicator').textContent = '';
  document.getElementById('score-number').textContent = '···';
  document.getElementById('score-label').textContent = 'analizando';
  document.getElementById('score-circle').classList.add('spinning');
  document.getElementById('verdict').style.display = 'none';
  document.getElementById('criteria-list').innerHTML = '';
  document.getElementById('btn-restart').style.display = 'none';
  showScreen('screen-select');
}}
</script>

</body>
</html>"""
    return html
