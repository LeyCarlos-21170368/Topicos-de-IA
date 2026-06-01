import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------
# FASE 2: PREPARACIÓN Y APRENDIZAJE TRANSFERIDO
# ---------------------------------------------------------
# Apuntamos a la carpeta de imágenes que ya fueron procesadas y multiplicadas
ruta_dataset = 'aumentadas' 
resolucion = (160, 160)
batch_size = 32

print("🔄 Cargando imágenes para entrenamiento y validación...")
# Dividimos el dataset: 80% para entrenar la IA y 20% para examinarla
generador = ImageDataGenerator(validation_split=0.2)

train_data = generador.flow_from_directory(
    ruta_dataset,
    target_size=resolucion,
    batch_size=batch_size,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

val_data = generador.flow_from_directory(
    ruta_dataset,
    target_size=resolucion,
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation',
    shuffle=False # Importante: No mezclar para que la Matriz de Confusión sea precisa
)

num_clases = len(train_data.class_indices)
nombres_clases = list(train_data.class_indices.keys())
print(f"🎓 Identificadores detectados: {nombres_clases}")

print("🧠 Descargando modelo base MobileNetV2...")
# Cargar modelo base pre-entrenado por Google (sin su capa de clasificación final)
base_model = MobileNetV2(input_shape=(160, 160, 3), include_top=False, weights='imagenet')

# Congelar capas preentrenadas (Evita sobreajuste y ahorra RAM)
base_model.trainable = False

# Añadir nuestra propia capa de salida (Hecha a la medida para tus alumnos)
x = base_model.output
x = GlobalAveragePooling2D()(x)
salida = Dense(num_clases, activation='softmax')(x)

modelo = Model(inputs=base_model.input, outputs=salida)

# ---------------------------------------------------------
# FASE 3: COMPILACIÓN Y ENTRENAMIENTO
# ---------------------------------------------------------
print("⚙️ Compilando el modelo...")
modelo.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("🚀 Iniciando entrenamiento...")
# 15 vueltas de aprendizaje (épocas). Puedes subirlo a 20 o 30 si quieres más precisión.
epocas = 15
historial = modelo.fit(
    train_data,
    validation_data=val_data,
    epochs=epocas
)

# ---------------------------------------------------------
# EVALUACIÓN: MATRIZ DE CONFUSIÓN
# ---------------------------------------------------------
print("📊 Generando Matriz de Confusión...")
predicciones = modelo.predict(val_data)
clases_predichas = np.argmax(predicciones, axis=1)
clases_reales = val_data.classes

cm = confusion_matrix(clases_reales, clases_predichas)

# Dibujar y guardar la gráfica
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=nombres_clases, yticklabels=nombres_clases)
plt.title('Matriz de Confusión del Modelo Facial')
plt.ylabel('Etiqueta Real')
plt.xlabel('Predicción del Modelo')
plt.tight_layout()
plt.savefig('matriz_confusion.png')
print("✅ Matriz guardada exitosamente como 'matriz_confusion.png'.")

# ---------------------------------------------------------
# FASE 4 (PREPARACIÓN): EXPORTACIÓN A TFLITE
# ---------------------------------------------------------
print("📱 Convirtiendo modelo a formato TFLite para dispositivo móvil...")
converter = tf.lite.TFLiteConverter.from_keras_model(modelo)
tflite_model = converter.convert()

with open('modelo_facial.tflite', 'wb') as f:
    f.write(tflite_model)

print("🎉 ¡Éxito! El archivo 'modelo_facial.tflite' está listo para integrarse en Android Studio.")