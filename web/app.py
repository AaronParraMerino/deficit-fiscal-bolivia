# web/app.py
import streamlit as st
from src.simulacion.montecarlo import correr_simulacion
from src.simulacion.escenarios import get_escenario

st.set_page_config(page_title="Déficit Fiscal Bolivia 2020–2025", layout="wide")

st.title("Modelo Estocástico del Déficit Fiscal y Deuda Pública en Bolivia")

escenario_nombre = st.sidebar.selectbox(
    "Escenario",
    ["Base", "Pesimista", "Optimista"]
)

N = st.sidebar.slider("Número de corridas Monte Carlo (N)", 100, 5000, 1000, step=100)

escenario = get_escenario(escenario_nombre)

if st.button("Ejecutar simulación"):
    resultados = correr_simulacion(escenario, N=N)
    # aquí llamas a funciones de graficos y análisis
