"""Generador de logs sintéticos para el benchmark.

No utiliza logs reales ni datos personales. Las IPs pertenecen al bloque
de documentación 192.0.2.0/24 (TEST-NET-1), los tokens son ficticios y los
timestamps son sintéticos.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

FAKE_IP_PREFIX = "192.0.2."
SYNTHETIC_INDICATOR = "/admin/export"

_PATHS = [
    "/login",
    "/api/v1/orders",
    "/admin/export",
    "/static/app.js",
    "/health",
    "/api/v1/users",
]
_METHODS = ["GET", "POST", "PUT", "DELETE"]
_STATUS_CODES = [200, 200, 200, 301, 400, 401, 403, 404, 500]
_TOKEN_ALPHABET = "0123456789ABCDEF"


def _fake_ip(rng: random.Random) -> str:
    """IP ficticia dentro de 192.0.2.0/24 (documentación, no enrutable)."""
    return f"{FAKE_IP_PREFIX}{rng.randint(1, 254)}"


def _fake_token(rng: random.Random) -> str:
    """Token ficticio, sin relación con credenciales reales."""
    suffix = "".join(rng.choice(_TOKEN_ALPHABET) for _ in range(16))
    return f"FAKE-TOKEN-{suffix}"


def _timestamp(index: int) -> str:
    """Timestamp sintético e incremental."""
    base = datetime(2025, 1, 1, tzinfo=timezone.utc)
    value = base + timedelta(seconds=index * 3)
    return value.isoformat().replace("+00:00", "Z")


def generate_log_corpus(
    n: int,
    rng: random.Random | None = None,
    indicator: str = SYNTHETIC_INDICATOR,
) -> str:
    """Genera un corpus de logs sintéticos de al menos ``n`` caracteres.

    El indicador se inserta periódicamente para que el benchmark tenga
    coincidencias reales que reportar. El texto se recorta a ``n`` caracteres.
    """
    if n < 0:
        raise ValueError("n debe ser >= 0")
    rng = rng or random.Random(42)
    lines: list[str] = []
    total = 0
    index = 0

    while total < n:
        # Cada 37 líneas se inserta el indicador; el resto usa rutas variadas.
        if index % 37 == 0:
            path = indicator
        else:
            path = rng.choice([p for p in _PATHS if p != indicator])

        line = (
            f"{_timestamp(index)} {_fake_ip(rng)} "
            f"{rng.choice(_METHODS)} {path} "
            f"status={rng.choice(_STATUS_CODES)} "
            f"bytes={rng.randint(100, 50000)} "
            f"token={_fake_token(rng)}"
        )
        lines.append(line)
        total += len(line) + 1
        index += 1

    return ("\n".join(lines) + "\n")[:n]


if __name__ == "__main__":
    sample = generate_log_corpus(500, random.Random(42))
    print(sample)
    print(f"\nLongitud: {len(sample)}")
    print(f"Indicador: {SYNTHETIC_INDICATOR}")
