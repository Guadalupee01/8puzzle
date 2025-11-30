import cv2

def main():
    print("Iniciando webcam solo con OpenCV...")

    # uso la camara 1 porque la camara de mi laptop no sirve
    camara = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    
    if camara.isOpened() is False:
        print("Error al iniciar la cámara.")
        return

    print("Presiona 's' para salir de la pantalla.")

    # bucle que lee los frames que hay en la camara
    while True:
        resultado, video_de_camara = camara.read()

        if resultado is False:
            print("No se pudo obtener el frame de la cámara.")
            break

        # mostrar el video de la webcam en la pantalla
        cv2.imshow("Prueba webcam OpenCV", video_de_camara)

        # asignacion de boton para salir
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break

    # liberar la camara y cerrar todas las ventanas
    camara.release()
    cv2.destroyAllWindows()
    print("Programa terminado.")

if __name__ == "__main__":
    main()
