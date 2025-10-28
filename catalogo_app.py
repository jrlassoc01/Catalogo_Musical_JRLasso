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
ARCHIVO_EXCEL = "catalogo_musical.xlsx"   # Asegúrate de que el nombre coincide exactamente

@st.cache_data
def cargar_catalogo(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)

    # Normalizar nombres de columnas (acentos y variantes)
    renames = {
        "Genero": "Género",
        "Duracion": "Duración",
        "Ubicacion": "Ubicación",
        "Posicion": "Posición",
        "Sello discografico": "Sello discográfico",
        "Sello Discografico": "Sello discográfico",
        "Catalogo": "Catálogo",
    }

    for old, new in renames.items():
        if old in df.columns and new not in df.columns:
            df = df.rename(columns={old: new})

    # Verificar que todas las columnas esperadas existan (crear vacías si faltan)
    cols_esperadas = [
        "Álbum","Intérprete","Canción","Duración","Orquesta/Solista","Compositor",
        "Género","Año","Formato","Sello discográfico","Catálogo","Ubicación","Posición","Notas"
    ]
    for c in cols_esperadas:
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
# BÚSQUEDA RÁPIDA
# ------------------------
busqueda = st.text_input("🔎 Buscar por cualquier palabra (álbum, sello, género, notas, etc.)", "")

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

cols_mostrar = [
    "Formato","Álbum","Intérprete","Canción","Duración","Orquesta/Solista","Compositor",
    "Género","Sello discográfico","Catálogo","Ubicación","Posición","Notas"
]
cols_presentes = [c for c in cols_mostrar if c in resultados.columns]

# Renombrar Formato (sin encabezado visible)
tabla = resultados[cols_presentes].rename(columns={"Formato": " "})

# Limpieza de filas vacías
subset_validas = [c for c in cols_presentes if c in tabla.columns]
tabla = tabla.replace(r"^\s*$", pd.NA, regex=True).dropna(how="all", subset=subset_validas)

# Altura dinámica según número de resultados
num_filas = len(tabla)
row_h = 38
header_h = 42
min_h = 140
max_h = 700
altura = min(max_h, max(min_h, header_h + row_h * max(1, num_filas)))

st.dataframe(tabla, use_container_width=True, hide_index=True, height=altura)
st.caption("💡 Consejo: añade este enlace a la pantalla de inicio del teléfono para usarlo como app.")
