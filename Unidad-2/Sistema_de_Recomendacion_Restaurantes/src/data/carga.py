import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

def cargar_platos():
    return pd.read_csv(DATA_DIR / "platos.csv")

def cargar_ingredientes():
    df = pd.read_csv(DATA_DIR / "ingredientes.csv")
    def to_list(x):
        if pd.isna(x) or str(x).strip() == "":
            return []
        return [s.strip() for s in str(x).split("|")]
    df["alergenos_list"] = df["alergenos"].apply(to_list)
    return df

def cargar_relacion():
    return pd.read_csv(DATA_DIR / "plato_ingrediente.csv")

def cargar_inventario():
    return pd.read_csv(DATA_DIR / "inventario.csv")

def derivar_banderas(platos, ingredientes, rel, inventario):
    for df in (platos, ingredientes, rel, inventario):
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.strip()

    drop_cols = [c for c in platos.columns if c.startswith("plato_")]
    platos = platos.drop(columns=drop_cols, errors="ignore").copy()

    pi = rel.merge(ingredientes, on="id_ingrediente", how="left")
    pi = pi.merge(inventario, on="id_ingrediente", suffixes=("", "_inv"), how="left")

    def to_list(x):
        if pd.isna(x) or str(x).strip() == "":
            return []
        return [s.strip() for s in str(x).split("|")]
    if "alergenos_list" not in pi.columns:
        pi["alergenos_list"] = pi.get("alergenos", "").apply(to_list)
    else:
        pi["alergenos_list"] = pi["alergenos_list"].apply(lambda x: x if isinstance(x, list) else to_list(x))

    pi["has_gluten"]  = pi["alergenos_list"].apply(lambda L: "gluten"  in L if isinstance(L, list) else False)
    pi["has_lacteos"] = pi["alergenos_list"].apply(lambda L: "lacteos" in L if isinstance(L, list) else False)
    pi["has_nueces"]  = pi["alergenos_list"].apply(lambda L: "nueces"  in L if isinstance(L, list) else False)
    for col in ["es_origen_animal", "es_marisco", "disponible"]:
        pi[col] = pd.to_numeric(pi.get(col, 0), errors="coerce").fillna(0).astype(int).astype(bool)

    if pi.empty:
        band = pd.DataFrame(columns=[
            "id_plato",
            "plato_contiene_gluten","plato_contiene_lacteos","plato_contiene_nueces",
            "plato_origen_animal","plato_es_marisco","plato_disponible"
        ])
    else:
        band = pi.groupby("id_plato").agg(
            plato_contiene_gluten = ("has_gluten", "max"),
            plato_contiene_lacteos = ("has_lacteos", "max"),
            plato_contiene_nueces = ("has_nueces", "max"),
            plato_origen_animal   = ("es_origen_animal", "max"),
            plato_es_marisco      = ("es_marisco", "max"),
            plato_disponible      = ("disponible", "min"),
        ).reset_index()

    needed = [
        "plato_contiene_gluten","plato_contiene_lacteos","plato_contiene_nueces",
        "plato_origen_animal","plato_es_marisco","plato_disponible"
    ]
    for col in needed:
        if col not in band.columns:
            band[col] = False

    platos2 = platos.merge(band, on="id_plato", how="left")
    for col in needed:
        if col not in platos2.columns:
            platos2[col] = 0
        else:
            platos2[col] = platos2[col].fillna(False).astype(int)

    for c in ["picante","dulce","marisco"]:
        if c in platos2.columns:
            platos2[c] = pd.to_numeric(platos2[c], errors="coerce").fillna(0).astype(int)

    return platos2
