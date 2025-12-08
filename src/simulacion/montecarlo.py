"""
Simulación Monte Carlo para análisis de escenarios estocásticos
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp


class SimuladorMonteCarlo:
    """
    Ejecuta simulaciones Monte Carlo del modelo fiscal
    
    Permite:
    - Múltiples trayectorias estocásticas
    - Análisis de distribuciones de resultados
    - Cálculo de probabilidades de eventos
    - Análisis de sensibilidad
    """
    
    def __init__(self, modelo_clase, configuracion):
        self.modelo_clase = modelo_clase
        self.config = configuracion
        self.resultados = []
        
    def simular_trayectoria(self, 
                           semilla: int,
                           agentes_factory,
                           num_periodos: int = None) -> Dict:
        """
        Simula una trayectoria individual
        
        Args:
            semilla: semilla aleatoria para esta trayectoria
            agentes_factory: función que crea instancias de agentes
            num_periodos: número de periodos a simular
        
        Returns:
            Diccionario con resultados de la trayectoria
        """
        # Configurar con semilla única
        config_temp = self.config
        config_temp.simulacion.semilla_aleatoria = semilla
        
        # Crear agentes
        agentes = agentes_factory(config_temp)
        
        # Crear modelo
        modelo = self.modelo_clase(config_temp, agentes)
        
        # Simular
        df_resultados = modelo.simular(num_periodos)
        
        # Métricas de sostenibilidad
        metricas = modelo.calcular_metricas_sostenibilidad()
        
        return {
            'semilla': semilla,
            'datos': df_resultados,
            'metricas': metricas
        }
    
    def ejecutar_montecarlo(self,
                           num_simulaciones: int,
                           agentes_factory,
                           num_periodos: int = None,
                           paralelo: bool = True) -> Dict:
        """
        Ejecuta simulaciones Monte Carlo
        
        Args:
            num_simulaciones: número de trayectorias a simular
            agentes_factory: función que crea agentes
            num_periodos: periodos por trayectoria
            paralelo: si usar procesamiento paralelo
        
        Returns:
            Diccionario con todos los resultados
        """
        print(f"Iniciando {num_simulaciones} simulaciones Monte Carlo...")
        
        # Generar semillas únicas
        semillas = list(range(num_simulaciones))
        
        resultados = []
        
        if paralelo and num_simulaciones > 10:
            # Procesamiento paralelo
            num_cores = max(1, mp.cpu_count() - 1)
            print(f"Usando {num_cores} núcleos en paralelo")
            
            with ProcessPoolExecutor(max_workers=num_cores) as executor:
                futures = {
                    executor.submit(
                        self.simular_trayectoria,
                        semilla,
                        agentes_factory,
                        num_periodos
                    ): semilla for semilla in semillas
                }
                
                for i, future in enumerate(as_completed(futures)):
                    try:
                        resultado = future.result()
                        resultados.append(resultado)
                        
                        if (i + 1) % 10 == 0:
                            print(f"Completado: {i+1}/{num_simulaciones}")
                    except Exception as e:
                        print(f"Error en simulación {futures[future]}: {e}")
        else:
            # Procesamiento secuencial
            for i, semilla in enumerate(semillas):
                resultado = self.simular_trayectoria(
                    semilla, agentes_factory, num_periodos
                )
                resultados.append(resultado)
                
                if (i + 1) % 10 == 0:
                    print(f"Completado: {i+1}/{num_simulaciones}")
        
        self.resultados = resultados
        
        print("✓ Simulaciones completadas")
        
        return self.analizar_resultados()
    
    def analizar_resultados(self) -> Dict:
        """
        Analiza resultados agregados de todas las simulaciones
        
        Returns:
            Diccionario con estadísticas agregadas
        """
        if not self.resultados:
            return {}
        
        # Extraer métricas de todas las simulaciones
        metricas_todas = [r['metricas'] for r in self.resultados]
        df_metricas = pd.DataFrame(metricas_todas)
        
        # Estadísticas descriptivas
        estadisticas = {}
        for col in df_metricas.columns:
            estadisticas[col] = {
                'media': df_metricas[col].mean(),
                'mediana': df_metricas[col].median(),
                'desv_std': df_metricas[col].std(),
                'min': df_metricas[col].min(),
                'max': df_metricas[col].max(),
                'percentil_5': df_metricas[col].quantile(0.05),
                'percentil_25': df_metricas[col].quantile(0.25),
                'percentil_75': df_metricas[col].quantile(0.75),
                'percentil_95': df_metricas[col].quantile(0.95)
            }
        
        # Probabilidades de eventos críticos
        probabilidades = self.calcular_probabilidades(df_metricas)
        
        # Trayectorias representativas
        trayectorias = self.seleccionar_trayectorias_representativas()
        
        return {
            'estadisticas': estadisticas,
            'probabilidades': probabilidades,
            'trayectorias_representativas': trayectorias,
            'df_metricas': df_metricas,
            'num_simulaciones': len(self.resultados)
        }
    
    def calcular_probabilidades(self, df_metricas: pd.DataFrame) -> Dict:
        """
        Calcula probabilidades de eventos críticos
        """
        n = len(df_metricas)
        if n == 0:
            return {}

        prob = {
            "deuda_mayor_60_pib": (df_metricas["ratio_deuda_pib_final"] > 0.60).sum() / n,
            "deuda_mayor_70_pib": (df_metricas["ratio_deuda_pib_final"] > 0.70).sum() / n,
            "deuda_mayor_80_pib": (df_metricas["ratio_deuda_pib_final"] > 0.80).sum() / n,
            "deficit_mayor_5_pib": (
                df_metricas["ratio_deficit_pib_promedio"] < -0.05
            ).sum() / n,
            "deficit_mayor_8_pib": (
                df_metricas["ratio_deficit_pib_promedio"] < -0.08
            ).sum() / n,
            "reservas_criticas": (df_metricas["reservas_finales"] < 3000).sum() / n,
            "crecimiento_negativo": (
                df_metricas["tasa_crecimiento_promedio"] < 0
            ).sum() / n,
            "carga_intereses_alta": (df_metricas["carga_intereses"] > 0.15).sum() / n,
        }

        return prob
    
    def seleccionar_trayectorias_representativas(self) -> Dict:
        """
        Selecciona trayectorias representativas:
        - Percentil 5 (pesimista)
        - Mediana (central)
        - Percentil 95 (optimista)
        """
        if not self.resultados:
            return {}
        
        # Ordenar por ratio deuda/PIB final
        resultados_ordenados = sorted(
            self.resultados,
            key=lambda x: x['metricas']['ratio_deuda_pib_final']
        )
        
        n = len(resultados_ordenados)
        
        indices = {
            'pesimista': int(n * 0.95),  # Peor escenario (alta deuda)
            'central': int(n * 0.50),    # Mediana
            'optimista': int(n * 0.05)   # Mejor escenario (baja deuda)
        }
        
        trayectorias = {}
        for nombre, idx in indices.items():
            trayectorias[nombre] = {
                'datos': resultados_ordenados[idx]['datos'],
                'metricas': resultados_ordenados[idx]['metricas'],
                'semilla': resultados_ordenados[idx]['semilla']
            }
        
        return trayectorias
    
    def calcular_valor_en_riesgo(self, 
                                 variable: str,
                                 nivel_confianza: float = 0.95) -> float:
        """
        Calcula Value at Risk (VaR) para una variable
        
        Args:
            variable: nombre de la métrica
            nivel_confianza: nivel de confianza (default 95%)
        
        Returns:
            Valor en el percentil correspondiente
        """
        metricas = [r['metricas'][variable] for r in self.resultados]
        return np.percentile(metricas, (1 - nivel_confianza) * 100)
    
    def calcular_cvar(self,
                     variable: str,
                     nivel_confianza: float = 0.95) -> float:
        """
        Calcula Conditional Value at Risk (CVaR)
        
        Promedio de los valores en el tail más allá del VaR
        """
        metricas = np.array([r['metricas'][variable] for r in self.resultados])
        var = self.calcular_valor_en_riesgo(variable, nivel_confianza)
        
        # Valores peores que el VaR
        tail = metricas[metricas >= var]  # Para deuda (mayor es peor)
        
        return tail.mean() if len(tail) > 0 else var
    
    def analisis_sensibilidad(self,
                             parametro: str,
                             valores: List[float],
                             agentes_factory) -> pd.DataFrame:
        """
        Análisis de sensibilidad para un parámetro
        
        Args:
            parametro: nombre del parámetro a variar (ej: 'gobierno.tasa_impositiva_base')
            valores: lista de valores a probar
            agentes_factory: función que crea agentes
        
        Returns:
            DataFrame con resultados para cada valor
        """
        print(f"Análisis de sensibilidad: {parametro}")
        
        resultados_sensibilidad = []
        
        for valor in valores:
            print(f"  Probando {parametro} = {valor}")
            
            # Modificar configuración
            config_temp = self.config
            partes = parametro.split('.')
            obj = getattr(config_temp, partes[0])
            setattr(obj, partes[1], valor)
            
            # Simular (con menos trayectorias)
            num_sims = min(100, self.config.simulacion.num_simulaciones)
            
            simulador_temp = SimuladorMonteCarlo(self.modelo_clase, config_temp)
            analisis = simulador_temp.ejecutar_montecarlo(
                num_sims, agentes_factory, paralelo=False
            )
            
            # Guardar resultado
            fila = {'parametro_valor': valor}
            for metrica, stats in analisis['estadisticas'].items():
                fila[f'{metrica}_media'] = stats['media']
                fila[f'{metrica}_std'] = stats['desv_std']
            
            resultados_sensibilidad.append(fila)
        
        return pd.DataFrame(resultados_sensibilidad)
    
    def generar_reporte(self, analisis: Dict) -> str:
        """Genera reporte textual de resultados"""
        lineas = []
        lineas.append("=" * 70)
        lineas.append("REPORTE DE SIMULACIÓN MONTE CARLO")
        lineas.append("=" * 70)
        lineas.append(f"\nNúmero de simulaciones: {analisis['num_simulaciones']}")
        
        lineas.append("\n" + "-" * 70)
        lineas.append("ESTADÍSTICAS DE RATIO DEUDA/PIB")
        lineas.append("-" * 70)
        stats = analisis['estadisticas']['ratio_deuda_pib_final']
        lineas.append(f"Media:           {stats['media']:.2%}")
        lineas.append(f"Mediana:         {stats['mediana']:.2%}")
        lineas.append(f"Desv. Estándar:  {stats['desv_std']:.2%}")
        lineas.append(f"Mínimo:          {stats['min']:.2%}")
        lineas.append(f"Máximo:          {stats['max']:.2%}")
        lineas.append(f"Percentil 5:     {stats['percentil_5']:.2%}")
        lineas.append(f"Percentil 95:    {stats['percentil_95']:.2%}")
        
        lineas.append("\n" + "-" * 70)
        lineas.append("PROBABILIDADES DE EVENTOS CRÍTICOS")
        lineas.append("-" * 70)
        prob = analisis['probabilidades']
        lineas.append(f"Deuda > 60% PIB:         {prob['deuda_mayor_60_pib']:.1%}")
        lineas.append(f"Deuda > 70% PIB:         {prob['deuda_mayor_70_pib']:.1%}")
        lineas.append(f"Deuda > 80% PIB:         {prob['deuda_mayor_80_pib']:.1%}")
        lineas.append(f"Déficit > 5% PIB:        {prob['deficit_mayor_5_pib']:.1%}")
        lineas.append(f"Déficit > 8% PIB:        {prob['deficit_mayor_8_pib']:.1%}")
        lineas.append(f"Reservas Críticas:       {prob['reservas_criticas']:.1%}")
        lineas.append(f"Crecimiento Negativo:    {prob['crecimiento_negativo']:.1%}")
        
        lineas.append("\n" + "=" * 70)
        
        return "\n".join(lineas)