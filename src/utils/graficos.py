"""
Funciones auxiliares para gráficos con matplotlib.
"""

import matplotlib.pyplot as plt
import pandas as pd

def grafico_deuda_con_bandas(df: pd.DataFrame):
    fig, ax = plt.subplots()
    ax.plot(df["anio"], df["deuda_pib_media"], label="Media")
    if "deuda_pib_p5" in df.columns and "deuda_pib_p95" in df.columns:
        ax.fill_between(
            df["anio"],
            df["deuda_pib_p5"],
            df["deuda_pib_p95"],
            alpha=0.3,
            label="P5–P95",
        )
    ax.set_xlabel("Año")
    ax.set_ylabel("Deuda/PIB (%)")
    ax.legend()
    return fig
