# main.py
from Tokenizacion_csv import (
    x_entrenamiento, y_entrenamiento,
    x_validacion, y_validacion,
    tokenizador, VOCAB_SIZE, MAX_LENGTH
)
from Red_Neuronal import ModeloSpam

# 1) Crear modelo (binario: 1 salida + sigmoid; lr pequeño)
modelo_spam = ModeloSpam(tam_vocabulario=VOCAB_SIZE, max_longitud=MAX_LENGTH, lr=0.001)

# 2) Entrenar (más épocas y batch un poco mayor)
hist = modelo_spam.entrenar(
    x_entrenamiento, y_entrenamiento,
    x_validacion, y_validacion,
    epocas=100, tam_lote=10
)

# 3) Evaluar
perdida, precision, auc = modelo_spam.evaluar(x_validacion, y_validacion)
print(f"[VALID] loss={perdida:.4f} | acc={precision:.4f} | auc={auc:.4f}")

# 4) Predicción (ejemplo claro)
#ejemplo = "remitente: promo@cash.win | asunto: ¡Has ganado un premio! | contenido: Reclama YA | enlaces: http://promo.win | adjuntos:"

#ejemplo = "remitente:manuel@gmail.com | asunto:Reunión de proyecto | contenido:Hola equipo, les recuerdo que tenemos una reunión mañana a las 10am para discutir los avances del proyecto. Por favor, preparen sus informes. | enlaces: | adjuntos:informe.pdf"

#ejemplo = "remitente:prestamos@coppel-x-pp.com  | asunto:Préstamo aprobado | contenido:¡Felicidades! Su préstamo ha sido aprobado. Nosotros no le mandaremos ningun enlace por este medio ni le pediremos información personal. | enlaces: | adjuntos:"

#ejemplo = "remitente:prestamos@coppel-x-pp.com  | asunto:Préstamo aprobado | contenido:¡Felicidades! Su préstamo ha sido aprobado. para revizar su estatus de click al siguiente enlace. | enlaces: http://coppel-x-pp.com/estatus | adjuntos:"

#
#ejemplo = "remitente: seguridad@bbva-verifica.com | asunto: URGENTE: tu cuenta será bloqueada | contenido: Verifica tus datos en 24 horas para evitar el cierre de tu banca. | enlaces: http://bbva-verifica.com/reacceso | adjuntos: acceso_seguro.html"

#ejemplo = "remitente: notificaciones@bbva.com.mx | asunto: Tu estado de cuenta de septiembre está listo | contenido: Tu estado de cuenta ya está disponible en la app BBVA. No compartas tus datos. | enlaces: https://www.bbva.mx | adjuntos:"

ejemplo= "remitente: notificaciones@coppel.com | asunto: Tu estado de cuenta de septiembre está listo | contenido: Tu estado de cuenta ya está disponible en la app Coppel. No compartas tus datos. | enlaces: https://www.coppel.com | adjuntos:"


etqs, confs, pspam = modelo_spam.predecir_desde_textos([ejemplo], tokenizador)

print("====================================")
print(f"Mensaje analizado:\n{ejemplo}")
print("------------------------------------")
if etqs[0] == "spam":
    print(f"Clasificación: SPAM con {confs[0]*100:.2f}% de confianza (p_spam={pspam[0]:.3f})")
else:
    print(f"Clasificación: NO SPAM (HAM) con {confs[0]*100:.2f}% de confianza (p_spam={pspam[0]:.3f})")
print("====================================")
