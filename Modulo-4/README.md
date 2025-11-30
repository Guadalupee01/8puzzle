# Proyecto Modulo IV: Aplicacion de Deteccion Facial

## Introduccion

El objetivo de este proyecto es que el sistema o aplicacion detecte las siguientes emociones: Felicidad, Tristeza, Enojo y Neutro.

Para ello se Utilizo un Modelo Preentrenado de deteccion de emociones el cual fue:
Emotion-ferplus-8.onnx

y tambien se utilizo.
Haarcascade como detector de rostro.

# Carpetas

Conociendo Modelo
aqui esta el codigo con el cual se estuvo probando el funionamiento de el modelo, utilizando una imagen, y utilizando Haarcascade para deteccion de rostros.

Conociendo OpenCV
aqui esta el codigo con el cual se estuvo viendo el funcinamiento de pues nuestras camaras en la computadora

Modelo_Emociones
aqui es donde esta el funcionamiento de nuestro proyecto, se divide en 3 clases las cuales son las siguientes:
1.- detector_de_rostro.py
2.- detector_de_webcam.py
3.- Modelo_emociones.py

# Documentacion
Tambien esta la documentacion de nuestro proyecto en un PDF

# ARCHIVOS
se encuentra el archivo del modelo preentrenado y Haarcascade

1.- emotion-ferplus-8.onnx
2.- haarcascade_frontalface_default.xml

# creacion del entrorno virtual
python -m venv .venv ° creacion
.\.venv\Scripts\activate °activacion

# Librerias a instalar
1.-pip install onnxruntime
2.-pip install opencv-python
3.-pip install numpy

# Guia de usuario
Ejecutar el codigo:
- detector_webcam.py


