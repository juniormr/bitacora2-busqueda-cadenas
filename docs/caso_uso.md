## Caso de uso profesional: auditoría de registros textuales y detección de indicadores en logs

En un equipo de auditoría de TI o de operaciones de seguridad, se revisan grandes volúmenes de logs de servidores web, proxy y autenticación para localizar indicadores textuales exactos asociados a incidentes: rutas de acceso anómalas, cadenas de error conocidas, identificadores de prueba, firmas de ataque documentadas o fragmentos de transacciones sospechosas. El proceso manual basado en herramientas ad hoc es difícil de auditar y de comparar bajo restricciones de tiempo y memoria. Por ello, se requiere un módulo en Python 3 que, dado un corpus de logs y un indicador textual, devuelva todas las posiciones de las ocurrencias exactas y permita comparar el comportamiento de KMP, Rabin-Karp y Boyer-Moore.

El caso se desarrolla en un entorno profesional simulado de auditoría y monitoreo de logs. Las restricciones principales son: uso exclusivo de datos sintéticos o anonimizados; búsqueda exacta y siempre sensible a mayúsculas; corpus procesable en memoria para la medición piloto; prohibición de usar `str.find`, expresiones regulares o librerías externas en las implementaciones principales; y necesidad de documentar semillas, versiones y comandos de reproducción. El alcance es la búsqueda de un patrón por ejecución. Si se requiere revisar un conjunto pequeño de indicadores, cada indicador se busca de forma independiente con cada algoritmo y se reporta el costo total; no se implementa un algoritmo multi-patrón. El módulo cubre únicamente el núcleo algorítmico en memoria; no incluye ingestión, parseo, streaming ni persistencia de logs.

## Contrato de salida

Las tres funciones (`kmp_search`, `rabin_karp_search` y `boyer_moore_search`) comparten este contrato:

- Entrada: `texto: str`, `patron: str` (Unicode; no se normaliza).
- Salida: `list[int]` con todas las posiciones de inicio, en orden ascendente.
- Se incluyen coincidencias solapadas.
- `patron == ""`, `len(patron) > len(texto)` o ausencia de coincidencias: `[]`.
- Búsqueda exacta y siempre sensible a mayúsculas; sin expresiones regulares.
- Un patrón por llamada. Para N indicadores se realizan N llamadas independientes; no hay algoritmo multi-patrón.

## Criterios de aceptación

1. Los tres algoritmos coinciden con la referencia de Python en las pruebas unitarias, de propiedades y diferenciales.
2. La suite completa pasa en el ambiente documentado.
3. El benchmark se regenera con `python experiments/benchmark.py` usando la semilla 42.
4. No se utilizan logs reales, direcciones IP reales, usuarios, credenciales ni datos personales o confidenciales; solo datos sintéticos.
