# Modelación Estocástica del Déficit Fiscal y la Dinámica de la Deuda Pública en Bolivia

Este proyecto implementa un modelo de simulación estocástica para analizar la dinámica del déficit fiscal y la deuda pública en Bolivia durante el período 2020–2025, bajo condiciones de incertidumbre económica.

## Objetivo del Proyecto

Desarrollar un modelo matemático estocástico y una interfaz web interactiva que permita simular y visualizar escenarios de sostenibilidad fiscal, considerando variables clave como ingresos públicos, gastos estatales, subsidios, precios internacionales de recursos naturales y acumulación de deuda.

## Componentes del Modelo

El modelo incluye los siguientes agentes y variables económicas:

- **Gobierno**: decisor de políticas fiscales y gasto público.
- **Empresas**: productores de gas y minerales.
- **Hogares**: consumo y demanda interna.
- **Sector financiero**: tasas de interés y financiamiento.
- **Sector externo**: precios internacionales, tipo de cambio, riesgo país.
- **Variables estocásticas**: precios del gas/minerales, demanda energética, recaudación tributaria.

## Características del Proyecto

- **Modelo estocástico**: simulación de escenarios bajo incertidumbre.
- **Interfaz web interactiva**: desarrollada con **Streamlit**.
- **Visualizaciones dinámicas**: gráficos de evolución del déficit, deuda, ingresos y gastos.
- **Análisis de sensibilidad**: permite ajustar parámetros y observar impactos en tiempo real.
- **Repositorio de datos**: fuentes verificables y documentadas.

## Instalación y Ejecución

### Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos para ejecutar

1. Clonar el repositorio:
```bash
git clone https://github.com/AaronParraMerino/deficit-fiscal-bolivia.git
```
```bash
cd deficit-fiscal-bolivia
```
2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```
3. 

## Uso del proyecto
```bash
cd web
```
```bash
streamlit run app.py
```
