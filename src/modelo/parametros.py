"""
Parámetros del modelo estocástico de déficit fiscal
"""
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ParametrosGobierno:
    """Parámetros del agente Gobierno"""
    
    # Ingresos
    tasa_impositiva_base: float = 0.25
    elasticidad_recaudacion_pib: float = 1.1
    
    # Ingresos de hidrocarburos
    participacion_regalias_gas: float = 0.18
    sensibilidad_precio_gas: float = 0.8
    
    # Ingresos de minerales
    participacion_regalias_minerales: float = 0.05
    sensibilidad_precio_minerales: float = 0.6
    
    # Gastos
    gasto_corriente_base: float = 0.30
    gasto_capital_base: float = 0.08
    subsidios_base: float = 0.05
    
    # Rigidez del gasto
    inercia_gasto: float = 0.85
    
    # Financiamiento
    limite_deficit_pib: float = 0.08
    preferencia_deuda_interna: float = 0.6
    
    # Parámetros estocásticos
    shock_recaudacion_std: float = 0.03
    shock_gasto_std: float = 0.02


@dataclass
class ParametrosEmpresas:
    """Parámetros del agente Empresas"""
    
    productividad_base: float = 1.0
    tasa_crecimiento_productividad: float = 0.02
    
    produccion_gas_base: float = 100.0
    capacidad_maxima_gas: float = 150.0
    costo_produccion_gas: float = 30.0
    
    produccion_minerales_base: float = 100.0
    capacidad_maxima_minerales: float = 140.0
    costo_produccion_minerales: float = 800.0
    
    tasa_inversion: float = 0.15
    sensibilidad_demanda: float = 1.2
    
    shock_productividad_std: float = 0.04
    shock_costos_std: float = 0.05


@dataclass
class ParametrosHogares:
    """Parámetros del agente Hogares"""
    
    propension_consumo_base: float = 0.75
    elasticidad_ingreso: float = 0.9
    
    tasa_ahorro: float = 0.15
    
    tasa_desempleo_base: float = 0.05
    sensibilidad_empleo_pib: float = 0.8
    
    peso_expectativas_inflacion: float = 0.4
    peso_expectativas_ingreso: float = 0.6
    
    shock_consumo_std: float = 0.03
    shock_expectativas_std: float = 0.02


@dataclass
class ParametrosSectorFinanciero:
    """Parámetros del sector financiero"""
    
    tasa_interes_domestica_base: float = 0.06
    spread_riesgo_pais_base: float = 0.03
    
    ratio_credito_pib: float = 0.40
    tasa_morosidad: float = 0.02
    
    ratio_liquidez: float = 0.15
    
    sensibilidad_tasa_deuda: float = 0.5
    sensibilidad_tasa_deficit: float = 0.3
    
    shock_tasa_interes_std: float = 0.01


@dataclass
class ParametrosSectorExterno:
    """Parámetros del sector externo"""
    
    precio_gas_base: float = 50.0
    precio_zinc_base: float = 2500.0
    precio_plata_base: float = 20.0
    precio_oro_base: float = 1800.0
    
    volatilidad_gas: float = 0.25
    volatilidad_minerales: float = 0.20
    
    tipo_cambio_base: float = 6.96
    volatilidad_tipo_cambio: float = 0.02
    
    tasa_libor_base: float = 0.04
    volatilidad_tasa_internacional: float = 0.015
    
    indice_demanda_global: float = 100.0
    sensibilidad_demanda_precio: float = -0.8
    
    correlacion_precios: float = 0.4


@dataclass
class ParametrosMacroeconomicos:
    """Parámetros macroeconómicos generales"""
    
    pib_inicial: float = 40000.0
    tasa_crecimiento_potencial: float = 0.03
    
    meta_inflacion: float = 0.04
    inflacion_inicial: float = 0.03
    
    reservas_iniciales: float = 7000.0
    nivel_minimo_reservas: float = 3000.0
    
    deuda_inicial_interna: float = 5000.0
    deuda_inicial_externa: float = 8000.0
    limite_deuda_pib: float = 0.60
    
    poblacion_inicial: float = 11.5
    tasa_crecimiento_poblacion: float = 0.015


