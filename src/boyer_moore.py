"""
Boyer-Moore - Algoritmo de búsqueda de patrones con heurísticas de salto.

Complejidad:
    - Preprocesamiento: O(m + σ) donde σ es el tamaño del alfabeto.
    - Búsqueda mejor caso: O(n / m)  (sublineal, saltos grandes).
    - Búsqueda peor caso: O(n * m)   (para ciertos patrones degenerados
      con la regla del buen sufijo sola; con la regla del mal carácter
      combinada, O(n) en la práctica para la mayoría de textos).

El algoritmo combina dos heurísticas:
    1. Regla del mal carácter (Bad Character): al encontrar una discrepancia,
       saltar para alinear el carácter del texto con su última aparición
       en el patrón.
    2. Regla del buen sufijo (Good Suffix): al encontrar una discrepancia
       después de un sufijo coincidente, saltar para alinear el siguiente
       sufijo del patrón que también coincida.
"""


def _compute_bad_character_table(pattern: str) -> dict[str, int]:
    """
    Tabla del mal carácter: última posición de cada carácter en el patrón.

    Args:
        pattern: El patrón a buscar.

    Returns:
        Diccionario {carácter: última_posición} para todos los caracteres
        presentes en el patrón.
    """
    table = {}
    m = len(pattern)
    for i in range(m):
        table[pattern[i]] = i
    return table


def _compute_good_suffix_table(pattern: str) -> list[int]:
    """
    Tabla del buen sufijo para la regla de salto.

    Para cada posición i del patrón, shift[i] indica cuántas posiciones
    desplazar cuando ocurre una discrepancia en la posición i, dado que
    pattern[i+1..m-1] coincide con el texto.

    Args:
        pattern: El patrón a buscar.

    Returns:
        Lista de desplazamientos, uno por cada posición del patrón.
    """
    m = len(pattern)
    shift = [0] * m
    # border_pos[i] = inicio del sufijo más amplio de pattern que es también
    # prefijo de pattern (para la parte starting at i).
    border_pos = [0] * (m + 1)

    # Caso 1: el sufijo coincide con alguna ocurrencia anterior en el patrón.
    i = m
    j = m + 1
    border_pos[i] = j

    while i > 0:
        while j <= m and pattern[i - 1] != pattern[j - 1]:
            if shift[j - 1] == 0:
                shift[j - 1] = j - i
            j = border_pos[j]
        i -= 1
        j -= 1
        border_pos[i] = j

    # Caso 2: el sufijo coincide con un prefijo del patrón.
    j = border_pos[0]
    for i in range(m):
        if shift[i] == 0:
            shift[i] = j
        if i == j:
            j = border_pos[j]

    return shift


def boyer_moore_search(text: str, pattern: str) -> list[int]:
    """
    Busca todas las ocurrencias de pattern en text usando Boyer-Moore.

    Combina las reglas del mal carácter y del buen sufijo, tomando el
    máximo de ambos saltos en cada paso.

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

    bad_char = _compute_bad_character_table(pattern)
    good_suffix = _compute_good_suffix_table(pattern)
    occurrences = []

    s = 0  # Desplazamiento del patrón respecto al texto.
    while s <= n - m:
        j = m - 1

        # Comparar de derecha a izquierda.
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1

        if j < 0:
            # Coincidencia completa encontrada.
            occurrences.append(s)
            # Saltar usando la regla del buen sufijo para desplazar.
            s += good_suffix[0]
        else:
            # Discrepancia en la posición j.
            # Regla del mal carácter.
            bad_char_shift = j - bad_char.get(text[s + j], -1)
            # Regla del buen sufijo.
            good_suffix_shift = good_suffix[j]
            # Tomar el máximo de ambos saltos.
            s += max(bad_char_shift, good_suffix_shift)

    return occurrences
