"""
Criterios de autenticación para productos Gucci.
Cada criterio define:
  - key:        identificador interno
  - label:      nombre legible
  - weight:     peso en el score final (deben sumar 1.0)
  - filename:   nombre base esperado del archivo de foto (sin extensión)
  - prompt:     instrucciones específicas para el modelo de visión
"""

GUCCI_CRITERIA = [
    {
        "key": "gg_canvas",
        "label": "Patrón GG Canvas",
        "weight": 0.20,
        "filename": "01_gg_canvas",
        "prompt": (
            "Eres un experto en autenticación de productos Gucci. "
            "Analiza el patrón GG Canvas de la imagen. Evalúa:\n"
            "1. Simetría y alineación del motivo GG (letras entrelazadas).\n"
            "2. Nitidez y uniformidad del patrón en toda la superficie.\n"
            "3. Tonalidad y contraste correctos (beis/marrón para GG Supreme, "
            "beige/dorado para GG Plus, negro brillante para GG Black).\n"
            "4. Ausencia de distorsiones, manchas o irregularidades.\n\n"
            "Responde SOLAMENTE con un JSON con este formato exacto:\n"
            '{\"score\": <número 0-100>, \"observaciones\": \"<texto breve>\"}\n'
            "Donde score=100 es completamente auténtico y score=0 es claramente falso."
        ),
    },
    {
        "key": "herrajes",
        "label": "Herrajes / Hardware",
        "weight": 0.15,
        "filename": "02_herrajes",
        "prompt": (
            "Eres un experto en autenticación de productos Gucci. "
            "Analiza los herrajes (cierres, argollas, hebillas) en la imagen. Evalúa:\n"
            "1. Calidad y uniformidad del acabado metálico (dorado, plateado o envejecido).\n"
            "2. Presencia y nitidez del grabado 'Gucci' en el herraje.\n"
            "3. Peso visual (los herrajes originales se ven sólidos, no huecos).\n"
            "4. Ausencia de descascaramientos, irregularidades o acabados baratos.\n\n"
            "Responde SOLAMENTE con un JSON con este formato exacto:\n"
            '{\"score\": <número 0-100>, \"observaciones\": \"<texto breve>\"}\n'
            "Donde score=100 es completamente auténtico y score=0 es claramente falso."
        ),
    },
    {
        "key": "etiqueta",
        "label": "Etiqueta Interior y Número Serial",
        "weight": 0.20,
        "filename": "03_etiqueta",
        "prompt": (
            "Eres un experto en autenticación de productos Gucci. "
            "Analiza la etiqueta interior y el número serial en la imagen. Evalúa:\n"
            "1. Tipografía: la fuente debe ser consistente, sin letras irregulares.\n"
            "2. El texto 'Gucci' debe estar en mayúsculas con espaciado correcto.\n"
            "3. El número de serie (generalmente 6 dígitos) debe estar debajo del logo.\n"
            "4. La etiqueta debe ser de cuero o material de calidad, bien cosida.\n"
            "5. 'Made in Italy' debe aparecer con la tipografía correcta.\n\n"
            "Responde SOLAMENTE con un JSON con este formato exacto:\n"
            '{\"score\": <número 0-100>, \"observaciones\": \"<texto breve>\"}\n'
            "Donde score=100 es completamente auténtico y score=0 es claramente falso."
        ),
    },
    {
        "key": "costuras",
        "label": "Costuras",
        "weight": 0.15,
        "filename": "04_costuras",
        "prompt": (
            "Eres un experto en autenticación de productos Gucci. "
            "Analiza las costuras del producto en la imagen. Evalúa:\n"
            "1. Regularidad: todas las puntadas deben tener el mismo tamaño y espacio.\n"
            "2. Tensión uniforme sin hilos sueltos, rizados o fruncidos.\n"
            "3. Color del hilo consistente con el material (generalmente tono similar).\n"
            "4. Las esquinas y curvas deben estar perfectamente acabadas.\n\n"
            "Responde SOLAMENTE con un JSON con este formato exacto:\n"
            '{\"score\": <número 0-100>, \"observaciones\": \"<texto breve>\"}\n'
            "Donde score=100 es completamente auténtico y score=0 es claramente falso."
        ),
    },
    {
        "key": "interior",
        "label": "Interior / Forro",
        "weight": 0.15,
        "filename": "05_interior",
        "prompt": (
            "Eres un experto en autenticación de productos Gucci. "
            "Analiza el interior y forro del producto en la imagen. Evalúa:\n"
            "1. Calidad del material del forro (generalmente microfibra suede o tela GG).\n"
            "2. Uniformidad del color y acabado interno.\n"
            "3. Bolsillos internos bien construidos y cosidos.\n"
            "4. Ausencia de adhesivos visibles, costuras irregulares o materiales baratos.\n\n"
            "Responde SOLAMENTE con un JSON con este formato exacto:\n"
            '{\"score\": <número 0-100>, \"observaciones\": \"<texto breve>\"}\n'
            "Donde score=100 es completamente auténtico y score=0 es claramente falso."
        ),
    },
    {
        "key": "cierre",
        "label": "Sistema de Cierre / Solapa",
        "weight": 0.10,
        "filename": "06_cierre",
        "prompt": (
            "Eres un experto en autenticación de productos Gucci. "
            "Analiza el sistema de cierre principal (solapa, cremallera, hebilla) en la imagen. Evalúa:\n"
            "1. Construcción y acabado del mecanismo de cierre.\n"
            "2. Alineación correcta de la solapa o cierre con el cuerpo del producto.\n"
            "3. Calidad del material en las zonas de mayor fricción.\n"
            "4. Funcionalidad aparente y precisión en el encaje.\n\n"
            "Responde SOLAMENTE con un JSON con este formato exacto:\n"
            '{\"score\": <número 0-100>, \"observaciones\": \"<texto breve>\"}\n'
            "Donde score=100 es completamente auténtico y score=0 es claramente falso."
        ),
    },
    {
        "key": "challenge",
        "label": "Challenge Anti-Fraude",
        "weight": 0.05,
        "filename": "07_challenge",
        "prompt": (
            "Analiza la imagen de verificación de posesión. "
            "Esta foto debe mostrar el producto junto a un código de sesión escrito o impreso en un papel. "
            "Evalúa:\n"
            "1. ¿Aparece un código/número claramente visible en la imagen junto al producto?\n"
            "2. ¿El producto y el código aparecen en la misma fotografía sin edición aparente?\n"
            "3. ¿La iluminación y perspectiva son consistentes (no composición de dos fotos)?\n\n"
            "Responde SOLAMENTE con un JSON con este formato exacto:\n"
            '{\"score\": <número 0-100>, \"observaciones\": \"<texto breve>\"}\n'
            "Donde score=100 significa posesión verificada y score=0 es foto claramente manipulada."
        ),
    },
]
