import numpy as np
from keras_preprocessing.sequence import pad_sequences
from tensorflow import keras

class ModeloSpam:
    def __init__(self, tam_vocabulario=5000, max_longitud=200,
                 dim_embedding=64, unidades=64, dropout=0.5, lr=0.001):
        self.tam_vocabulario = tam_vocabulario
        self.max_longitud = max_longitud

        self.modelo = keras.Sequential([
            keras.layers.Input(shape=(self.max_longitud,), dtype="int32"),
            keras.layers.Embedding(input_dim=self.tam_vocabulario,
                                   output_dim=dim_embedding,
                                   mask_zero=True), # ignora padding
            keras.layers.GlobalAveragePooling1D(),
            keras.layers.Dense(unidades, activation="relu"),
            keras.layers.Dropout(dropout),
            keras.layers.Dense(1, activation="sigmoid")#1 salida
        ])

        self.modelo.compile(
            optimizer=keras.optimizers.Adam(learning_rate=lr),
            loss="binary_crossentropy", #binaria
            metrics=["accuracy", keras.metrics.AUC(name="auc")]
        )

    def entrenar(self, x_entrenamiento, y_entrenamiento,
                 x_validacion, y_validacion,
                 epocas=30, tam_lote=8, usar_callbacks=True):
        callbacks = []
        if usar_callbacks:
            callbacks = [
                keras.callbacks.EarlyStopping(monitor="val_auc", mode="max",
                                              patience=4, restore_best_weights=True),
                keras.callbacks.ReduceLROnPlateau(monitor="val_loss",
                                                  factor=0.5, patience=2, min_lr=1e-5)
            ]
        return self.modelo.fit(
            x_entrenamiento, y_entrenamiento,  # y como 0/1
            validation_data=(x_validacion, y_validacion),
            epochs=epocas, batch_size=tam_lote,
            callbacks=callbacks, verbose=1, shuffle=True
        )

    def evaluar(self, x_validacion, y_validacion):
        return self.modelo.evaluate(x_validacion, y_validacion, verbose=0)

    def predecir_desde_indices(self, entradas_padded):
        p_spam = self.modelo.predict(entradas_padded, verbose=0).ravel()  # [0..1]
        etiquetas = np.where(p_spam >= 0.5, "spam", "ham")
        confianzas = np.where(p_spam >= 0.5, p_spam, 1 - p_spam)
        return etiquetas.tolist(), confianzas.tolist(), p_spam.tolist()

    def predecir_desde_textos(self, textos, tokenizador):
        sec = tokenizador.texts_to_sequences(textos)
        X = pad_sequences(sec, maxlen=self.max_longitud, padding="post", truncating="post")
        return self.predecir_desde_indices(X)

   