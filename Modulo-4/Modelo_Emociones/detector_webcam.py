import cv2
from Modelo_emociones import ModeloDeEmociones 
from detector_de_rostro import DetectorDeRostro

ruta_del_modelo= "emotion-ferplus-8.onnx"
ruta_del_haar_cascade = "haarcascade_frontalface_default.xml"

def main():
    modelo_de_emociones = ModeloDeEmociones(ruta_del_modelo)
    detector_de_rostros= DetectorDeRostro(ruta_del_haar_cascade)

    #inicializar opencv para la webcam

    #utilizo la uno porque la camara de la laptop no sirve
    #y uso una webcam externa
    camara= cv2.VideoCapture(1, cv2.CAP_DSHOW)

    #si la camara no abre, marcar error
    if camara.isOpened() is False:
        print("Error al iniciar la cámara")
        return
    
    print("se inicio la camara, presiona 's' para salir")

    while True:
        resultado, video_de_camara= camara.read()
        if resultado is False:
            print("No se pudo activar la camara")
            break

        coordenadas_de_el_rostro=detector_de_rostros.detector_de_cara(video_de_camara)
        texto_a_mostrar_pantalla= "sin rostro" # si no detecta una cara

        if coordenadas_de_el_rostro is not None:
            x, y, w, h= coordenadas_de_el_rostro

            #dibujar un rectangulo alrededor del rostro
            cv2.rectangle(
                video_de_camara,
                (x,y),
                (x+w, y+h),
                (0,255,0),
                2
            )

            
            rostro_extraido= video_de_camara[y:y+h, x:x+w]

            try:
                emocion, confianza = modelo_de_emociones.Reconocimiento_de_emocion(rostro_extraido)
                texto_a_mostrar_pantalla = f"{emocion} - {round(confianza, 1)}%"
            except Exception as e:
                texto_a_mostrar_pantalla = "error en predicción"

            
            cv2.putText(
            video_de_camara,
            texto_a_mostrar_pantalla,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2
        )
            

        cv2.imshow("Detector de emociones", video_de_camara)
          
        if cv2.waitKey(1) & 0xFF == ord('s'):
                break

    camara.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()