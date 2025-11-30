import onnxruntime as ort
import numpy as np
import cv2

# listo las emociones en el orden que usa el modelo FER+
Emociones = [
    "neutral",  
    "Feliz",    
    "Sorpresa", 
    "Triste",   
    "Enojo",    
    "Asco",     
    "Miedo",    
    "Desprecio" 
]


class ModeloDeEmociones:
    def __init__(rostro, ruta_del_modelo: str):
        rostro.modelo_de_emociones= ort.InferenceSession(
            ruta_del_modelo,
            providers=["CPUExecutionProvider"]
        )
        rostro.input_name= rostro.modelo_de_emociones.get_inputs()[0].name
        rostro.output_name= rostro.modelo_de_emociones.get_outputs()[0].name

        
    def conversion_de_rostros_compatibles_con_modelo(modelo, rostro_OpenCV_extraido):
        # conversion de la imagen a escala de grises compatible con el modelo
        rostro_en_escala_de_grises= cv2.cvtColor(rostro_OpenCV_extraido, cv2.COLOR_BGR2GRAY)
    
        # cambiando el tamaño de la imagen a 64x64 pixeles, que es como lo pide el modelo
        rostro_tamaño_64x64= cv2.resize(rostro_en_escala_de_grises, (64,64))

        # .reshape Cambia la forma del arreglo, el modelo espera (1, 1, 64, 64), como lo indique en la documentacion
        entrada_para_el_modelo= rostro_tamaño_64x64.astype("float32").reshape(1,1,64,64)

        return entrada_para_el_modelo
    
    def Reconocimiento_de_emocion(modelo, entreda_opencv):
        entrada = modelo.conversion_de_rostros_compatibles_con_modelo(entreda_opencv)

        # ejecucion del modelo, obtencion de las puntuaciones
        puntuaciones_de_emociones= modelo.modelo_de_emociones.run(
            [modelo.output_name],
            {modelo.input_name: entrada}
        )[0]

        probabilidad_para_la_emocion= Resultados(puntuaciones_de_emociones)[0]

        indice_mas_alto_probable= int(np.argmax(probabilidad_para_la_emocion))

        emocion_resultante= Emociones[indice_mas_alto_probable]

        nivel_de_confianza_o_certeza= float(probabilidad_para_la_emocion[indice_mas_alto_probable]*100)

        return emocion_resultante, nivel_de_confianza_o_certeza
    
    

def Resultados(puntuaciones: np.ndarray) -> np.ndarray:
    # calculo las probabilidades que el modelo asigna a cada emocion
    
    
    porcentaje = np.exp(puntuaciones - np.max(puntuaciones))
    probabilidades= porcentaje / np.sum(porcentaje)
    return probabilidades







