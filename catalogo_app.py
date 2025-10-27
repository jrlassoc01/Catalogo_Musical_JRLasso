import streamlit as st
import pandas as pd

# ------------------------
# Configuración inicial
# ------------------------
st.set_page_config(page_title="Catálogo de Discos", page_icon="🎶", layout="wide")

# ------------------------
# Estilos visuales
# ------------------------
st.markdown("""
    <style>
      .app-title {font-size: 40px; font-weight: 800; text-align:center; color:#0F172A; margin-bottom:0}
      .app-sub  {font-size: 16px; text-align:center; color:#475569; margin-top:4px }
      .stDataFrame, .stTable {background: #FFFFFF; border-radius: 12px}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-title">🎶 Catálogo de Vinilos y CDs</div>', unsafe_allow_html=True)
st.markdown('<div class="app-sub">Explora tus canciones y descubre en qué álbum o formato se encuentran</div>', unsafe_allow_html=True)
st.divider()

# ------------------------
# Cargar el catálogo
# ------------------------
ARCHIVO_EXCEL = "catalogo_musical.xlsx"   # Ajusta si tu archivo tiene otro nombre

@st.cache_data
def cargar_catalogo(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)

    # Normalizaciones mínimas
    if "Orquesta" in df.columns and "Orquesta/Solista" not in df.columns:
        df = df.rename(columns={"Orquesta": "Orquesta/Solista"})
    if "Año" not in df.columns:
        df["Año"] = ""

    # Columna auxiliar para filtros numéricos por año (si la usas luego)
    df["_Año_num"] = pd.to_numeric(df["Año"], errors="coerce")

    # Asegurar columnas esperadas
    cols_necesarias = ["Álbum","Intérprete","Canción","Orquesta/Solista","Compositor","Año","Formato",
                       "Sello","Número de catálogo","País","Notas"]
    for c in cols_necesarias:
        if c not in df.columns:
            df[c] = pd.Series(dtype="object")

    return df

try:
    df = cargar_catalogo(ARCHIVO_EXCEL)
    resultados = df.copy()
except FileNotFoundError:
    st.error(f"❌ No se encontró el archivo **{ARCHIVO_EXCEL}**. Sube el archivo correcto o ajusta el nombre en el código.")
    st.stop()

# ------------------------
# FILTROS AVANZADOS (primero)
# ------------------------
st.sidebar.header("🎧 Filtros principales")
st.sidebar.caption("Selecciona una o más opciones para refinar tu búsqueda:")

canciones    = ["(Todas)"] + sorted(df["Canción"].dropna().unique().tolist())
interpretes  = ["(Todos)"] + sorted(df["Intérprete"].dropna().unique().tolist())
orq_solistas = ["(Todas)"] + sorted(df["Orquesta/Solista"].dropna().unique().tolist())
compositores = ["(Todos)"] + sorted(df["Compositor"].dropna().unique().tolist())

can_sel  = st.sidebar.selectbox("🎵 Canción", canciones)
int_sel  = st.sidebar.selectbox("🎤 Intérprete", interpretes)
orq_sel  = st.sidebar.selectbox("🎺 Orquesta / Solista", orq_solistas)
comp_sel = st.sidebar.selectbox("✍️ Compositor", compositores)

# Aplicar filtros en orden
if can_sel != "(Todas)":
    resultados = resultados[resultados["Canción"] == can_sel]
if int_sel != "(Todos)":
    resultados = resultados[resultados["Intérprete"] == int_sel]
if orq_sel != "(Todas)":
    resultados = resultados[resultados["Orquesta/Solista"] == orq_sel]
if comp_sel != "(Todos)":
    resultados = resultados[resultados["Compositor"] == comp_sel]

st.divider()

# ------------------------
# BÚSQUEDA RÁPIDA (después de los filtros)
# ------------------------
busqueda = st.text_input("🔎 Buscar por cualquier palabra (álbum, sello, país, notas, etc.)", "")

if busqueda.strip():
    mask = resultados.apply(
        lambda row: row.astype(str).str.contains(busqueda, case=False, na=False).any(), axis=1
    )
    resultados = resultados[mask]

st.divider()

# ------------------------
# Mostrar resultados
# ------------------------
st.markdown("### 📋 Resultados filtrados")

# Reordenar: Formato primero y sin encabezado visible
cols_mostrar = ["Formato","Álbum","Intérprete","Canción","Orquesta/Solista","Compositor",
                "Año","Sello","Número de catálogo","País","Notas"]
cols_presentes = [c for c in cols_mostrar if c in resultados.columns]

# Renombrar 'Formato' a un encabezado vacío
tabla = resultados[cols_presentes].rename(columns={"Formato": " "})

# Mostrar sin índice y con Formato como primera columna (encabezado vacío)
st.dataframe(tabla, use_container_width=True, height=520, hide_index=True)

st.caption("💡 Consejo: añade este enlace a la pantalla de inicio del teléfono para usarlo como app.")
