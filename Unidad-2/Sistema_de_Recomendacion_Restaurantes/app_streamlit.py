import streamlit as st
import pandas as pd

from src.data.carga import (
    cargar_platos, cargar_ingredientes, cargar_relacion, cargar_inventario, derivar_banderas
)
from src.logica.filtro import filtrar_platos
from src.logica.no_monotono import explicar_cambio
from src.modelo.bn import construir_modelo, inferir_p_recomendable

st.set_page_config(page_title="Recomendador de Menús", layout="wide")
st.title("Recomendador de Menús ")
st.caption("Streamlit + PGMPy (Red Bayesiana) — con razonamiento no monótono")

@st.cache_data
def cargar_dataset():
    platos = cargar_platos()
    ingredientes = cargar_ingredientes()
    rel = cargar_relacion()
    inventario = cargar_inventario()
    platos2 = derivar_banderas(platos, ingredientes, rel, inventario)
    return platos2, ingredientes, rel, inventario

@st.cache_resource
def cargar_modelo():
    model = construir_modelo()
    from pgmpy.inference import VariableElimination
    infer = VariableElimination(model)
    return infer

platos_inicial, ingredientes, rel, inventario_full = cargar_dataset()

# Sidebar: Perfil e Inventario
with st.sidebar:
    st.header("Perfil del cliente")
    dieta = st.selectbox("Dieta", ["omnivora","vegetariana","vegana"], index=0)
    alergia_gluten = st.checkbox("Alergia: Gluten", value=False)
    alergia_lacteos = st.checkbox("Alergia: Lácteos", value=False)
    alergia_nueces = st.checkbox("Alergia: Nueces", value=False)
    gusta_picante = st.checkbox("Le gusta lo picante", value=False)
    gusta_dulce = st.checkbox("Le gusta lo dulce", value=False)
    gusta_marisco = st.checkbox("Le gustan los mariscos", value=False)
    top_k = st.slider("Top-N recomendaciones", 1, 10, 5)

    # simulacion de inventario
    st.header("Inventario (simulación)")
    st.caption("Marca ingredientes NO disponibles (afecta plato_disponible).")

    # IDs de ingredientes como str y normalizados (funciona para merges posteriores)
    ingredientes["id_ingrediente"] = ingredientes["id_ingrediente"].astype(str).str.strip()
    ingr_nombres = dict(zip(ingredientes["id_ingrediente"], ingredientes["nombre"]))
    opciones_ids = list(ingr_nombres.keys())

    # Widget con key estable y rerun inmediato
    st.multiselect(
        "Ingredientes NO disponibles",
        options=opciones_ids,
        format_func=lambda iid: f"{iid} — {ingr_nombres.get(iid, iid)}",
        key="k_ids_no_disp",
        on_change=st.rerun,   # fuerza el rerun al cambiar selección
    )

    # Toggle para aplicar disponibilidad en el filtro
    st.header("Depuración")
    aplicar_disp = st.checkbox("Aplicar disponibilidad (inventario)", value=True)

perfil = {
    "dieta": dieta,
    "alergia_gluten": int(alergia_gluten),
    "alergia_lacteos": int(alergia_lacteos),
    "alergia_nueces": int(alergia_nueces),
    "gusta_picante": int(gusta_picante),
    "gusta_dulce": int(gusta_dulce),
    "gusta_marisco": int(gusta_marisco),
}

# Inventario simulado aplicado
inventario_sim = cargar_inventario().copy()
inventario_sim["id_ingrediente"] = inventario_sim["id_ingrediente"].astype(str).str.strip()

ids_no_disp_sim = [str(x).strip() for x in st.session_state.get("k_ids_no_disp", [])]
if ids_no_disp_sim:
    inventario_sim.loc[
        inventario_sim["id_ingrediente"].isin(ids_no_disp_sim),
        "disponible"
    ] = 0

# Recalcular banderas SIEMPRE desde catálogo base
# (evita estados corruptos por caché)
platos_base = cargar_platos()
platos = derivar_banderas(platos_base, ingredientes, rel, inventario_sim)

