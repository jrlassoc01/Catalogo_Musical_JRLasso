import streamlit as st
import pandas as pd

# ------------------------
# Configuración inicial
# ------------------------
st.set_page_config(page_title="Catálogo de Discos", layout="wide")
st.title("🎶 Catálogo de Vinilos y CDs")

# ------------------------
# Cargar el catálogo
# ------------------------
archivo_excel = "catalogo_musical.xlsx"  # Cambia el nombre si tu archivo es distinto

@st.cache_data
def cargar_catalogo(archivo):
    return pd.read_excel(archivo)

try:
    df = cargar_catalogo(archivo_excel)
except FileNotFoundError:
    st.error(f"No se encontró el archivo {archivo_excel}. Asegúrate de que esté en la misma carpeta.")
    st.stop()


# ------------------------
# Filtros especiales
# ------------------------
with st.expander("🔧 Filtros avanzados"):
    col3, col2, col4 = st.columns(3)

    with col3:
        cancion = st.selectbox("Filtrar por Canción", ["(Todos)"] + sorted(df["Canción"].dropna().unique().tolist()))
    with col2:
        interprete = st.selectbox("Filtrar por Intérprete", ["(Todos)"] + sorted(df["Intérprete"].dropna().unique().tolist()))
    with col4:
        orquesta = st.selectbox("Filtrar por Orquesta", ["(Todos)"] + sorted(df["Orquesta"].dropna().unique().tolist()))

    if cancion != "(Todos)":
        resultados = resultados[resultados["Canción"] == cancion]
    if interprete != "(Todos)":
        resultados = resultados[resultados["Intérprete"] == interprete]
    if orquesta != "(Todos)":
        resultados = resultados[resultados["Orquesta"] == orquesta]

# ------------------------
# Mostrar resultados finales
# ------------------------
st.subheader("📋 Resultados filtrados")
st.dataframe(resultados, use_container_width=True)

# ------------------------
# Búsqueda general
# ------------------------
busqueda = st.text_input("🔍 Buscar por álbum, intérprete, canción, compositor, etc.")

if busqueda:
    filtro = df.apply(lambda row: row.astype(str).str.contains(busqueda, case=False, na=False).any(), axis=1)
    resultados = df[filtro]
else:
    resultados = df

st.write(f"📀 Resultados encontrados: {len(resultados)}")
st.dataframe(resultados, use_container_width=True)
