"""
Módulo para carga y procesamiento de datos CSV
Todos los archivos tienen 'anio' como primera columna
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class DataLoader:
    """Cargador de datos económicos de Bolivia desde CSV"""
    
    def __init__(self, data_dir: str = "data/processed"):
        self.data_dir = Path(data_dir)
        self.datos_cargados = {}
        
    def cargar_csv(self, nombre_archivo: str) -> pd.DataFrame:
        """
        Carga un archivo CSV genérico
        Todos tienen 'anio' como primera columna
        """
        ruta = self.data_dir / f"{nombre_archivo}.csv"
        
        if not ruta.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {ruta}")
        
        df = pd.read_csv(ruta)
        
        # Asegurar que 'anio' sea la primera columna y esté en formato correcto
        if 'anio' in df.columns:
            df['anio'] = pd.to_numeric(df['anio'], errors='coerce')
            df = df.dropna(subset=['anio'])
            df['anio'] = df['anio'].astype(int)
            df = df.sort_values('anio').reset_index(drop=True)
        
        return df
    
    def cargar_balanza_pagos(self) -> pd.DataFrame:
        """Carga datos de balanza de pagos"""
        df = self.cargar_csv('balanza_pagos')
        self.datos_cargados['balanza_pagos'] = df
        return df
    
    def cargar_deuda_publica_externa(self) -> pd.DataFrame:
        """Carga datos de deuda pública externa"""
        df = self.cargar_csv('deuda_publica_externa')
        self.datos_cargados['deuda_externa'] = df
        return df
    
    def cargar_ipc(self) -> pd.DataFrame:
        """Carga datos del Índice de Precios al Consumidor"""
        df = self.cargar_csv('IPC')
        self.datos_cargados['ipc'] = df
        return df
    
    def cargar_minerales(self) -> pd.DataFrame:
        """Carga datos de precios/producción de minerales"""
        df = self.cargar_csv('minerales')
        self.datos_cargados['minerales'] = df
        return df
    
    def cargar_pib_actividad(self) -> pd.DataFrame:
        """Carga PIB por actividad económica"""
        df = self.cargar_csv('PIB_actividad_economica')
        self.datos_cargados['pib_actividad'] = df
        return df
    
    def cargar_pib_gasto(self) -> pd.DataFrame:
        """Carga PIB por tipo de gasto"""
        df = self.cargar_csv('PIB_tipo_gasto')
        self.datos_cargados['pib_gasto'] = df
        return df
    
    def cargar_spnf(self) -> pd.DataFrame:
        """Carga datos del Sector Público No Financiero"""
        df = self.cargar_csv('SPNF')
        self.datos_cargados['spnf'] = df
        return df
    
    def cargar_stock_deuda(self) -> pd.DataFrame:
        """Carga stock de deuda pública"""
        df = self.cargar_csv('stock_deuda_publica')
        self.datos_cargados['stock_deuda'] = df
        return df
    
    def cargar_tasa_interes(self) -> pd.DataFrame:
        """Carga tasas de interés internacionales"""
        df = self.cargar_csv('tasa_interes_internacional')
        self.datos_cargados['tasa_interes'] = df
        return df
    
    def cargar_tipo_cambio(self) -> pd.DataFrame:
        """Carga tipo de cambio"""
        df = self.cargar_csv('tipo_de_camnio')  # Nota: el archivo tiene typo "camnio"
        self.datos_cargados['tipo_cambio'] = df
        return df
    
    def cargar_todos(self) -> Dict[str, pd.DataFrame]:
        """Carga todos los archivos de datos"""
        print("Cargando todos los datasets desde CSV...")
        
        datasets = {
            'balanza_pagos': self.cargar_balanza_pagos,
            'deuda_externa': self.cargar_deuda_publica_externa,
            'ipc': self.cargar_ipc,
            'minerales': self.cargar_minerales,
            'pib_actividad': self.cargar_pib_actividad,
            'pib_gasto': self.cargar_pib_gasto,
            'spnf': self.cargar_spnf,
            'stock_deuda': self.cargar_stock_deuda,
            'tasa_interes': self.cargar_tasa_interes,
            'tipo_cambio': self.cargar_tipo_cambio
        }
        
        for nombre, func in datasets.items():
            try:
                func()
                print(f"✓ {nombre} cargado ({len(self.datos_cargados[nombre])} registros)")
            except Exception as e:
                print(f"✗ Error cargando {nombre}: {str(e)}")
        
        return self.datos_cargados
    
    def obtener_serie_temporal(self, dataset: str, columna: str, 
                              año_inicio: int = None, 
                              año_fin: int = None) -> pd.Series:
        """
        Extrae una serie temporal específica
        
        Args:
            dataset: nombre del dataset (ej: 'spnf', 'pib_gasto')
            columna: nombre de la columna a extraer
            año_inicio: año inicial (opcional)
            año_fin: año final (opcional)
        
        Returns:
            Serie temporal indexada por año
        """
        if dataset not in self.datos_cargados:
            raise ValueError(f"Dataset '{dataset}' no está cargado")
        
        df = self.datos_cargados[dataset]
        
        if columna not in df.columns:
            raise ValueError(f"Columna '{columna}' no existe en {dataset}")
        
        # Filtrar por años si se especifica
        if año_inicio is not None:
            df = df[df['anio'] >= año_inicio]
        if año_fin is not None:
            df = df[df['anio'] <= año_fin]
        
        # Crear serie con índice de año
        serie = df.set_index('anio')[columna]
        return serie
    
    def fusionar_datasets(self, datasets: List[str], 
                         columnas: Dict[str, List[str]] = None,
                         año_inicio: int = None,
                         año_fin: int = None) -> pd.DataFrame:
        """
        Fusiona múltiples datasets por año
        
        Args:
            datasets: lista de nombres de datasets a fusionar
            columnas: dict con columnas a incluir por dataset (opcional)
            año_inicio, año_fin: rango de años (opcional)
        
        Returns:
            DataFrame fusionado por año
        """
        dfs = []
        
        for dataset in datasets:
            if dataset not in self.datos_cargados:
                continue
            
            df = self.datos_cargados[dataset].copy()
            
            # Filtrar columnas si se especifica
            if columnas and dataset in columnas:
                cols = ['anio'] + columnas[dataset]
                df = df[cols]
            
            # Filtrar por años
            if año_inicio:
                df = df[df['anio'] >= año_inicio]
            if año_fin:
                df = df[df['anio'] <= año_fin]
            
            # Renombrar columnas para evitar conflictos (excepto 'anio')
            df.columns = ['anio'] + [f"{dataset}_{col}" if col != 'anio' else col 
                                     for col in df.columns[1:]]
            
            dfs.append(df)
        
        # Fusionar todos por 'anio'
        df_final = dfs[0]
        for df in dfs[1:]:
            df_final = pd.merge(df_final, df, on='anio', how='outer')
        
        df_final = df_final.sort_values('anio').reset_index(drop=True)
        
        return df_final


class DataCalibrator:
    """Calibra parámetros del modelo desde datos históricos"""
    
    def __init__(self, datos: Dict[str, pd.DataFrame]):
        self.datos = datos
        
    def calcular_ratios_fiscales(self) -> Dict[str, float]:
        """
        Calcula ratios fiscales promedio históricos
        Necesita: SPNF, PIB
        """
        if 'spnf' not in self.datos or 'pib_gasto' not in self.datos:
            raise ValueError("Necesita datos de SPNF y PIB")
        
        df_spnf = self.datos['spnf']
        df_pib = self.datos['pib_gasto']
        
        # Fusionar por año
        df = pd.merge(df_spnf, df_pib[['anio', 'pib']], on='anio')
        
        # Calcular ratios (ajustar nombres de columnas según tu CSV)
        ratios = {}
        
        # NOTA: Estos nombres de columnas son ejemplos
        # Deberás ajustarlos según tus datos reales
        if 'ingresos_totales' in df.columns:
            ratios['tasa_ingreso_pib'] = (df['ingresos_totales'] / df['pib']).mean()
        
        if 'gastos_totales' in df.columns:
            ratios['tasa_gasto_pib'] = (df['gastos_totales'] / df['pib']).mean()
        
        if 'gasto_corriente' in df.columns:
            ratios['tasa_gasto_corriente_pib'] = (df['gasto_corriente'] / df['pib']).mean()
        
        return ratios
    
    def estimar_volatilidades(self) -> Dict[str, float]:
        """
        Estima volatilidades históricas para shocks estocásticos
        """
        volatilidades = {}
        
        # Volatilidad de PIB
        if 'pib_gasto' in self.datos:
            df_pib = self.datos['pib_gasto']
            if 'pib' in df_pib.columns:
                crecimiento = df_pib['pib'].pct_change().dropna()
                volatilidades['pib'] = crecimiento.std()
        
        # Volatilidad de precios de minerales
        if 'minerales' in self.datos:
            df_min = self.datos['minerales']
            # Ajustar según tus columnas de precios
            for col in df_min.columns:
                if 'precio' in col.lower():
                    retornos = df_min[col].pct_change().dropna()
                    volatilidades[f'minerales_{col}'] = retornos.std()
        
        return volatilidades
    
    def calibrar_deuda_inicial(self, año: int = 2020) -> Dict[str, float]:
        """
        Obtiene valores iniciales de deuda para un año específico
        """
        if 'stock_deuda' not in self.datos:
            return {}
        
        df_deuda = self.datos['stock_deuda']
        fila = df_deuda[df_deuda['anio'] == año]
        
        if fila.empty:
            return {}
        
        # Ajustar nombres de columnas según tu CSV
        valores = {}
        for col in fila.columns:
            if col != 'anio':
                valores[col] = fila[col].values[0]
        
        return valores
    
    def generar_configuracion_calibrada(self) -> Dict:
        """
        Genera diccionario de parámetros calibrados desde datos históricos
        """
        config = {}
        
        # Ratios fiscales
        ratios = self.calcular_ratios_fiscales()
        config['gobierno'] = ratios
        
        # Volatilidades
        volatilidades = self.estimar_volatilidades()
        config['volatilidades'] = volatilidades
        
        # Valores iniciales
        deuda_inicial = self.calibrar_deuda_inicial(2020)
        config['deuda_inicial'] = deuda_inicial
        
        return config


def generar_reporte_datos(datos: Dict[str, pd.DataFrame]) -> str:
    """Genera un reporte de los datos cargados"""
    lineas = []
    lineas.append("=" * 70)
    lineas.append("REPORTE DE DATOS CARGADOS (CSV)")
    lineas.append("=" * 70)
    
    for nombre, df in datos.items():
        lineas.append(f"\n{nombre.upper()}")
        lineas.append("-" * 50)
        lineas.append(f"Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas")
        lineas.append(f"Rango años: {df['anio'].min():.0f} - {df['anio'].max():.0f}")
        lineas.append(f"Columnas: {', '.join(df.columns[1:6].tolist())}...")
        
        # Valores nulos
        nulos = df.isnull().sum()
        if nulos.sum() > 0:
            lineas.append("Valores nulos:")
            for col, num in nulos[nulos > 0].items():
                lineas.append(f"  - {col}: {num}")
    
    lineas.append("\n" + "=" * 70)
    
    return "\n".join(lineas)


def exportar_resultados(df: pd.DataFrame, 
                       nombre_archivo: str,
                       directorio: str = "resultados") -> None:
    """Exporta resultados de simulación a CSV"""
    Path(directorio).mkdir(exist_ok=True)
    ruta = Path(directorio) / f"{nombre_archivo}.csv"
    df.to_csv(ruta, index=False)
    print(f"✓ Resultados exportados a: {ruta}")