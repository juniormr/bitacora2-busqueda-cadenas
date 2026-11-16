"""
Pruebas unitarias, basadas en propiedades y diferenciales para KMP.

Semilla fija: SEED = 42
Referencia diferencial: str.find / re.search
"""
import re
import unittest
from hypothesis import given, settings, strategies as st

from src.kmp import kmp_search, compute_failure

SEED = 42


class TestKMPUnitarios(unittest.TestCase):
    """Mínimo 5 pruebas unitarias con casos límite."""

    def test_patron_vacio(self):
        """Patrón vacío → lista vacía."""
        self.assertEqual(kmp_search("abcabc", ""), [])

    def test_texto_vacio(self):
        """Texto vacío con patrón no vacío → lista vacía."""
        self.assertEqual(kmp_search("", "abc"), [])

    def test_ambos_vacios(self):
        """Ambos vacíos → lista vacía."""
        self.assertEqual(kmp_search("", ""), [])

    def test_patron_mas_largo_que_texto(self):
        """Patrón más largo que el texto → lista vacía."""
        self.assertEqual(kmp_search("abc", "abcdef"), [])

    def test_coincidencia_exacta(self):
        """Texto idéntico al patrón → [0]."""
        self.assertEqual(kmp_search("abc", "abc"), [0])

    def test_multiples_ocurrencias(self):
        """Múltiples ocurrencias."""
        self.assertEqual(kmp_search("abcabcabc", "abc"), [0, 3, 6])

    def test_ocurrencias_superpuestas(self):
        """Ocurrencias superpuestas: 'aba' en 'abababa'."""
        self.assertEqual(kmp_search("abababa", "aba"), [0, 2, 4])

    def test_sin_coincidencias(self):
        """Sin coincidencias."""
        self.assertEqual(kmp_search("abcdefgh", "xyz"), [])

    def test_un_solo_caracter(self):
        """Un solo carácter como patrón."""
        self.assertEqual(kmp_search("aabacba", "a"), [0, 1, 3, 6])

    def test_caracter_no_presente(self):
        """Carácter no presente en el texto."""
        self.assertEqual(kmp_search("abcdef", "z"), [])

    def test_sensible_a_mayusculas(self):
        """La búsqueda es exacta y distingue mayúsculas de minúsculas."""
        self.assertEqual(kmp_search("AbcabcABC", "abc"), [3])
        self.assertEqual(kmp_search("AbcabcABC", "ABC"), [6])
        self.assertEqual(kmp_search("AbcabcABC", "Abc"), [0])

    def test_patron_al_final(self):
        """Ocurrencia exactamente al final del texto."""
        self.assertEqual(kmp_search("xyzabcdef", "abcdef"), [3])


class TestKMPPropiedades(unittest.TestCase):
    """Pruebas basadas en propiedades con Hypothesis."""

    @given(
        text=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126),
                     min_size=0, max_size=200),
        pattern=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126),
                        min_size=1, max_size=50),
    )
    @settings(max_examples=200, database=None, derandomize=True)
    def test_coincide_con_str_find(self, text, pattern):
        """
        Propiedad: KMP encuentra exactamente las mismas posiciones
        que str.find en todas sus iteraciones.
        """
        kmp_results = kmp_search(text, pattern)
        # Reconstruir resultados con str.find.
        ref_results = []
        start = 0
        while True:
            idx = text.find(pattern, start)
            if idx == -1:
                break
            ref_results.append(idx)
            start = idx + 1  # Permitir ocurrencias superpuestas.
        self.assertEqual(kmp_results, ref_results)

    @given(
        pattern=st.text(alphabet="ab", min_size=1, max_size=100),
    )
    @settings(max_examples=200, database=None, derandomize=True)
    def test_invariante_funcion_de_fallo(self, pattern):
        """
        Invariante de la función de fallo:
        1. fail[0] == 0
        2. Para todo i: 0 <= fail[i] <= i  (y fail[i] < i si i > 0)
        3. pattern[0:fail[i]] == pattern[i - fail[i] + 1:i + 1]
        4. fail[i] es el máximo que cumple la propiedad 3.
        """
        fail = compute_failure(pattern)
        m = len(pattern)
        self.assertEqual(len(fail), m)

        for i in range(m):
            self.assertGreaterEqual(fail[i], 0)
            self.assertLessEqual(fail[i], i)

            if fail[i] > 0:
                prefijo = pattern[:fail[i]]
                sufijo = pattern[i - fail[i] + 1:i + 1]
                self.assertEqual(prefijo, sufijo,
                                 f"Posición {i}: prefijo={prefijo!r} != sufijo={sufijo!r}")

                # Verificar que es el máximo.
                for k in range(fail[i] + 1, i + 1):
                    if k > 0:
                        p = pattern[:k]
                        s = pattern[i - k + 1:i + 1]
                        self.assertNotEqual(p, s,
                                            f"Posición {i}: fail[i]={fail[i]} no es máximo; k={k} también cumple.")


class TestKMPDiferencial(unittest.TestCase):
    """Prueba diferencial contra str.find."""

    def test_diferencial_vs_str_find(self):
        """
        Comparar KMP contra str.find en un conjunto determinista de entradas.
        """
        import random
        rng = random.Random(SEED)
        alfabeto = "abcdefgh"

        for _ in range(50):
            n = rng.randint(10, 300)
            m = rng.randint(1, 20)
            text = "".join(rng.choice(alfabeto) for _ in range(n))
            pattern = "".join(rng.choice(alfabeto) for _ in range(m))

            kmp_results = kmp_search(text, pattern)

            # Referencia con str.find (permitiendo superposiciones).
            ref_results = []
            start = 0
            while True:
                idx = text.find(pattern, start)
                if idx == -1:
                    break
                ref_results.append(idx)
                start = idx + 1

            self.assertEqual(kmp_results, ref_results,
                             f"Fallo en text={text!r}, pattern={pattern!r}")

    def test_diferencial_vs_regex(self):
        """
        Comparar KMP contra re.finditer en cadenas sin regex especial.
        Nota: re no encuentra superpuestos por defecto; usamos lookahead.
        """
        import random
        rng = random.Random(SEED + 1)
        alfabeto = "ab"

        for _ in range(30):
            n = rng.randint(10, 100)
            m = rng.randint(1, 10)
            text = "".join(rng.choice(alfabeto) for _ in range(n))
            pattern = "".join(rng.choice(alfabeto) for _ in range(m))

            kmp_results = kmp_search(text, pattern)

            # Referencia con regex usando lookahead para superposiciones.
            escaped = re.escape(pattern)
            ref_results = [m.start() for m in re.finditer(f"(?={escaped})", text)]

            self.assertEqual(kmp_results, ref_results,
                             f"Fallo regex en text={text!r}, pattern={pattern!r}")


if __name__ == "__main__":
    unittest.main()
