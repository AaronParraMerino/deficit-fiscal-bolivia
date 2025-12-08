"""
Agente Empresas: Sector productivo (hidrocarburos y minerales)
"""
import numpy as np
from typing import Dict
from dataclasses import dataclass


@dataclass
class EstadoEmpresas:
    """Estado del sector empresarial"""
    # Producción
    produccion_gas: float = 0.0
    produccion_minerales: float = 0.0
    
    # Ingresos
    ingresos_gas: float = 0.0
    ingresos_minerales: float = 0.0
    ingresos_totales: float = 0.0
    
    # Costos
    costos_produccion: float = 0.0
    
    # Utilidades
    utilidades: float = 0.0
    
    # Inversión
    inversion: float = 0.0
    
    # Capacidad
    utilizacion_capacidad_gas: float = 0.0
    utilizacion_capacidad_minerales: float = 0.0


class AgenteEmpresas:
    """
    Agente que representa al sector empresarial productivo
    
    Comportamiento:
    1. Decide nivel de producción según precios y demanda
    2. Calcula ingresos y costos
    3. Determina inversión
    4. Responde a shocks de productividad
    """
    
    def __init__(self, parametros):
        self.params = parametros
        self.estado = EstadoEmpresas()
        self.historia = []
        
        # Inicializar producción base
        self.estado.produccion_gas = parametros.produccion_gas_base
        self.estado.produccion_minerales = parametros.produccion_minerales_base
    
    def calcular_produccion_gas(self,
                               precio: float,
                               demanda_global: float = 1.0,
                               shock: float = 0.0) -> float:
        """
        Calcula producción de gas natural
        
        Función de oferta elástica al precio:
        Q = Q_base * (P/P_base)^elasticidad * demanda * (1 + shock)
        """
        precio_base = 50.0  # USD referencia
        elasticidad_oferta = 0.5  # Elasticidad precio de oferta
        
        # Efecto precio
        factor_precio = (precio / precio_base) ** elasticidad_oferta
        
        # Efecto demanda
        factor_demanda = demanda_global
        
        # Shock de productividad
        factor_shock = 1 + shock
        
        # Producción deseada
        produccion = (self.params.produccion_gas_base * 
                     factor_precio * 
                     factor_demanda * 
                     factor_shock)
        
        # Límite de capacidad
        produccion = min(produccion, self.params.capacidad_maxima_gas)
        produccion = max(produccion, 0)
        
        return produccion
    
    def calcular_produccion_minerales(self,
                                     precio: float,
                                     demanda_global: float = 1.0,
                                     shock: float = 0.0) -> float:
        """
        Calcula producción de minerales (zinc, plata, etc.)
        """
        precio_base = 2500.0  # USD/ton referencia
        elasticidad_oferta = 0.4
        
        factor_precio = (precio / precio_base) ** elasticidad_oferta
        factor_demanda = demanda_global
        factor_shock = 1 + shock
        
        produccion = (self.params.produccion_minerales_base * 
                     factor_precio * 
                     factor_demanda * 
                     factor_shock)
        
        produccion = min(produccion, self.params.capacidad_maxima_minerales)
        produccion = max(produccion, 0)
        
        return produccion
    
    def calcular_ingresos(self,
                         precio_gas: float,
                         precio_minerales: float) -> Dict[str, float]:
        """Calcula ingresos por ventas"""
        ingresos_gas = self.estado.produccion_gas * precio_gas
        ingresos_minerales = self.estado.produccion_minerales * precio_minerales * 0.001  # Ajuste de escala
        
        return {
            'gas': ingresos_gas,
            'minerales': ingresos_minerales,
            'totales': ingresos_gas + ingresos_minerales
        }
    
    def calcular_costos(self, shock_costos: float = 0.0) -> float:
        """
        Calcula costos de producción
        
        C = c_gas * Q_gas + c_minerales * Q_minerales
        """
        costo_gas = (self.params.costo_produccion_gas * 
                    self.estado.produccion_gas * 
                    (1 + shock_costos))
        
        costo_minerales = (self.params.costo_produccion_minerales * 
                          self.estado.produccion_minerales * 
                          0.001 *  # Ajuste de escala
                          (1 + shock_costos))
        
        return costo_gas + costo_minerales
    
    def calcular_inversion(self, utilidades: float) -> float:
        """
        Determina inversión basada en utilidades
        
        I = tasa_inversion * max(utilidades, 0)
        """
        if utilidades > 0:
            return self.params.tasa_inversion * utilidades
        return 0.0
    
    def actualizar_estado(self,
                         precio_gas: float,
                         precio_minerales: float,
                         demanda_global: float = 1.0,
                         shock_productividad: float = 0.0,
                         shock_costos: float = 0.0) -> EstadoEmpresas:
        """
        Actualiza el estado completo del sector empresarial
        """
        # 1. Calcular producción
        self.estado.produccion_gas = self.calcular_produccion_gas(
            precio_gas, demanda_global, shock_productividad
        )
        
        self.estado.produccion_minerales = self.calcular_produccion_minerales(
            precio_minerales, demanda_global, shock_productividad
        )
        
        # 2. Calcular ingresos
        ingresos = self.calcular_ingresos(precio_gas, precio_minerales)
        self.estado.ingresos_gas = ingresos['gas']
        self.estado.ingresos_minerales = ingresos['minerales']
        self.estado.ingresos_totales = ingresos['totales']
        
        # 3. Calcular costos
        self.estado.costos_produccion = self.calcular_costos(shock_costos)
        
        # 4. Calcular utilidades
        self.estado.utilidades = self.estado.ingresos_totales - self.estado.costos_produccion
        
        # 5. Determinar inversión
        self.estado.inversion = self.calcular_inversion(self.estado.utilidades)
        
        # 6. Calcular utilización de capacidad
        self.estado.utilizacion_capacidad_gas = (
            self.estado.produccion_gas / self.params.capacidad_maxima_gas
        )
        self.estado.utilizacion_capacidad_minerales = (
            self.estado.produccion_minerales / self.params.capacidad_maxima_minerales
        )
        
        # Guardar historia
        self.historia.append(self.estado.__dict__.copy())
        
        return self.estado
    
    def ajustar_capacidad(self, inversion_acumulada: float):
        """
        Ajusta capacidad productiva con inversión acumulada
        
        Nueva_Capacidad = Capacidad_actual * (1 + α * Inversión)
        """
        factor_expansion = 0.0001  # Tasa de expansión por inversión
        
        if inversion_acumulada > 0:
            self.params.capacidad_maxima_gas *= (1 + factor_expansion * inversion_acumulada)
            self.params.capacidad_maxima_minerales *= (1 + factor_expansion * inversion_acumulada)
    
    def get_exportaciones(self) -> float:
        """Retorna valor de exportaciones totales"""
        return self.estado.ingresos_totales * 0.8  # 80% se exporta
    
    def reset(self):
        """Reinicia el estado del agente"""
        self.estado = EstadoEmpresas()
        self.estado.produccion_gas = self.params.produccion_gas_base
        self.estado.produccion_minerales = self.params.produccion_minerales_base
        self.historia = []