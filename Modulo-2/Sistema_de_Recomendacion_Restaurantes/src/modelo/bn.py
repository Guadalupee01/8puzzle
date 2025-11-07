from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

ALTA, MEDIA, BAJA = "Alta","Media","Baja"
SI, NO = "Si","No"

def _cpd_afinidad(var_af, var_gusta, var_rasgo):
    return TabularCPD(
        variable=var_af, #NOMBRE DEL NODO HIJO, POR EJEMPLO AFINIDAD TOTAL
        variable_card=3, # 3 ESTADOS= ALTA, MEDIA, BAJA
        values=[
            [0.75, 0.20, 0.05, 0.15], #AFINIDAD TOTAL
            [0.20, 0.60, 0.25, 0.60], #AFINIDAD MEDIA
            [0.05, 0.20, 0.70, 0.25], #AFINIDAD BAJA
        ],
        evidence=[var_gusta, var_rasgo],
        evidence_card=[2,2],
        #FIJA EL ORDEN DE ESTADOS PARA CADA VARIABLE
        state_names={
            var_af: [ALTA, MEDIA, BAJA],
            var_gusta: [SI, NO],
            var_rasgo: [SI, NO],
        }
    )

def _cpd_afinidad_total():
    states = [ALTA, MEDIA, BAJA]
    cols = []
    for a in states:
        for b in states:
            for c in states:
                pts = (2 if a==ALTA else 1 if a==MEDIA else 0)                     + (2 if b==ALTA else 1 if b==MEDIA else 0)                     + (2 if c==ALTA else 1 if c==MEDIA else 0)
                if pts >= 4: #ALTA 
                    cols.append([0.70, 0.25, 0.05])
                elif pts >= 2: #MEDIA
                    cols.append([0.20, 0.70, 0.10])
                else: #BAJA
                    cols.append([0.05, 0.20, 0.75])
    table_T = list(zip(*cols))
    return TabularCPD(
        variable="AfinidadTotal", variable_card=3,
        values=table_T,
        evidence=["AfinidadPicante","AfinidadDulce","AfinidadMarisco"],
        evidence_card=[3,3,3],
        state_names={
            "AfinidadTotal": [ALTA, MEDIA, BAJA],
            "AfinidadPicante": [ALTA, MEDIA, BAJA],
            "AfinidadDulce": [ALTA, MEDIA, BAJA],
            "AfinidadMarisco": [ALTA, MEDIA, BAJA],
        }
    )

#para nodos que se fijan por evidencia SI/NO
def _cpd_dummy_binaria(var):
    return TabularCPD(var, 2, [[0.5],[0.5]], state_names={var:[SI,NO]})

#CPD RECOMENDABLE
# TRABAJA CON, PLATOCOMPATIBLEDIETA, PLATOSEGUROALERGENOS, PLATODISPONIBLE, AFINIDAD TOTAL
# H: RECOMENDABLE (SI/NO)
#LOGICA= VETO SI CUALQUIER CONDICION=(DIETA/ALERGENOS/DISPONIBILIDAD) ES NO
#SI LOS TRES SON SI LA AFINIDAD LA AFINIDAD TOTAL ESCALA LA POSIBILIDAD DE SI
def _cpd_recomendable():
    cols = []
    #RECORRE LAS COMBINACIONES DE (CD, SA, DISP, AF) EN EL ORDEN DECLARADO COMO EVIDENCIA
    for cd in [SI, NO]:
      for sa in [SI, NO]:
        for disp in [SI, NO]:
          for af in [ALTA, MEDIA, BAJA]:
            if cd==SI and sa==SI and disp==SI:
                #NINGUN VETO ACTIVO: USA AFINIDADTOTAL COMO POTENCIA DE RECOMENDACION
                if af==ALTA: cols.append([0.85, 0.15])
                elif af==MEDIA: cols.append([0.60, 0.40])
                else: cols.append([0.20, 0.80])
            else:
                #CUALQUIER NO EN PUERTAS, NO SE RECOMIENDA
                cols.append([0.00, 1.00])
    table_T = list(zip(*cols))
    return TabularCPD(
        "Recomendable", 2,
        table_T,
        evidence=["PlatoCompatibleDieta","PlatoSeguroAlergenos","PlatoDisponible","AfinidadTotal"],
        evidence_card=[2,2,2,3],
        state_names={
            "Recomendable":[SI,NO],
            "PlatoCompatibleDieta":[SI,NO],
            "PlatoSeguroAlergenos":[SI,NO],
            "PlatoDisponible":[SI,NO],
            "AfinidadTotal":[ALTA,MEDIA,BAJA]
        }
    )

