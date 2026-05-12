"""
scraper_paises.py
=================
Script de web scraping profesional para extraer nombres de países y sus capitales
desde: https://www.scrapethissite.com/pages/simple/

Librerías requeridas:
    pip install requests beautifulsoup4 pandas

Autor  : Generado con Claude (Anthropic)
Fecha  : 2026
Salida : paises_lista.csv
"""

import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd


# ─────────────────────────────────────────────
# CONFIGURACIÓN GENERAL
# ─────────────────────────────────────────────

URL = "https://www.scrapethissite.com/pages/simple/"

# Cabeceras HTTP para simular un navegador real y evitar bloqueos básicos
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
}

# Nombre del archivo de salida
ARCHIVO_SALIDA = "paises_lista.csv"


# ─────────────────────────────────────────────
# FUNCIÓN: Obtener el HTML de la página
# ─────────────────────────────────────────────

def obtener_html(url: str) -> str:
    """
    Realiza una petición GET a la URL indicada y devuelve el contenido HTML.

    Parámetros:
        url (str): Dirección web a consultar.

    Retorna:
        str: Contenido HTML de la página.

    Lanza:
        SystemExit: Si la petición falla (timeout, error HTTP, etc.).
    """
    print(f"[1/4] Conectando a: {url}")
    try:
        respuesta = requests.get(url, headers=HEADERS, timeout=15)
        # Lanza una excepción automática si el código HTTP indica error (4xx / 5xx)
        respuesta.raise_for_status()
    except requests.exceptions.Timeout:
        print("  ✗  Error: La petición tardó demasiado (timeout).")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"  ✗  Error HTTP: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"  ✗  Error de conexión: {e}")
        sys.exit(1)

    print(f"  ✓  Respuesta OK — Código HTTP: {respuesta.status_code}")
    return respuesta.text


# ─────────────────────────────────────────────
# FUNCIÓN: Parsear y extraer datos del HTML
# ─────────────────────────────────────────────

def extraer_paises(html: str) -> list[dict]:
    """
    Analiza el HTML con BeautifulSoup y extrae los datos de cada país.

    La página estructura cada país dentro de un <div class="country">.
    Dentro de ese contenedor se encuentran:
        - <h3 class="country-name">  → nombre del país
        - <span class="country-capital"> → capital
        - <span class="country-population"> → población
        - <span class="country-area"> → área en km²

    Parámetros:
        html (str): Contenido HTML crudo de la página.

    Retorna:
        list[dict]: Lista de diccionarios con los campos extraídos.
    """
    print("[2/4] Analizando el HTML con BeautifulSoup...")

    # Usamos el parser estándar incluido en Python (no requiere instalación extra)
    soup = BeautifulSoup(html, "html.parser")

    # Seleccionamos todos los contenedores de país
    contenedores = soup.find_all("div", class_="country")

    if not contenedores:
        print("  ✗  No se encontraron países en la página. "
              "Verifica que la estructura HTML no haya cambiado.")
        sys.exit(1)

    print(f"  ✓  Se encontraron {len(contenedores)} países.")

    registros = []

    for contenedor in contenedores:
        # ── Nombre del país ──────────────────────────────────────────────────
        tag_nombre = contenedor.find("h3", class_="country-name")
        nombre = tag_nombre.get_text(strip=True) if tag_nombre else "N/D"

        # ── Capital ──────────────────────────────────────────────────────────
        tag_capital = contenedor.find("span", class_="country-capital")
        capital = tag_capital.get_text(strip=True) if tag_capital else "N/D"

        # ── Población ────────────────────────────────────────────────────────
        tag_poblacion = contenedor.find("span", class_="country-population")
        poblacion = tag_poblacion.get_text(strip=True) if tag_poblacion else "N/D"

        # ── Área (km²) ───────────────────────────────────────────────────────
        tag_area = contenedor.find("span", class_="country-area")
        area = tag_area.get_text(strip=True) if tag_area else "N/D"

        registros.append({
            "País":       nombre,
            "Capital":    capital,
            "Población":  poblacion,
            "Área (km²)": area,
        })

    return registros