# ReCÁLCULO EN TIEMPO REAL de 'plato_disponible' (AND lógico)
# Garantiza que si falta 1 ingrediente, el plato NO esté disponible
disp_rt = (
    cargar_relacion()  # relación fresca N:M
      .merge(inventario_sim, on="id_ingrediente", how="left")
      .assign(disponible=lambda df: pd.to_numeric(df["disponible"], errors="coerce").fillna(0).astype(int))
      .groupby("id_plato")["disponible"].min()   # AND sobre los ingredientes del plato
      .astype(int)
      .reset_index()
      .rename(columns={"disponible": "plato_disponible_rt"})
)

platos = (
    platos.drop(columns=["plato_disponible"], errors="ignore")
          .merge(disp_rt, on="id_plato", how="left")
)
platos["plato_disponible"] = platos["plato_disponible_rt"].fillna(0).astype(int)
platos = platos.drop(columns=["plato_disponible_rt"])

# ReCÁLCULO EN TIEMPO REAL de ALÉRGENOS (gluten/lácteos/nueces)
pi_rt = cargar_relacion().merge(
    ingredientes[["id_ingrediente", "alergenos"]], on="id_ingrediente", how="left"
)

def _to_list(x):
    if pd.isna(x) or str(x).strip() == "":
        return []
    return [s.strip().lower() for s in str(x).split("|")]

pi_rt["alergenos_list_rt"] = pi_rt["alergenos"].apply(_to_list)
pi_rt["has_gluten_rt"]  = pi_rt["alergenos_list_rt"].apply(lambda L: "gluten"  in L)
pi_rt["has_lacteos_rt"] = pi_rt["alergenos_list_rt"].apply(lambda L: "lacteos" in L)
pi_rt["has_nueces_rt"]  = pi_rt["alergenos_list_rt"].apply(lambda L: "nueces"  in L)

aler_rt = pi_rt.groupby("id_plato").agg(
    plato_contiene_gluten=("has_gluten_rt", "max"),
    plato_contiene_lacteos=("has_lacteos_rt", "max"),
    plato_contiene_nueces=("has_nueces_rt", "max"),
).reset_index()

platos = (
    platos.drop(columns=["plato_contiene_gluten","plato_contiene_lacteos","plato_contiene_nueces"], errors="ignore")
          .merge(aler_rt, on="id_plato", how="left")
)

for col in ["plato_contiene_gluten","plato_contiene_lacteos","plato_contiene_nueces"]:
    platos[col] = platos[col].fillna(False).astype(int)

infer = cargar_modelo()

st.subheader("Catálogo (resumen)")
st.dataframe(platos[[
    "id_plato","nombre","tipo_dieta","categoria","picante","dulce","marisco",
    "plato_contiene_gluten","plato_contiene_lacteos","plato_contiene_nueces",
    "plato_disponible"
]])

# Filtro con toggle
elegibles, trazas_out = filtrar_platos(platos, perfil, aplicar_disponibilidad=aplicar_disp)

st.subheader("Platos excluidos (traza)")
if len(trazas_out)==0:
    st.write("No hay exclusiones por reglas duras.")
else:
    for t in trazas_out:
        razones = ", ".join([f"{cat}: {msg}" for cat, msg in t["exclusion"]])
        st.write(f"**{t['id_plato']} {t['nombre']}** → {razones}")

# Auditorías 
with st.expander("🔎 Auditoría de disponibilidad por plato"):
    if not platos.empty:
        sel = st.selectbox("Plato", platos["nombre"].tolist(), key="aud_disp")
        pid = platos.loc[platos["nombre"]==sel, "id_plato"].iloc[0]
        rel_sel = rel[rel["id_plato"]==pid].merge(ingredientes, on="id_ingrediente").merge(
            inventario_sim, on="id_ingrediente", suffixes=("", "_inv"), how="left"
        )[["id_ingrediente","nombre","disponible"]].rename(columns={"nombre":"ingrediente"})
        st.write(rel_sel)
        disp_plato = int((rel_sel["disponible"]==1).all()) if not rel_sel.empty else 0
        st.write("plato_disponible (AND):", disp_plato)

