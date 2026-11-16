# Búsqueda de Cadenas — Algoritmos KMP, Rabin-Karp y Boyer-Moore

Proyecto de maestría: implementación, pruebas y benchmark de algoritmos
clásicos de búsqueda de patrones en cadenas de texto.

---

## Estructura del proyecto

```
busqueda_cadenas/
├── src/                              # Implementaciones
│   ├── __init__.py
│   ├── kmp.py                        # Knuth-Morris-Pratt
│   ├── rabin_karp.py                 # Rabin-Karp
│   └── boyer_moore.py                # Boyer-Moore
├── tests/                            # Pruebas
│   ├── __init__.py
│   ├── test_kmp.py                   # Unitarias + Hypothesis + diferencial
│   ├── test_rabin_karp.py
│   └── test_boyer_moore.py
├── experiments/                      # Benchmarks y plan experimental
│   ├── __init__.py
│   ├── benchmark.py                  # Medición piloto pareada
│   ├── generar_logs_sinteticos.py    # Generador de logs sintéticos
│   ├── plan_parte2.md                # Plan para la Parte 2
│   └── results/                      # JSON, Excel, PNG y salidas de ejecución
├── docs/
│   ├── caso_uso.md                   # Caso de uso y contrato de salida
│   └── declaracion_uso_ia.md         # Plantilla pendiente de completar
├── spec.md                           # Especificación original
├── requirements.txt                  # Dependencias
├── requirements.lock.txt             # Versiones exactas del entorno verificado
└── README.md                         # Este archivo
```

---

## Requisitos y entorno

- **Python verificado: 3.12.0** (ambiente en el que se regeneraron las pruebas y el benchmark).
- Dependencias declaradas en `requirements.txt` y versiones exactas en `requirements.lock.txt`.

Crear el entorno virtual e instalar:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

python -m pip install -r requirements.txt
```

Para reproducir exactamente las versiones del artefacto:

```bash
python -m pip install -r requirements.lock.txt
```

---

## Caso de uso y contrato de salida

El caso profesional es la auditoría de registros textuales y la detección de
indicadores exactos en logs. Ver [`docs/caso_uso.md`](docs/caso_uso.md).

Las tres funciones (`kmp_search`, `rabin_karp_search` y `boyer_moore_search`)
comparten este contrato:

- Entrada: `texto: str`, `patron: str` (Unicode; no se normaliza).
- Salida: `list[int]` con **todas** las posiciones de inicio, en orden ascendente.
- Se incluyen coincidencias solapadas.
- `patron == ""`, `len(patron) > len(texto)` o ausencia de coincidencias: `[]`.
- Búsqueda exacta y **siempre** sensible a mayúsculas; sin expresiones regulares.
- Un patrón por llamada. Para N indicadores se realizan N llamadas independientes;
  no se implementa un algoritmo multi-patrón.
- El alcance es únicamente el núcleo algorítmico en memoria; no incluye ingestión,
  parseo, streaming ni persistencia de logs.

---

## Comandos para reproducir

### 1. Ejecutar todas las pruebas

```bash
python -m pytest tests/ -v
```

La salida completa de la ejecución de referencia se guarda en
`experiments/results/pytest_output.txt`.

### 2. Ejecutar pruebas de un algoritmo específico

```bash
python -m pytest tests/test_kmp.py -v
python -m pytest tests/test_rabin_karp.py -v
python -m pytest tests/test_boyer_moore.py -v
```

### 3. Ejecutar el benchmark piloto

```bash
python experiments/benchmark.py
```

Esto genera:

- `experiments/results/benchmark_results.json` — datos crudos, ambiente, timestamp y versiones.
- `experiments/results/benchmark_results.xlsx` — hojas `Ambiente`, `Configuracion`, `Resumen` y `Detalle`.
- `experiments/results/benchmark_plot.png` — gráfica de dos paneles (texto aleatorio y logs sintéticos).
- `experiments/results/pip_freeze.txt` — versiones instaladas al momento de la medición.

### 4. Smoke test de los módulos

```bash
python -c "from src.kmp import kmp_search; print(kmp_search('abababab', 'ab'))"
python -c "from src.rabin_karp import rabin_karp_search; print(rabin_karp_search('abababab', 'ab'))"
python -c "from src.boyer_moore import boyer_moore_search; print(boyer_moore_search('abababab', 'ab'))"
```

---

## Resumen de algoritmos

| Algoritmo    | Preprocesamiento | Búsqueda típica | Peor caso |
|--------------|------------------|-----------------|-----------|
| KMP          | O(m)             | O(n)            | O(n + m)  |
| Rabin-Karp   | O(m)             | O(n + m)        | O(n·m) por colisiones |
| Boyer-Moore  | O(m + σ)         | O(n/m) con alfabeto grande | O(n·m) con la heurística de mal carácter |

- **n** = tamaño del texto, **m** = tamaño del patrón, **σ** = tamaño del alfabeto.
- En Boyer-Moore, la regla del buen sufijo mejora el comportamiento práctico.
  No se afirma O(n+m) como cota general sin citar la regla de Galil.

---

## Pruebas implementadas

Cada archivo de pruebas (`tests/test_*.py`) contiene:

| Categoría                | Cantidad | Descripción                                       |
|--------------------------|----------|---------------------------------------------------|
| Unitarias (casos límite) | ≥ 5      | Patrón vacío, texto vacío, superposiciones, etc.  |
| Basadas en propiedades   | 2        | Invariante de función de fallo, corrección total  |
| Diferenciales            | 1        | Contra `str.find` y `re.finditer` (lookahead)     |

- Total: 47 pruebas (16 KMP, 16 Rabin-Karp, 15 Boyer-Moore).
- Semilla fija: `SEED = 42`.
- Las pruebas de propiedades usan `derandomize=True`, `database=None` y
  `max_examples=200` para que la generación sea reproducible.
- Framework: `pytest` + `hypothesis`.

---

## Medición piloto

- Dos escenarios: texto aleatorio uniforme y corpus sintético de logs.
- Tres tamaños: 1 000, 10 000 y 100 000 caracteres.
- Tres repeticiones por algoritmo, tamaño y escenario.
- Entradas precalculadas una sola vez y reutilizadas por los tres algoritmos.
- Warm-up por algoritmo/tamaño y verificación cruzada antes de medir.
- `time.perf_counter()` mide **tiempo de pared**, no CPU puro.
- Semilla 42; los logs sintéticos usan `random.Random(43)`.
- Los logs sintéticos usan IPs del bloque de documentación `192.0.2.0/24`,
  timestamps ficticios, tokens falsos y paths. **No son logs reales.**

---

## Ambiente de referencia

| Componente | Versión |
|------------|---------|
| Python     | 3.12.0 |
| OS         | Windows 11 (10.0.26200) |
| pytest     | 9.2.0 |
| hypothesis | 6.170.15 |
| matplotlib | 3.11.2 |
| pandas     | 3.1.1 |
| openpyxl   | 3.1.5 |
| psutil     | 7.2.2 |

El JSON del benchmark incluye timestamp ISO, versión de Python, sistema
operativo, CPU, RAM, semilla y un resumen de versiones instaladas. El archivo
`requirements.lock.txt` contiene el `pip freeze` completo.

---

## Datos y uso de IA

- Solo se usan datos sintéticos. No se incluyen logs reales, IPs reales,
  usuarios, credenciales ni información personal o confidencial.
- La declaración de uso de IA está en
  [`docs/declaracion_uso_ia.md`](docs/declaracion_uso_ia.md) y queda
  **pendiente de completar por el equipo**.
