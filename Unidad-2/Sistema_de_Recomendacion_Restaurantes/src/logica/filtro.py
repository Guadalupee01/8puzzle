import pandas as pd

PRIORIDADES = ["seguridad", "dieta", "disponibilidad", "preferencias"]

def filtrar_platos(platos, perfil, aplicar_disponibilidad=True):
    trazas = []
    elegibles = []
    for _, p in platos.iterrows():
        razones_out = []

        if perfil.get("alergia_gluten",0)==1 and int(p.get("plato_contiene_gluten",0))==1:
            razones_out.append(("seguridad","Contiene gluten"))
        if perfil.get("alergia_lacteos",0)==1 and int(p.get("plato_contiene_lacteos",0))==1:
            razones_out.append(("seguridad","Contiene lácteos"))
        if perfil.get("alergia_nueces",0)==1 and int(p.get("plato_contiene_nueces",0))==1:
            razones_out.append(("seguridad","Contiene nueces"))

        dieta = str(perfil.get("dieta","omnivora")).strip().lower()
        tipo = str(p.get("tipo_dieta","")).strip().lower()
        if dieta == "vegana":
            if tipo != "vegana":
                razones_out.append(("dieta","No compatible con dieta vegana (etiqueta del plato)"))
        elif dieta == "vegetariana":
            if tipo not in ("vegana","vegetariana"):
                razones_out.append(("dieta","No compatible con dieta vegetariana (etiqueta del plato)"))

        if aplicar_disponibilidad and int(p.get("plato_disponible",0)) != 1:
            razones_out.append(("disponibilidad","Ingrediente(s) no disponible(s)"))

        if len(razones_out)==0:
            elegibles.append(p.to_dict())
        else:
            razones_out.sort(key=lambda x: PRIORIDADES.index(x[0]))
            trazas.append({"id_plato": p.get("id_plato","?"), "nombre": p.get("nombre","?"), "exclusion": razones_out})

    df_elegibles = pd.DataFrame(elegibles)
    return df_elegibles, trazas
