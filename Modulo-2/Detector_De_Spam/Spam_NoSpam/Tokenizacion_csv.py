import numpy as np
import re
import pandas as pd
from sklearn.model_selection import train_test_split
from keras_preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences



df= pd.read_csv("Datasets/emails/dataset_grande.csv", encoding="utf-8")
for col in ["remitente", "asunto","contenido","enlaces","adjuntos"]:
    df[col] = df[col].astype(str).fillna("")

def Normalizacion_de_texto(texto: str) -> str:
    #convertir todo el texto a minusculas
    texto = texto.lower()

    # re.sub se usa para detectar emails y reemplazarlos por el token "email"
    # usa expresiones regulares
    texto = re.sub(r"[a-z0-9.\-_+]+@[a-z0-9\.\-]+\.[a-z]{2,}", " <email> ", texto)
    
    # ahora lo configuro para que detecte urls y las reemplace por el token "url"
    texto = re.sub(r"https?://\S+|www\.\S+", " <url> ", texto)
    
    texto = re.sub(r"\s+", " ", texto).strip()  # quita espacios multiples

    # perfecto, para represetar mejor que es lo que se hace aqui
    # pongo un ejemplo porque soy muy olvidadizo
    # pase de esto---> Reclama tu regalo ahora!!! https://regaloconfiable.win/recogelo contacto promo@ganaste.ru
    # a esto---> reclama tu regalo ahora <url> contacto <email>

    return texto

for columna in ["remitente", "asunto", "contenido", "enlaces", "adjuntos"]:
    df[columna] = df[columna].apply(Normalizacion_de_texto)

df["texto"] = (
    "remitente: " + df["remitente"] +
    " | asunto: " + df["asunto"] +
    " | contenido: " + df["contenido"] +
    " | enlaces: " + df["enlaces"] +
    " | adjuntos: " + df["adjuntos"]
)


# esto lo que va a haces es lo siguiente
# remitente,asunto,contenido,enlaces,adjuntos
# remitente: prof.juarez@tecnm.mx,
# asunto: Clase de IA – enlace a Teams,
# contenido: "Buenas tardes, comparto el enlace para la clase de hoy a las 18:00.",
# enlaces: https://teams.microsoft.com/l/meetup-join/abc123
# aduntos,,

# a los siguiente---> remitente: prof.juarez@tecnm.mx| asunto: Clase de IA – enlace a Teams| contenido: "Buenas tardes, comparto el enlace para la clase de hoy a las 18:00."| enlaces: https://teams.microsoft.com/l/meetup-join/abc123
# | adjuntos: 

# localizar los que son spam y los que no lo son
localizar_label = {"spam": 1, "ham": 0}       # convierte a tipo numerico de 32 bits, porque? porque tensorflow/keras esperan tensores numericos(no strings)
label= df["label"].map(localizar_label).astype("int32").values

entradas_de_entrenamiento, entradas_de_validacion, etiquetas_de_entrenamiento, etiquetas_de_validacion = train_test_split(
    df["texto"].values, label, test_size=0.2, random_state=42, stratify=label
                               #usar 20% de los datos para validacion
                               #semilla aleatoria y es fija, para que la division sea siempre la misma
)

VOCAB_SIZE = 5000  # considerar las 2000 palabras mas comunes
MAX_LENGTH = 200   # MAXIMO DE TOKENS POR EMAIL

tokenizador =Tokenizer(num_words=VOCAB_SIZE, oov_token="<OOV>")
tokenizador.fit_on_texts(entradas_de_entrenamiento)

x_entrenamiento= pad_sequences(
    tokenizador.texts_to_sequences(entradas_de_entrenamiento),
    maxlen=MAX_LENGTH, padding="post", truncating="post"
)

x_validacion= pad_sequences(
    tokenizador.texts_to_sequences(entradas_de_validacion),
    maxlen=MAX_LENGTH, padding="post", truncating="post"
)

y_entrenamiento= np.array(etiquetas_de_entrenamiento, dtype="int32")
y_validacion= np.array(etiquetas_de_validacion, dtype="int32")

print("X_entrenamiento:", x_entrenamiento.shape)
print("X_validacion  :", x_validacion.shape)
print("y_entrenamiento:", y_entrenamiento.shape)
print("y_validacion  :", y_validacion.shape)



