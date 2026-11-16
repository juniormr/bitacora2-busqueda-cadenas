# Plan Experimental – Parte 2: Análisis Comparativo de Algoritmos de Búsqueda de Patrones

## 1. Objetivos

Extender la medición piloto para caracterizar el comportamiento asintótico
de KMP, Rabin-Karp y Boyer-Moore en escenarios controlados, contrastando
las complejidades teóricas con el rendimiento empírico.

## 2. Hipótesis a contrastar

| ID  | Hipótesis                                                                                     | Algoritmo(s)    |
|-----|-----------------------------------------------------------------------------------------------|-----------------|
| H1  | KMP exhibe crecimiento lineal O(n+m) independientemente del alfabeto o patrón.               | KMP             |
| H2  | Rabin-Karp tiene peor caso O(n·m) en textos con muchas colisiones de hash (alfabeto pequeño, patrón repetitivo). | Rabin-Karp      |
| H3  | Boyer-Moore es sublineal O(n/m) en el caso promedio con alfabetos grandes y patrones largos. | Boyer-Moore     |
| H4  | Boyer-Moore degrada a O(n·m) en patrones degenerados (ej. patrón = texto parcial repetido).  | Boyer-Moore     |
| H5  | Para alfabetos pequeños (σ=2), Boyer-Moore pierde su ventaja frente a KMP.                   | BM vs KMP       |
| H6  | Rabin-Karp con módulo primo grande (10⁹+7) tiene tasa de colisiones despreciable en la práctica. | Rabin-Karp |

## 3. Variables experimentales

| Variable             | Valores                                                      |
|----------------------|--------------------------------------------------------------|
| Tamaño del texto (n) | 1 000, 5 000, 10 000, 50 000, 100 000, 500 000, 1 000 000  |
| Tamaño del patrón(m) | 5, 20, 50, 100, 500                                         |
| Alfabeto (σ)         | 2 (binario), 4 (ADN), 26 (letras), 95 (ASCII imprimible)    |
| Tipo de texto        | Aleatorio, repetitivo (aaaa…), patrón incrustado periódicamente |
| Repeticiones         | 5 por configuración                                          |

## 4. Métricas

- Tiempo de ejecución (CPU, no wall-clock) con `time.process_time()`.
- Número de comparaciones de caracteres (requiere instrumentación).
- Número de colisiones de hash en Rabin-Karp.
- Uso de memoria pico (`tracemalloc`).

## 5. Metodología

1. **Diseño factorial fraccionado**: no se prueban todas las combinaciones.
   Se fija un factor y se varían los demás (análisis univariado).
2. **Escenario peor caso**: construir textos que maximicen colisiones (RK)
   o desplacements mínimos (BM).
3. **Análisis estadístico**: media, desviación estándar, intervalos de
   confianza al 95%. Regresión lineal en escala log-log para estimar el
   exponente empírico de crecimiento.
4. **Reproducibilidad**: semilla fija (SEED=42), ambiente documentado
   automáticamente.

## 6. Entregables esperados

- Tablas de tiempos por configuración.
- Gráficas log-log con líneas de referencia O(n), O(n log n), O(n²).
- Documento de conclusiones contrastando H1–H6 con evidencia empírica.
