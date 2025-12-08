"""
Modelo Estocástico de Déficit Fiscal y Deuda Pública
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class EstadoEconomia:
    """Estado agregado de la economía"""
    periodo: int = 0
    año: int = 2020
    trimestre: int = 1
    
    # Variables macroeconómicas
    pib: float = 0.0
    tasa_crecimiento_pib: float = 0.0
    inflacion: float = 0.0
    tipo_cambio: float = 6.96
    reservas_internacionales: float = 0.0
    
    # Precios internacionales
    precio_gas: float = 50.0
    precio_minerales: float = 2500.0
    
    # Producción
    produccion_gas: float = 100.0
    produccion_minerales: float = 100.0
    
    # Tasas de interés
    tasa_interes_domestica: float = 0.06
    tasa_interes_internacional: float = 0.04
    
    # Sector real
    consumo: float = 0.0
    inversion: float = 0.0
    exportaciones: float = 0.0
    importaciones: float = 0.0


class ModeloEstocastico:
    """
    Modelo estocástico del sistema fiscal boliviano
    
    Integra:
    - Gobierno (ingresos, gastos, deuda)
    - Empresas (producción, precios)
    - Hogares (consumo, ahorro)
    - Sector financiero (tasas, crédito)
    - Sector externo (precios, tipo de cambio)
    """
    
    def __init__(self, configuracion, agentes: Dict):
        self.config = configuracion
        self.params_sim = configuracion.simulacion
        self.params_macro = configuracion.macroeconomicos
        
        # Agentes
        self.gobierno = agentes.get('gobierno')
        self.empresas = agentes.get('empresas')
        self.hogares = agentes.get('hogares')
        self.sector_financiero = agentes.get('sector_financiero')
        self.sector_externo = agentes.get('sector_externo')
        
        # Estado
        self.estado = EstadoEconomia()
        self.historia = []
        
        # Generador de números aleatorios
        self.rng = np.random.RandomState(self.params_sim.semilla_aleatoria)
        
    def inicializar(self):
        """Inicializa el modelo con valores iniciales"""
        self.estado.periodo = 0
        self.estado.año = self.params_sim.año_inicio
        self.estado.trimestre = 1
        
        # Valores iniciales macroeconómicos
        self.estado.pib = self.params_macro.pib_inicial
        self.estado.inflacion = self.params_macro.inflacion_inicial
        self.estado.reservas_internacionales = self.params_macro.reservas_iniciales
        
        # Precios iniciales
        self.estado.precio_gas = self.config.sector_externo.precio_gas_base
        self.estado.precio_minerales = self.config.sector_externo.precio_zinc_base
        
        # Producción inicial
        self.estado.produccion_gas = self.config.empresas.produccion_gas_base
        self.estado.produccion_minerales = self.config.empresas.produccion_minerales_base
        
        # Tasas de interés
        self.estado.tasa_interes_domestica = self.config.sector_financiero.tasa_interes_domestica_base
        self.estado.tasa_interes_internacional = self.config.sector_externo.tasa_libor_base
        
        # Inicializar gobierno
        if self.gobierno:
            self.gobierno.reset(
                self.params_macro.deuda_inicial_interna,
                self.params_macro.deuda_inicial_externa
            )
        
        self.historia = []
        
    def generar_shocks(self) -> Dict[str, float]:
        """
        Genera shocks estocásticos para el periodo
        
        Usa distribución normal o t-student según configuración
        """
        if self.params_sim.tipo_distribucion_shocks == "normal":
            shock_precio_gas = self.rng.normal(
                0, self.config.sector_externo.volatilidad_gas
            )
            shock_precio_minerales = self.rng.normal(
                0, self.config.sector_externo.volatilidad_minerales
            )
            shock_pib = self.rng.normal(0, 0.02)
            shock_ingresos = self.rng.normal(
                0, self.config.gobierno.shock_recaudacion_std
            )
            shock_gastos = self.rng.normal(
                0, self.config.gobierno.shock_gasto_std
            )
            shock_tipo_cambio = self.rng.normal(
                0, self.config.sector_externo.volatilidad_tipo_cambio
            )
            
        elif self.params_sim.tipo_distribucion_shocks == "t-student":
            df = self.params_sim.grados_libertad_t
            shock_precio_gas = self.rng.standard_t(df) * self.config.sector_externo.volatilidad_gas / np.sqrt(df/(df-2))
            shock_precio_minerales = self.rng.standard_t(df) * self.config.sector_externo.volatilidad_minerales / np.sqrt(df/(df-2))
            shock_pib = self.rng.standard_t(df) * 0.02 / np.sqrt(df/(df-2))
            shock_ingresos = self.rng.standard_t(df) * self.config.gobierno.shock_recaudacion_std / np.sqrt(df/(df-2))
            shock_gastos = self.rng.standard_t(df) * self.config.gobierno.shock_gasto_std / np.sqrt(df/(df-2))
            shock_tipo_cambio = self.rng.standard_t(df) * self.config.sector_externo.volatilidad_tipo_cambio / np.sqrt(df/(df-2))
        else:
            # Sin shocks
            return {k: 0.0 for k in ['precio_gas', 'precio_minerales', 'pib', 
                                     'ingresos', 'gastos', 'tipo_cambio']}
        
        return {
            'precio_gas': shock_precio_gas,
            'precio_minerales': shock_precio_minerales,
            'pib': shock_pib,
            'ingresos': shock_ingresos,
            'gastos': shock_gastos,
            'tipo_cambio': shock_tipo_cambio
        }
    
    def actualizar_precios_internacionales(self, shocks: Dict):
        """
        Actualiza precios internacionales con procesos estocásticos
        
        Usa Geometric Brownian Motion (GBM):
        dS = μ·S·dt + σ·S·dW
        """
        # Precio del gas
        drift_gas = 0.02  # 2% tendencia anual
        self.estado.precio_gas *= (1 + drift_gas/4 + shocks['precio_gas'])
        self.estado.precio_gas = max(self.estado.precio_gas, 20.0)  # Piso
        
        # Precio de minerales
        drift_minerales = 0.01
        self.estado.precio_minerales *= (1 + drift_minerales/4 + shocks['precio_minerales'])
        self.estado.precio_minerales = max(self.estado.precio_minerales, 1000.0)
        
    def actualizar_pib(self, shocks: Dict):
        """
        Actualiza PIB con crecimiento tendencial y shocks
        
        PIB_t = PIB_{t-1} · (1 + g + shock)
        """
        tasa_crecimiento = (self.params_macro.tasa_crecimiento_potencial / 4 + 
                           shocks['pib'])
        
        self.estado.pib *= (1 + tasa_crecimiento)
        self.estado.tasa_crecimiento_pib = tasa_crecimiento * 4  # Anualizado
        
    def actualizar_tipo_cambio(self, shocks: Dict):
        """Actualiza tipo de cambio"""
        # En Bolivia hay tipo de cambio relativamente fijo
        # pero puede haber presiones por déficit y reservas
        
        presion_deficit = 0.0
        if self.gobierno:
            if self.gobierno.estado.deficit < 0:
                presion_deficit = 0.005
        
        presion_reservas = 0.0
        if self.estado.reservas_internacionales < self.params_macro.nivel_minimo_reservas:
            presion_reservas = 0.01
        
        self.estado.tipo_cambio *= (1 + shocks['tipo_cambio'] + 
                                   presion_deficit + presion_reservas)
        
    def actualizar_tasas_interes(self):
        """
        Actualiza tasas de interés considerando riesgo país
        
        r_domestica = r_internacional + spread + prima_riesgo
        """
        # Tasa internacional base
        tasa_base = self.config.sector_externo.tasa_libor_base
        
        # Spread base
        spread = self.config.sector_financiero.spread_riesgo_pais_base
        
        # Prima de riesgo por nivel de deuda
        if self.gobierno:
            ratio_deuda = self.gobierno.estado.ratio_deuda_pib
            if ratio_deuda > 0.5:
                prima_deuda = (ratio_deuda - 0.5) * 0.1
            else:
                prima_deuda = 0.0
            
            # Prima por déficit
            ratio_deficit = abs(self.gobierno.estado.ratio_deficit_pib)
            prima_deficit = ratio_deficit * 0.5
        else:
            prima_deuda = 0.0
            prima_deficit = 0.0
        
        self.estado.tasa_interes_domestica = (tasa_base + spread + 
                                              prima_deuda + prima_deficit)
        self.estado.tasa_interes_domestica = min(self.estado.tasa_interes_domestica, 0.20)
        
    def actualizar_reservas(self):
        """
        Actualiza reservas internacionales
        
        ΔR = Exportaciones - Importaciones + Flujo_Capital - Servicio_Deuda_Externa
        """
        if not self.gobierno:
            return
        
        # Simplificado: las reservas caen con déficit y servicio de deuda externa
        deficit = self.gobierno.estado.deficit
        servicio_externa = (self.gobierno.estado.deuda_externa * 
                          self.estado.tasa_interes_internacional)
        
        # Exportaciones (hidrocarburos y minerales)
        exportaciones = (self.estado.precio_gas * self.estado.produccion_gas * 0.8 +
                        self.estado.precio_minerales * self.estado.produccion_minerales * 0.0004)
        
        # Importaciones (función del PIB)
        importaciones = self.estado.pib * 0.25
        
        balanza_comercial = exportaciones - importaciones
        
        cambio_reservas = balanza_comercial - servicio_externa
        if deficit < 0:
            cambio_reservas += deficit * 0.3  # Parte del déficit reduce reservas
        
        self.estado.reservas_internacionales += cambio_reservas
        self.estado.reservas_internacionales = max(
            self.estado.reservas_internacionales, 0
        )
        
    def simular_periodo(self) -> EstadoEconomia:
        """
        Simula un periodo (trimestre)
        
        Secuencia:
        1. Generar shocks estocásticos
        2. Actualizar precios internacionales
        3. Actualizar PIB
        4. Actualizar tasas de interés
        5. Gobierno actualiza su estado
        6. Actualizar reservas
        7. Guardar estado
        """
        # 1. Generar shocks
        shocks = self.generar_shocks()
        
        # 2. Actualizar variables exógenas
        self.actualizar_precios_internacionales(shocks)
        self.actualizar_pib(shocks)
        self.actualizar_tipo_cambio(shocks)
        self.actualizar_tasas_interes()
        
        # 3. Gobierno toma decisiones
        if self.gobierno:
            self.gobierno.actualizar_estado(
                pib=self.estado.pib,
                precio_gas=self.estado.precio_gas,
                precio_minerales=self.estado.precio_minerales,
                produccion_gas=self.estado.produccion_gas,
                produccion_minerales=self.estado.produccion_minerales,
                tasa_interes_interna=self.estado.tasa_interes_domestica,
                tasa_interes_externa=self.estado.tasa_interes_internacional,
                shock_ingresos=shocks['ingresos'],
                shock_gastos=shocks['gastos']
            )
        
        # 4. Actualizar reservas internacionales
        self.actualizar_reservas()
        
        # 5. Avanzar periodo
        self.estado.periodo += 1
        self.estado.trimestre += 1
        if self.estado.trimestre > 4:
            self.estado.trimestre = 1
            self.estado.año += 1
        
        # 6. Guardar en historia
        estado_dict = {
            **self.estado.__dict__,
            'gobierno': self.gobierno.estado.__dict__ if self.gobierno else {}
        }
        self.historia.append(estado_dict)
        
        return self.estado
    
    def simular(self, num_periodos: int = None) -> pd.DataFrame:
        """
        Ejecuta simulación completa
        
        Args:
            num_periodos: número de periodos a simular (trimestres)
        
        Returns:
            DataFrame con historia completa
        """
        if num_periodos is None:
            años = self.params_sim.año_fin - self.params_sim.año_inicio
            num_periodos = años * self.params_sim.periodos_por_año
        
        self.inicializar()
        
        for t in range(num_periodos):
            self.simular_periodo()
        
        return self.obtener_resultados()
    
    def obtener_resultados(self) -> pd.DataFrame:
        """Convierte la historia en DataFrame"""
        if not self.historia:
            return pd.DataFrame()
        
        # Aplanar estructura anidada
        datos = []
        for registro in self.historia:
            fila = {k: v for k, v in registro.items() if k != 'gobierno'}
            
            # Agregar variables del gobierno con prefijo
            if 'gobierno' in registro:
                for k, v in registro['gobierno'].items():
                    fila[f'gob_{k}'] = v
            
            datos.append(fila)
        
        return pd.DataFrame(datos)
    
    def calcular_metricas_sostenibilidad(self) -> Dict:
        """
        Calcula métricas de sostenibilidad fiscal al final de la simulación
        """
        if not self.gobierno:
            return {}
        
        df = self.obtener_resultados()
        
        # Último periodo
        ultimo = df.iloc[-1]
        
        # Promedio últimos 4 trimestres (1 año)
        ultimo_año = df.iloc[-4:]
        
        metricas = {
            'ratio_deuda_pib_final': ultimo['gob_ratio_deuda_pib'],
            'ratio_deuda_pib_promedio': ultimo_año['gob_ratio_deuda_pib'].mean(),
            'ratio_deficit_pib_final': ultimo['gob_ratio_deficit_pib'],
            'ratio_deficit_pib_promedio': ultimo_año['gob_ratio_deficit_pib'].mean(),
            'carga_intereses': (ultimo['gob_servicio_deuda'] / ultimo['pib']),
            'deuda_total_final': ultimo['gob_deuda_total'],
            'reservas_finales': ultimo['reservas_internacionales'],
            'pib_final': ultimo['pib'],
            'tasa_crecimiento_promedio': df['tasa_crecimiento_pib'].mean()
        }
        
        return metricas