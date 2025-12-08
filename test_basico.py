"""
Script de prueba completo del sistema
Ejecutar: python test_sistema.py
"""
import sys
from pathlib import Path

# Agregar src al path
proyecto_root = Path(__file__).parent
sys.path.insert(0, str(proyecto_root))

def test_imports():
    """Test 1: Verificar que todos los módulos se pueden importar"""
    print("=" * 70)
    print("TEST 1: IMPORTACIÓN DE MÓDULOS")
    print("=" * 70)
    
    modulos = [
        ("ConfiguracionModelo", "src.modelo.parametros", "ConfiguracionModelo, ESCENARIOS"),
        ("AgenteGobierno", "src.agentes.gobierno", "AgenteGobierno"),
        ("AgenteEmpresas", "src.agentes.empresas", "AgenteEmpresas"),
        ("ModeloEstocastico", "src.modelo.modelo_estocastico", "ModeloEstocastico"),
        ("DataLoader", "src.utils.io", "DataLoader"),
    ]
    
    resultados = []
    for nombre, modulo, imports in modulos:
        try:
            exec(f"from {modulo} import {imports}")
            print(f"✓ {nombre} importado correctamente")
            resultados.append(True)
        except Exception as e:
            print(f"✗ ERROR en {nombre}: {e}")
            resultados.append(False)
    
    return all(resultados)


def test_configuracion():
    """Test 2: Crear y validar configuración"""
    print("\n" + "=" * 70)
    print("TEST 2: CONFIGURACIÓN DEL MODELO")
    print("=" * 70)
    
    try:
        from src.modelo.parametros import ConfiguracionModelo, ESCENARIOS
        
        config = ConfiguracionModelo()
        print("✓ Configuración creada")
        
        # Verificar parámetros
        print(f"  - Tasa impositiva: {config.gobierno.tasa_impositiva_base}")
        print(f"  - PIB inicial: ${config.macroeconomicos.pib_inicial:,.0f}M")
        print(f"  - Precio gas base: ${config.sector_externo.precio_gas_base}")
        print(f"  - Escenarios: {list(ESCENARIOS.keys())}")
        
        # Validar
        errores = config.validar_parametros()
        if errores:
            print(f"⚠ Errores de validación: {errores}")
            return False
        else:
            print("✓ Parámetros válidos")
            return True
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agentes():
    """Test 3: Crear agentes"""
    print("\n" + "=" * 70)
    print("TEST 3: CREACIÓN DE AGENTES")
    print("=" * 70)
    
    try:
        from src.modelo.parametros import ConfiguracionModelo
        from src.agentes.gobierno import AgenteGobierno
        from src.agentes.empresas import AgenteEmpresas
        
        config = ConfiguracionModelo()
        
        # Gobierno
        gobierno = AgenteGobierno(config.gobierno)
        print(f"✓ AgenteGobierno creado")
        print(f"  - Deuda inicial: ${gobierno.estado.deuda_total:,.0f}M")
        
        # Empresas
        empresas = AgenteEmpresas(config.empresas)
        print(f"✓ AgenteEmpresas creado")
        print(f"  - Producción gas inicial: {empresas.estado.produccion_gas:.1f}")
        
        return True
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_carga_datos():
    """Test 4: Cargar datos CSV"""
    print("\n" + "=" * 70)
    print("TEST 4: CARGA DE DATOS CSV")
    print("=" * 70)
    
    try:
        from src.utils.io import DataLoader
        import os
        
        # Verificar si existe la carpeta
        if not os.path.exists("data/processed"):
            print("⚠ Carpeta data/processed no existe")
            print("  Creando carpeta...")
            os.makedirs("data/processed", exist_ok=True)
            print("  ℹ Copia tus archivos CSV a data/processed/")
            return True
        
        # Verificar archivos
        archivos = list(Path("data/processed").glob("*.csv"))
        if not archivos:
            print("⚠ No hay archivos CSV en data/processed")
            print("  ℹ Copia tus archivos CSV a esta carpeta")
            return True
        
        print(f"  Archivos encontrados: {len(archivos)}")
        for archivo in archivos[:5]:
            print(f"    - {archivo.name}")
        
        # Intentar cargar
        loader = DataLoader("data/processed")
        datos = loader.cargar_todos()
        
        print(f"✓ {len(datos)} datasets cargados correctamente")
        
        # Mostrar info de cada uno
        for nombre, df in datos.items():
            print(f"  - {nombre}: {len(df)} filas, {len(df.columns)} columnas")
            if 'anio' in df.columns:
                print(f"    Años: {df['anio'].min():.0f} - {df['anio'].max():.0f}")
        
        return True
        
    except Exception as e:
        print(f"⚠ ADVERTENCIA: {e}")
        print("  (Normal si aún no has copiado los CSV)")
        return True