def construir_modelo():
    model = DiscreteBayesianNetwork([
        #GUSTOS + RASGOS = AFINIDAD POR RASGO
        ("GustaPicante","AfinidadPicante"),("RasgoPicante","AfinidadPicante"),
        ("GustaDulce","AfinidadDulce"),("RasgoDulce","AfinidadDulce"),
        ("GustaMarisco","AfinidadMarisco"),("RasgoMarisco","AfinidadMarisco"),
        #AFINIDADES POR RASGO= AFINIDAD TOTAL
        ("AfinidadPicante","AfinidadTotal"),
        ("AfinidadDulce","AfinidadTotal"),
        ("AfinidadMarisco","AfinidadTotal"),
        
        #PUERTAS + AFINIDAD TOTAL= RECOMENDALE
        ("PlatoCompatibleDieta","Recomendable"),
        ("PlatoSeguroAlergenos","Recomendable"),
        ("PlatoDisponible","Recomendable"),
        ("AfinidadTotal","Recomendable"),
    ])

#CPD UNIFORMES PARA NODOS DE ENTRADA (SE SOBRE ESCRIBEN CON LA EVIDENCIA EN LA CONSULTA)
    cpd_gusta_pic = TabularCPD("GustaPicante", 2, [[0.5],[0.5]], state_names={"GustaPicante":[SI,NO]})
    cpd_rasgo_pic = TabularCPD("RasgoPicante", 2, [[0.5],[0.5]], state_names={"RasgoPicante":[SI,NO]})
    cpd_gusta_dul = TabularCPD("GustaDulce", 2, [[0.5],[0.5]], state_names={"GustaDulce":[SI,NO]})
    cpd_rasgo_dul = TabularCPD("RasgoDulce", 2, [[0.5],[0.5]], state_names={"RasgoDulce":[SI,NO]})
    cpd_gusta_mar = TabularCPD("GustaMarisco", 2, [[0.5],[0.5]], state_names={"GustaMarisco":[SI,NO]})
    cpd_rasgo_mar = TabularCPD("RasgoMarisco", 2, [[0.5],[0.5]], state_names={"RasgoMarisco":[SI,NO]})

#AFINIDADES POR RASGO
    cpd_af_pic = _cpd_afinidad("AfinidadPicante","GustaPicante","RasgoPicante")
    cpd_af_dul = _cpd_afinidad("AfinidadDulce","GustaDulce","RasgoDulce")
    cpd_af_mar = _cpd_afinidad("AfinidadMarisco","GustaMarisco","RasgoMarisco")
    
    #AFINIDAD TOTAL(AGREGA 3 AFINIDADES)
    cpd_af_total = _cpd_afinidad_total()

    cpd_cd = _cpd_dummy_binaria("PlatoCompatibleDieta")
    cpd_sa = _cpd_dummy_binaria("PlatoSeguroAlergenos")
    cpd_disp = _cpd_dummy_binaria("PlatoDisponible")
    cpd_rec = _cpd_recomendable()


#REGISTRA TODAS LAS CPD EN EL MODELO
    model.add_cpds(cpd_gusta_pic, cpd_rasgo_pic, cpd_gusta_dul, cpd_rasgo_dul,
                   cpd_gusta_mar, cpd_rasgo_mar, cpd_af_pic, cpd_af_dul, cpd_af_mar,
                   cpd_af_total, cpd_cd, cpd_sa, cpd_disp, cpd_rec)

    model.check_model()
    return model

def inferir_p_recomendable(infer, evidencia):
    q = infer.query(["Recomendable"], evidence=evidencia, show_progress=False)
    return float(q.values[0])
