import json
import pathlib

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

from gucci.criteria import GUCCI_CRITERIA

PRODUCTS_PATH = pathlib.Path(__file__).parent.parent.parent / "gucci" / "products.json"

router = APIRouter(tags=["admin"])

ALL_CRITERIA = {c["key"]: c["label"] for c in GUCCI_CRITERIA}


def _load_products() -> dict:
    return json.loads(PRODUCTS_PATH.read_text())


def _save_products(data: dict):
    PRODUCTS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))


@router.get("/admin", response_class=HTMLResponse)
def admin_page():
    products = _load_products()
    criteria_keys = list(ALL_CRITERIA.keys())

    rows = ""
    for pid, product in products.items():
        active = set(product["criteria"])
        cells = ""
        for key in criteria_keys:
            checked = "checked" if key in active else ""
            cells += f"""
            <td class="cell">
              <input type="checkbox" name="{pid}:{key}" {checked}>
            </td>"""
        rows += f"""
        <tr>
          <td class="product-cell">
            <div class="product-name">{product['name']}</div>
            <div class="product-desc">{product['description']}</div>
          </td>
          {cells}
        </tr>"""

    header_cells = "".join(
        f'<th class="criterion-header"><span>{label}</span></th>'
        for label in ALL_CRITERIA.values()
    )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ASG — Configuración de Productos</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0f4f8; color: #1a1a2e; }}

    .header {{
      background: #1a1a2e;
      color: white;
      padding: 24px 40px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .header h1 {{ font-size: 20px; font-weight: 600; letter-spacing: 0.5px; }}
    .header span {{ font-size: 13px; color: #8892a4; }}

    .container {{ padding: 40px; max-width: 1100px; margin: 0 auto; }}

    .card {{
      background: white;
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.08);
      overflow: hidden;
    }}

    .card-header {{
      padding: 20px 28px;
      border-bottom: 1px solid #e8edf2;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .card-header h2 {{ font-size: 15px; font-weight: 600; color: #1a1a2e; }}
    .card-header p {{ font-size: 13px; color: #8892a4; margin-top: 2px; }}

    table {{ width: 100%; border-collapse: collapse; }}

    th {{
      background: #f8fafc;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #6b7a8d;
      padding: 12px 8px;
      border-bottom: 1px solid #e8edf2;
    }}
    .criterion-header {{ width: 80px; text-align: center; }}
    .criterion-header span {{
      writing-mode: vertical-rl;
      transform: rotate(180deg);
      display: inline-block;
      padding: 4px 0;
    }}
    .product-col {{ width: 260px; text-align: left; padding-left: 28px; }}

    tr:not(:last-child) td {{ border-bottom: 1px solid #f0f4f8; }}
    tr:hover td {{ background: #f8fafc; }}

    .product-cell {{ padding: 16px 20px 16px 28px; }}
    .product-name {{ font-size: 14px; font-weight: 600; color: #1a1a2e; }}
    .product-desc {{ font-size: 12px; color: #8892a4; margin-top: 3px; }}

    .cell {{ text-align: center; padding: 16px 8px; }}
    input[type="checkbox"] {{
      width: 18px; height: 18px;
      cursor: pointer;
      accent-color: #0f3460;
    }}

    .save-btn {{
      background: #0f3460;
      color: white;
      border: none;
      padding: 10px 24px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
    }}
    .save-btn:hover {{ background: #1a4a7a; }}
    .save-btn:disabled {{ background: #8892a4; cursor: not-allowed; }}

    .toast {{
      position: fixed; bottom: 32px; right: 32px;
      background: #1a1a2e; color: white;
      padding: 12px 20px; border-radius: 8px;
      font-size: 14px; opacity: 0;
      transition: opacity 0.3s;
      pointer-events: none;
    }}
    .toast.show {{ opacity: 1; }}
    .toast.error {{ background: #c0392b; }}
  </style>
</head>
<body>

<div class="header">
  <div>
    <h1>ASG — Configuración de Productos</h1>
    <span>Definí qué criterios aplican a cada modelo de producto</span>
  </div>
</div>

<div class="container">
  <div class="card">
    <div class="card-header">
      <div>
        <h2>Modelos Gucci</h2>
        <p>Activá los criterios que correspondan para cada modelo. Los pesos se redistribuyen automáticamente.</p>
      </div>
      <button class="save-btn" onclick="save()">Guardar cambios</button>
    </div>

    <form id="config-form">
      <table>
        <thead>
          <tr>
            <th class="product-col">Modelo</th>
            {header_cells}
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </form>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
  function showToast(msg, isError) {{
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.className = 'toast show' + (isError ? ' error' : '');
    setTimeout(() => t.className = 'toast', 2500);
  }}

  async function save() {{
    const btn = document.querySelector('.save-btn');
    btn.disabled = true;
    btn.textContent = 'Guardando...';

    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    const products = {{}};

    checkboxes.forEach(cb => {{
      const [productId, criterionKey] = cb.name.split(':');
      if (!products[productId]) products[productId] = [];
      if (cb.checked) products[productId].push(criterionKey);
    }});

    try {{
      const res = await fetch('/admin/save', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify(products)
      }});
      if (res.ok) {{
        showToast('✓ Cambios guardados');
      }} else {{
        showToast('Error al guardar', true);
      }}
    }} catch(e) {{
      showToast('Error de conexión', true);
    }}

    btn.disabled = false;
    btn.textContent = 'Guardar cambios';
  }}
</script>

</body>
</html>"""
    return html


@router.post("/admin/save")
async def save_config(request: Request):
    updates = await request.json()
    products = _load_products()

    for product_id, criteria_list in updates.items():
        if product_id in products:
            products[product_id]["criteria"] = criteria_list

    _save_products(products)
    return {"status": "ok"}
