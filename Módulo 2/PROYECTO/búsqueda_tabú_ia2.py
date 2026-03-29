import csv
import os
import random
import math
import collections
#Funcion para leer los archivos .csv con las matrices de cada grupo
#EL CODIGO SOLO ACEPTA VALORES NUMERICOS EN LAS MATRICES, SIN ENCABEZADOS
#unica funcion que ni nosotros sabemos como funciona, pero es para no tener que cambiar los valores de la matriz 1 por 1
def leer_matriz_csv(ruta, tamaño_esperado=10):
    matriz = []
    with open(ruta, newline='', encoding='utf-8') as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            if fila:
                fila_numeros = []
                for valor in fila:
                    try:
                        fila_numeros.append(float(valor))
                    except ValueError:
                        fila_numeros.append(0.0)
                matriz.append(fila_numeros)
    return matriz

# MATRIZ DE DISTANCIAS
try:
    ruta_distancias = os.path.join(os.getcwd(), 'C:\\Users\\leyca\\.vscode\\Phyton\\IA2\\matriz_distancias_Centro_1.csv')
    M_distancia = leer_matriz_csv(ruta_distancias, tamaño_esperado=10)
except (FileNotFoundError, ValueError) as e:
    print(f"Error al cargar la matriz de distancias: {e}. Usando una matriz en ceros.")
    M_distancia = [[0 for _ in range(10)] for _ in range(10)]

# MATRIZ DE COSTOS DE GASOLINA
try:
    ruta_gasolina = os.path.join(os.getcwd(), 'C:\\Users\\leyca\\.vscode\\Phyton\\IA2\\costos_combustible_Centro_1.csv')
    M_gasolina = leer_matriz_csv(ruta_gasolina, tamaño_esperado=10)
except (FileNotFoundError, ValueError) as e:
    print(f"Error al cargar la matriz de gasolina: {e}. Usando una matriz en ceros.")
    M_gasolina = [[0 for _ in range(10)] for _ in range(10)]


# GENERADOR DE SOLUCIONES
# Swaps generados de 2 en 2
def Generador(Sol_Inicio):
    vecindario = []
    n = len(Sol_Inicio)
    for i in range(n):
        for j in range(i + 1, n):
            nueva_sol = Sol_Inicio.copy()
            nueva_sol[i], nueva_sol[j] = nueva_sol[j], nueva_sol[i]
            vecindario.append(nueva_sol)
    return vecindario

# FUNCIÓN OBJETIVO
def calcular_costo(ruta, M_distancia, M_gasolina):
    costo_total_distancia = 0
    costo_total_gasolina = 0

    for i in range(len(ruta) - 1):
        origen = ruta[i] - 1
        destino = ruta[i+1] - 1

        #cada costo depende de su respectiva matriz
        costo_total_distancia += M_distancia[origen][destino]
        costo_total_gasolina += M_gasolina[origen][destino]

    # formula de importancia: no podemos sumar valores de longitud con monetarios
    # dependendiendo de si el cliente le importa mas la distanci o el dinero se modifican los valores
    # por default decimos que valen igual, asi que es una relacion 50/50
    puntaje_final = (costo_total_distancia * 0.5) + (costo_total_gasolina * 0.5)
    return puntaje_final

#ORDENADOR DE SOLUCIONES
def ordenar_soluciones(vecindario, M_distancia, M_gasolina):
    return sorted(vecindario, key=lambda ruta: calcular_costo(ruta, M_distancia, M_gasolina))

# GENERACIÓN ALEATORIA DE SOLUCION INICIAL
n = len(M_distancia)
sol_inicial = random.sample(range(1, n + 1), n)
costo_inicial_global = calcular_costo(sol_inicial, M_distancia, M_gasolina)

# ITERACIONES
vueltas = 10 # <--- Cuantas iteraciones hace el programa antes de preguntar si quieres continuar
duracion_tabu = 5000 # <--- Cuantas iteraciones se queda una solución en la lsita tabu

print("--- INICIO DE LAS ITERACIONES ---")
print(f"Solución Inicial Global (aleatoria): {sol_inicial} | Costo Total: {costo_inicial_global}")

mejor_solucion_global = sol_inicial
mejor_costo_global = costo_inicial_global
iteracion = 0

lista_tabu = collections.deque(maxlen=duracion_tabu)
lista_tabu.append(tuple(sol_inicial)) # La solucion initial se va a la lista tabu

while True:
    for iter_step in range(vueltas):
        iteracion += 1
        print(f"\n--- Iteración {iteracion} ---")
        print(f"Solución Actual: {sol_inicial} | Costo: {calcular_costo(sol_inicial, M_distancia, M_gasolina)}")

        # MANDADA A LLAMAR DE LOS MÉTODOS
        resultado = Generador(sol_inicial)
        ordenamiento = ordenar_soluciones(resultado, M_distancia, M_gasolina)

        mejor_sol_actual = None
        mejor_costo_actual = float('inf')

        #ordenas las soluciones con la función objetivo y checamos que no esten en la lista tabu
        for vecino in ordenamiento:
            costo_vecino = calcular_costo(vecino, M_distancia, M_gasolina)
            es_tabu = tuple(vecino) in lista_tabu

            # Si no es tabu, se acepta
            if not es_tabu:
                mejor_sol_actual = vecino
                mejor_costo_actual = costo_vecino
                break
            # Si es tabú, se ignora y se sigue buscando.

        # si todos los vecinos son tabu, se toma la mejor solución del vecindario aunque sea tabu
        if mejor_sol_actual is None:
            mejor_sol_actual = ordenamiento[0]
            mejor_costo_actual = calcular_costo(mejor_sol_actual, M_distancia, M_gasolina)

        print(f"Mejor solución encontrada en esta iteración: {mejor_sol_actual} | Costo: {mejor_costo_actual}")

        # Actualizar la solución inicial para la próxima iteración
        sol_inicial = mejor_sol_actual

        # Añadir la nueva solución actual a la lista tabú
        lista_tabu.append(tuple(sol_inicial))

        # Actualizar la mejor solución global si se encuentra una mejor
        if mejor_costo_actual < mejor_costo_global:
            mejor_costo_global = mejor_costo_actual
            mejor_solucion_global = mejor_sol_actual

    print(f"\n--- RESULTADOS DESPUES DE {iteracion} ITERACIONES---")
    print(f"Mejor Solución Global Encontrada hasta ahora: {mejor_solucion_global} | Costo Total: {mejor_costo_global}")

    # Calcular y mostrar la mejora porcentual
    if costo_inicial_global > 0:
        mejora_porcentual = ((costo_inicial_global - mejor_costo_global) / costo_inicial_global) * 100
        print(f"Mejora porcentual respecto a la solución inicial: {mejora_porcentual:.2f}%")
    else:
        print("No se puede calcular la mejora porcentual (costo inicial es cero).")

    continuar = input("¿Desea continuar con más iteraciones? (s/n): ")
    if continuar.lower() != 's':
        break

print("\n--- RESULTADOS FINALES ---")
print(f"Mejor Solución Global Final: {mejor_solucion_global} | Costo Total: {mejor_costo_global}")
mejora_porcentual_final = ((costo_inicial_global - mejor_costo_global) / costo_inicial_global) * 100
print(f"Mejora porcentual final respecto a la solución inicial: {mejora_porcentual_final:.2f}%")