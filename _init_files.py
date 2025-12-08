"""
Script para crear archivos __init__.py en todas las carpetas necesarias
"""
from pathlib import Path

# Directorios que necesitan __init__.py
directorios = [
    'src',
    'src/agentes',
    'src/modelo',
    'src/simulacion',
    'src/utils',
]

def crear_init_files():
    """Crea archivos __init__.py en todos los directorios"""
    proyecto_root = Path(__file__).parent
    
    for directorio in directorios:
        ruta = proyecto_root / directorio
        archivo_init = ruta / '__init__.py'
        
        # Crear directorio si no existe
        ruta.mkdir(parents=True, exist_ok=True)
        
        # Crear __init__.py si no existe
        if not archivo_init.exists():
            archivo_init.touch()
            print(f"✓ Creado: {archivo_init}")
        else:
            print(f"  Ya existe: {archivo_init}")

if __name__ == "__main__":
    print("Creando archivos __init__.py...")
    print("-" * 50)
    crear_init_files()
    print("-" * 50)
    print("✓ Completado!")