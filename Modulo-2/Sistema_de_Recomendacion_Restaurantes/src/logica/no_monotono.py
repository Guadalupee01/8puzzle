
# PREV_TOP_ID= ID DE LOS PLATOS QUE ESTABAN EN EL TOP N ANTERIOR
# NEW_TOP = ID DE LOS PLATOS QUE ESTAN EN EL TOP ACTUAL
def explicar_cambio(prev_top_ids, new_top_ids):
    prev = set(prev_top_ids or []) # CONVIERTE LISTAS EN CONJUNTOS SET PARA PODER USAR OPERACIONES DE DIFERENCIA
    new = set(new_top_ids or []) # EL OR GARANTIZA QUE SI ALGUNA LISTA VIENE COMO NONE, SU USE UNA LISTA VACIA EN SU LUGAR
    salieron = list(prev - new) #DEVUELVE ELEMENTOS QUE ESTABAN ANTES PERO NO AHORA
    entraron = list(new - prev) # DEVUELVE ELEMENTOS QUE NO ESTABAN ANTES PERO AHORA SI
    return {"salieron": salieron, "entraron": entraron}
