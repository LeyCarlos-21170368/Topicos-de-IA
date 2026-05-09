#ALGORITMO DE ENJAMBRE DE PARTICULAS (PSO)
#TOPICOS DE INTELIGENCIA ARTIFICIAL
#Ley Garcia Jose Carlos
#Mauricio Lopez Lara
import pandas
import numpy
import pyswarms
import matplotlib.pyplot
import seaborn
from scipy.spatial.distance import cdist

#LECTURA DE DATOS
df = pandas.read_csv('cultivos_guasave.csv')
df.columns = df.columns.str.strip()
df['Cultivo'] = df['Cultivo'].str.strip()


#PRIORIZAR LOS CULTIVOS
prioridad_cultivo = {'Maíz': 0.33, 'Tomate': 0.33, 'Chile': 0.33}
df['Prioridad_Cultivo'] = df['Cultivo'].map(prioridad_cultivo)

# Normalizamos las variables para que estén en la misma escala (0 a 1)
# Esto le da valores entre 0 y 1 a cada valor
# Esto hace que cada variable tenga la misma importancia al sacar su valor calculado
# (La humedad es negativa por que se busca maximizala en lugar de minimizarla como las otras variables)
df['Humedad_Norm'] = 1 - ((df['Humedad (%)'] - df['Humedad (%)'].min()) / (df['Humedad (%)'].max() - df['Humedad (%)'].min()))
df['Salinidad_Norm'] = (df['Salinidad (dS/m)'] - df['Salinidad (dS/m)'].min()) / (df['Salinidad (dS/m)'].max() - df['Salinidad (dS/m)'].min())
df['Elevacion_Norm'] = (df['Elevación (m)'] - df['Elevación (m)'].min()) / (df['Elevación (m)'].max() - df['Elevación (m)'].min())
df['Temp_Norm'] = (df['Temperatura (°C)'] - df['Temperatura (°C)'].min()) / (df['Temperatura (°C)'].max() - df['Temperatura (°C)'].min())


# FORMULAR EL VALOR CALCULADO
# pesos de importancia (no es obligtorio que sumen 1.0, pero es recomendable)
W_h, W_s, W_e, W_t, W_c = 0.20, 0.20, 0.20, 0.20, 0.20 
# en este caso les dimos el mismo peso
df['Peso'] = (W_h * df['Humedad_Norm']) + \
                    (W_s * df['Salinidad_Norm']) + \
                    (W_e * df['Elevacion_Norm']) + \
                    (W_t * df['Temp_Norm']) + \
                    (W_c * df['Prioridad_Cultivo'])
coordenadas = df[['Latitud', 'Longitud']].values
valor_calculado = df['Peso'].values

# FUNCION OBJETIVO
# Cambia este valor para ajustar el número de sensores que se van  a instalar
numero_de_sensores = 3
def objetivo_function(posicion_particula):

#EVALUACION DEL ENJAMBRE
    n_particulas = posicion_particula.shape[0]
    obj = numpy.zeros(n_particulas, dtype=numpy.float64)
    
#MOVER LAS PARTICULAS
    for i in range(n_particulas):
        sensores = posicion_particula[i].reshape(numero_de_sensores, 2)
        distancias = cdist(sensores, coordenadas)
        cultivos_mas_cercanos = numpy.argmin(distancias, axis=1)
        
        cultivos_unicos = numpy.unique(cultivos_mas_cercanos)
        suma_total_importancia = numpy.sum(valor_calculado[cultivos_unicos])
#NOTA: el valor es negativo si se maximiza el valor objetivo, positivo si se minimiza
        obj[i] = -suma_total_importancia
    return obj.astype(numpy.float64)


# definimos los límites
lat_min, lat_max = df['Latitud'].min(), df['Latitud'].max()
lon_min, lon_max = df['Longitud'].min(), df['Longitud'].max()


# Por cada sensor, repetir los límites dentro del array
limites_inf = numpy.array([lat_min, lon_min] * numero_de_sensores)
limites_sup = numpy.array([lat_max, lon_max] * numero_de_sensores)
limites = (limites_inf, limites_sup)

# Parametros del enjambre
# c1: local
# c2: global
#  w: inercia
options = {'c1': 1.5, 'c2': 1.5, 'w': 0.5}

# ----------OPTIMIZAMOS EL ENJAMBRE----------
optimizer = pyswarms.single.GlobalBestPSO(n_particles=50, dimensions=2 * numero_de_sensores, options=options, bounds=limites)
best_cost, best_pos = optimizer.optimize(objetivo_function, iters=100)  

# graficamos el avance del enjambre en la optimización
matplotlib.pyplot.figure(figsize=(8, 5))
historial_porcentaje = [-valor * 100 for valor in optimizer.cost_history]
matplotlib.pyplot.plot(historial_porcentaje, color='green', linewidth=2)
matplotlib.pyplot.title('Optimización del Enjambre')
matplotlib.pyplot.xlabel('Iteraciones')
matplotlib.pyplot.ylabel('Valor Calculado')
matplotlib.pyplot.grid(True)
matplotlib.pyplot.show()

# GRAFICAMOS LOS RESULTADOS
# la ubicacion optima del sensor se marca con una X roja
# Esta seccion fue 100% hecho por IA, ya que nunca hemos usado matplotlib antes, pero si logramos entender mas o menos como grafica
print(f"Mejor ubicación encontrada para el sensor: Lat: {best_pos[0]:.6f}, Lon: {best_pos[1]:.6f}")
matplotlib.pyplot.figure(figsize=(10, 6))
seaborn.scatterplot(data=df, x='Longitud', y='Latitud', size='Peso', hue='Cultivo', sizes=(20, 200), alpha=0.7, palette='viridis')
mejores_sensores = best_pos.reshape(numero_de_sensores, 2)
print("--- UBICACIONES ÓPTIMAS ENCONTRADAS ---")
for i, sensor in enumerate(mejores_sensores):
    print(f"Sensor {i+1}: Lat: {sensor[0]:.6f}, Lon: {sensor[1]:.6f}")
    matplotlib.pyplot.scatter(sensor[1], sensor[0], color='red', marker='X', s=200)
matplotlib.pyplot.title(f'Ubicación Óptima de {numero_de_sensores} Sensores')
matplotlib.pyplot.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
matplotlib.pyplot.grid(True)
matplotlib.pyplot.tight_layout()
matplotlib.pyplot.show()