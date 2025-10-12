def explicar_cambio(prev_top_ids, new_top_ids):
    prev = set(prev_top_ids or [])
    new = set(new_top_ids or [])
    salieron = list(prev - new)
    entraron = list(new - prev)
    return {"salieron": salieron, "entraron": entraron}
