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

        # .reshape Cambia la forma del arreglo, el modelo espera (1, 1, 64, 64)
        # 1: numero de imagenes (batch size)
        # 2: numero de canales (1 canal para escala de grises)
        # 3: altura de la imagen
        # 4: ancho de la imagen
        entrada_para_el_modelo= rostro_tamaño_64x64.astype("float32").reshape(1,1,64,64)

        return entrada_para_el_modelo
    
    def Reconocimiento_de_emocion(modelo, entreda_opencv):
        entrada = modelo.conversion_de_rostros_compatibles_con_modelo(entreda_opencv)

        # obtencion de las puntuaciones
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


ruta_del_modelo = "emotion-ferplus-8.onnx"
ruta_de_imagen = "foto_sonriendo.jpg"

def main():
    print("Cargando modelo FER+ desde:", ruta_del_modelo)
    modelo_de_emociones = ModeloDeEmociones(ruta_del_modelo)
    print("Modelo cargado.\n")

    # cargar la imagen con OpenCV
    imagen_OpenCV = cv2.imread(ruta_de_imagen)
    if imagen_OpenCV is None:
        print("Error: no se pudo leer la imagen, revisa la ruta:", ruta_de_imagen)
        return
    

    # aqui no detectare la cara, voy mando toda la imagen como si fuera el rostro
    emocion_resultante, nivel_de_confianza_o_certeza = modelo_de_emociones.Reconocimiento_de_emocion(imagen_OpenCV)

    print("Emoción resultante:", emocion_resultante)
    print("Nivel de confianza:", round(nivel_de_confianza_o_certeza, 2), "%")

    
    entrada_para_el_modelo = modelo_de_emociones.conversion_de_rostros_compatibles_con_modelo(imagen_OpenCV)

    puntuaciones_de_emociones = modelo_de_emociones.modelo_de_emociones.run(
        [modelo_de_emociones.output_name],
        {modelo_de_emociones.input_name: entrada_para_el_modelo}
    )[0]

    probabilidad_para_la_emocion = Resultados(puntuaciones_de_emociones)[0]

    print("\nResultados del modelo (todas las emociones):")
    for i in range(len(probabilidad_para_la_emocion)):
        print(
            Emociones[i],
            ":",
            round(probabilidad_para_la_emocion[i] * 100, 2),
            "%"
        )

    # texto que se va agregar a la imagen.
    texto_emocion = f"{emocion_resultante} ({round(nivel_de_confianza_o_certeza, 1)}%)"

    cv2.putText(
        imagen_OpenCV,
        texto_emocion,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 0),
        2
    )

    cv2.imshow("Prueba del modelo con una foto", imagen_OpenCV)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