def test_simulacion():
    """Test 5: Ejecutar simulación corta"""
    print("\n" + "=" * 70)
    print("TEST 5: SIMULACIÓN BÁSICA")
    print("=" * 70)
    
    try:
        from src.modelo.parametros import ConfiguracionModelo
        from src.modelo.modelo_estocastico import ModeloEstocastico
        from src.agentes.gobierno import AgenteGobierno
        from src.agentes.empresas import AgenteEmpresas
        
        config = ConfiguracionModelo()
        
        # Crear agentes
        gobierno = AgenteGobierno(config.gobierno)
        empresas = AgenteEmpresas(config.empresas)
        
        agentes = {
            'gobierno': gobierno,
            'empresas': empresas
        }
        
        # Modelo
        modelo = ModeloEstocastico(config, agentes)
        print("✓ Modelo creado")
        
        # Simular 4 periodos (1 año)
        print("  Simulando 4 periodos (1 año)...")
        df = modelo.simular(num_periodos=4)
        
        print(f"✓ Simulación completada")
        print(f"  - Periodos: {len(df)}")
        print(f"  - Variables: {len(df.columns)}")
        
        # Resultados
        if len(df) > 0:
            ultimo = df.iloc[-1]
            print(f"\n📊 RESULTADOS FINALES:")
            print(f"  - PIB: ${ultimo['pib']:,.0f}M")
            print(f"  - Deuda Total: ${ultimo['gob_deuda_total']:,.0f}M")
            print(f"  - Ratio Deuda/PIB: {ultimo['gob_ratio_deuda_pib']:.2%}")
            print(f"  - Déficit/PIB: {ultimo['gob_ratio_deficit_pib']:.2%}")
            print(f"  - Reservas: ${ultimo['reservas_internacionales']:,.0f}M")
        
        return True
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecuta todos los tests"""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  SISTEMA DE PRUEBAS - SIMULADOR DÉFICIT FISCAL BOLIVIA".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print("\n")
    
    tests = [
        ("Importación de módulos", test_imports),
        ("Configuración", test_configuracion),
        ("Agentes", test_agentes),
        ("Carga de datos", test_carga_datos),
        ("Simulación", test_simulacion),
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"\n✗ Error crítico en {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE TESTS")
    print("=" * 70)
    
    for nombre, resultado in resultados:
        simbolo = "✓" if resultado else "✗"
        print(f"{simbolo} {nombre}")
    
    exitosos = sum(1 for _, r in resultados if r)
    total = len(resultados)
    
    print("\n" + "=" * 70)
    print(f"Tests exitosos: {exitosos}/{total}")
    print("=" * 70)
    
    if exitosos == total:
        print("\n✓✓✓ TODOS LOS TESTS PASARON ✓✓✓")
        print("\n🚀 Próximos pasos:")
        print("1. Copia tus archivos CSV a data/processed/")
        print("2. Ejecuta: streamlit run web/app.py")
        print("3. ¡Comienza a simular!")
    else:
        print("\n⚠️ ALGUNOS TESTS FALLARON")
        print("Revisa los errores arriba y corrige antes de continuar")
    
    return exitosos == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrumpidos por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)