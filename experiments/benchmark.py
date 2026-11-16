"""Medición piloto pareada de KMP, Rabin-Karp y Boyer-Moore.

Escenarios:
  - Texto aleatorio uniforme.
  - Corpus sintético de logs (IPs 192.0.2.x, timestamps y tokens ficticios).

Diseño:
  - 3 tamaños de entrada: 1_000, 10_000 y 100_000 caracteres.
  - 3 repeticiones por algoritmo, tamaño y escenario.
  - Semilla fija 42.
  - Las mismas entradas se reutilizan para los tres algoritmos.
  - Warm-up y verificación cruzada antes de medir.
  - `time.perf_counter()` mide tiempo de pared, no CPU puro.

Uso:
    python experiments/benchmark.py
"""
from __future__ import annotations

import json
import os
import platform
import random
import statistics
import sys
import time
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

import pandas as pd
import matplotlib

matplotlib.use("Agg")  # Backend sin GUI para entornos headless.
import matplotlib.pyplot as plt  # noqa: E402

# Añadir la raíz del proyecto al path antes de importar `src` y `experiments`.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.kmp import kmp_search  # noqa: E402
from src.rabin_karp import rabin_karp_search  # noqa: E402
from src.boyer_moore import boyer_moore_search  # noqa: E402
from experiments.generar_logs_sinteticos import (  # noqa: E402
    FAKE_IP_PREFIX,
    SYNTHETIC_INDICATOR,
    generate_log_corpus,
)

# -- Configuración experimental ------------------------------------------------
SEED = 42
SIZES = [1_000, 10_000, 100_000]
REPETITIONS = 3
PATTERN_SIZE = 20
ALPHABET = "abcdefghij"
OUTPUT_DIR = ROOT / "experiments" / "results"

SCENARIOS = {
    "random": "Texto aleatorio uniforme sobre el alfabeto abcdefghij.",
    "synthetic_logs": (
        "Corpus sintético de logs con IPs 192.0.2.x, timestamps ficticios, "
        "tokens falsos y paths; no son logs reales."
    ),
}

RELEVANT_PACKAGES = [
    "pytest",
    "hypothesis",
    "matplotlib",
    "pandas",
    "openpyxl",
    "psutil",
    "numpy",
]


def get_pip_freeze() -> list[str]:
    """Devuelve las distribuciones instaladas en formato pip freeze."""
    rows = []
    for dist in metadata.distributions():
        name = dist.metadata.get("Name")
        if name:
            rows.append(f"{name}=={dist.version}")
    return sorted(set(rows), key=str.lower)


def get_relevant_versions() -> dict[str, str | None]:
    """Versiones de las librerías relevantes para el experimento."""
    versions: dict[str, str | None] = {}
    for package in RELEVANT_PACKAGES:
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = None
    return versions


def get_environment_info() -> dict:
    """Recopila ambiente, timestamp y versiones de paquetes."""
    import psutil

    ram = psutil.virtual_memory()
    freeze = get_pip_freeze()
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        "python_version_short": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "ram_total_gb": round(ram.total / (1024**3), 2),
        "ram_available_gb": round(ram.available / (1024**3), 2),
        "pip_freeze_relevant": get_relevant_versions(),
        "pip_freeze_total": len(freeze),
    }


def generate_text(n: int, rng: random.Random) -> str:
    """Genera un texto aleatorio de longitud n."""
    return "".join(rng.choice(ALPHABET) for _ in range(n))


def generate_pattern(m: int, rng: random.Random) -> str:
    """Genera un patrón aleatorio de longitud m."""
    return "".join(rng.choice(ALPHABET) for _ in range(m))


def build_inputs() -> dict[str, dict[int, tuple[str, str]]]:
    """Precalcula una única entrada por escenario y tamaño.

    Las mismas tuplas (texto, patrón) se reutilizan para los tres algoritmos.
    """
    rng_random = random.Random(SEED)
    rng_logs = random.Random(SEED + 1)
    inputs: dict[str, dict[int, tuple[str, str]]] = {
        "random": {},
        "synthetic_logs": {},
    }

    for n in SIZES:
        inputs["random"][n] = (
            generate_text(n, rng_random),
            generate_pattern(PATTERN_SIZE, rng_random),
        )
        inputs["synthetic_logs"][n] = (
            generate_log_corpus(n, rng_logs),
            SYNTHETIC_INDICATOR,
        )

    return inputs


