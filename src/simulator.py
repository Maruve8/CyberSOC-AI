from pathlib import Path

import pandas as pd


# ruta al dataset procesado
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "cic_ids2017_clean.parquet"


def load_simulation_sample(
    benign_count=10,
    attack_count=10,
    random_state=42
):
    """
    Crea una muestra pequeña de tráfico para la demo.

    Incluye registros benignos y ataques reales extraídos
    del dataset CIC-IDS2017 ya procesado.
    """

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"No se encuentra el dataset procesado: {DATA_FILE}"
        )

    # cargar el dataset procesado
    df = pd.read_parquet(DATA_FILE)

    #separar tráfico benigno y de ataque
    benign = df[df["is_attack"] == 0]
    attacks = df[df["is_attack"] == 1]

    # coger una muestra reproducible de cada grupo
    benign_sample = benign.sample(
        n=min(benign_count, len(benign)),
        random_state=random_state
    )

    attack_sample = attacks.sample(
        n=min(attack_count, len(attacks)),
        random_state=random_state
    )

    #mezclar ambos para simular un flujo de eventos
    simulation = pd.concat(
        [benign_sample, attack_sample],
        ignore_index=True
    )

    simulation = simulation.sample(
        frac=1,
        random_state=random_state
    ).reset_index(drop=True)

    return simulation