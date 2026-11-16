"""
Pruebas unitarias, basadas en propiedades y diferenciales para Boyer-Moore.

Semilla fija: SEED = 42
Referencia diferencial: str.find / re.search
"""
import re
import unittest
from hypothesis import given, settings, strategies as st

from src.boyer_moore import boyer_moore_search

SEED = 42


class TestBoyerMooreUnitarios(unittest.TestCase):
    """Mínimo 5 pruebas unitarias con casos límite."""

    def test_patron_vacio(self):
        """Patrón vacío → lista vacía."""
        self.assertEqual(boyer_moore_search("abcabc", ""), [])

    def test_texto_vacio(self):
        """Texto vacío con patrón no vacío → lista vacía."""
        self.assertEqual(boyer_moore_search("", "abc"), [])

    def test_ambos_vacios(self):
        """Ambos vacíos → lista vacía."""
        self.assertEqual(boyer_moore_search("", ""), [])

    def test_patron_mas_largo_que_texto(self):
        """Patrón más largo que el texto → lista vacía."""
        self.assertEqual(boyer_moore_search("abc", "abcdef"), [])

    def test_coincidencia_exacta(self):
        """Texto idéntico al patrón → [0]."""
        self.assertEqual(boyer_moore_search("abc", "abc"), [0])

    def test_multiples_ocurrencias(self):
        """Múltiples ocurrencias."""
        self.assertEqual(boyer_moore_search("abcabcabc", "abc"), [0, 3, 6])

    def test_ocurrencias_superpuestas(self):
        """Ocurrencias superpuestas: 'aba' en 'abababa'."""
        self.assertEqual(boyer_moore_search("abababa", "aba"), [0, 2, 4])

    def test_sin_coincidencias(self):
        """Sin coincidencias."""
        self.assertEqual(boyer_moore_search("abcdefgh", "xyz"), [])

    def test_un_solo_caracter(self):
        """Un solo carácter como patrón."""
        self.assertEqual(boyer_moore_search("aabacba", "a"), [0, 1, 3, 6])

    def test_patron_al_final(self):
        """Ocurrencia al final del texto."""
        self.assertEqual(boyer_moore_search("xyzabcdef", "abcdef"), [3])

    def test_patron_caracter_unico_repetido(self):
        """Patrón con un solo carácter repetido."""
        self.assertEqual(boyer_moore_search("aaaaaa", "aa"), [0, 1, 2, 3, 4])


class TestBoyerMoorePropiedades(unittest.TestCase):
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
        Propiedad: Boyer-Moore encuentra exactamente las mismas posiciones
        que str.find iterando (con superposiciones).
        """
        bm_results = boyer_moore_search(text, pattern)
        ref_results = []
        start = 0
        while True:
            idx = text.find(pattern, start)
            if idx == -1:
                break
            ref_results.append(idx)
            start = idx + 1
        self.assertEqual(bm_results, ref_results)

    @given(
        text=st.text(alphabet="abc", min_size=5, max_size=200),
        pattern=st.text(alphabet="abc", min_size=1, max_size=20),
    )
    @settings(max_examples=200, database=None, derandomize=True)
    def test_orden_y_validacion(self, text, pattern):
        """
        Propiedad: Índices en orden ascendente y cada subcadena coincide con el patrón.
        """
        results = boyer_moore_search(text, pattern)
        m = len(pattern)
        n = len(text)

        # Orden ascendente.
        for i in range(1, len(results)):
            self.assertGreater(results[i], results[i - 1])

        # Validez de cada índice.
        for idx in results:
            self.assertGreaterEqual(idx, 0)
            self.assertLessEqual(idx, n - m)
            self.assertEqual(text[idx:idx + m], pattern)


class TestBoyerMooreDiferencial(unittest.TestCase):
    """Prueba diferencial contra str.find."""

    def test_diferencial_vs_str_find(self):
        """
        Comparar Boyer-Moore contra str.find en un conjunto determinista.
        """
        import random
        rng = random.Random(SEED)
        alfabeto = "abcdefgh"

        for _ in range(50):
            n = rng.randint(10, 300)
            m = rng.randint(1, 20)
            text = "".join(rng.choice(alfabeto) for _ in range(n))
            pattern = "".join(rng.choice(alfabeto) for _ in range(m))

            bm_results = boyer_moore_search(text, pattern)

            ref_results = []
            start = 0
            while True:
                idx = text.find(pattern, start)
                if idx == -1:
                    break
                ref_results.append(idx)
                start = idx + 1

            self.assertEqual(bm_results, ref_results,
                             f"Fallo en text={text[:50]!r}..., pattern={pattern!r}")

    def test_diferencial_vs_regex(self):
        """
        Comparar Boyer-Moore contra re.finditer con lookahead.
        """
        import random
        rng = random.Random(SEED + 1)
        alfabeto = "ab"

        for _ in range(30):
            n = rng.randint(10, 100)
            m = rng.randint(1, 10)
            text = "".join(rng.choice(alfabeto) for _ in range(n))
            pattern = "".join(rng.choice(alfabeto) for _ in range(m))

            bm_results = boyer_moore_search(text, pattern)

            escaped = re.escape(pattern)
            ref_results = [m.start() for m in re.finditer(f"(?={escaped})", text)]

            self.assertEqual(bm_results, ref_results,
                             f"Fallo regex en text={text!r}, pattern={pattern!r}")


if __name__ == "__main__":
    unittest.main()
