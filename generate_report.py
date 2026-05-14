from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import date

OUTPUT = "/Users/damian/Documents/Claude/Projects/Score de Calidad/ASG/ASG_Analisis_Costos.pdf"

# ── Paleta de colores ──────────────────────────────────────────────────────────
DARK    = colors.HexColor("#1a1a2e")
ACCENT  = colors.HexColor("#0f3460")
BLUE    = colors.HexColor("#16213e")
LIGHT   = colors.HexColor("#e8f4f8")
GREEN   = colors.HexColor("#2ecc71")
ORANGE  = colors.HexColor("#e67e22")
RED     = colors.HexColor("#e74c3c")
GRAY    = colors.HexColor("#7f8c8d")
LGRAY   = colors.HexColor("#ecf0f1")
WHITE   = colors.white
TBLHEAD = colors.HexColor("#0f3460")

# ── Estilos ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def style(name, **kwargs):
    return ParagraphStyle(name, **kwargs)

S_TITLE = style("Title",
    fontSize=28, fontName="Helvetica-Bold",
    textColor=WHITE, alignment=TA_LEFT, leading=34)

S_SUBTITLE = style("Subtitle",
    fontSize=14, fontName="Helvetica",
    textColor=colors.HexColor("#a8d8ea"), alignment=TA_LEFT, leading=20)

S_DATE = style("Date",
    fontSize=10, fontName="Helvetica",
    textColor=colors.HexColor("#a8d8ea"), alignment=TA_LEFT)

S_SECTION = style("Section",
    fontSize=14, fontName="Helvetica-Bold",
    textColor=ACCENT, spaceBefore=18, spaceAfter=6, leading=18)

S_SUBSECTION = style("Subsection",
    fontSize=11, fontName="Helvetica-Bold",
    textColor=DARK, spaceBefore=10, spaceAfter=4)

S_BODY = style("Body",
    fontSize=9.5, fontName="Helvetica",
    textColor=colors.HexColor("#2c3e50"), leading=15, spaceAfter=4)

S_SMALL = style("Small",
    fontSize=8.5, fontName="Helvetica",
    textColor=GRAY, leading=13)

S_BOLD = style("Bold",
    fontSize=9.5, fontName="Helvetica-Bold",
    textColor=DARK, leading=15)

S_NOTE = style("Note",
    fontSize=8.5, fontName="Helvetica-Oblique",
    textColor=GRAY, leading=13, leftIndent=10)

S_HIGHLIGHT = style("Highlight",
    fontSize=10, fontName="Helvetica-Bold",
    textColor=ACCENT, leading=15)

S_CENTER = style("Center",
    fontSize=9.5, fontName="Helvetica",
    textColor=colors.HexColor("#2c3e50"), leading=15, alignment=TA_CENTER)

# ── Helpers ────────────────────────────────────────────────────────────────────
def hr(color=LGRAY, thickness=0.5):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=8, spaceBefore=4)

def sp(h=6):
    return Spacer(1, h)

def section(title):
    return [sp(4), Paragraph(title, S_SECTION), hr(ACCENT, 1.5)]

def tbl(data, col_widths, style_cmds):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    base = [
        ("BACKGROUND",  (0, 0), (-1, 0),  TBLHEAD),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0),  9),
        ("FONTNAME",    (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LGRAY]),
        ("GRID",        (0, 0), (-1, -1), 0.3, colors.HexColor("#bdc3c7")),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    t.setStyle(TableStyle(base + style_cmds))
    return t

