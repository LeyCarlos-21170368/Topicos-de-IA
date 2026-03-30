import csv, os, random, math
#Funcion para leer los archivos .csv con las matrices de cada grupo
#EL CODIGO SOLO ACEPTA VALORES NUMERICOS EN LAS MATRICES, SIN ENCABEZADOS
#unica funcion que ni nosotros sabemos como funciona, pero es para no tener la matriz de 100x100 escrita aquí tapando medio código
def leer_matriz_csv(ruta):
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
ruta_distancias = os.path.join(os.getcwd(), r"C:\Users\leyca\.vscode\Phyton\IA2\matriz_distancias.csv")
M_distancia = leer_matriz_csv(ruta_distancias)

# MATRIZ DE COSTOS DE GASOLINA
ruta_gasolina = os.path.join(os.getcwd(), r"C:\Users\leyca\.vscode\Phyton\IA2\matriz_costos_combustible.csv")
M_gasolina = leer_matriz_csv(ruta_gasolina)


#----------------------------------------------------------FUNCION PRINCIPAL----------------------------------------------------------
def recocido_simulado(solucion_inicial,funcion_objetivo,generar_vecino,bajar_temperatura,M_distancia,M_gasolina,temperatura_inicial=100.0,temperatura_minima=1,iteraciones_por_temp=1):
    solucion_actual = solucion_inicial
    mejor_solucion = solucion_inicial
    costo_actual = funcion_objetivo(solucion_actual, M_distancia, M_gasolina)
    mejor_costo = costo_actual
    costo_inicial = costo_actual
    temperatura = temperatura_inicial
    iteracion = 0
    #marcar los multipos de 10 para las paradas de control
    prompted_multiples_of_10 = set()

    print(f"Costo de la solución inicial: {mejor_costo}")

    #ALGORITMO BASICO DE RECOCIDO
    while temperatura > temperatura_minima:
        mejor_costo_en_temp_actual = costo_actual
        for _ in range(iteraciones_por_temp):

            # Generar vecino
            solucion_vecina = generar_vecino(solucion_actual)
            costo_vecino = funcion_objetivo(solucion_vecina, M_distancia, M_gasolina)


            # Calcular la probabilidad de aceptación
            if costo_vecino < costo_actual:
                probabilidad_aceptacion = 1.0
            else:

            #Distribución de Boltzmann
                probabilidad_aceptacion = math.exp((costo_actual - costo_vecino) / temperatura)
            if random.random() < probabilidad_aceptacion:
                solucion_actual = solucion_vecina
                costo_actual = costo_vecino

            # nueva mejor solución global
            if costo_actual < mejor_costo:
                mejor_solucion = solucion_actual
                mejor_costo = costo_actual

            # Mejor costo para la temperatura actual
            if costo_actual < mejor_costo_en_temp_actual:
                mejor_costo_en_temp_actual = costo_actual

        # Aplicar la nueva temperatura
        temperatura = bajar_temperatura(temperatura, iteracion)
        iteracion +=1

        #Imprimir la iteración
        print(f"Temperatura: {temperatura:.4f}, Mejor Costo de esta Temp: {mejor_costo_en_temp_actual:.4f}")

        #cada 10 grados de temperatura bajados
        #preguntar al usuario si desea continuar
        #mostrar el porcentaje de mejora
        current_int_temp = int(temperatura)
        if current_int_temp % 10 == 0 and current_int_temp > 0 and current_int_temp not in prompted_multiples_of_10:
            prompted_multiples_of_10.add(current_int_temp)

            if costo_inicial > 0:
                mejora_porcentaje = ((costo_inicial - mejor_costo) / costo_inicial) * 100
            else:
                mejora_porcentaje = 0.0

            print("\n--- PARADA DE CONTROL ---")
            print(f"Temperatura: {current_int_temp}")
            print(f"Mejor costo actual: {mejor_costo:.4f} (Costo inicial: {costo_inicial:.4f})")
            print(f"Porcentaje de mejora: {mejora_porcentaje:.2f}%")
            respuesta = input("¿Desea continuar el recocido simulado? (s/n): ").lower()
            if respuesta != 's':
                print("Recocido simulado detenido por el usuario.")
                break

    return mejor_solucion, mejor_costo, costo_inicial

#solución inicial (aleatoria)
def generador_sol_ini(num_elementos=100):
    return random.sample(range(1, num_elementos + 1), num_elementos)

# GENERADOR DE SOLUCIONES
def generar_vecino_aleatorio(solucion):
    nueva_solucion = list(solucion)
    # Intercambia dos elementos aleatorios para generar un vecino
    idx1, idx2 = random.sample(range(len(nueva_solucion)), 2)
    nueva_solucion[idx1], nueva_solucion[idx2] = nueva_solucion[idx2], nueva_solucion[idx1]
    return nueva_solucion

#FUNCION OBJETIVO
def calcular_costo(ruta, M_distancia, M_gasolina):
    costo_total_distancia = 0
    costo_total_gasolina = 0
    for i in range(len(ruta) - 1):
        origen = int(ruta[i]) - 1
        destino = int(ruta[i+1]) - 1
        costo_total_distancia += M_distancia[origen][destino]
        costo_total_gasolina += M_gasolina[origen][destino]

    # formula de importancia: no podemos sumar valores de longitud con monetarios
    # dependendiendo de si el cliente le importa mas la distanci o el dinero se modifican los valores
    # por default decimos que valen igual, asi que es una relacion 50/50
    puntaje_final = (costo_total_distancia * 0.5) + (costo_total_gasolina * 0.5)
    return puntaje_final

#Bajada de temperatura
def enfriamiento(temperatura_actual, iteracion):
    return temperatura_actual * 0.99


if __name__ == '__main__':
    print("--------------- INICIO ---------------")
    #LLAMADA DE LAS FUNCIONES
    sol_inicial = generador_sol_ini(num_elementos=100)
    print(f"Solución inicial Aleatoria: {sol_inicial}")
    mejor_sol_encontrada, costo_final, costo_inicial_total = recocido_simulado(
        solucion_inicial=sol_inicial,
        funcion_objetivo=calcular_costo,
        generar_vecino=generar_vecino_aleatorio,
        bajar_temperatura=enfriamiento,
        M_distancia=M_distancia,
        M_gasolina=M_gasolina,
        temperatura_inicial=100.0,
        temperatura_minima=1,
        iteraciones_por_temp=100
    )

    print("\n--- RESULTADOS FINALES ---")
    print(f"Mejor solución encontrada: {mejor_sol_encontrada}")
    print(f"Costo inicial: {costo_inicial_total:.4f}")
    print(f"Costo final: {costo_final:.4f}")
    if costo_inicial_total > 0:
        mejora_total_porcentaje = ((costo_inicial_total - costo_final) / costo_inicial_total) * 100
        print(f"Porcentaje de mejora total: {mejora_total_porcentaje:.2f}%")
