import sys
from pathlib import Path

# Añadir la carpeta raíz del proyecto al PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import streamlit as st
import matplotlib.pyplot as plt

from src.simulacion.escenarios import get_escenario
from src.simulacion.montecarlo import correr_simulacion

st.set_page_config(page_title="Déficit y Deuda Pública Bolivia", layout="wide")

st.title("Modelo Estocástico del Déficit Fiscal y Deuda Pública (Bolivia 2020–2025)")

st.sidebar.header("Parámetros de simulación")

escenario_nombre = st.sidebar.selectbox(
    "Escenario",
    ["Base", "Pesimista", "Optimista"]
)

N = st.sidebar.slider("Número de corridas Monte Carlo", 100, 5000, 1000, step=100)

if st.button("Ejecutar simulación"):
    param = get_escenario(escenario_nombre)
    resumen = correr_simulacion(param, N=N)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Deuda/PIB esperada")
        fig, ax = plt.subplots()
        ax.plot(resumen["anio"], resumen["deuda_pib_media"])
        ax.fill_between(
            resumen["anio"],
            resumen["deuda_pib_p5"],
            resumen["deuda_pib_p95"],
            alpha=0.3
        )
        ax.set_xlabel("Año")
        ax.set_ylabel("Deuda/PIB (%)")
        st.pyplot(fig)

    with col2:
        st.subheader("PIB medio")
        fig2, ax2 = plt.subplots()
        ax2.plot(resumen["anio"], resumen["pib_medio"])
        ax2.set_xlabel("Año")
        ax2.set_ylabel("PIB (índice)")
        st.pyplot(fig2)
