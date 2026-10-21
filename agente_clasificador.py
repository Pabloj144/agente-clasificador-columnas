import os
import json
import pandas as pd
from openai import OpenAI

# -------------------------------------------------------------------
# CONFIGURACIÓN DE OPENROUTER Y MODELO
# -------------------------------------------------------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "API_KEY")
MODELO_GEMINI = "google/gemini-3.8-flash"
TAMANO_LOTE_MAX = 30  # Lote fijado a máximo 30 columnas

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# -------------------------------------------------------------------
# FASE 1: GENERAR EXTRACTO JSON LIGERO POR LOTE
# -------------------------------------------------------------------
def generar_extracto_lote(df, columnas_lote):
    """
    Crea un JSON reducido únicamente para las columnas del lote actual:
    incluye tipos de datos, % de nulos y solo 3 filas de muestra.
    """
    df_sub = df[columnas_lote]
    muestra_filas = df_sub.head(3).astype(str).to_dict(orient="records")
    
    informacion_cols = []
    for col in columnas_lote:
        informacion_cols.append({
            "columna": col,
            "tipo_dato": str(df_sub[col].dtype),
            "porcentaje_nulos": round((df_sub[col].isnull().sum() / len(df_sub)) * 100, 2)
        })
        
    return {
        "columnas_en_este_lote": len(columnas_lote),
        "muestra_3_filas": muestra_filas,
        "metadatos_columnas": informacion_cols
    }

def dividir_en_lotes(lista, tamano=30):
    """Divide la lista de columnas en bloques de máximo 30."""
    for i in range(0, len(lista), tamano):
        yield lista[i:i + tamano]

# -------------------------------------------------------------------
# FASE 2: CONSULTA AL MODELO GEMINI
# -------------------------------------------------------------------
def consultar_agente_lote(json_lote, consulta_usuario, numero_lote, total_lotes):
    """
    Envía el extracto JSON de un lote de máximo 30 columnas a Gemini Flash.
    """
    prompt_sistema = """
    Eres un Agente Clasificador de Datos por Lotes.
    Tu objetivo es evaluar ÚNICAMENTE las columnas incluidas en el JSON recibido para responder a la necesidad del usuario.

    FORMATO OBLIGATORIO DE CLASIFICACIÓN POR COLUMNA:
    - 🟢 ÚTILES: Columnas indispensables para responder a la consulta o regla de negocio.
    - 🟡 SECUNDARIAS / OPCIONALES: Columnas que aportan contexto secundario.
    - 🔴 NO ÚTILES / DESCARTABLES: Columnas irrelevantes, redundantes o innecesarias.

    Solo clasifica una columna como 🟢 ÚTIL si es estrictamente imprescindible para responder a la consulta.

    Ante la menor duda o si la columna solo aporta contexto adicional, MUVÉLA OBLIGATORIAMENTE A 🟡 SECUNDARIA. Es preferible tener menos columnas verdes que sobre-incluir.    

    Menciona CADA UNA de las columnas recibidas en el lote con su respectiva justificación breve.

    REGLA PROHIBITIVA STRICTA:
    NO incluyas sugerencias de infraestructura, recomendaciones de arquitectura de datos, ni textos de conclusión generales fuera de la clasificación.
    """

    prompt_usuario = f"""
    PREGUNTA / OBJETIVO DEL USUARIO:
    "{consulta_usuario}"

    EVALUANDO LOTE {numero_lote} DE {total_lotes}

    EXTRACTO EN JSON DEL LOTE (SÓLO 3 FILAS DE MUESTRA Y METADATOS):
    {json.dumps(json_lote, indent=2, ensure_ascii=False)}
    """

    response = client.chat.completions.create(
        model=MODELO_GEMINI,
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ],
        temperature=0.1
    )

    return response.choices[0].message.content

# -------------------------------------------------------------------
# FASE 3: EJECUCIÓN Y SALIDA ESTRUCTURADA
# -------------------------------------------------------------------
def procesar_consulta_agente(ruta_csv, consulta_usuario, tamano_lote=30):
    try:
        df = pd.read_csv(ruta_csv, sep=None, engine='python')
    except Exception as e:
        print(f"❌ Error al leer el CSV: {e}")
        return

    total_filas = len(df)
    columnas_totales = list(df.columns)
    total_columnas = len(columnas_totales)

    lotes_columnas = list(dividir_en_lotes(columnas_totales, tamano_lote))
    total_lotes = len(lotes_columnas)

    print("\n" + "=" * 60)
    print("🤖 RESPUESTA DEL AGENTE CLASIFICADOR")
    print("=" * 60)
    
    # 1. RESPUESTA DIRECTA Y OBJETIVO
    print(f"1. RESPUESTA A LA CONSULTA:")
    print(f"   Análisis ejecutado con éxito para la regla de negocio: '{consulta_usuario}'")
    
    # 2. DIMENSIONES
    print(f"\n2. DIMENSIONES DEL DATASET:")
    print(f"   • Total de Filas: {total_filas:,}")
    print(f"   • Total de Columnas: {total_columnas} (Procesadas en {total_lotes} lote(s) de máximo {tamano_lote} columnas)")
    
    # 3. CLASIFICACIÓN DE COLUMNAS POR LOTE
    print(f"\n3. CLASIFICACIÓN DE COLUMNAS:")
    print("-" * 60)

    for idx, lote in enumerate(lotes_columnas, 1):
        print(f"\n📦 LOTE {idx}/{total_lotes} ({len(lote)} columnas):")
        json_lote = generar_extracto_lote(df, lote)
        respuesta_lote = consultar_agente_lote(json_lote, consulta_usuario, idx, total_lotes)
        print(respuesta_lote)
    
    print("\n" + "=" * 60)

# -------------------------------------------------------------------
# BUCLE INTERACTIVO
# -------------------------------------------------------------------
if __name__ == "__main__":
    RUTA_ARCHIVO = "data/dataset_benchmark.csv"

    print("=" * 60)
    print("AGENTE CLASIFICADOR DE DATOS (LOTES DE MÁXIMO 30 COLUMNAS)")
    print("=" * 60)

    while True:
        consulta = input("\n💬 Haz tu pregunta o regla de negocio (o 'salir' para finalizar) > ")
        
        if consulta.lower().strip() in ['salir', 'exit', 'quit']:
            print("Programa finalizado.")
            break
            
        if not consulta.strip():
            continue

        print("\n⏳ Procesando en lotes de 30 columnas con extracto JSON...")
        procesar_consulta_agente(RUTA_ARCHIVO, consulta, tamano_lote=TAMANO_LOTE_MAX)