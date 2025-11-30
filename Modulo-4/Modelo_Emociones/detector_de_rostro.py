import cv2

class DetectorDeRostro:
    def __init__(rostro, ruta_de_cascade: str):
        # cargar el face cascade de opencv
        rostro.haarcascade= cv2.CascadeClassifier(ruta_de_cascade)


    def detector_de_cara(rostro, imagen_OpenCV):
        # se convierte la imagen a la escala de grises, que pide el modelo
        imagen_convertida_a_gris= cv2.cvtColor(imagen_OpenCV, cv2.COLOR_BGR2GRAY)

        # detectar rostros en la imagen
        coordenadas_de_el_rostro= rostro.haarcascade.detectMultiScale(
            imagen_convertida_a_gris,
            scaleFactor=1.3, # escala para el tamaño del rostro
            minNeighbors=5, # control de detecciones para aceptar cara
            minSize=(60,60) # tamaño mínimo de el rostro
        )

        if len(coordenadas_de_el_rostro) == 0:
            return None
        

        # retornar las coordenadas del primer rostro detectado
        # tomo el 0 índice porque solo me interesa el primer rostro
        # y luego separo las coordenadas en x, y, w, h para poder usarlas
        coordenadas_de_el_rostro= coordenadas_de_el_rostro[0]
        x = coordenadas_de_el_rostro[0]
        y = coordenadas_de_el_rostro[1]
        w = coordenadas_de_el_rostro[2]
        h = coordenadas_de_el_rostro[3]
        return (x, y, w, h)