with st.expander("Auditoría de alérgenos por plato"):
    if not platos.empty:
        sel2 = st.selectbox("Plato", platos["nombre"].tolist(), key="aud_alerg")
        pid2 = platos.loc[platos["nombre"]==sel2, "id_plato"].iloc[0]
        rel_al = rel[rel["id_plato"]==pid2].merge(
            ingredientes[["id_ingrediente","nombre","alergenos"]], on="id_ingrediente", how="left"
        )
        rel_al["alergenos_list"] = rel_al["alergenos"].apply(
            lambda x: [] if pd.isna(x) or str(x).strip()=="" else [s.strip() for s in str(x).split("|")]
        )
        st.write(rel_al[["id_ingrediente","nombre","alergenos","alergenos_list"]])
        st.write("plato_contiene_gluten:", int("gluten"  in sum(rel_al["alergenos_list"], [])))
        st.write("plato_contiene_lacteos:", int("lacteos" in sum(rel_al["alergenos_list"], [])))
        st.write("plato_contiene_nueces:", int("nueces"  in sum(rel_al["alergenos_list"], [])))

# Scoring BN

rows = []
for _, p in elegibles.iterrows():
    tipo_plato = str(p.get("tipo_dieta","")).strip().lower()
    if perfil["dieta"] == "vegana":
        comp_dieta = "Si" if tipo_plato == "vegana" else "No"
    elif perfil["dieta"] == "vegetariana":
        comp_dieta = "Si" if tipo_plato in ("vegana","vegetariana") else "No"
    else:
        comp_dieta = "Si"  # Omnívora acepta todos

    evidencia = {
        "GustaPicante": "Si" if perfil["gusta_picante"]==1 else "No",
        "RasgoPicante": "Si" if int(p["picante"])==1 else "No",
        "GustaDulce": "Si" if perfil["gusta_dulce"]==1 else "No",
        "RasgoDulce": "Si" if int(p["dulce"])==1 else "No",
        "GustaMarisco": "Si" if perfil["gusta_marisco"]==1 else "No",
        "RasgoMarisco": "Si" if int(p["marisco"])==1 else "No",
        "PlatoCompatibleDieta": comp_dieta,
        "PlatoSeguroAlergenos": "Si" if not (
            (perfil["alergia_gluten"]==1 and p["plato_contiene_gluten"]==1) or
            (perfil["alergia_lacteos"]==1 and p["plato_contiene_lacteos"]==1) or
            (perfil["alergia_nueces"]==1 and p["plato_contiene_nueces"]==1)
        ) else "No",
        "PlatoDisponible": "Si" if int(p["plato_disponible"])==1 else "No",
    }
    p_rec = inferir_p_recomendable(infer, evidencia)

    # si la dieta es omnivora ajusta platos omnivoros al usuario
    bonus = 0.0
    if perfil["dieta"] == "omnivora" and tipo_plato == "omnivora":
        bonus = 0.02  # puedes ajustar 0.01–0.05

    rows.append({
        "id_plato": p["id_plato"],
        "nombre": p["nombre"],
        "tipo_dieta": tipo_plato,
        "p_Recomendable_Si": round(p_rec + bonus, 3)
        
    })

df_scores = pd.DataFrame(rows)

st.subheader("Recomendaciones")
if df_scores.empty:
    st.warning("No hay platos elegibles con el perfil actual.")
    new_top_ids = []
else:
    df_scores = df_scores.sort_values("p_Recomendable_Si", ascending=False)
    df_top = df_scores.head(top_k)
    st.dataframe(df_top[["id_plato","nombre","p_Recomendable_Si"]])
    new_top_ids = df_top["id_plato"].tolist()

prev_top_ids = st.session_state.get("prev_top_ids", [])
if prev_top_ids:
    dif = explicar_cambio(prev_top_ids, new_top_ids)
    if dif["salieron"] or dif["entraron"]:
        st.info(f"🔄 Cambio en Top-{top_k} — Entraron: {dif['entraron']} | Salieron: {dif['salieron']}")
st.session_state["prev_top_ids"] = new_top_ids

st.caption("Compatibilidad de dieta, alérgenos y disponibilidad se usan como evidencias deterministas dentro de la Red Bayesiana. Cambios en inventario o perfil pueden retraer recomendaciones (razonamiento no monótono).")

