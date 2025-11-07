# logica, datos y funcion de diagnostico del sistema experto

# enfermedades que puede presentar el pasiente 
enfermedades = {
    "Asma": {
        "sintomas": [
            "sibilancias", "tos_noche", "antecedentes_alergia",
            "opresion_pecho", "silbido_respirar", "mejora_broncodilatadores" ]
    },
    "Neumonía": {
        "sintomas": [ 
            "fiebre_alta", "tos_con_flemas", "dificultad_respirar",
            "crepitantes", "dolor_toracico", "escalofrios" ] 
    },
    "Bronquitis Aguda": {
        "sintomas": [
            "tos", "infeccion_respiratoria_previa", "duracion_menor_3_semanas",
            "sin_consolidacion_rx", "irritacion_garganta", "tos_persistente"  ]
    },
    "COVID-19": {
        "sintomas": [
            "fiebre", "tos_seca", "fatiga", "dificultad_respirar",
            "perdida_olfato_gusto", "dolor_cabeza", "dolor_muscular"]
    },
    "Gripe (Influenza)": {
        "sintomas": [
            "fiebre", "dolor_muscular", "fatiga", "tos_seca", "congestion_nasal", "escalofrios"]
    },
    "Resfriado Común": {
        "sintomas": ["tos", "congestion_nasal", "dolor_garganta", "estornudos" ]
    }
}

def diagnosticar(paciente):
    resultados = {}
    for enfermedad, datos in enfermedades.items():
        sintomas = datos["sintomas"]
        coincidencias = sum(1 for s in sintomas if paciente.get(s, False))
        porcentaje = int((coincidencias / len(sintomas)) * 100)
        resultados[enfermedad] = porcentaje
    return resultados

def mejor_diagnostico(diagnosticos):
    #Devuelve (nombre_enfermedad, porcentaje).
    if not diagnosticos:
        return None, 0
    mejor = max(diagnosticos, key=diagnosticos.get)
    return mejor, diagnosticos[mejor]

# --- explicación del porqué ---
def explicar_todos(paciente):
    """
    Devuelve:
      { enfermedad: {"coincidentes": [...], "faltantes": [...]} }
    basado en los síntomas definidos por cada enfermedad.
    """
    explic = {}
    for enfermedad, datos in enfermedades.items():
        lista = datos["sintomas"]
        coinc = [s for s in lista if paciente.get(s, False)]
        falt  = [s for s in lista if not paciente.get(s, False)]
        explic[enfermedad] = {"coincidentes": coinc, "faltantes": falt}
    return explic