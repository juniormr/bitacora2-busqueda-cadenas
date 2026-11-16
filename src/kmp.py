"""
Knuth-Morris-Pratt (KMP) - Algoritmo de búsqueda de patrones en cadenas.

Complejidad:
    - Preprocesamiento (función de fallo): O(m)
    - Búsqueda: O(n)
    - Total: O(n + m)

donde n = len(texto) y m = len(patrón).

Invariantes de la función de fallo (índices 0-based):
    1. fail[0] = 0 (caso base).
    2. Para todo i >= 1: 0 <= fail[i] < i.
    3. pattern[0:fail[i]] coincide con pattern[i-fail[i]+1:i+1].
    4. fail[i] es el valor MÁXIMO que satisface la propiedad 3.
"""


def compute_failure(pattern: str) -> list[int]:
    """
    Calcula la función de fallo (tabla de prefijos) del patrón.

    Args:
        pattern: El patrón a buscar.

    Returns:
        Lista de enteros donde fail[i] indica la longitud del prefijo propio
        más largo de pattern[0..i] que también es sufijo de pattern[0..i].
    """
    m = len(pattern)
    if m == 0:
        return []

    fail = [0] * m
    fail[0] = 0  # Un solo carácter no tiene prefijo/sufijo propio.
    k = 0  # Longitud del prefijo que también es sufijo.

    for i in range(1, m):
        while k > 0 and pattern[k] != pattern[i]:
            k = fail[k - 1]
        if pattern[k] == pattern[i]:
            k += 1
        fail[i] = k

    return fail


def kmp_search(text: str, pattern: str) -> list[int]:
    """
    Busca todas las ocurrencias de pattern en text usando KMP.

    Args:
        text: Cadena donde buscar.
        pattern: Cadena a encontrar.

    Returns:
        Lista con los índices de inicio de cada ocurrencia (orden ascendente).
        Lista vacía si pattern no se encuentra o está vacío.
    """
    n = len(text)
    m = len(pattern)

    if m == 0:
        return []
    if m > n:
        return []

    fail = compute_failure(pattern)
    occurrences = []
    j = 0  # Número de caracteres que coinciden en pattern.

    for i in range(n):
        while j > 0 and pattern[j] != text[i]:
            j = fail[j - 1]
        if pattern[j] == text[i]:
            j += 1
        if j == m:
            occurrences.append(i - m + 1)
            j = fail[j - 1]

    return occurrences
