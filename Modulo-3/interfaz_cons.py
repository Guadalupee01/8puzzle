from informacion import diagnosticar, explicar_todos

#validacion de preguntas, para evitar que el usuario se equivoque al escibirlas por si acaso cree este metodo para hacerlo de una manera mas acxesible 
def pedir_booleano(pregunta):

    while True:
        respuesta = input(f"{pregunta} (s/n): ").lower()
        if respuesta == "s":
            return True
        elif respuesta == "n":
            return False
        else:
            print("Entrada inválida. Por favor, responda con 's' para Sí o 'n' para No.")

def pedir_tipo_tos():

    while True:
        tipo_tos = input("¿Tos seca o con flemas?: ").lower()
        if tipo_tos in ["seca", "con flemas"]:
            return tipo_tos
        else:
            print("Entrada inválida. Por favor, ingrese 'seca' o 'con flemas'.")

def pedir_datos_paciente():
    paciente = {}
    paciente["nombre"] = input("Nombre del paciente: ")
    
    # Validar sexo
    while True:
        sexo = input("Sexo (M/F): ").upper()
        if sexo in ["M", "F"]:
            paciente["sexo"] = sexo
            break
        else:
            print("Por favor, ingrese M o F.")

    #convertimos el string a int
    paciente["edad"] = int(input("Edad: "))

    print("\nResponda con 's' para Sí o 'n' para No:\n")

    # Síntomas comunes
    paciente["tos"] = pedir_booleano("¿Tiene tos?")
    
    if paciente["tos"]:
        # Se llama a la función de validación del tipo de tos
        tipo_tos = pedir_tipo_tos() 
        
        # Se usan los strings validados para asignar los booleanos
        paciente["tos_seca"] = tipo_tos == "seca"
        paciente["tos_con_flemas"] = tipo_tos == "con flemas"
        
        paciente["tos_noche"] = pedir_booleano("¿Tose más por la noche o con ejercicio?")
        paciente["tos_persistente"] = pedir_booleano("¿La tos ha durado más de una semana?")
    else:
        # Se asigna False a todas las variables de tos si el paciente no tiene tos
        paciente["tos_seca"] = paciente["tos_con_flemas"] = paciente["tos_noche"] = paciente["tos_persistente"] = False

    paciente["fiebre"] = pedir_booleano("¿Tiene fiebre?")
    
    if paciente["fiebre"]:
        paciente["fiebre_alta"] = pedir_booleano("¿La fiebre es mayor a 38.5°C?")
    else:
        paciente["fiebre_alta"] = False 

    # El resto de las preguntas usan pedir_booleano
    paciente["fatiga"] = pedir_booleano("¿Siente fatiga o cansancio?")
    paciente["dificultad_respirar"] = pedir_booleano("¿Tiene dificultad para respirar?")
    paciente["sibilancias"] = pedir_booleano("¿Tiene silbidos al respirar (sibilancias)?")
    paciente["antecedentes_alergia"] = pedir_booleano("¿Tiene antecedentes de alergias o asma?")
    paciente["opresion_pecho"] = pedir_booleano("¿Siente opresión en el pecho?")
    paciente["silbido_respirar"] = pedir_booleano("¿Escucha silbidos al respirar?")
    paciente["mejora_broncodilatadores"] = pedir_booleano("¿Mejora con broncodilatadores?")
    paciente["crepitantes"] = pedir_booleano("¿Escucha crepitaciones al respirar?")
    paciente["dolor_toracico"] = pedir_booleano("¿Tiene dolor torácico al respirar?")
    paciente["escalofrios"] = pedir_booleano("¿Tiene escalofríos?")
    paciente["infeccion_respiratoria_previa"] = pedir_booleano("¿Tuvo una infección respiratoria reciente?")
    paciente["duracion_menor_3_semanas"] = pedir_booleano("¿Los síntomas han durado menos de 21 días?")
    
    radiografia_previa = pedir_booleano("¿Se ha hecho una radiografía de tórax antes de esta consulta?")
    if radiografia_previa:
        paciente["sin_consolidacion_rx"] = pedir_booleano("¿La radiografía no muestra consolidación pulmonar?")
    else:
        paciente["sin_consolidacion_rx"] = False 
        
    paciente["irritacion_garganta"] = pedir_booleano("¿Tiene irritación de garganta?")
    paciente["perdida_olfato_gusto"] = pedir_booleano("¿Ha perdido el olfato o el gusto?")
    paciente["dolor_cabeza"] = pedir_booleano("¿Tiene dolor de cabeza?")
    paciente["dolor_muscular"] = pedir_booleano("¿Tiene dolor muscular?")
    paciente["congestion_nasal"] = pedir_booleano("¿Tiene congestión nasal?")
    paciente["estornudos"] = pedir_booleano("¿Tiene estornudos frecuentes?")
    paciente["dolor_garganta"] = pedir_booleano("¿Tiene dolor de garganta?")

    return paciente

def mostrar_resultados(paciente, diagnosticos):
    print("\n--- Resultados del Diagnóstico ---")
    print(f"Paciente: {paciente['nombre']} ({paciente['edad']} años, {paciente['sexo']})\n")
    for enfermedad, certeza in diagnosticos.items():
        print(f"- {enfermedad}: certeza {certeza}%")
    mejor = max(diagnosticos, key=diagnosticos.get)
    print(f"\nDiagnóstico más probable: {mejor} ({diagnosticos[mejor]}%)")

    # --- explicación del porqué ---
    explicaciones = explicar_todos(paciente)
    exp = explicaciones.get(mejor, {"coincidentes": [], "faltantes": []})
    coinc = exp["coincidentes"]
    falt = exp["faltantes"]

    print("\n--- Explicación del porqué ---")
    print(f"Reglas activadas, síntomas presentes relevantes para {mejor} fueron las siguientes: "
          f"{', '.join(coinc) if coinc else '—'}")
    print(f"y los Síntomas faltantes esperados para {mejor} fueron los siguientes: "
          f"{', '.join(falt) if falt else '—'}")

def main():
    paciente = pedir_datos_paciente()
    diagnosticos = diagnosticar(paciente)
    mostrar_resultados(paciente, diagnosticos)


main()