@dataclass
class ParametrosSimulacion:
    """Parámetros de la simulación"""
    
    año_inicio: int = 2020
    año_fin: int = 2030
    periodos_por_año: int = 4
    
    num_simulaciones: int = 1000
    semilla_aleatoria: int = 42
    
    tolerancia: float = 1e-6
    max_iteraciones: int = 100
    
    tipo_distribucion_shocks: str = "normal"
    grados_libertad_t: int = 5


class ConfiguracionModelo:
    """Configuración completa del modelo"""
    
    def __init__(self):
        self.gobierno = ParametrosGobierno()
        self.empresas = ParametrosEmpresas()
        self.hogares = ParametrosHogares()
        self.sector_financiero = ParametrosSectorFinanciero()
        self.sector_externo = ParametrosSectorExterno()
        self.macroeconomicos = ParametrosMacroeconomicos()
        self.simulacion = ParametrosSimulacion()
        
    def to_dict(self) -> Dict:
        """Convierte todos los parámetros a diccionario"""
        return {
            'gobierno': self.gobierno.__dict__,
            'empresas': self.empresas.__dict__,
            'hogares': self.hogares.__dict__,
            'sector_financiero': self.sector_financiero.__dict__,
            'sector_externo': self.sector_externo.__dict__,
            'macroeconomicos': self.macroeconomicos.__dict__,
            'simulacion': self.simulacion.__dict__
        }
    
    def actualizar_desde_dict(self, parametros: Dict):
        """Actualiza parámetros desde un diccionario"""
        for seccion, valores in parametros.items():
            if hasattr(self, seccion):
                obj = getattr(self, seccion)
                for key, value in valores.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
    
    def validar_parametros(self) -> List[str]:
        """Valida que los parámetros sean consistentes"""
        errores = []
        
        if not (0 <= self.gobierno.tasa_impositiva_base <= 1):
            errores.append("Tasa impositiva debe estar entre 0 y 1")
        
        if not (0 <= self.hogares.propension_consumo_base <= 1):
            errores.append("Propensión al consumo debe estar entre 0 y 1")
        
        if self.macroeconomicos.pib_inicial <= 0:
            errores.append("PIB inicial debe ser positivo")
        
        if self.macroeconomicos.reservas_iniciales < 0:
            errores.append("Reservas iniciales no pueden ser negativas")
        
        if self.simulacion.año_fin <= self.simulacion.año_inicio:
            errores.append("Año final debe ser posterior al año inicial")
        
        return errores
    
    def generar_escenario(self, nombre: str, ajustes: Dict) -> 'ConfiguracionModelo':
        """Genera un nuevo escenario con parámetros ajustados"""
        import copy
        nuevo_config = copy.deepcopy(self)
        nuevo_config.actualizar_desde_dict(ajustes)
        return nuevo_config


# Escenarios predefinidos
ESCENARIOS = {
    "base": {
        "descripcion": "Escenario base con parámetros históricos",
        "ajustes": {}
    },
    
    "optimista": {
        "descripcion": "Precios altos de commodities, crecimiento económico fuerte",
        "ajustes": {
            "sector_externo": {
                "precio_gas_base": 70.0,
                "precio_zinc_base": 3000.0
            },
            "macroeconomicos": {
                "tasa_crecimiento_potencial": 0.045
            },
            "gobierno": {
                "elasticidad_recaudacion_pib": 1.2
            }
        }
    },
    
    "pesimista": {
        "descripcion": "Crisis de precios, recesión económica",
        "ajustes": {
            "sector_externo": {
                "precio_gas_base": 35.0,
                "precio_zinc_base": 1800.0,
                "volatilidad_gas": 0.35
            },
            "macroeconomicos": {
                "tasa_crecimiento_potencial": 0.01
            },
            "gobierno": {
                "elasticidad_recaudacion_pib": 0.9
            }
        }
    },
    
    "ajuste_fiscal": {
        "descripcion": "Política de ajuste fiscal estricto",
        "ajustes": {
            "gobierno": {
                "gasto_corriente_base": 0.25,
                "subsidios_base": 0.03,
                "limite_deficit_pib": 0.05
            }
        }
    },
    
    "crisis_deuda": {
        "descripcion": "Crisis de deuda con altas tasas de interés",
        "ajustes": {
            "sector_financiero": {
                "spread_riesgo_pais_base": 0.08,
                "tasa_interes_domestica_base": 0.10
            },
            "sector_externo": {
                "tasa_libor_base": 0.06
            }
        }
    }
}