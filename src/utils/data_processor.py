"""
Procesamiento avanzado de datos económicos
"""
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Tuple, List, Optional


class DataProcessor:
    """Procesador de datos para análisis estocástico"""
    
    @staticmethod
    def calcular_estadisticas(serie: pd.Series) -> Dict:
        """Calcula estadísticas descriptivas completas"""
        return {
            'media': serie.mean(),
            'mediana': serie.median(),
            'desviacion': serie.std(),
            'varianza': serie.var(),
            'minimo': serie.min(),
            'maximo': serie.max(),
            'rango': serie.max() - serie.min(),
            'percentil_05': serie.quantile(0.05),
            'percentil_25': serie.quantile(0.25),
            'percentil_75': serie.quantile(0.75),
            'percentil_95': serie.quantile(0.95),
            'coef_variacion': serie.std() / serie.mean() if serie.mean() != 0 else np.nan,
            'asimetria': serie.skew(),
            'curtosis': serie.kurtosis(),
            'n_observaciones': len(serie.dropna())
        }
    
    @staticmethod
    def calcular_tasas_crecimiento(serie: pd.Series, 
                                   periodos: int = 1) -> pd.Series:
        """
        Calcula tasas de crecimiento
        
        Args:
            serie: serie temporal
            periodos: número de periodos para el cálculo (1=interanual)
        """
        return serie.pct_change(periods=periodos) * 100
    
    @staticmethod
    def detectar_tendencia(serie: pd.Series) -> Dict:
        """
        Detecta tendencia lineal mediante regresión
        
        Returns:
            Dict con pendiente, intercepto, R², p-value
        """
        serie_limpia = serie.dropna()
        x = np.arange(len(serie_limpia))
        y = serie_limpia.values
        
        if len(x) < 2:
            return {'pendiente': 0, 'intercepto': serie.mean(), 'r2': 0, 'p_value': 1}
        
        # Regresión lineal
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        return {
            'pendiente': slope,
            'intercepto': intercept,
            'r2': r_value**2,
            'p_value': p_value,
            'error_std': std_err,
            'significativa': p_value < 0.05
        }
    
    @staticmethod
    def estimar_volatilidad(serie: pd.Series, 
                           ventana: int = None,
                           anualizar: bool = True) -> float:
        """
        Estima volatilidad histórica
        
        Args:
            serie: serie de precios/valores
            ventana: ventana móvil (None = toda la serie)
            anualizar: si multiplicar por sqrt(periodos_por_año)
        """
        retornos = serie.pct_change().dropna()
        
        if ventana:
            volatilidad = retornos.rolling(window=ventana).std().iloc[-1]
        else:
            volatilidad = retornos.std()
        
        if anualizar:
            # Asumiendo datos anuales
            volatilidad = volatilidad * np.sqrt(1)
        
        return volatilidad
    
    @staticmethod
    def calcular_correlaciones(df: pd.DataFrame, 
                              metodo: str = 'pearson') -> pd.DataFrame:
        """
        Calcula matriz de correlaciones
        
        Args:
            df: DataFrame con múltiples series
            metodo: 'pearson', 'spearman', 'kendall'
        """
        return df.corr(method=metodo)
    
    @staticmethod
    def identificar_distribucion(serie: pd.Series) -> Dict:
        """
        Identifica la mejor distribución estadística para los datos
        """
        datos = serie.dropna().values
        
        if len(datos) < 3:
            return {'mejor_distribucion': 'insuficientes_datos'}
        
        # Distribuciones a probar
        distribuciones = {
            'normal': stats.norm,
            'lognormal': stats.lognorm,
            't-student': stats.t,
            'gamma': stats.gamma,
            'exponencial': stats.expon
        }
        
        resultados = {}
        
        for nombre, dist in distribuciones.items():
            try:
                # Ajustar distribución
                params = dist.fit(datos)
                
                # Test de Kolmogorov-Smirnov
                ks_stat, p_value = stats.kstest(datos, 
                                                lambda x: dist.cdf(x, *params))
                
                # Test de Anderson-Darling (más sensible)
                try:
                    ad_result = stats.anderson(datos)
                    ad_stat = ad_result.statistic
                except:
                    ad_stat = np.nan
                
                resultados[nombre] = {
                    'parametros': params,
                    'ks_statistic': ks_stat,
                    'p_value': p_value,
                    'anderson_darling': ad_stat
                }
            except Exception as e:
                continue
        
        if not resultados:
            return {'mejor_distribucion': 'error'}
        
        # Seleccionar mejor distribución (mayor p-value en KS test)
        mejor = max(resultados.items(), key=lambda x: x[1]['p_value'])
        
        return {
            'mejor_distribucion': mejor[0],
            'parametros': mejor[1]['parametros'],
            'p_value': mejor[1]['p_value'],
            'todas': resultados,
            'test_normalidad': {
                'shapiro_wilk': stats.shapiro(datos) if len(datos) < 5000 else (np.nan, np.nan),
                'jarque_bera': stats.jarque_bera(datos)
            }
        }
    
    @staticmethod
    def detectar_outliers(serie: pd.Series, 
                         metodo: str = 'iqr',
                         umbral: float = 1.5) -> pd.Series:
        """
        Detecta outliers
        
        Args:
            serie: serie de datos
            metodo: 'iqr', 'zscore', 'modified_zscore'
            umbral: umbral para detección (1.5 para IQR, 3 para z-score)
        """
        if metodo == 'iqr':
            Q1 = serie.quantile(0.25)
            Q3 = serie.quantile(0.75)
            IQR = Q3 - Q1
            outliers = (serie < (Q1 - umbral * IQR)) | (serie > (Q3 + umbral * IQR))
            
        elif metodo == 'zscore':
            z_scores = np.abs((serie - serie.mean()) / serie.std())
            outliers = z_scores > umbral
            
        elif metodo == 'modified_zscore':
            median = serie.median()
            mad = np.median(np.abs(serie - median))
            modified_z = 0.6745 * (serie - median) / mad
            outliers = np.abs(modified_z) > umbral
            
        else:
            raise ValueError(f"Método '{metodo}' no reconocido")
        
        return outliers
    
    @staticmethod
    def suavizar_serie(serie: pd.Series, 
                      metodo: str = 'ma',
                      ventana: int = 3) -> pd.Series:
        """
        Suaviza una serie temporal
        
        Args:
            metodo: 'ma' (media móvil), 'ewm' (exponencial)
            ventana: tamaño de ventana
        """
        if metodo == 'ma':
            return serie.rolling(window=ventana, center=True).mean()
        elif metodo == 'ewm':
            return serie.ewm(span=ventana).mean()
        else:
            raise ValueError(f"Método '{metodo}' no reconocido")
    
    @staticmethod
    def interpolar_datos_faltantes(serie: pd.Series,
                                   metodo: str = 'linear') -> pd.Series:
        """
        Interpola datos faltantes
        
        Args:
            metodo: 'linear', 'polynomial', 'spline', 'time'
        """
        return serie.interpolate(method=metodo)
    
    @staticmethod
    def calcular_autocorrelacion(serie: pd.Series, 
                                 nlags: int = 10) -> np.ndarray:
        """Calcula función de autocorrelación"""
        from statsmodels.tsa.stattools import acf
        return acf(serie.dropna(), nlags=nlags)
    
    @staticmethod
    def test_estacionariedad(serie: pd.Series) -> Dict:
        """
        Test de estacionariedad (Augmented Dickey-Fuller)
        """
        from statsmodels.tsa.stattools import adfuller
        
        resultado = adfuller(serie.dropna())
        
        return {
            'adf_statistic': resultado[0],
            'p_value': resultado[1],
            'valores_criticos': resultado[4],
            'es_estacionaria': resultado[1] < 0.05,
            'conclusion': 'Serie estacionaria' if resultado[1] < 0.05 else 'Serie no estacionaria'
        }
    
    @staticmethod
    def descomponer_serie(serie: pd.Series, 
                         periodo: int = None,
                         modelo: str = 'additive') -> Dict:
        """
        Descomposición de serie temporal (tendencia, estacionalidad, residuos)
        
        Args:
            periodo: período de estacionalidad (None = automático)
            modelo: 'additive' o 'multiplicative'
        """
        from statsmodels.tsa.seasonal import seasonal_decompose
        
        if periodo is None:
            periodo = min(12, len(serie) // 2)
        
        decomposition = seasonal_decompose(
            serie.dropna(), 
            model=modelo, 
            period=periodo,
            extrapolate_trend='freq'
        )
        
        return {
            'tendencia': decomposition.trend,
            'estacional': decomposition.seasonal,
            'residuo': decomposition.resid,
            'observado': decomposition.observed
        }


class TimeSeriesAnalyzer:
    """Analizador especializado de series temporales"""
    
    def __init__(self, serie: pd.Series, nombre: str = "Serie"):
        self.serie = serie
        self.nombre = nombre
        self.processor = DataProcessor()
    
    def analisis_completo(self) -> Dict:
        """Ejecuta un análisis completo de la serie"""
        resultados = {
            'nombre': self.nombre,
            'estadisticas': self.processor.calcular_estadisticas(self.serie),
            'tendencia': self.processor.detectar_tendencia(self.serie),
            'volatilidad': self.processor.estimar_volatilidad(self.serie),
            'distribucion': self.processor.identificar_distribucion(self.serie),
            'outliers': self.processor.detectar_outliers(self.serie).sum(),
            'estacionariedad': self.processor.test_estacionariedad(self.serie)
        }
        
        return resultados
    
    def generar_reporte(self) -> str:
        """Genera reporte textual del análisis"""
        analisis = self.analisis_completo()
        
        lineas = []
        lineas.append("=" * 60)
        lineas.append(f"ANÁLISIS DE SERIE TEMPORAL: {self.nombre}")
        lineas.append("=" * 60)
        
        # Estadísticas
        stats = analisis['estadisticas']
        lineas.append("\n📊 ESTADÍSTICAS DESCRIPTIVAS")
        lineas.append("-" * 40)
        lineas.append(f"Media:           {stats['media']:.2f}")
        lineas.append(f"Mediana:         {stats['mediana']:.2f}")
        lineas.append(f"Desv. Estándar:  {stats['desviacion']:.2f}")
        lineas.append(f"Coef. Variación: {stats['coef_variacion']:.3f}")
        lineas.append(f"Rango:           [{stats['minimo']:.2f}, {stats['maximo']:.2f}]")
        
        # Tendencia
        tend = analisis['tendencia']
        lineas.append("\n📈 TENDENCIA")
        lineas.append("-" * 40)
        lineas.append(f"Pendiente:       {tend['pendiente']:.4f}")
        lineas.append(f"R²:              {tend['r2']:.3f}")
        lineas.append(f"Significativa:   {'Sí' if tend['significativa'] else 'No'}")
        
        # Distribución
        dist = analisis['distribucion']
        lineas.append("\n📐 DISTRIBUCIÓN")
        lineas.append("-" * 40)
        lineas.append(f"Mejor ajuste:    {dist['mejor_distribucion']}")
        lineas.append(f"P-value (KS):    {dist.get('p_value', 0):.4f}")
        
        # Outliers
        lineas.append("\n⚠️  OUTLIERS")
        lineas.append("-" * 40)
        lineas.append(f"Detectados:      {analisis['outliers']}")
        
        # Estacionariedad
        estac = analisis['estacionariedad']
        lineas.append("\n🔄 ESTACIONARIEDAD")
        lineas.append("-" * 40)
        lineas.append(f"Conclusión:      {estac['conclusion']}")
        lineas.append(f"P-value (ADF):   {estac['p_value']:.4f}")
        
        lineas.append("\n" + "=" * 60)
        
        return "\n".join(lineas)


def preparar_datos_para_modelo(datos: Dict[str, pd.DataFrame],
                               año_inicio: int = 2020,
                               año_fin: int = 2023) -> Dict:
    """
    Prepara y valida datos para alimentar el modelo
    
    Returns:
        Dict con datos validados y procesados
    """
    datos_modelo = {}
    
    # Filtrar por rango de años
    for nombre, df in datos.items():
        df_filtrado = df[(df['anio'] >= año_inicio) & (df['anio'] <= año_fin)].copy()
        datos_modelo[nombre] = df_filtrado
    
    # Validaciones
    validaciones = {
        'datos_completos': all(len(df) > 0 for df in datos_modelo.values()),
        'años_consistentes': len(set(
            tuple(df['anio'].values) for df in datos_modelo.values()
        )) == 1,
        'sin_nulos_criticos': True  # Implementar según necesidad
    }
    
    return {
        'datos': datos_modelo,
        'validaciones': validaciones,
        'rango_años': (año_inicio, año_fin)
    }