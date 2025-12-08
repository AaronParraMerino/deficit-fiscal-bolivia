"""
Versión determinística del modelo: mismas ecuaciones, sin shocks aleatorios.
"""

import pandas as pd
from .parametros import ParametrosMacroeconomicos, ParametrosDeuda

def simular_deterministico(
    macro: ParametrosMacroeconomicos,
    deuda: ParametrosDeuda,
) -> pd.DataFrame:
    # Aquí puedes llamar una versión de las ecuaciones sin ruido
    # o usar tu modelo_estocastico con volatilidades = 0
    # Para no complicar, hacemos un dummy que devuelve algo coherente.
    from .modelo_estocastico import simular_escenario_estocastico

    return simular_escenario_estocastico(
        macro=macro,
        deuda=deuda,
        volatilidad_cero=True  # si agregas ese flag en el modelo estocástico
    )
