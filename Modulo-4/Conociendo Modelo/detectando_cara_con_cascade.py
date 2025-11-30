import cv2

ruta_del_haar_cascade = "haarcascade_frontalface_default.xml"

def main():
    haarcascade = cv2.CascadeClassifier(ruta_del_haar_cascade)

    camara = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    # si la camara no abre, marcar error
    if camara.isOpened() is False:
        print("Error al iniciar la cámara")
        return
    
    print("se inicio la camara, presiona 's' para salir")

    while True:
        resultado, video_de_camara = camara.read()
        if resultado is False:
            print("No se pudo activar la camara")
            break

        # valor por defecto si no hay rostro
        texto_a_mostrar_pantalla = "sin rostro"

        # convertir a escala de grises
        video_a_escala_de_grises = cv2.cvtColor(video_de_camara, cv2.COLOR_BGR2GRAY)

        # detectar rostro
        coordenadas_de_el_rostro = haarcascade.detectMultiScale(
            video_a_escala_de_grises,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(60, 60)
        )




        # le digo que si detecta al menos un rostro
        if len(coordenadas_de_el_rostro) > 0:
            x, y, w, h = coordenadas_de_el_rostro[0]

            # dibujar rectángulo alrededor del rostro
            cv2.rectangle(
                video_de_camara,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            texto_a_mostrar_pantalla = "rostro detectado"

        # escribir texto arriba
        cv2.putText(
            video_de_camara,
            texto_a_mostrar_pantalla,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2
        )

        cv2.imshow("Prueba", video_de_camara)
          
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break

    camara.release()
    cv2.destroyAllWindows()
    print("Programa terminado.")

if __name__ == "__main__":
    main()

