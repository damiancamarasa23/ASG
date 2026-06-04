"""
Criterios de autenticación para productos Gucci.
Cada criterio define:
  - key:        identificador interno
  - label:      nombre legible
  - weight:     peso en el score final (deben sumar 1.0)
  - filename:   nombre base esperado del archivo de foto (sin extensión)
  - prompt:     instrucciones específicas para el modelo de visión
"""

# Prefijo común a todos los prompts: valida que el objeto sea un producto Gucci
# antes de evaluar el criterio específico.
_PRODUCT_GUARD = (
    "Eres un experto en autenticación de productos Gucci (bolsos, carteras, "
    "billeteras y accesorios de cuero de alta costura).\n\n"
    "PASO 1 — VERIFICACIÓN DEL OBJETO: Antes de evaluar, confirmá que la imagen "
    "muestra un bolso, cartera, billetera u accesorio de cuero de la marca Gucci. "
    "Si la imagen muestra cualquier otro tipo de objeto (documento, pasaporte, "
    "ropa, calzado, accesorio de otra marca, persona, paisaje, etc.), respondé "
    "INMEDIATAMENTE con:\n"
    '{"score": 0, "observaciones": "La imagen no muestra un producto Gucci válido para este criterio. '
    'Se esperaba [TIPO DE FOTO]. Se encontró: [DESCRIPCIÓN BREVE DE LO QUE SE VE]."}\n\n'
    "PASO 2 — EVALUACIÓN (solo si el objeto es correcto): "
)

_JSON_FOOTER = (
    "\n\nResponde SOLAMENTE con un JSON con este formato exacto:\n"
    '{"score": <número 0-100>, "observaciones": "<texto breve>"}\n'
    "Donde score=100 es completamente auténtico y score=0 es claramente falso. "
    "No agregues ningún texto fuera del JSON."
)

GUCCI_CRITERIA = [
    {
        "key": "gg_canvas",
        "label": "Patrón GG Canvas",
        "weight": 0.20,
        "filename": "01_gg_canvas",
        "prompt": (
            _PRODUCT_GUARD
            + "Se esperaba una foto del frente o exterior de un bolso/cartera Gucci "
            "mostrando claramente el patrón GG Canvas. Evaluá:\n"
            "1. Simetría y alineación del motivo GG (letras entrelazadas).\n"
            "2. Nitidez y uniformidad del patrón en toda la superficie visible.\n"
            "3. Tonalidad y contraste correctos (beis/marrón para GG Supreme, "
            "beige/dorado para GG Plus, negro brillante para GG Black).\n"
            "4. Ausencia de distorsiones, manchas o irregularidades en el tejido."
            + _JSON_FOOTER
        ),
    },
    {
        "key": "herrajes",
        "label": "Herrajes / Hardware",
        "weight": 0.15,
        "filename": "02_herrajes",
        "prompt": (
            _PRODUCT_GUARD
            + "Se esperaba un close-up de los herrajes (cierres, argollas o hebillas) "
            "de un bolso o accesorio Gucci. Evaluá:\n"
            "1. Calidad y uniformidad del acabado metálico (dorado, plateado o envejecido).\n"
            "2. Presencia y nitidez del grabado 'Gucci' en el herraje.\n"
            "3. Peso visual: los herrajes originales se ven sólidos, no huecos ni frágiles.\n"
            "4. Ausencia de descascaramientos, burbujas o acabados irregulares."
            + _JSON_FOOTER
        ),
    },
    {
        "key": "etiqueta",
        "label": "Etiqueta Interior y Número Serial",
        "weight": 0.20,
        "filename": "03_etiqueta",
        "prompt": (
            _PRODUCT_GUARD
            + "Se esperaba una foto del interior de un bolso Gucci mostrando la etiqueta "
            "de cuero con el nombre de la marca y el número serial. Evaluá:\n"
            "1. Tipografía: fuente consistente, sin letras irregulares o pixeladas.\n"
            "2. El texto 'Gucci' en mayúsculas con espaciado y kerning correcto.\n"
            "3. Número de serie (generalmente 6 dígitos) debajo del logo de la marca.\n"
            "4. La etiqueta debe ser de cuero o material de calidad, cosida solo por el borde superior.\n"
            "5. 'Made in Italy' en tipografía correcta, generalmente en minúsculas."
            + _JSON_FOOTER
        ),
    },
    {
        "key": "costuras",
        "label": "Costuras",
        "weight": 0.15,
        "filename": "04_costuras",
        "prompt": (
            _PRODUCT_GUARD
            + "Se esperaba una foto del detalle de costuras laterales o de borde "
            "de un bolso o cartera Gucci. Evaluá:\n"
            "1. Regularidad: todas las puntadas con el mismo tamaño y espaciado.\n"
            "2. Tensión uniforme, sin hilos sueltos, rizados o que sobresalgan.\n"
            "3. Color del hilo consistente y apropiado para el material.\n"
            "4. Esquinas y curvas perfectamente acabadas, sin exceso de hilo."
            + _JSON_FOOTER
        ),
    },
    {
        "key": "interior",
        "label": "Interior / Forro",
        "weight": 0.15,
        "filename": "05_interior",
        "prompt": (
            _PRODUCT_GUARD
            + "Se esperaba una foto del interior abierto de un bolso o cartera Gucci, "
            "mostrando el forro interno. Evaluá:\n"
            "1. Material del forro: generalmente microfibra suede, tela GG o cuero suave.\n"
            "2. Color y acabado uniformes, sin manchas ni variaciones.\n"
            "3. Bolsillos internos bien construidos, con costuras prolijas.\n"
            "4. Ausencia de adhesivos visibles, pestañas de tela suelta o materiales sintéticos baratos."
            + _JSON_FOOTER
        ),
    },
    {
        "key": "cierre",
        "label": "Sistema de Cierre / Solapa",
        "weight": 0.10,
        "filename": "06_cierre",
        "prompt": (
            _PRODUCT_GUARD
            + "Se esperaba una foto del sistema de cierre principal de un bolso Gucci: "
            "solapa, cremallera central o hebilla de cierre. Evaluá:\n"
            "1. Construcción y acabado del mecanismo de cierre.\n"
            "2. Alineación correcta de la solapa o cierre con el cuerpo del producto.\n"
            "3. Calidad del material en las zonas de mayor fricción y uso.\n"
            "4. Precisión en el encaje: sin holgura excesiva ni desalineación."
            + _JSON_FOOTER
        ),
    },
    {
        "key": "challenge",
        "label": "Challenge Anti-Fraude",
        "weight": 0.05,
        "filename": "07_challenge",
        "prompt": (
            "Eres un sistema de verificación de posesión para autenticación de productos Gucci.\n\n"
            "PASO 1 — VERIFICACIÓN: La imagen debe mostrar simultáneamente: "
            "(a) un bolso, cartera u accesorio Gucci, Y "
            "(b) un papel o pantalla con un código alfanumérico de sesión visible. "
            "Si falta cualquiera de los dos elementos, o si el objeto no es un producto Gucci, respondé:\n"
            '{"score": 0, "observaciones": "Challenge inválido: [explicar qué falta o qué objeto se ve]."}\n\n'
            "PASO 2 — EVALUACIÓN (solo si ambos elementos están presentes):\n"
            "1. ¿El código de sesión es claramente legible en la imagen?\n"
            "2. ¿El producto Gucci y el código aparecen en la misma toma sin edición aparente?\n"
            "3. ¿La iluminación y perspectiva son consistentes (no es composición de dos fotos)?\n"
            + _JSON_FOOTER
        ),
    },
]