# ── Documento ──────────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="ASG — Análisis de Costos de Infraestructura",
        author="Authenticity Score Generator",
    )

    W = A4[0] - 4*cm   # ancho útil
    story = []

    # ── HEADER BANNER ──────────────────────────────────────────────────────────
    header_data = [[
        Paragraph("ASG", style("H", fontSize=36, fontName="Helvetica-Bold",
                               textColor=WHITE, alignment=TA_LEFT)),
        Paragraph(
            "Authenticity Score Generator<br/>"
            "<font size='11' color='#a8d8ea'>Análisis de Costos de Infraestructura</font><br/>"
            f"<font size='9' color='#7fb3c8'>{date.today().strftime('%d de %B de %Y')}</font>",
            style("Hb", fontSize=18, fontName="Helvetica-Bold",
                  textColor=WHITE, alignment=TA_LEFT, leading=26)),
        Paragraph(
            "<font size='9' color='#a8d8ea'>Documento preparado para<br/>"
            "análisis de caso de negocio</font>",
            style("Hr", fontSize=9, fontName="Helvetica",
                  textColor=WHITE, alignment=TA_RIGHT, leading=14)),
    ]]
    h = Table(header_data, colWidths=[2.5*cm, 10*cm, None])
    h.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DARK),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story += [h, sp(20)]

    # ── RESUMEN EJECUTIVO ──────────────────────────────────────────────────────
    story += section("1. Resumen Ejecutivo")
    story.append(Paragraph(
        "Este documento proyecta los costos variables de infraestructura cloud para la solución "
        "ASG, con foco en el componente de inteligencia artificial que representa el ítem de mayor "
        "peso. El análisis compara distintos modelos de visión disponibles y proyecta el costo "
        "mensual en función del volumen de sesiones de scoring generadas.",
        S_BODY))
    story.append(sp(8))

    # KPI boxes
    kpis = [
        ["~$0.008", "Costo variable\npor sesión (recomendado)"],
        ["8 llamadas", "al modelo de visión\npor sesión"],
        ["~$80", "Costo AI a\n10.000 sesiones/mes"],
        [">95%", "Margen infraestructura\nvs. precio sugerido $1+"],
    ]
    kpi_tbl = Table(
        [[[Paragraph(v, style(f"V{i}", fontSize=18, fontName="Helvetica-Bold",
                              textColor=ACCENT, alignment=TA_CENTER, leading=22)),
           Paragraph(l.replace("\n", "<br/>"),
                     style(f"L{i}", fontSize=8, fontName="Helvetica",
                           textColor=GRAY, alignment=TA_CENTER, leading=12))]
          for i, (v, l) in enumerate(kpis)]],
        colWidths=[W/4]*4
    )
    kpi_tbl.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
    ]))
    story += [kpi_tbl, sp(16)]

    # ── ARQUITECTURA ───────────────────────────────────────────────────────────
    story += section("2. Arquitectura Propuesta")
    story.append(Paragraph(
        "La solución se apoya en servicios serverless de AWS, lo que elimina costos fijos de "
        "infraestructura. Solo se paga por uso efectivo.", S_BODY))
    story.append(sp(6))

    arch = [
        ["Servicio", "Rol en la arquitectura", "Modelo de costo"],
        ["API Gateway", "Punto de entrada para todos los endpoints", "Por request"],
        ["Lambda", "Endpoints sync: create_session, get_upload_url,\nconfirm_upload, scoring_status", "Por ejecución + duración"],
        ["SQS", "Buffer entre /generate_scoring/ y Step Functions", "Por mensaje"],
        ["Step Functions", "Orquestación del flujo de scoring async\n(Map State para procesar N imágenes en paralelo)", "Por transición de estado"],
        ["Bedrock / Gemini", "Modelos de visión para scoring por imagen\ny análisis de coherencia global", "Por token (input/output)"],
        ["S3", "Almacenamiento de imágenes originales", "Por GB almacenado + requests"],
        ["DynamoDB", "Estado de sesiones, imágenes y resultados", "Por lectura/escritura"],
    ]
    story.append(tbl(arch,
        [3.5*cm, 7.5*cm, 4*cm],
        [("ALIGN", (0, 0), (0, -1), "LEFT"),
         ("ALIGN", (1, 0), (1, -1), "LEFT"),
         ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
         ("TEXTCOLOR", (0, 1), (0, -1), ACCENT)]))
    story.append(sp(16))

    # ── MODELO DE CONSUMO DE TOKENS ────────────────────────────────────────────
    story += section("3. Modelo de Consumo por Sesión de Scoring")
    story.append(Paragraph(
        "Cada sesión de scoring implica analizar hasta 7 fotos de distintas partes del producto, "
        "más un análisis final de coherencia global. El código actual redimensiona las imágenes "
        "a 800px antes de enviarlas al modelo, lo cual es una optimización de costo importante "
        "que se mantiene en la arquitectura propuesta.", S_BODY))
    story.append(sp(8))

    story.append(Paragraph("Calls al modelo por sesión:", S_SUBSECTION))
    calls = [
        ["Tipo de análisis", "Cant.", "Input tokens", "Output tokens", "Notas"],
        ["Análisis por imagen\n(criterios individuales)", "7", "~1.000\n(800 img + 200 prompt)", "~150\n(JSON score)", "Claude Haiku\nrecomendado"],
        ["Análisis de coherencia global", "1", "~500\n(texto con resultados)", "~300\n(evaluación global)", "Claude Sonnet\nrecomendado"],
        ["TOTAL POR SESIÓN", "8", "~7.500 tokens", "~1.350 tokens", ""],
    ]
    story.append(tbl(calls,
        [4.5*cm, 1.5*cm, 3*cm, 3*cm, 3*cm],
        [("ALIGN", (0, 0), (0, -1), "LEFT"),
         ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
         ("BACKGROUND", (0, -1), (-1, -1), LIGHT),
         ("TEXTCOLOR", (0, -1), (-1, -1), ACCENT)]))
    story.append(sp(6))
    story.append(Paragraph(
        "* El análisis de coherencia global recibe solo los resultados en texto (scores + "
        "observaciones de cada imagen), no las imágenes originales. Esto reduce el costo de "
        "ese paso en ~90% respecto a reenviar todas las fotos.",
        S_NOTE))
    story.append(sp(16))

    # ── COMPARATIVA DE MODELOS ─────────────────────────────────────────────────
    story += section("4. Comparativa de Modelos de IA")
    story.append(Paragraph(
        "La elección del modelo de visión es la palanca de costo más importante de toda la "
        "arquitectura. La tabla compara las opciones más relevantes:", S_BODY))
    story.append(sp(8))

    models = [
        ["Modelo", "Input\n$/M tokens", "Output\n$/M tokens", "Costo\npor sesión", "Calidad\nvision", "Latencia"],
        ["Gemini 2.0 Flash", "$0.10", "$0.40", "~$0.001", "Alta", "Baja"],
        ["Claude Haiku 3.5\n(Bedrock)", "$0.80", "$4.00", "~$0.005", "Muy alta", "Baja"],
        ["Gemini 1.5 Pro", "$1.25", "$5.00", "~$0.012", "Muy alta", "Media"],
        ["Claude Sonnet 3.5\n(Bedrock)", "$3.00", "$15.00", "~$0.025", "Excelente", "Media"],
    ]
    story.append(tbl(models,
        [3.8*cm, 2.2*cm, 2.2*cm, 2.5*cm, 2.5*cm, 1.8*cm],
        [("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#eafaf1")),
         ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
         ("TEXTCOLOR", (3, 1), (3, -1), colors.HexColor("#27ae60"))]))
    story.append(sp(8))

    # Estrategia recomendada
    rec_data = [[
        Paragraph("Estrategia Recomendada", style("RT", fontSize=10,
                  fontName="Helvetica-Bold", textColor=WHITE)),
        Paragraph(
            "Usar <b>Claude Haiku</b> para los 7 análisis por imagen (velocidad + costo) y "
            "<b>Claude Sonnet</b> para el análisis de coherencia global (1 sola llamada, "
            "mayor razonamiento). Esto da el mejor balance calidad/costo: <b>~$0.008 por sesión</b>.",
            style("RB", fontSize=9, fontName="Helvetica", textColor=WHITE, leading=14)),
    ]]
    rec_tbl = Table(rec_data, colWidths=[4*cm, 11*cm])
    rec_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story += [rec_tbl, sp(16)]

    # ── PROYECCIÓN MENSUAL ─────────────────────────────────────────────────────
    story += section("5. Proyección de Costos Mensuales")
    story.append(Paragraph(
        "La siguiente tabla proyecta el costo total de infraestructura por nivel de volumen "
        "mensual de sesiones de scoring procesadas:", S_BODY))
    story.append(sp(8))

    proj = [
        ["Sesiones/mes", "AI (Haiku+Sonnet)", "Step Functions", "Lambda+DynDB+S3", "Total Infraestr.", "Costo/sesión"],
        ["1.000",    "$8",    "$1",   "$2",    "$11",    "$0.011"],
        ["5.000",    "$40",   "$3",   "$8",    "$51",    "$0.010"],
        ["10.000",   "$80",   "$6",   "$15",   "$101",   "$0.010"],
        ["25.000",   "$200",  "$16",  "$35",   "$251",   "$0.010"],
        ["50.000",   "$400",  "$31",  "$65",   "$496",   "$0.010"],
        ["100.000",  "$800",  "$63",  "$125",  "$988",   "$0.010"],
    ]
    story.append(tbl(proj,
        [3*cm, 3*cm, 3*cm, 3*cm, 2.8*cm, 2.2*cm],
        [("TEXTCOLOR", (4, 1), (4, -1), ACCENT),
         ("FONTNAME",  (4, 1), (4, -1), "Helvetica-Bold"),
         ("ALIGN",     (1, 0), (-1, -1), "RIGHT"),
         ("ALIGN",     (0, 0), (0, -1), "CENTER")]))
    story.append(sp(6))
    story.append(Paragraph(
        "* El costo por sesión se mantiene estable (~$0.010) gracias al modelo de precios "
        "pay-per-use de todos los servicios involucrados. No hay costos fijos de infraestructura.",
        S_NOTE))
    story.append(sp(16))

    # ── ANÁLISIS DE MARGEN ─────────────────────────────────────────────────────
    story += section("6. Análisis de Margen sobre Precio de Venta")
    story.append(Paragraph(
        "Considerando distintos escenarios de precio de venta por sesión de scoring a "
        "plataformas B2B clientes:", S_BODY))
    story.append(sp(8))

    margin = [
        ["Precio de venta\npor sesión", "Costo infraestr.\npor sesión", "Margen bruto\npor sesión", "Margen %", "Break-even\n(sesiones/mes)"],
        ["$0.25",  "$0.010", "$0.240", "96%", "—"],
        ["$0.50",  "$0.010", "$0.490", "98%", "—"],
        ["$1.00",  "$0.010", "$0.990", "99%", "—"],
        ["$2.00",  "$0.010", "$1.990", "99.5%", "—"],
    ]
    story.append(tbl(margin,
        [3.2*cm, 3.2*cm, 3.2*cm, 2.5*cm, 3*cm],
        [("TEXTCOLOR", (3, 1), (3, -1), colors.HexColor("#27ae60")),
         ("FONTNAME",  (3, 1), (3, -1), "Helvetica-Bold"),
         ("ALIGN",     (1, 0), (-1, -1), "CENTER")]))
    story.append(sp(6))
    story.append(Paragraph(
        "El costo de infraestructura representa menos del 2% del precio de venta en cualquier "
        "escenario razonable. El margen bruto del negocio estará determinado principalmente por "
        "costos de desarrollo, go-to-market y soporte, no por infraestructura.",
        S_BODY))
    story.append(sp(16))

    # ── RIESGOS Y MITIGACIONES ─────────────────────────────────────────────────
    story += section("7. Riesgos de Costo y Mitigaciones")
    story.append(sp(4))

    risks = [
        ["Riesgo", "Impacto", "Mitigación"],
        ["Imágenes en alta resolución\nsin redimensionar",
         "Costo de tokens\n3x-10x más alto",
         "Resize a 800px antes de enviar\nal modelo (ya implementado en el prototipo)"],
        ["Spike inesperado de volumen",
         "Factura mensual elevada",
         "Throttling por consumer_platform_id\nen API Gateway + alertas en CloudWatch"],
        ["Dependencia de proveedor único\n(solo Gemini o solo Bedrock)",
         "Riesgo de disponibilidad\ny cambios de precio",
         "Abstraer el modelo detrás de una interfaz\n(el analyzer.py actual ya tiene este patrón)"],
        ["Sesiones de scoring incompletas\n(usuario no llama /generate_scoring/)",
         "Imágenes huérfanas\nacumulando costo en S3",
         "TTL en DynamoDB + lifecycle policy en S3\npara eliminar imágenes sin scoring tras 7 días"],
    ]
    story.append(tbl(risks,
        [4*cm, 3.5*cm, 7.5*cm],
        [("ALIGN",   (0, 0), (-1, -1), "LEFT"),
         ("VALIGN",  (0, 0), (-1, -1), "TOP"),
         ("TEXTCOLOR", (1, 1), (1, -1), ORANGE),
         ("FONTNAME",  (1, 1), (1, -1), "Helvetica-Bold")]))
    story.append(sp(16))

    # ── CONCLUSIÓN ─────────────────────────────────────────────────────────────
    story += section("8. Conclusión")
    story.append(Paragraph(
        "El modelo de costos de infraestructura de ASG es altamente favorable para un negocio "
        "B2B. Los puntos clave a retener para el caso de negocio son:", S_BODY))
    story.append(sp(6))

    conclusions = [
        ["01", "Costo variable de ~$0.010 por sesión de scoring, independiente del volumen."],
        ["02", "Sin costos fijos de infraestructura: arquitectura 100% serverless (AWS Lambda, "
               "Step Functions, S3, DynamoDB)."],
        ["03", "El componente de mayor costo es el modelo de IA (~80% del total), con opciones "
               "de optimización claras según calidad requerida."],
        ["04", "Margen bruto sobre infraestructura superior al 96% en cualquier escenario de "
               "precio de venta razonable."],
        ["05", "La arquitectura escala desde 1.000 a 100.000+ sesiones/mes sin cambios "
               "estructurales ni inversión adicional."],
    ]
    for num, text in conclusions:
        row = Table([[
            Paragraph(num, style(f"N{num}", fontSize=11, fontName="Helvetica-Bold",
                                 textColor=WHITE, alignment=TA_CENTER)),
            Paragraph(text, style(f"T{num}", fontSize=9.5, fontName="Helvetica",
                                  textColor=DARK, leading=14))
        ]], colWidths=[1.2*cm, W-1.2*cm])
        row.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (0, 0), ACCENT),
            ("BACKGROUND",    (1, 0), (1, 0), LIGHT),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (1, 0), (1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ]))
        story += [row, sp(3)]

    story.append(sp(20))

    # ── FOOTER ─────────────────────────────────────────────────────────────────
    story.append(hr(LGRAY))
    footer_data = [[
        Paragraph("ASG — Authenticity Score Generator", S_SMALL),
        Paragraph(f"Documento generado el {date.today().strftime('%d/%m/%Y')} · Confidencial",
                  style("FR", fontSize=8.5, fontName="Helvetica", textColor=GRAY,
                        alignment=TA_RIGHT)),
    ]]
    footer = Table(footer_data, colWidths=[W/2, W/2])
    footer.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE")]))
    story.append(footer)

    doc.build(story)
    print(f"PDF generado: {OUTPUT}")

build()
