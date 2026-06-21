"""
Generador de Contenido SEO/AEO — adidas LAM
Demo para Business Case — Rol SEO interno
"""

import os
import json
import requests
import streamlit as st
import anthropic
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="adidas LAM — Generador SEO/AEO",
    page_icon="⚡",
    layout="wide",
)

# ═══════════════════════════════════════════════════════════
# API KEYS — desde Streamlit Secrets (nunca hardcodeadas)
# ═══════════════════════════════════════════════════════════
try:
    ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]
    SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
except (KeyError, FileNotFoundError):
    st.error(
        "⚠️ Faltan las API keys. Configúralas en Settings → Secrets "
        "de Streamlit Cloud. Ver instrucciones al final de este archivo."
    )
    st.stop()

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def call_claude(system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
    """Una llamada a Claude."""
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


def parse_json_safe(text: str):
    """Limpia el texto si Claude lo envuelve en ```json ... ```."""
    clean = text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


# ═══════════════════════════════════════════════════════════
# DICCIONARIOS DE CONFIGURACIÓN (idénticos al notebook)
# ═══════════════════════════════════════════════════════════
MERCADOS = {
    "Colombia": (
        "Mercado: Colombia. Escribe en español. Vocabulario local: "
        "'tenis' (no 'zapatillas'), 'guayos' para calzado de fútbol, "
        "'camisetas', 'chaquetas', 'sudaderas', 'medias'. Tuteo."
    ),
    "Mexico": (
        "Mercado: México. Escribe en español. Vocabulario local: "
        "'tenis' (no 'zapatillas'), 'tacos de fútbol' para calzado de fútbol, "
        "'playeras' (no 'camisetas'), 'chamarras' (no 'chaquetas'), "
        "'pants', 'calcetines'. Tuteo."
    ),
    "Argentina": (
        "Mercado: Argentina. Escribe en español rioplatense. Vocabulario local: "
        "'zapatillas' (no 'tenis'), 'botines' para calzado de fútbol, "
        "'remeras' (no 'camisetas'), 'camperas' (no 'chaquetas'), 'buzos'. "
        "Voseo natural (vos tenés, elegí, sumate)."
    ),
    "Brasil": (
        "Mercado: Brasil. Escribe TODO el contenido en portugués brasileño. "
        "Vocabulario: 'tênis', 'chuteiras' para calzado de fútbol, "
        "'camisetas', 'jaquetas', 'moletons', 'meias'."
    ),
    "Chile": (
        "Mercado: Chile. Escribe en español. Vocabulario local: "
        "'zapatillas' (no 'tenis'), 'zapatos de fútbol' para calzado de fútbol, "
        "'poleras' (no 'camisetas'), 'polerones' para hoodies, 'chaquetas'. Tuteo."
    ),
    "Peru": (
        "Mercado: Perú. Escribe en español. Vocabulario local: "
        "'zapatillas' (no 'tenis'), 'chimpunes' para calzado de fútbol, "
        "'polos' (no 'camisetas'), 'casacas' (no 'chaquetas'), 'medias'. Tuteo."
    ),
}

SITIOS_WEB = {
    "Colombia": "adidas.co",
    "Mexico": "adidas.mx",
    "Argentina": "adidas.com.ar",
    "Brasil": "adidas.com.br",
    "Chile": "adidas.cl",
    "Peru": "adidas.pe",
}

GUIAS_CONTENIDO = {
    "ORIGINALS": (
        "Segmento: adidas Originals (incluye Skateboarding, Y-3, "
        "L.A. Partnerships, R.O.W. Partnerships). "
        "Enfócate en historia, herencia cultural, autoexpresión y estilo urbano. "
        "Tono: cultura, identidad, streetwear, lifestyle. "
        "NO incluyas secciones de autenticidad, cómo detectar falsos ni dónde "
        "comprar originales. El lector ya está en adidas — ya está en el lugar "
        "correcto. El blog habla de historia, cultura y estilo, no de falsificaciones. "
        "Para Y-3 y colabs premium, énfasis en exclusividad y diseño de vanguardia."
    ),
    "RUNNING": (
        "Segmento: Running (calzado, ropa y accesorios de running). "
        "Enfócate en rendimiento, técnica, beneficios funcionales y ocasión de uso. "
        "Tono: coaching empático, empowerment, técnico pero accesible. "
        "NO incluyas autenticidad ni 'dónde comprar originales'. "
        "Menciona tecnologías propias como Boost o Lightstrike cuando aplique."
    ),
    "TRAINING": (
        "Segmento: Training (gym, functional training, HIIT, crossfit, "
        "entrenamiento híbrido). "
        "Enfócate en funcionalidad, versatilidad de uso dentro y fuera del gym, "
        "y beneficios durante el entrenamiento. "
        "El entrenamiento híbrido (combinación de fuerza y resistencia "
        "cardiovascular en un mismo circuito) es una tendencia relevante "
        "para este segmento — puedes mencionarla como tipo de entrenamiento "
        "sin nombrar marcas o competiciones de terceros. "
        "Tono: motivacional, directo, orientado a resultados. "
        "NO incluyas autenticidad ni precios."
    ),
    "FOOTBALL": (
        "Segmento: Football/Fútbol (guayos, ropa de juego, accesorios, "
        "camisetas licensed/genéricas de fútbol). "
        "Para camisetas licensed: puedes incluir sección breve de autenticidad. "
        "Para calzado y ropa genérica: enfócate en rendimiento y superficie de juego. "
        "Tono: pasión deportiva, competitividad, identidad de hincha."
    ),
    "SPORTSWEAR": (
        "Segmento: Sportswear (ropa y calzado casual/lifestyle del día a día). "
        "Enfócate en versatilidad, comodidad, looks cotidianos y ocasiones de uso. "
        "Tono: accesible, inclusivo, estilo de vida activo. "
        "NO incluyas fichas técnicas ni autenticidad."
    ),
    "BASKETBALL": (
        "Segmento: Basketball (calzado, ropa y accesorios de basketball). "
        "Enfócate en cultura del basketball, rendimiento en cancha y estilo off-court. "
        "Tono: cultura urbana, competitivo, aspiracional."
    ),
    "OUTDOOR": (
        "Segmento: Outdoor (senderismo, trail, montaña — línea TERREX). "
        "Enfócate en aventura, rendimiento en naturaleza y durabilidad. "
        "Tono: exploración, conexión con la naturaleza, técnico pero inspirador."
    ),
    "MOTORSPORTS": (
        "Segmento: Motorsport (colecciones inspiradas en racing, F1). "
        "Enfócate en la cultura de la velocidad y el estilo racing en el día a día. "
        "Tono: adrenalina, precisión, cultura de pista, lifestyle premium."
    ),
    "SPS": (
        "Segmento: Specialist Sports (Golf, Tennis, Swim, otros deportes). "
        "Enfócate en el deporte específico de la keyword. "
        "Tono: experto pero accesible, orientado al deportista específico."
    ),
}

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

BRAND_TONE = {
    "description": (
        "Motivacional, directo, performance. Habla de atletas y movimiento. "
        "Sin fluff. Copy activo, verbos fuertes. "
        "Nada de 'descubre el maravilloso mundo de...'"
    ),
    "voice_examples": [
        "Corre más rápido. Llega más lejos.",
        "Diseñado para ganar. Construido para durar.",
        "No es suerte. Es entrenamiento.",
    ],
    "alt_text_examples": [
        "Corredor con tenis adidas Ultraboost en pista urbana al amanecer",
        "Cerca de la suela Boost mostrando la tecnología de cápsulas de energía",
        "Atleta entrenando con camiseta adidas Originals en gimnasio",
    ],
    "avoid": [
        "descubrir", "maravilloso", "increíble", "fantástico",
        "bienvenido al mundo de", "en este artículo te contaremos",
    ],
}

GOOGLE_DOMINIO = {
    "Colombia": "google.com.co", "Mexico": "google.com.mx",
    "Argentina": "google.com.ar", "Brasil": "google.com.br",
    "Chile": "google.cl", "Peru": "google.com.pe",
}
GOOGLE_PAIS = {
    "Colombia": "co", "Mexico": "mx", "Argentina": "ar",
    "Brasil": "br", "Chile": "cl", "Peru": "pe",
}
GOOGLE_IDIOMA = {
    "Colombia": "es", "Mexico": "es", "Argentina": "es",
    "Brasil": "pt", "Chile": "es", "Peru": "es",
}

TERMINOS_GENERICOS = [
    "outfit", "outfits", "look", "looks", "cómo", "como",
    "combinar", "usar", "vestir", "estilo", "para", "con",
    "de", "la", "el", "los", "las", "un", "una", "y", "o",
    "mujer", "hombre", "niño", "niña", "adidas", "colombia",
    "mexico", "argentina", "brasil", "chile", "peru",
    "qué", "que", "cuál", "cual", "mejor", "mejores",
]


# ═══════════════════════════════════════════════════════════
# FUNCIONES DEL PIPELINE
# ═══════════════════════════════════════════════════════════

def buscar_serp(query, mercado):
    params = {
        "engine": "google",
        "q": query,
        "google_domain": GOOGLE_DOMINIO[mercado],
        "gl": GOOGLE_PAIS[mercado],
        "hl": GOOGLE_IDIOMA[mercado],
        "location": mercado if mercado != "Brasil" else "Brazil",
        "api_key": SERPAPI_KEY,
    }
    response = requests.get("https://serpapi.com/search", params=params)
    return response.json()


def ejecutar_paso0(keyword, mercado):
    """SerpAPI: Google + site:adidas.xx. Devuelve dict con todo el contexto."""
    sitio = SITIOS_WEB[mercado]

    data = buscar_serp(keyword, mercado)

    palabras = keyword.lower().split()
    termino_producto = " ".join(
        [p for p in palabras if p not in TERMINOS_GENERICOS]
    )
    query_adidas = f"site:{sitio} {termino_producto}"
    data_adidas = buscar_serp(query_adidas, mercado)

    organic_top5 = []
    for r in data.get("organic_results", [])[:5]:
        organic_top5.append({
            "posicion": r.get("position"),
            "titulo": r.get("title"),
            "sitio": r.get("source", r.get("displayed_link", "")),
            "snippet": r.get("snippet", ""),
        })

    related_searches = [r["query"] for r in data.get("related_searches", [])[:8]]

    people_also_ask = [
        q.get("question", "")
        for q in data.get("related_questions", [])[:6]
        if q.get("question")
    ]

    video_titles = []
    for v in data.get("inline_videos", [])[:5]:
        t = v.get("title", "").strip()
        if t:
            video_titles.append(t)
    for v in data.get("short_videos", [])[:5]:
        t = v.get("title", "").strip()
        if t:
            video_titles.append(t)

    productos_adidas = []
    for r in data_adidas.get("organic_results", [])[:5]:
        if sitio in r.get("link", ""):
            productos_adidas.append({
                "titulo": r.get("title", ""),
                "snippet": r.get("snippet", ""),
                "link": r.get("link", ""),
            })

    snippet_adidas = ""
    for r in data.get("organic_results", [])[:5]:
        if "adidas" in r.get("link", ""):
            snippet_adidas = r.get("snippet", "")
            break

    seccion_paa = ""
    if people_also_ask:
        seccion_paa = "PREGUNTAS REALES DE GOOGLE (People Also Ask):\n"
        seccion_paa += "\n".join(f"- {q}" for q in people_also_ask)

    seccion_videos = ""
    if video_titles:
        seccion_videos = "TÍTULOS DE VIDEOS QUE RANKEAN (intents reales):\n"
        seccion_videos += "\n".join(f"- {t}" for t in video_titles)

    seccion_snippet_adidas = ""
    if snippet_adidas:
        seccion_snippet_adidas = f"DESCRIPCIÓN OFICIAL ADIDAS:\n{snippet_adidas}"

    seccion_productos = ""
    if productos_adidas:
        seccion_productos = f"PRODUCTOS REALES DE {sitio.upper()}:\n"
        seccion_productos += "\n".join(
            f'- {p["titulo"]}: {p["snippet"]}' for p in productos_adidas
        )

    secciones = [
        f'DATOS REALES DE GOOGLE ({mercado}) PARA "{keyword}":',
        "",
        "TOP 5 QUE RANKEAN HOY:",
        "\n".join(
            f"{r['posicion']}. {r['titulo']} — {r['sitio']}" for r in organic_top5
        ),
        "",
        "LO QUE LA GENTE TAMBIÉN BUSCA (related searches):",
        "\n".join(f"- {q}" for q in related_searches),
    ]
    for seccion in [seccion_paa, seccion_videos, seccion_snippet_adidas, seccion_productos]:
        if seccion:
            secciones.extend(["", seccion])

    contexto_serp = "\n".join(secciones).strip()

    return {
        "contexto_serp": contexto_serp,
        "seccion_productos": seccion_productos,
        "productos_adidas": productos_adidas,
        "organic_top5": organic_top5,
        "related_searches": related_searches,
        "people_also_ask": people_also_ask,
        "video_titles": video_titles,
        "termino_producto": termino_producto,
        "sitio": sitio,
    }


def ejecutar_paso1(keyword, mercado, paso0):
    """Genera 3 opciones de H1."""
    system_h1 = f"""Eres un copywriter senior especializado en SEO y marcas de performance.
Tu trabajo es escribir H1s que:
- Incluyan la keyword principal de forma natural (idealmente al inicio)
- Sean entre 50-70 caracteres
- Suenen a marca, no a SEO genérico
- Usen voz activa y verbos de acción

Tono de marca: {BRAND_TONE['description']}

Ejemplos del tono correcto:
{chr(10).join(f'- "{e}"' for e in BRAND_TONE['voice_examples'])}

Palabras y frases a EVITAR: {', '.join(BRAND_TONE['avoid'])}

Contexto del producto: la keyword corresponde a un producto adidas. Si conoces
el producto, respeta su posicionamiento real (ej: Samba = herencia de fútbol
sala, ícono lifestyle/terrace — NO es un tenis de running).

{MERCADOS[mercado]}

El contexto del producto es para evitar errores de posicionamiento —
NO lo repitas literalmente en los H1s. Usa tu propio ángulo creativo.

═══════════════════════════════════════
PRODUCTOS REALES DETECTADOS
═══════════════════════════════════════
{paso0['seccion_productos'] if paso0['seccion_productos'] else "Sin productos específicos detectados."}

INSTRUCCIÓN CRÍTICA: Las 3 opciones de H1 DEBEN usar nombres de productos
reales DIFERENTES de la lista de PRODUCTOS REALES DETECTADOS arriba — no
repitas la keyword genérica cuando tienes nombres específicos disponibles.
Si hay 3 o más productos distintos en la lista, usa un producto distinto
en cada una de las 3 opciones. Si hay menos de 3 productos, usa el más
relevante en más de una opción pero con ángulos completamente distintos
(emocional, factual, de uso).

Estructura: "[Nombre del producto real]: [beneficio o gancho con la
keyword]".

Si NO hay productos reales detectados, genera 3 ángulos distintos sin
nombre de producto: uno emocional, uno de estilo, uno informativo.

Responde SOLO con los H1s. Sin explicaciones, sin numeración, sin comillas."""

    user_h1 = f"""Keyword principal: "{keyword}"

Genera 3 opciones de H1 optimizado. Una por línea."""

    h1_raw = call_claude(system_h1, user_h1, max_tokens=300)
    h1_options = [line.strip() for line in h1_raw.split("\n") if line.strip()]
    return h1_options


def ejecutar_paso1_5(keyword, h1_elegido):
    """Meta description con autocorrección de longitud."""
    system_meta = """Eres un SEO copywriter especializado en e-commerce de moda y deporte.
Tu tarea es escribir la meta description del artículo.

Reglas ESTRICTAS:
- Entre 150-160 caracteres EXACTOS — ni uno más, ni uno menos
- Segunda persona ("tú", "te", "tu") — habla directo al lector
- Incluye la keyword principal de forma natural
- Termina con un beneficio claro o llamado a la acción
- Tono: directo, informativo, sin clickbait barato
- Puede usar "nuestra guía" o "nuestros expertos" (aquí sí se permite primera persona de marca)
- NUNCA empieces con la keyword sola — arranca con contexto o verbo

PROCESO OBLIGATORIO:
1. Escribe la meta description
2. Cuenta los caracteres tú mismo, incluyendo espacios
3. Si tiene más de 160 o menos de 150, reescríbela
4. Repite hasta que quede entre 150-160 caracteres
5. Responde SOLO con el texto final. Sin comillas, sin explicaciones, sin conteo."""

    user_meta = f"""Keyword principal: "{keyword}"
H1 del artículo: {h1_elegido}

Escribe la meta description. Recuerda: debe tener entre 150-160 caracteres exactos."""

    meta_description = call_claude(system_meta, user_meta, max_tokens=200).strip()
    chars = len(meta_description)

    if chars < 150 or chars > 160:
        user_meta_fix = f"""La meta description que escribiste tiene {chars} caracteres:
"{meta_description}"

{"Es demasiado corta" if chars < 150 else "Es demasiado larga"}.
Necesita tener entre 150-160 caracteres exactos.
{"Agrégale más contexto o amplía el CTA." if chars < 150 else "Recórtala sin perder la keyword ni el CTA."}
Responde SOLO con el texto corregido. Sin comillas ni explicaciones."""

        meta_description = call_claude(system_meta, user_meta_fix, max_tokens=200).strip()
        chars = len(meta_description)

    return meta_description, chars


def ejecutar_paso2(keyword, mercado, contexto_serp):
    """Genera FAQs ancladas en datos reales."""
    system_faq = f"""Eres un especialista en SEO y AEO (Answer Engine Optimization).
Tu tarea es generar preguntas frecuentes que reflejen búsquedas REALES.

Contexto del producto: la keyword corresponde a un PRODUCTO ADIDAS (calzado,
ropa o accesorio deportivo). Todas las preguntas deben ser sobre el producto
— NUNCA sobre otros significados de la palabra (bailes, música, lugares, etc.).

DATOS REALES DE GOOGLE — estas son las señales que DEBES usar:
{contexto_serp}

{MERCADOS[mercado]}

Formato de respuesta — JSON estricto, sin markdown, sin texto fuera del JSON:
[
  {{"pregunta": "¿...?", "intent": "informacional|comparativo|transaccional|troubleshooting"}}
]"""

    user_faq = f"""Keyword: "{keyword}"

Genera entre 6-8 preguntas frecuentes sobre el producto adidas.

INSTRUCCIÓN CRÍTICA: basa las preguntas DIRECTAMENTE en los datos
reales de Google que tienes arriba:

- El People Also Ask de Google son preguntas REALES — úsalas como
  base y adáptalas al producto adidas
- Los related searches revelan intents reales — conviértelos en
  preguntas
- NUNCA inventes preguntas que no vengan de señales reales de búsqueda
- MÁXIMO 1 pregunta sobre autenticidad — no es el foco del artículo
- Incluye al menos 1-2 preguntas de duda real del consumidor
  (tallas, comodidad, versatilidad, combinaciones)"""

    faqs = parse_json_safe(call_claude(system_faq, user_faq, max_tokens=1000))
    return faqs


def ejecutar_paso3(keyword, mercado):
    """Keyword cluster."""
    system_kw = f"""Eres un SEO strategist especializado en keyword research semántico.

Contexto del producto: la keyword corresponde a un PRODUCTO ADIDAS (calzado,
ropa o accesorio deportivo). Todo el cluster debe ser sobre el producto —
NUNCA sobre otros significados de la palabra (bailes, música, lugares, etc.).

{MERCADOS[mercado]}

Formato JSON estricto, sin markdown:
{{
  "secundarias": [...],
  "lsi": [...],
  "long_tail": [...],
  "entidades": [...]
}}"""

    user_kw = f"""Keyword principal: "{keyword}"

Genera el keyword cluster completo:
- Secundarias: 5-8 keywords
- LSI: 8-12 términos
- Long tail: 5-7 frases
- Entidades: 3-5 entidades relevantes"""

    keywords = parse_json_safe(call_claude(system_kw, user_kw, max_tokens=800))
    return keywords


def ejecutar_paso4(keyword, mercado, categoria, h1_elegido, faqs, keywords,
                    contexto_serp, productos_adidas, sitio):
    """Genera el blog completo."""
    hoy = datetime.now()
    fecha_blog = f"{MESES_ES[hoy.month]} {hoy.year}"

    system_blog = f"""Eres el editor senior del blog oficial de adidas.

═══════════════════════════════════════
PERSONA Y VOZ
═══════════════════════════════════════
Eres un "Personal Trainer o Style Mentor". Tu tono es autoritario pero
empático. Hablas SIEMPRE en segunda persona ("tú", "tu", "te").
Nunca usas "nosotros" ni voz corporativa.

Frases representativas del tono:
- "Calienta. Enfría. Sin excepciones."
- "¿Listo para ponerlo en práctica? Amárrate los tenis y vamos."
- "Todo el mundo merece verse bien y sentirse bien..."
- "Deja el análisis paralítico en la banca."

═══════════════════════════════════════
CONTEXTO REAL DE MERCADO
═══════════════════════════════════════
Usa estos datos reales de Google para anclar el contenido:
{contexto_serp}

Cómo usar estos datos:
- Related searches → úsalos como base para H2s y ángulos del artículo
- People Also Ask → respóndelos dentro del artículo o en las FAQs
- Snippet adidas → referencia de descripción oficial del producto
- Productos reales de adidas → úsalos para nombrar productos con
  precisión. NUNCA inventes nombres de producto.
- Si adidas no está en posición 1, cubre los ángulos que los
  competidores están respondiendo mejor

═══════════════════════════════════════
ESTRUCTURA OBLIGATORIA
═══════════════════════════════════════

BLOQUE DE METADATA (primera línea, antes del H1):
*adidas · {fecha_blog} · Lectura de X minutos*

HOOK (elige UNO de estos tres estilos):
1. Validación empática: reconoce que el tema puede ser abrumador
2. Dato de impacto: solo si tienes el dato 100% verificado
3. Contexto cultural/deportivo: conecta el producto a un momento cultural real

INTRO: máximo 3-6 frases después del hook, antes del primer H2.

H2s (6-8 por artículo): alterna entre:
- Preguntas conversacionales SEO: "¿Qué son los tenis Samba?"
- Afirmaciones instruccionales en MAYÚSCULAS: "DOMINA TU ESTILO CON LOS SAMBA"

H3s: úsalos SOLO para clasificación de productos o pasos cronológicos.

═══════════════════════════════════════
FORMATO DE PÁRRAFOS Y TEXTO
═══════════════════════════════════════
- Párrafos de máximo 1-4 FRASES. Estilo revista lifestyle.
- USA NEGRITAS para:
  * Las KEYWORDS PRINCIPALES (keyword principal + secundarias del cluster)
    — deben aparecer en negrita la primera vez que se mencionan, y la
    keyword principal específicamente debe aparecer en negrita al menos
    una vez en el primer párrafo
  * Nombres de modelos: **Samba OG**, **Gazelle**, **Ultraboost**
  * Tecnologías propias adidas CON NOMBRE PROPIO registrado (ej: Boost,
    Primeknit) — NO tecnologías genéricas o descriptivas
  * Reglas de fit: **snug but not tight**, **un dedo de espacio**
  * Marcadores de lista: **El look perfecto:**, **Top tip:**

- NUNCA uses negrita en términos técnicos GENÉRICOS que describen
  características (no nombres de marca/tecnología registrada) — EXCEPTO
  las keywords principales, que siempre deben llevar negrita cuando aparecen.

- LISTAS: bullets para outfits, opciones o factores no lineales.
  Numeración SOLO para pasos cronológicos.
- TABLAS: COMPLETAMENTE PROHIBIDAS.
- IMÁGENES: cada 2-3 secciones, incluye un marcador de imagen así:
  ![alt text descriptivo siguiendo el estilo de marca](#)
  El alt text debe describir QUÉ se ve, sin adjetivos de venta.

═══════════════════════════════════════
LINKS INTERNOS
═══════════════════════════════════════
Incluye 8-15 links distribuidos en 3 niveles:
1. Contextuales: "[guía de tallas](#)"
2. De producto: "[Samba OG](#)"
3. CTAs comerciales: "[COMPRA ULTRABOOST →](#)"

Anchor text para CTAs: VERBO + PRODUCTO + →

═══════════════════════════════════════
SECCIÓN DE FAQs
═══════════════════════════════════════
- Formato: pregunta en H3, respuesta de 1-3 frases máximo.
- REGLA CRÍTICA: cada respuesta DEBE empezar con "Sí", "No" o dato directo.
- Nunca respuestas largas.

═══════════════════════════════════════
CIERRE Y CTA FINAL
═══════════════════════════════════════
Cierra con 2-3 frases inspiracionales. Luego bloque de botones acorde
a la categoría del producto.

═══════════════════════════════════════
REGLAS DE MARCA — CRÍTICAS
═══════════════════════════════════════
- NUNCA menciones marcas competidoras.
- NUNCA uses tablas.
- NUNCA inventes datos, precios, estadísticas ni porcentajes.
  Si no tienes el dato verificado, omítelo completamente.
- NUNCA incluyas fichas técnicas — esto es editorial.
- NUNCA menciones precios ni redirijas a ningún sitio para consultarlos.
- NUNCA hagas de la autenticidad el tema central del artículo.
  Si la mencionas, máximo una frase en el CTA final.
  El foco es inspirar, no advertir sobre falsificaciones.
- NO incluyas secciones de "cómo detectar falsos", "dónde comprar
  originales" ni "señales de alerta". El lector ya está en adidas —
  ya está en el lugar correcto.
- NUNCA inventes nombres de producto. Solo usa productos que aparezcan
  en el CONTEXTO_SERP o que sean modelos icónicos verificados
  (Samba, Gazelle, Ultraboost, Superstar, Stan Smith, Forum).
- CRÍTICO: Solo usa URLs que aparezcan TEXTUALMENTE en el CONTEXTO_SERP.
  Si no tienes la URL exacta, usa (#) como placeholder.
  NUNCA construyas ni inventes URLs.

{MERCADOS[mercado]}

Guía de contenido para este segmento:
{GUIAS_CONTENIDO[categoria]}

Tono adicional: {BRAND_TONE['description']}
Palabras a evitar: {', '.join(BRAND_TONE['avoid'])}
Ejemplos de alt text en el tono de marca: {', '.join(BRAND_TONE['alt_text_examples'])}

Responde SOLO con el artículo en Markdown."""

    if productos_adidas:
        links_reales = "\n".join(
            f'- Anchor text: "{p["titulo"]}" → URL: {p["link"]}'
            for p in productos_adidas
        )
        instruccion_links = f"""
LINKS INTERNOS REALES DE {sitio.upper()} — usa estos EXACTAMENTE como
anchor text y como URLs. NO los parafrasees ni modifiques el texto:
{links_reales}

REGLA CRÍTICA: Si un producto NO aparece en la lista de arriba,
usa (#) como placeholder. NUNCA construyas ni deduzcas URLs.
Si no está en la lista, es (#). Sin excepciones.
"""
    else:
        instruccion_links = "Para todos los links internos usa (#) como placeholder."

    faq_list = "\n".join(f"- {f['pregunta']}" for f in faqs)

    user_blog = f"""Escribe el artículo completo siguiendo el manual editorial de adidas.

DATOS:
- Keyword principal: "{keyword}"
- H1 (úsalo tal cual): {h1_elegido}
- FAQs para la sección final (elige las 5 mejores):
{faq_list}
- Keywords secundarias: {', '.join(keywords['secundarias'])}
- Términos LSI: {', '.join(keywords['lsi'])}
- Long tail (base para H2s/H3s): {', '.join(keywords['long_tail'])}

{instruccion_links}

Largo objetivo: 900-1200 palabras.
Enfoque: rendimiento, tecnología, cómo elegir, cómo usar.
El artículo es ASPIRACIONAL e INSPIRACIONAL — no una guía de compra defensiva.
Sin fichas técnicas. Sin comparativas con otras marcas. Sin precios.
Sin autenticidad como tema."""

    blog = call_claude(system_blog, user_blog, max_tokens=4000)
    return blog


# ═══════════════════════════════════════════════════════════
# SESSION STATE — mantiene el progreso entre clics
# ═══════════════════════════════════════════════════════════
if "paso0" not in st.session_state:
    st.session_state.paso0 = None
if "h1_options" not in st.session_state:
    st.session_state.h1_options = None
if "h1_elegido" not in st.session_state:
    st.session_state.h1_elegido = None
if "meta_description" not in st.session_state:
    st.session_state.meta_description = None
if "faqs" not in st.session_state:
    st.session_state.faqs = None
if "keywords" not in st.session_state:
    st.session_state.keywords = None
if "blog" not in st.session_state:
    st.session_state.blog = None


# ═══════════════════════════════════════════════════════════
# SIDEBAR — INPUTS
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.title("⚡ Generador SEO/AEO")
    st.caption("adidas LAM — Demo Business Case")

    keyword = st.text_input(
        "Keyword principal",
        placeholder="ej: ultraboost, balón de fútbol, samba",
    )
    mercado = st.selectbox("Mercado", list(MERCADOS.keys()))
    categoria = st.selectbox("Categoría", list(GUIAS_CONTENIDO.keys()))

    generar = st.button("🚀 Generar Blog", type="primary", use_container_width=True)

    st.divider()
    st.caption(
        "Pipeline: SerpAPI (Google + adidas.xx) → H1 → Meta → "
        "FAQs → Keyword Cluster → Blog completo"
    )


# ═══════════════════════════════════════════════════════════
# LÓGICA PRINCIPAL
# ═══════════════════════════════════════════════════════════
st.title("Generador de Contenido SEO/AEO")
st.caption("Blogs editoriales anclados en datos reales de búsqueda — multi-mercado LAM")

if generar:
    if not keyword.strip():
        st.warning("⚠️ Escribe una keyword antes de generar.")
        st.stop()

    # Reset de todo el progreso anterior
    st.session_state.paso0 = None
    st.session_state.h1_options = None
    st.session_state.h1_elegido = None
    st.session_state.meta_description = None
    st.session_state.faqs = None
    st.session_state.keywords = None
    st.session_state.blog = None

    with st.spinner("🔍 Consultando Google y adidas.xx en tiempo real..."):
        st.session_state.paso0 = ejecutar_paso0(keyword, mercado)
        st.session_state.keyword = keyword
        st.session_state.mercado = mercado
        st.session_state.categoria = categoria

    with st.spinner("✍️ Generando opciones de H1..."):
        st.session_state.h1_options = ejecutar_paso1(
            keyword, mercado, st.session_state.paso0
        )

# ── Mostrar contexto de búsqueda (siempre que exista) ──────
if st.session_state.paso0:
    paso0 = st.session_state.paso0
    with st.expander("📊 Datos reales de Google (clic para ver)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Top 5 orgánicos:**")
            for r in paso0["organic_top5"]:
                tag = " 🟢 ADIDAS" if "adidas" in r["sitio"].lower() else ""
                st.markdown(f"{r['posicion']}. {r['sitio']}{tag}")

            st.markdown("**Related searches:**")
            for q in paso0["related_searches"][:6]:
                st.markdown(f"- {q}")

        with col2:
            if paso0["people_also_ask"]:
                st.markdown("**People Also Ask:**")
                for q in paso0["people_also_ask"][:6]:
                    st.markdown(f"- {q}")

            if paso0["productos_adidas"]:
                st.markdown(f"**Productos reales en {paso0['sitio']}:**")
                for p in paso0["productos_adidas"][:5]:
                    st.markdown(f"- {p['titulo']}")
            else:
                st.warning(f"Sin productos adidas detectados para esta keyword")

# ── Selector de H1 ───────────────────────────────────────────
if st.session_state.h1_options:
    st.subheader("1️⃣ Elige el H1")
    h1_elegido = st.radio(
        "Opciones generadas (cada una mezcla producto real + keyword):",
        st.session_state.h1_options,
        key="h1_radio",
    )
    st.session_state.h1_elegido = h1_elegido

    if st.button("✅ Confirmar H1 y continuar"):
        with st.spinner("📝 Generando meta description..."):
            meta, chars = ejecutar_paso1_5(
                st.session_state.keyword, st.session_state.h1_elegido
            )
            st.session_state.meta_description = meta
            st.session_state.meta_chars = chars

        with st.spinner("❓ Generando FAQs ancladas en datos reales..."):
            st.session_state.faqs = ejecutar_paso2(
                st.session_state.keyword,
                st.session_state.mercado,
                st.session_state.paso0["contexto_serp"],
            )

        with st.spinner("🔑 Generando keyword cluster..."):
            st.session_state.keywords = ejecutar_paso3(
                st.session_state.keyword, st.session_state.mercado
            )

        with st.spinner("📄 Escribiendo el blog completo (puede tomar ~30-60s)..."):
            st.session_state.blog = ejecutar_paso4(
                st.session_state.keyword,
                st.session_state.mercado,
                st.session_state.categoria,
                st.session_state.h1_elegido,
                st.session_state.faqs,
                st.session_state.keywords,
                st.session_state.paso0["contexto_serp"],
                st.session_state.paso0["productos_adidas"],
                st.session_state.paso0["sitio"],
            )

# ── Meta description ────────────────────────────────────────
if st.session_state.meta_description:
    st.subheader("2️⃣ Meta description")
    chars = st.session_state.meta_chars
    if 150 <= chars <= 160:
        st.success(f"✅ {chars} caracteres")
    else:
        st.warning(f"⚠️ {chars} caracteres (fuera de rango 150-160)")
    st.text_area("", st.session_state.meta_description, height=70, label_visibility="collapsed")

# ── FAQs ─────────────────────────────────────────────────────
if st.session_state.faqs:
    with st.expander("3️⃣ FAQs generadas (ancladas en People Also Ask real)"):
        for f in st.session_state.faqs:
            st.markdown(f"**[{f['intent']}]** {f['pregunta']}")

# ── Keyword cluster ──────────────────────────────────────────
if st.session_state.keywords:
    with st.expander("4️⃣ Keyword cluster"):
        kw = st.session_state.keywords
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Secundarias:**")
            for k in kw["secundarias"]:
                st.markdown(f"- {k}")
            st.markdown("**LSI:**")
            for k in kw["lsi"]:
                st.markdown(f"- {k}")
        with col2:
            st.markdown("**Long tail:**")
            for k in kw["long_tail"]:
                st.markdown(f"- {k}")
            st.markdown("**Entidades:**")
            for k in kw["entidades"]:
                st.markdown(f"- {k}")

# ── Blog final ───────────────────────────────────────────────
if st.session_state.blog:
    st.subheader("5️⃣ Blog completo")
    st.markdown("---")
    st.markdown(st.session_state.blog)
    st.markdown("---")

    st.download_button(
        "💾 Descargar como .md",
        st.session_state.blog,
        file_name=f"blog_{st.session_state.keyword.replace(' ', '_')}.md",
        mime="text/markdown",
    )
