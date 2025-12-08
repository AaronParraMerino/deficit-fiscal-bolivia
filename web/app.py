"""
Aplicación Web para Simulación de Déficit Fiscal y Deuda Pública de Bolivia
Versión Simplificada - Funcional
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modelo.parametros import ConfiguracionModelo, ESCENARIOS
from src.modelo.modelo_estocastico import ModeloEstocastico
from src.agentes.gobierno import AgenteGobierno
from src.agentes.empresas import AgenteEmpresas
from src.utils.io import DataLoader, generar_reporte_datos

# Configuración de la página
st.set_page_config(
    page_title="Simulador Déficit Fiscal Bolivia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f2f6 0%, #ffffff 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


def inicializar_sesion():
    """Inicializa variables de sesión"""
    if 'configuracion' not in st.session_state:
        st.session_state.configuracion = ConfiguracionModelo()
    
    if 'datos_cargados' not in st.session_state:
        st.session_state.datos_cargados = False
        st.session_state.datos = {}
    
    if 'resultados_simulacion' not in st.session_state:
        st.session_state.resultados_simulacion = None
    
    if 'resultados_montecarlo' not in st.session_state:
        st.session_state.resultados_montecarlo = None


def cargar_datos():
    """Carga los datos desde archivos CSV"""
    try:
        loader = DataLoader("../data/processed")
        datos = loader.cargar_todos()
        
        if len(datos) == 0:
            return False, "No se encontraron archivos CSV en data/processed"
        
        st.session_state.datos = datos
        st.session_state.datos_cargados = True
        
        return True, datos
    except Exception as e:
        return False, str(e)


def crear_agentes(config):
    """Factory para crear instancias de agentes"""
    gobierno = AgenteGobierno(config.gobierno)
    empresas = AgenteEmpresas(config.empresas)
    
    return {
        'gobierno': gobierno,
        'empresas': empresas,
        'hogares': None,
        'sector_financiero': None,
        'sector_externo': None
    }


def main():
    """Función principal de la aplicación"""
    
    inicializar_sesion()
    
    # Header
    st.markdown('<div class="main-header">🇧🇴 Simulador de Déficit Fiscal y Deuda Pública de Bolivia</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    **Modelo Estocástico de Simulación - Periodo 2020-2030**
    
    Sistema de simulación para analizar la dinámica del déficit fiscal y deuda pública bajo incertidumbre.
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Selector de escenario
        escenario_seleccionado = st.selectbox(
            "Escenario de Simulación",
            options=list(ESCENARIOS.keys()),
            format_func=lambda x: x.capitalize()
        )
        
        st.info(ESCENARIOS[escenario_seleccionado]['descripcion'])
        
        if st.button("Aplicar Escenario"):
            config = ConfiguracionModelo()
            if escenario_seleccionado != "base":
                config.actualizar_desde_dict(ESCENARIOS[escenario_seleccionado]['ajustes'])
            st.session_state.configuracion = config
            st.success(f"✓ Escenario '{escenario_seleccionado}' aplicado")
        
        st.markdown("---")
        
        # Cargar datos
        st.subheader("📂 Datos")
        if st.button("Cargar Datos CSV"):
            with st.spinner("Cargando datos..."):
                exito, resultado = cargar_datos()
                if exito:
                    st.success(f"✓ {len(resultado)} datasets cargados")
                else:
                    st.error(f"✗ Error: {resultado}")
        
        if st.session_state.datos_cargados:
            st.info(f"✓ {len(st.session_state.datos)} archivos cargados")
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Datos y Configuración",
        "🎲 Simulación Simple",
        "📈 Simulación Monte Carlo",
        "📋 Resultados"
    ])
    
    # TAB 1: Datos y Configuración
    with tab1:
        st.header("Datos Cargados")
        
        if st.session_state.datos_cargados and len(st.session_state.datos) > 0:
            # Mostrar resumen
            st.subheader("Resumen de Datasets")
            
            datos_info = []
            for nombre, df in st.session_state.datos.items():
                datos_info.append({
                    'Dataset': nombre,
                    'Filas': len(df),
                    'Columnas': len(df.columns),
                    'Año Min': int(df['anio'].min()) if 'anio' in df.columns else 'N/A',
                    'Año Max': int(df['anio'].max()) if 'anio' in df.columns else 'N/A'
                })
            
            df_info = pd.DataFrame(datos_info)
            st.dataframe(df_info, use_container_width=True)
            
            # Selector de dataset
            st.subheader("Vista Detallada")
            dataset_ver = st.selectbox(
                "Seleccionar dataset",
                options=list(st.session_state.datos.keys())
            )
            
            if dataset_ver:
                df_sel = st.session_state.datos[dataset_ver]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Filas", len(df_sel))
                with col2:
                    st.metric("Columnas", len(df_sel.columns))
                with col3:
                    nulos = df_sel.isnull().sum().sum()
                    st.metric("Valores Nulos", nulos)
                
                st.dataframe(df_sel, use_container_width=True)
                
                # Gráfico simple
                if len(df_sel.columns) > 1:
                    col_grafico = st.selectbox(
                        "Columna para graficar",
                        options=[c for c in df_sel.columns if c != 'anio']
                    )
                    
                    if col_grafico and 'anio' in df_sel.columns:
                        fig = px.line(df_sel, x='anio', y=col_grafico,
                                     title=f"Evolución de {col_grafico}")
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("👈 Carga los datos desde el panel lateral")
        
        st.markdown("---")
        st.subheader("⚙️ Parámetros del Modelo")
        
        config = st.session_state.configuracion
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Parámetros Fiscales**")
            config.gobierno.tasa_impositiva_base = st.slider(
                "Tasa Impositiva Base",
                0.0, 0.5, config.gobierno.tasa_impositiva_base, 0.01
            )
            
            config.gobierno.gasto_corriente_base = st.slider(
                "Gasto Corriente (% PIB)",
                0.15, 0.40, config.gobierno.gasto_corriente_base, 0.01
            )
            
            config.gobierno.subsidios_base = st.slider(
                "Subsidios (% PIB)",
                0.0, 0.10, config.gobierno.subsidios_base, 0.01
            )
        
        with col2:
            st.write("**Parámetros Macroeconómicos**")
            config.macroeconomicos.pib_inicial = st.number_input(
                "PIB Inicial (millones USD)",
                10000, 100000, int(config.macroeconomicos.pib_inicial), 1000
            )
            
            config.macroeconomicos.tasa_crecimiento_potencial = st.slider(
                "Tasa Crecimiento Potencial",
                -0.05, 0.10, config.macroeconomicos.tasa_crecimiento_potencial, 0.005
            )
            
            config.sector_externo.precio_gas_base = st.number_input(
                "Precio Gas Base (USD)",
                20, 100, int(config.sector_externo.precio_gas_base), 5
            )
    
    # TAB 2: Simulación Simple
    with tab2:
        st.header("Simulación Estocástica Simple")
        
        st.write("""
        Ejecuta una simulación con los parámetros configurados para ver una posible 
        trayectoria del déficit fiscal y la deuda pública.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            num_periodos = st.number_input(
                "Número de Periodos a Simular",
                4, 80, 40, 4,
                help="4 periodos = 1 año (trimestral)"
            )
        with col2:
            semilla = st.number_input(
                "Semilla Aleatoria",
                0, 9999, 42,
                help="Para reproducibilidad"
            )
        
        if st.button("▶️ Ejecutar Simulación", type="primary", key="sim_simple"):
            with st.spinner("Ejecutando simulación..."):
                try:
                    config = st.session_state.configuracion
                    config.simulacion.semilla_aleatoria = semilla
                    
                    agentes = crear_agentes(config)
                    modelo = ModeloEstocastico(config, agentes)
                    df_resultados = modelo.simular(num_periodos=num_periodos)
                    
                    st.session_state.resultados_simulacion = df_resultados
                    st.success("✓ Simulación completada")
                    
                except Exception as e:
                    st.error(f"Error en simulación: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        
        # Mostrar resultados si existen
        if st.session_state.resultados_simulacion is not None:
            df = st.session_state.resultados_simulacion
            
            st.subheader("📊 Resultados")
            
            # Métricas finales
            if len(df) > 0:
                ultimo = df.iloc[-1]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if 'gob_ratio_deuda_pib' in ultimo:
                        st.metric("Ratio Deuda/PIB Final", 
                                f"{ultimo['gob_ratio_deuda_pib']:.1%}")
                    else:
                        st.metric("Ratio Deuda/PIB Final", "N/A")
                
                with col2:
                    if 'gob_ratio_deficit_pib' in df.columns:
                        st.metric("Déficit/PIB Promedio",
                                f"{df['gob_ratio_deficit_pib'].mean():.1%}")
                    else:
                        st.metric("Déficit/PIB Promedio", "N/A")
                
                with col3:
                    if 'gob_deuda_total' in ultimo:
                        st.metric("Deuda Total Final",
                                f"${ultimo['gob_deuda_total']:.0f}M")
                    else:
                        st.metric("Deuda Total Final", "N/A")
                
                with col4:
                    if 'reservas_internacionales' in ultimo:
                        st.metric("Reservas Finales",
                                f"${ultimo['reservas_internacionales']:.0f}M")
                    else:
                        st.metric("Reservas Finales", "N/A")
                
                # Gráficos
                st.subheader("Evolución Temporal")
                
                if 'gob_ratio_deuda_pib' in df.columns:
                    fig1 = px.line(df, x='periodo', y='gob_ratio_deuda_pib',
                                  title='Ratio Deuda/PIB',
                                  labels={'gob_ratio_deuda_pib': 'Ratio (%)', 
                                         'periodo': 'Periodo'})
                    fig1.add_hline(y=0.6, line_dash="dash", line_color="red",
                                  annotation_text="Límite 60%")
                    st.plotly_chart(fig1, use_container_width=True)
                
                if 'pib' in df.columns:
                    fig2 = px.line(df, x='periodo', y='pib',
                                  title='Evolución del PIB',
                                  labels={'pib': 'PIB (millones USD)', 
                                         'periodo': 'Periodo'})
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Tabla de datos
                with st.expander("📋 Ver Tabla de Datos Completa"):
                    st.dataframe(df, use_container_width=True)
                    
                    # Botón de descarga
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "💾 Descargar CSV",
                        csv,
                        "simulacion_resultados.csv",
                        "text/csv"
                    )
    
    # TAB 3: Monte Carlo
    with tab3:
        st.header("Simulación Monte Carlo")
        
        st.write("""
        Ejecuta múltiples simulaciones para analizar distribuciones de resultados 
        y probabilidades de eventos críticos.
        """)
        
        st.warning("⚠️ **Funcionalidad en desarrollo**: Requiere completar módulo de Monte Carlo")
        
        num_sims = st.number_input(
            "Número de Simulaciones",
            10, 500, 100, 10
        )
        
        if st.button("▶️ Ejecutar Monte Carlo", type="primary", disabled=True):
            st.info("Funcionalidad próximamente disponible")
    
    # TAB 4: Resultados
    with tab4:
        st.header("Análisis de Resultados")
        
        if st.session_state.resultados_simulacion is not None:
            df = st.session_state.resultados_simulacion
            
            st.subheader("📈 Análisis Estadístico")
            
            # Seleccionar variables para analizar
            variables_disponibles = [c for c in df.columns 
                                   if c.startswith('gob_') or c in ['pib', 'reservas_internacionales']]
            
            variable_analizar = st.selectbox(
                "Variable a analizar",
                options=variables_disponibles
            )
            
            if variable_analizar and variable_analizar in df.columns:
                serie = df[variable_analizar].dropna()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Media", f"{serie.mean():.2f}")
                with col2:
                    st.metric("Desv. Estándar", f"{serie.std():.2f}")
                with col3:
                    st.metric("Mediana", f"{serie.median():.2f}")
                
                # Histograma
                fig = px.histogram(serie, nbins=30,
                                  title=f"Distribución de {variable_analizar}")
                st.plotly_chart(fig, use_container_width=True)
                
                # Serie temporal
                fig2 = px.line(df, x='periodo', y=variable_analizar,
                              title=f"Evolución de {variable_analizar}")
                st.plotly_chart(fig2, use_container_width=True)
            
            st.markdown("---")
            st.subheader("💾 Exportar Resultados")
            
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Descargar Resultados CSV",
                csv,
                "resultados_completos.csv",
                "text/csv"
            )
        else:
            st.info("👈 Ejecuta una simulación primero para ver el análisis")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Error en la aplicación: {e}")
        import traceback
        st.code(traceback.format_exc())