# ─────────────────────────────────────────────
# FUNCIÓN: Crear DataFrame y limpiar datos
# ─────────────────────────────────────────────

def construir_dataframe(registros: list[dict]) -> pd.DataFrame:
    """
    Convierte la lista de registros en un DataFrame de Pandas
    y aplica limpieza básica de datos.

    Parámetros:
        registros (list[dict]): Datos crudos extraídos del scraping.

    Retorna:
        pd.DataFrame: DataFrame limpio y listo para exportar.
    """
    print("[3/4] Construyendo el DataFrame y limpiando datos...")

    df = pd.DataFrame(registros)

    # Convertir columnas numéricas — ignorar errores para valores no numéricos
    df["Población"]  = pd.to_numeric(df["Población"],  errors="coerce")
    df["Área (km²)"] = pd.to_numeric(df["Área (km²)"], errors="coerce")

    # Eliminar filas completamente vacías (si las hubiera)
    df.dropna(how="all", inplace=True)

    # Resetear el índice tras la limpieza
    df.reset_index(drop=True, inplace=True)

    print(f"  ✓  DataFrame creado: {len(df)} filas × {len(df.columns)} columnas.")
    return df


# ─────────────────────────────────────────────
# FUNCIÓN: Guardar CSV
# ─────────────────────────────────────────────

def guardar_csv(df: pd.DataFrame, ruta: str) -> None:
    """
    Exporta el DataFrame a un archivo CSV.

    Parámetros:
        df   (pd.DataFrame): Datos a guardar.
        ruta (str)         : Ruta/nombre del archivo de salida.
    """
    print(f"[4/4] Guardando datos en '{ruta}'...")

    # index=False evita que Pandas escriba la columna de índice numérico
    # encoding='utf-8-sig' asegura compatibilidad con Excel en Windows
    df.to_csv(ruta, index=False, encoding="utf-8-sig")

    print(f"  ✓  Archivo guardado correctamente.")


# ─────────────────────────────────────────────
# FUNCIÓN: Mostrar resumen en consola
# ─────────────────────────────────────────────

def mostrar_resumen(df: pd.DataFrame) -> None:
    """Imprime un resumen estadístico y una vista previa del DataFrame."""
    print("\n" + "═" * 60)
    print("  RESUMEN DEL DATASET")
    print("═" * 60)
    print(f"  Total de países extraídos : {len(df)}")
    print(f"  Columnas                  : {', '.join(df.columns)}")
    print(f"  Valores nulos             : {df.isnull().sum().sum()}")
    print("═" * 60)
    print("\n  Vista previa (primeros 10 registros):\n")
    # Ajustar opciones de visualización para que quepan en la terminal
    with pd.option_context("display.max_columns", None,
                           "display.width", 100,
                           "display.float_format", "{:,.0f}".format):
        print(df[["País", "Capital"]].head(10).to_string(index=False))
    print()


# ─────────────────────────────────────────────
# PUNTO DE ENTRADA PRINCIPAL
# ─────────────────────────────────────────────

def main() -> None:
    """Orquesta todo el flujo: descarga → parseo → limpieza → exportación."""
    print("\n" + "═" * 60)
    print("  WEB SCRAPER — Países y Capitales del Mundo")
    print("═" * 60 + "\n")

    # Paso 1 — Descargar el HTML
    html = obtener_html(URL)

    # Paso 2 — Extraer los datos con BeautifulSoup
    registros = extraer_paises(html)

    # Paso 3 — Construir y limpiar el DataFrame
    df = construir_dataframe(registros)

    # Paso 4 — Guardar en CSV
    guardar_csv(df, ARCHIVO_SALIDA)

    # Mostrar resumen en consola
    mostrar_resumen(df)

    print(f"  Proceso completado. Revisa el archivo: '{ARCHIVO_SALIDA}'\n")


if __name__ == "__main__":
    main()