def measure_algorithm(
    func, text: str, pattern: str, reps: int
) -> tuple[list[float], list[int]]:
    """Mide tiempo de pared de `reps` ejecuciones y devuelve el último resultado."""
    times: list[float] = []
    result: list[int] = []
    for _ in range(reps):
        start = time.perf_counter()
        result = func(text, pattern)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    return times, result


def run_benchmark() -> tuple[dict, dict]:
    """Ejecuta el benchmark completo en ambos escenarios."""
    env = get_environment_info()
    inputs = build_inputs()

    print("=" * 78)
    print("BENCHMARK PAREADO - ALGORITMOS DE BUSQUEDA DE PATRONES")
    print("=" * 78)
    print(f"Python:       {env['python_version_short']}")
    print(f"Plataforma:   {env['platform']}")
    print(f"CPU:          {env['processor']} ({env['cpu_count']} cores)")
    print(f"RAM total:    {env['ram_total_gb']} GB")
    print(f"Timestamp:    {env['timestamp_utc']}")
    print(f"Seed:         {SEED}")
    print("=" * 78)

    algorithms = {
        "KMP": kmp_search,
        "Rabin-Karp": rabin_karp_search,
        "Boyer-Moore": boyer_moore_search,
    }

    results: dict[str, dict[str, dict[int, dict]]] = {}

    for scenario, description in SCENARIOS.items():
        print(f"\n### Escenario: {scenario}")
        print(description)
        scenario_results: dict[str, dict[int, dict]] = {
            name: {} for name in algorithms
        }

        for n in SIZES:
            text, pattern = inputs[scenario][n]

            # Verificación cruzada: los tres deben devolver exactamente lo mismo.
            check = {name: fn(text, pattern) for name, fn in algorithms.items()}
            unique = {tuple(value) for value in check.values()}
            if len(unique) != 1:
                raise RuntimeError(
                    f"Discrepancia entre algoritmos en {scenario}, n={n}: "
                    f"{ {name: len(value) for name, value in check.items()} }"
                )

            for algo_name, func in algorithms.items():
                func(text, pattern)  # warm-up, no medido
                times, result = measure_algorithm(
                    func, text, pattern, REPETITIONS
                )
                mean_t = statistics.mean(times)
                std_t = (
                    statistics.stdev(times) if len(times) > 1 else 0.0
                )
                scenario_results[algo_name][n] = {
                    "times": times,
                    "mean": mean_t,
                    "std": std_t,
                    "n": n,
                    "m": len(pattern),
                    "matches": len(result),
                }
                print(
                    f"  {algo_name:12s} n={n:>7,} m={len(pattern):>2} "
                    f"matches={len(result):>4} "
                    f"media={mean_t:.6f}s std={std_t:.6f}s"
                )

        results[scenario] = scenario_results

    # Guardar JSON.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    freeze = get_pip_freeze()
    (OUTPUT_DIR / "pip_freeze.txt").write_text(
        "\n".join(freeze) + "\n", encoding="utf-8"
    )

    results_path = OUTPUT_DIR / "benchmark_results.json"
    payload = {
        "environment": env,
        "config": {
            "seed": SEED,
            "sizes": SIZES,
            "repetitions": REPETITIONS,
            "pattern_size": PATTERN_SIZE,
            "alphabet": ALPHABET,
            "scenarios": list(SCENARIOS),
            "scenario_descriptions": SCENARIOS,
            "time_metric": "time.perf_counter() (reloj de pared, segundos)",
            "synthetic_log_indicator": SYNTHETIC_INDICATOR,
            "synthetic_log_ip_prefix": FAKE_IP_PREFIX,
            "synthetic_logs_are_real": False,
        },
        "scenarios": {
            scenario: {
                "description": SCENARIOS[scenario],
                "results": results[scenario],
            }
            for scenario in SCENARIOS
        },
    }
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"\nResultados guardados en: {results_path}")

    # Guardar Excel.
    xlsx_path = OUTPUT_DIR / "benchmark_results.xlsx"
    save_to_excel(results, env, xlsx_path)
    print(f"Resultados guardados en: {xlsx_path}")

    # Generar gráfica.
    generate_plot(results)
    return results, env


