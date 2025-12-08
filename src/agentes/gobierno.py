"""
Agente Gobierno: Gestiona ingresos, gastos, déficit y deuda
"""
import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class EstadoGobierno:
    """Estado del gobierno en un periodo t"""
    ingresos_totales: float = 0.0
    ingresos_tributarios: float = 0.0
    ingresos_hidrocarburos: float = 0.0
    ingresos_minerales: float = 0.0
    otros_ingresos: float = 0.0
    
    gastos_totales: float = 0.0
    gasto_corriente: float = 0.0
    gasto_capital: float = 0.0
    subsidios: float = 0.0
    servicio_deuda: float = 0.0
    
    deficit: float = 0.0
    deficit_primario: float = 0.0
    superavit_primario: float = 0.0
    
    deuda_interna: float = 0.0
    deuda_externa: float = 0.0
    deuda_total: float = 0.0
    
    ratio_deuda_pib: float = 0.0
    ratio_deficit_pib: float = 0.0


class AgenteGobierno:
    """
    Agente que representa al Gobierno
    
    Comportamiento:
    1. Calcula ingresos (tributarios, regalías, otros)
    2. Determina gastos (corriente, capital, subsidios)
    3. Calcula déficit/superávit
    4. Gestiona endeudamiento y servicio de deuda
    """
    
    def __init__(self, parametros):
        self.params = parametros
        self.estado = EstadoGobierno()
        self.historia = []
        
    def calcular_ingresos(self, 
                         pib: float,
                         precio_gas: float,
                         precio_minerales: float,
                         produccion_gas: float,
                         produccion_minerales: float,
                         shock: float = 0.0) -> Dict[str, float]:
        """
        Calcula ingresos del gobierno
        
        I_total = I_tributarios + I_hidrocarburos + I_minerales + Otros
        """
        # Ingresos tributarios (función del PIB con elasticidad)
        base_tributaria = pib * self.params.tasa_impositiva_base
        ingresos_trib = base_tributaria * (1 + self.params.elasticidad_recaudacion_pib * 0.01)
        
        # Shock estocástico en recaudación
        ingresos_trib *= (1 + shock)
        
        # Ingresos de hidrocarburos (regalías del gas)
        ingresos_gas = (precio_gas * produccion_gas * 
                       self.params.participacion_regalias_gas)
        
        # Ingresos de minerales
        ingresos_minerales = (precio_minerales * produccion_minerales * 
                             self.params.participacion_regalias_minerales)
        
        # Otros ingresos (tasas, multas, etc.) - simplificado
        otros_ingresos = pib * 0.02
        
        ingresos_totales = (ingresos_trib + ingresos_gas + 
                           ingresos_minerales + otros_ingresos)
        
        return {
            'tributarios': ingresos_trib,
            'hidrocarburos': ingresos_gas,
            'minerales': ingresos_minerales,
            'otros': otros_ingresos,
            'totales': ingresos_totales
        }
    
    def calcular_gastos(self,
                       pib: float,
                       gasto_anterior: float,
                       demanda_social: float = 1.0,
                       shock: float = 0.0) -> Dict[str, float]:
        """
        Calcula gastos del gobierno
        
        Modelo con inercia: G_t = α·G_{t-1} + (1-α)·G_base
        """
        # Gasto corriente (salarios, operación)
        gasto_base_corriente = pib * self.params.gasto_corriente_base
        
        if gasto_anterior > 0:
            # Inercia del gasto
            gasto_corriente = (self.params.inercia_gasto * gasto_anterior * 0.8 + 
                             (1 - self.params.inercia_gasto) * gasto_base_corriente)
        else:
            gasto_corriente = gasto_base_corriente
        
        # Shock estocástico
        gasto_corriente *= (1 + shock)
        
        # Gasto de capital (inversión pública)
        gasto_capital = pib * self.params.gasto_capital_base
        
        # Subsidios (combustibles, alimentos)
        subsidios = pib * self.params.subsidios_base * demanda_social
        
        gastos_totales = gasto_corriente + gasto_capital + subsidios
        
        return {
            'corriente': gasto_corriente,
            'capital': gasto_capital,
            'subsidios': subsidios,
            'totales_sin_deuda': gastos_totales
        }
    
    def calcular_servicio_deuda(self,
                               deuda_interna: float,
                               deuda_externa: float,
                               tasa_interna: float,
                               tasa_externa: float) -> float:
        """
        Calcula servicio de la deuda (intereses)
        """
        servicio_interna = deuda_interna * tasa_interna
        servicio_externa = deuda_externa * tasa_externa
        
        return servicio_interna + servicio_externa
    
    def calcular_deficit(self,
                        ingresos: float,
                        gastos: float,
                        servicio_deuda: float) -> Tuple[float, float]:
        """
        Calcula déficit fiscal
        
        Returns:
            (deficit_total, deficit_primario)
        """
        deficit_total = ingresos - (gastos + servicio_deuda)
        deficit_primario = ingresos - gastos
        
        return deficit_total, deficit_primario
    
    def gestionar_financiamiento(self,
                                deficit: float,
                                pib: float,
                                tasa_interna: float,
                                tasa_externa: float) -> Tuple[float, float]:
        """
        Determina cómo financiar el déficit
        
        Returns:
            (nueva_deuda_interna, nueva_deuda_externa)
        """
        if deficit >= 0:  # Superávit
            return 0.0, 0.0
        
        # Monto a financiar
        monto_deficit = abs(deficit)
        
        # Límite de déficit
        deficit_maximo = pib * self.params.limite_deficit_pib
        monto_a_financiar = min(monto_deficit, deficit_maximo)
        
        # Distribución entre deuda interna y externa
        nueva_deuda_interna = monto_a_financiar * self.params.preferencia_deuda_interna
        nueva_deuda_externa = monto_a_financiar * (1 - self.params.preferencia_deuda_interna)
        
        return nueva_deuda_interna, nueva_deuda_externa
    
    def actualizar_estado(self,
                         pib: float,
                         precio_gas: float,
                         precio_minerales: float,
                         produccion_gas: float,
                         produccion_minerales: float,
                         tasa_interes_interna: float,
                         tasa_interes_externa: float,
                         shock_ingresos: float = 0.0,
                         shock_gastos: float = 0.0) -> EstadoGobierno:
        """
        Actualiza el estado completo del gobierno en un periodo
        """
        # 1. Calcular ingresos
        ingresos = self.calcular_ingresos(
            pib, precio_gas, precio_minerales,
            produccion_gas, produccion_minerales,
            shock_ingresos
        )
        
        # 2. Calcular gastos
        gasto_anterior = self.estado.gastos_totales
        gastos = self.calcular_gastos(
            pib, gasto_anterior, 1.0, shock_gastos
        )
        
        # 3. Calcular servicio de deuda
        servicio = self.calcular_servicio_deuda(
            self.estado.deuda_interna,
            self.estado.deuda_externa,
            tasa_interes_interna,
            tasa_interes_externa
        )
        
        # 4. Calcular déficit
        deficit_total, deficit_primario = self.calcular_deficit(
            ingresos['totales'],
            gastos['totales_sin_deuda'],
            servicio
        )
        
        # 5. Financiamiento
        nueva_deuda_int, nueva_deuda_ext = self.gestionar_financiamiento(
            deficit_total, pib,
            tasa_interes_interna, tasa_interes_externa
        )
        
        # 6. Actualizar deudas
        deuda_interna = self.estado.deuda_interna + nueva_deuda_int
        deuda_externa = self.estado.deuda_externa + nueva_deuda_ext
        deuda_total = deuda_interna + deuda_externa
        
        # 7. Actualizar estado
        self.estado.ingresos_totales = ingresos['totales']
        self.estado.ingresos_tributarios = ingresos['tributarios']
        self.estado.ingresos_hidrocarburos = ingresos['hidrocarburos']
        self.estado.ingresos_minerales = ingresos['minerales']
        self.estado.otros_ingresos = ingresos['otros']
        
        self.estado.gastos_totales = gastos['totales_sin_deuda'] + servicio
        self.estado.gasto_corriente = gastos['corriente']
        self.estado.gasto_capital = gastos['capital']
        self.estado.subsidios = gastos['subsidios']
        self.estado.servicio_deuda = servicio
        
        self.estado.deficit = deficit_total
        self.estado.deficit_primario = deficit_primario
        self.estado.superavit_primario = -deficit_primario
        
        self.estado.deuda_interna = deuda_interna
        self.estado.deuda_externa = deuda_externa
        self.estado.deuda_total = deuda_total
        
        self.estado.ratio_deuda_pib = deuda_total / pib if pib > 0 else 0
        self.estado.ratio_deficit_pib = deficit_total / pib if pib > 0 else 0
        
        # Guardar en historia
        self.historia.append(self.estado.__dict__.copy())
        
        return self.estado
    
    def evaluar_sostenibilidad(self, pib: float, tasa_crecimiento: float) -> Dict:
        """
        Evalúa la sostenibilidad fiscal
        
        Indicadores:
        - Ratio deuda/PIB
        - Carga de intereses
        - Balance primario requerido
        """
        r = (self.estado.servicio_deuda / self.estado.deuda_total 
             if self.estado.deuda_total > 0 else 0)  # Tasa efectiva
        g = tasa_crecimiento  # Crecimiento del PIB
        
        # Balance primario necesario para estabilizar deuda
        # sp* = (r - g) * (D/Y)
        sp_requerido = (r - g) * self.estado.ratio_deuda_pib
        
        # Margen fiscal
        margen = self.estado.superavit_primario / pib - sp_requerido
        
        return {
            'ratio_deuda_pib': self.estado.ratio_deuda_pib,
            'carga_intereses': self.estado.servicio_deuda / pib if pib > 0 else 0,
            'balance_primario_requerido': sp_requerido,
            'balance_primario_actual': self.estado.superavit_primario / pib if pib > 0 else 0,
            'margen_fiscal': margen,
            'sostenible': margen >= 0
        }
    
    def reset(self, deuda_interna_inicial: float, deuda_externa_inicial: float):
        """Reinicia el estado del gobierno"""
        self.estado = EstadoGobierno()
        self.estado.deuda_interna = deuda_interna_inicial
        self.estado.deuda_externa = deuda_externa_inicial
        self.estado.deuda_total = deuda_interna_inicial + deuda_externa_inicial
        self.historia = []