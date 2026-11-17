# Declaración de Transparencia Tecnológica y Uso de IA

**Proyecto:** Búsqueda exacta de cadenas (KMP, Rabin-Karp y Boyer-Moore)
**Equipo:** 7
**Fecha:** 16 de Noviembre de 2026

## Nivel de uso declarado: ÁMBAR

Se utilizó Inteligencia Artificial como asistente de programación y QA para la optimización del código y la configuración de pruebas. La IA no redactó el análisis formal ni las demostraciones teóricas del informe; dichas secciones fueron elaboradas y verificadas por el equipo.

## 1. Herramienta y Versión

- **Herramienta:** Opencode (Agente de IA en terminal).
- **Modelo:** Qwen 3.7 Plus / DeepSeek V4.1 Flash Free.

## 2. Resumen de Prompts Utilizados

Los prompts se enfocaron en auditar el proyecto local, reparar la lógica del benchmark y estandarizar el entorno de pruebas. Los comandos exactos enviados a la IA fueron:

- "Actúa como auditor técnico y QA... verifica si la carpeta cumple lo exigido para la Bitácora 2 y si el caso de uso profesional está presente..."
- "Aplica parches para arreglar el benchmark: precalcula entradas una sola vez para los tres algoritmos, añade warm-up y verificación cruzada..."
- "Añade `derandomize=True` a los 7 `@settings` de Hypothesis en `tests/test_*.py` para asegurar la semilla fija..."
- "Crea un generador de logs sintéticos (`generar_logs_sinteticos.py`) con IPs ficticias para el escenario de benchmark..."
- "Genera un archivo `requirements.lock.txt` y configura el `.gitignore`..."

## 3. Qué se generó con IA y cómo fue verificado

| Artefacto generado / modificado                      | Verificación realizada por el equipo                                                                                                             |
| :--------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Benchmark pareado (`benchmark.py`)**               | Se ejecutó el script y se verificó en consola que los 3 algoritmos devolvieran las mismas posiciones para el mismo texto (verificación cruzada). |
| **Pruebas de propiedades (`tests/`)**                | Se ejecutó `pytest -v` y se confirmó que las 47 pruebas pasaran exitosamente (`47 passed in 1.05s`).                                             |
| **Generador de logs (`generar_logs_sinteticos.py`)** | Se inspeccionó el código para confirmar que no hubiera datos personales reales (solo IPs de documentación `192.0.2.x` y tokens `FAKE-TOKEN`).    |
| **Configuración `.gitignore` y `requirements.lock`** | Se ejecutó `git status` para verificar que la carpeta `.venv` no se subiera al repositorio.                                                      |

## 4. Qué se descartó (Juicio Crítico)

- **Lógica vieja del benchmark:** La IA sugirió inicialmente dejar el bucle original, pero el equipo descartó esa idea porque generaba textos distintos para cada algoritmo, invalidando la comparación. Se forzó el uso de entradas idénticas.
- **Redacción del Análisis Formal:** Se descartó el uso de IA para redactar los invariantes del bucle, las cotas asintóticas (\(c\) y \(n_0\)) y la demostración formal en el documento Word/PDF. El equipo determinó que delegar esto constituiría un nivel **Rojo** (prohibido), por lo que esa sección fue redactada por los maestrantes basándose en bibliografía (Cormen, Sedgewick).
- **Uso de dependencias externas:** Se descartó instalar librerías extra para las implementaciones principales (se mantuvo Python puro sin `re` ni `str.find`).

## 5. Conclusión del Equipo

El código entregado es reproducible, está respaldado por 47 pruebas automatizadas y el benchmark sigue el método científico (pareado y con semilla fija). El uso de IA aceleró la refactorización técnica, pero la validación empírica y el juicio algorítmico fueron responsabilidad exclusiva del equipo.
