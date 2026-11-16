"""
Rabin-Karp - Algoritmo de búsqueda de patrones con hashing rodante.

Complejidad:
    - Preprocesamiento (hash del patrón): O(m)
    - Búsqueda mejor caso: O(n + m)
    - Búsqueda peor caso: O(n * m)  (cuando hay muchas colisiones de hash)

El algoritmo utiliza un hash rodante (rolling hash) para comparar ventanas
del texto con el patrón en tiempo O(1) amortizado. Cuando el hash coincide,
se verifica carácter por carácter para descartar falsos positivos.

Se usa aritmética modular con un primo grande para reducir colisiones.
"""

# Constantes del algoritmo.
DEFAULT_BASE = 256       # Tamaño del alfabeto (ASCII extendido).
DEFAULT_MOD = 10**9 + 7  # Primo grande para aritmética modular.


def _rolling_hash(text: str, pattern: str, base: int = DEFAULT_BASE,
                  mod: int = DEFAULT_MOD) -> tuple[int, int, int]:
    """
    Calcula el hash inicial del patrón y de la primera ventana del texto.

    Returns:
        Tupla (hash_pattern, hash_window, power) donde power = base^(m-1) mod mod.
    """
    m = len(pattern)
    hash_p = 0
    hash_w = 0

    # hash = sum(ord(c_i) * base^(m-1-i)) mod mod, estilo Horner.
    for i in range(m):
        hash_p = (hash_p * base + ord(pattern[i])) % mod
        hash_w = (hash_w * base + ord(text[i])) % mod

    power = pow(base, m - 1, mod)
    return hash_p, hash_w, power


def rabin_karp_search(text: str, pattern: str, base: int = DEFAULT_BASE,
                      mod: int = DEFAULT_MOD) -> list[int]:
    """
    Busca todas las ocurrencias de pattern en text usando Rabin-Karp.

    Args:
        text: Cadena donde buscar.
        pattern: Cadena a encontrar.
        base: Base para la función hash polinomial.
        mod: Módulo primo para aritmética modular.

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

    hash_p, hash_w, power = _rolling_hash(text, pattern, base, mod)
    occurrences = []

    # Verificar la primera ventana.
    if hash_p == hash_w and text[:m] == pattern:
        occurrences.append(0)

    # Deslizar la ventana a lo largo del texto.
    for i in range(1, n - m + 1):
        # Actualizar hash: remover carácter anterior, agregar nuevo.
        hash_w = (hash_w - ord(text[i - 1]) * power) % mod
        hash_w = (hash_w * base + ord(text[i + m - 1])) % mod
        # Asegurar valor no negativo (Python lo maneja, pero por claridad).
        hash_w = hash_w % mod

        # Verificación: si hash coincide, confirmar carácter a carácter.
        if hash_p == hash_w and text[i:i + m] == pattern:
            occurrences.append(i)

    return occurrences