def save_to_excel(results: dict, env: dict, xlsx_path: Path) -> None:
    """Guarda ambiente, configuración, resumen y detalle en Excel."""
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        env_rows = [
            {"Campo": "Timestamp UTC", "Valor": env["timestamp_utc"]},
            {"Campo": "Python", "Valor": env["python_version"]},
            {"Campo": "Plataforma", "Valor": env["platform"]},
            {"Campo": "Procesador", "Valor": env["processor"]},
            {"Campo": "Núcleos CPU", "Valor": env["cpu_count"]},
            {"Campo": "RAM Total (GB)", "Valor": env["ram_total_gb"]},
            {"Campo": "RAM Disponible (GB)", "Valor": env["ram_available_gb"]},
            {"Campo": "Seed", "Valor": SEED},
            {"Campo": "Tamaños de entrada", "Valor": str(SIZES)},
            {"Campo": "Repeticiones", "Valor": REPETITIONS},
            {"Campo": "Tamaño del patrón", "Valor": PATTERN_SIZE},
            {"Campo": "Alfabeto aleatorio", "Valor": ALPHABET},
            {"Campo": "Indicador sintético", "Valor": SYNTHETIC_INDICATOR},
            {"Campo": "Métrica de tiempo", "Valor": "perf_counter (pared)"},
        ]
        pd.DataFrame(env_rows).to_excel(
            writer, sheet_name="Ambiente", index=False
        )

        config_rows = [
            {"Tipo": "Escenario", "Nombre": scenario, "Valor": description}
            for scenario, description in SCENARIOS.items()
        ]
        config_rows += [
            {"Tipo": "Paquete", "Nombre": name, "Valor": version}
            for name, version in env["pip_freeze_relevant"].items()
        ]
        pd.DataFrame(config_rows).to_excel(
            writer, sheet_name="Configuracion", index=False
        )

        resumen_rows = []
        detalle_rows = []
        for scenario, scenario_data in results.items():
            for algo_name, data in scenario_data.items():
                for n in sorted(data):
                    row = data[n]
                    resumen_rows.append(
                        {
                            "Escenario": scenario,
                            "Algoritmo": algo_name,
                            "n (texto)": n,
                            "m (patrón)": row["m"],
                            "Coincidencias": row["matches"],
                            "Media (s)": row["mean"],
                            "Std (s)": row["std"],
                        }
                    )
                    for i, t in enumerate(row["times"]):
                        detalle_rows.append(
                            {
                                "Escenario": scenario,
                                "Algoritmo": algo_name,
                                "n (texto)": n,
                                "m (patrón)": row["m"],
                                "Repetición": i + 1,
                                "Tiempo (s)": t,
                            }
                        )

        pd.DataFrame(resumen_rows).to_excel(
            writer, sheet_name="Resumen", index=False
        )
        pd.DataFrame(detalle_rows).to_excel(
            writer, sheet_name="Detalle", index=False
        )


def generate_plot(results: dict) -> None:
    """Genera una gráfica de dos paneles, uno por escenario."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=False)
    markers = {"KMP": "o", "Rabin-Karp": "s", "Boyer-Moore": "^"}
    colors = {
        "KMP": "#1f77b4",
        "Rabin-Karp": "#ff7f0e",
        "Boyer-Moore": "#2ca02c",
    }

    for ax, scenario in zip(axes, SCENARIOS):
        scenario_data = results[scenario]
        for algo_name, data in scenario_data.items():
            sizes = sorted(data)
            means = [data[s]["mean"] for s in sizes]
            stds = [data[s]["std"] for s in sizes]
            ax.errorbar(
                sizes,
                means,
                yerr=stds,
                marker=markers.get(algo_name, "x"),
                color=colors.get(algo_name, "#333"),
                label=algo_name,
                capsize=5,
                linewidth=2,
                markersize=8,
            )
            # Anotar solo el tamaño mayor para evitar solapamientos en n=1000.
            ax.annotate(
                f"{data[sizes[-1]]['mean']:.5f}s",
                (sizes[-1], data[sizes[-1]]["mean"]),
                textcoords="offset points",
                xytext=(0, 12),
                fontsize=8,
                ha="center",
            )

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Tamaño del texto (n)", fontsize=11)
        ax.set_ylabel("Tiempo de pared (s)", fontsize=11)
        ax.set_title(scenario.replace("_", " ").title(), fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, which="both", alpha=0.25)
        ax.tick_params(axis="both", labelsize=9)
        ax.text(
            0.02,
            0.02,
            "time.perf_counter()",
            transform=ax.transAxes,
            fontsize=8,
            color="#555",
        )

    fig.suptitle(
        "Benchmark pareado: búsqueda de patrones\n"
        "(KMP vs Rabin-Karp vs Boyer-Moore)",
        fontsize=14,
        fontweight="bold",
    )
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plot_path = OUTPUT_DIR / "benchmark_plot.png"
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)
    print(f"Gráfica guardada en:    {plot_path}")


if __name__ == "__main__":
    run_benchmark()
