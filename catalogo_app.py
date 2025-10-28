import streamlit as st
import pandas as pd
import math

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
      .card {
          border:1px solid #E2E8F0; border-radius:14px; padding:14px; margin-bottom:12px;
          background:#FFFFFF;
          box-shadow: 0 1px 2px rgba(0,0,0,0.04);
      }
      .badge {
          display:inline-block; padding:2px 10px; border-radius:999px; font-size:12px;
          border:1px solid #CBD5E1; color:#334155; background:#F1F5F9; margin-right:8px
      }
      .song {font-size:18px; font-weight:700; margin:2px 0 8px 0; color:#0F172A}
      .meta  {font-size:14px; color:#334155; line-height:1.5}
      .label {color:#64748B}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-title">🎶 Catálogo de Vinilos y CDs</div>', unsafe_allow_html=True)
st.markdown('<div class="app-sub">Explora tus canciones y descubre en qué álbum o formato se encuentran</div>', unsafe_allow_html=True)
st.divider()

# ------------------------
# Cargar el catálogo
# ------------------------
ARCHIVO_EXCEL = "catalogo_musical.xlsx"   # Asegúrate de que coincide

@st.cache_data
def cargar_catalogo(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)

    # Normalizar nombres (según tu encabezado real)
    renames = {
        "Genero": "Género",
        "Duracion": "Duración",
        "Ubicacion": "Ubicación",
        "Posicion": "Posición",
        "Sello discografico": "Sello discográfico",
        "Sello Discografico": "Sello discográfico",
        "Catalogo": "Catálogo",
        "Orquesta": "Orquesta/Solista",
    }
    for old, new in renames.items():
        if old in df.columns and new not in df.columns:
            df = df.rename(columns={old: new})

    # Asegurar columnas esperadas
    cols = ["Álbum","Intérprete","Canción","Duración","Orquesta/Solista","Compositor",
            "Género","Año","Formato","Sello discográfico","Catálogo","Ubicación","Posición","Notas"]
    for c in cols:
        if c not in df.columns:
            df[c] = pd.Series(dtype="object")

    return df

try:
    df = cargar_catalogo(ARCHIVO_EXCEL)
    resultados = df.copy()
except FileNotFoundError:
    st.error(f"❌ No se encontró el archivo **{ARCHIVO_EXCEL}**. Sube el archivo o ajusta el nombre en el código.")
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

# Limpiar filas totalmente vacías en columnas clave visibles
cols_visibles = ["Formato","Álbum","Intérprete","Canción","Duración","Orquesta/Solista","Compositor",
                 "Género","Sello discográfico","Catálogo","Ubicación","Posición","Notas"]
subset_validas = [c for c in cols_visibles if c in resultados.columns]
resultados = (resultados
              .replace(r"^\s*$", pd.NA, regex=True)
              .dropna(how="all", subset=subset_validas))

st.divider()

# ------------------------
# Selector de vista
# ------------------------
col_v1, col_v2 = st.columns([2,1])
with col_v1:
    vista = st.radio("Vista", ["Tabla", "Tarjetas"], horizontal=True)
with col_v2:
    st.write("")  # espaciador
    st.metric("Resultados", len(resultados))

# ------------------------
# Vista: TABLA
# ------------------------
if vista == "Tabla":
    st.markdown("### 📋 Resultados (Tabla)")
    # Formato primero y sin encabezado
    cols_mostrar = ["Formato","Álbum","Intérprete","Canción","Duración","Orquesta/Solista","Compositor",
                    "Género","Sello discográfico","Catálogo","Ubicación","Posición","Notas"]
    cols_presentes = [c for c in cols_mostrar if c in resultados.columns]
    tabla = resultados[cols_presentes].rename(columns={"Formato": " "})

    # Altura dinámica
    num_filas = len(tabla)
    row_h = 38
    header_h = 42
    min_h = 140
    max_h = 700
    altura = min(max_h, max(min_h, header_h + row_h * max(1, num_filas)))

    st.dataframe(tabla, use_container_width=True, hide_index=True, height=altura)

# ------------------------
# Vista: TARJETAS
# ------------------------
else:
    st.markdown("### 🗂️ Resultados (Tarjetas)")

    # Parámetros de tarjetas
    por_pagina = st.slider("Resultados por página", 5, 30, 12, 1)
    total = len(resultados)
    paginas = max(1, math.ceil(total / por_pagina))
    col_pag1, col_pag2, col_pag3 = st.columns([1,2,1])
    with col_pag1:
        pag = st.number_input("Página", min_value=1, max_value=paginas, value=1, step=1)
    with col_pag2:
        st.write(f"Mostrando {min(total, por_pagina)} de {total} resultados por página")
    with col_pag3:
        st.write("")

    ini = (pag - 1) * por_pagina
    fin = ini + por_pagina
    df_page = resultados.iloc[ini:fin]

    # Cuántas columnas de tarjetas por fila
    cols_tarjetas = st.slider("Tarjetas por fila", 1, 3, 2)

    # Función para badge de formato
    def formato_badge(valor: str) -> str:
        v = str(valor or "").strip().lower()
        if "vinilo" in v or "lp" in v:
            return "📀 Vinilo"
        if "cd" in v:
            return "💿 CD"
        return "🎵 " + (valor if valor else "—")

    # Render de tarjetas
    rows = math.ceil(len(df_page) / cols_tarjetas)
    items = df_page.to_dict(orient="records")

    idx = 0
    for _ in range(rows):
        cols = st.columns(cols_tarjetas)
        for c in cols:
            if idx >= len(items):
                c.empty()
                continue
            r = items[idx]; idx += 1

            c.markdown(f"""
            <div class="card">
              <div class="badge">{formato_badge(r.get('Formato'))}</div>
              <div class="song">{r.get('Canción', '—')}</div>
              <div class="meta"><span class="label">Álbum:</span> {r.get('Álbum','—')}</div>
              <div class="meta"><span class="label">Intérprete:</span> {r.get('Intérprete','—')}</div>
              <div class="meta"><span class="label">Orquesta/Solista:</span> {r.get('Orquesta/Solista','—')}</div>
              <div class="meta"><span class="label">Compositor:</span> {r.get('Compositor','—')}</div>
              <div class="meta"><span class="label">Año:</span> {r.get('Año','—')}  &nbsp;•&nbsp; <span class="label">Género:</span> {r.get('Género','—')}</div>
              <div class="meta"><span class="label">Sello:</span> {r.get('Sello discográfico','—')}  &nbsp;•&nbsp; <span class="label">Catálogo:</span> {r.get('Catálogo','—')}</div>
              <div class="meta"><span class="label">Ubicación:</span> {r.get('Ubicación','—')}  &nbsp;•&nbsp; <span class="label">Posición:</span> {r.get('Posición','—')}</div>
              {"<div class='meta'><span class='label'>Notas:</span> " + str(r.get('Notas')) + "</div>" if str(r.get('Notas','')).strip() != '' else ""}
            </div>
            """, unsafe_allow_html=True)

    st.caption("Sugerencia: usa 1 tarjeta por fila en el móvil para mejor lectura.")

st.caption("💡 Consejo: añade este enlace a la pantalla de inicio del teléfono para usarlo como app.")
