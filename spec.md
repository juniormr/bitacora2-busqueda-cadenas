1.- Crea la estructura del código de la siguiente manera: src/, tests/ y experiments/.
2.- Dentro de la carpeta src haz la implementación inicial en Python 3 de los algoritmos KMP (Knuth-Morris-Pratt), Rabin-Karp y Boyer-Moore funcional y legible de manera separada por archivos .py (uno para cada algoritmo).
3.- Dentro de la carpeta tests implementa las pruebas con las siguientes especificaciones: mínimo 5 pruebas unitarias (con casos límite), 2 pruebas basadas en propiedades (Hypothesis) y 1 prueba diferencial contra una implementación de referencia:
	Propiedad o invariante a argumentar: Invariante de la función de fallo.
	Costos a analizar: O(n+m), Rabin-Karp peor caso O(nm).
	Referencia para la prueba diferencial: str.find o re).
Para este tarea 3 implementa un archivo por cada algoritmo utilizando semilla fija y reproducible.
4.- Realiza una Medición piloto y plan experimental: al menos 3 tamaños de entrada, 3 repeticiones, ambiente documentado (CPU, RAM, versión de Python) y una gráfica. Además, ½ página con el plan de la Parte 2 y las hipótesis a contrastar.
5.- Crea un README.md con los comandos para reproducir todo.
6.- Crea un archivo requirements.txt donde escribiras los requerimientos para ejecutar toda la implementación.
