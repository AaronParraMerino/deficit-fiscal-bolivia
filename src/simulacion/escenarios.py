from src.modelo.parametros import ParametrosModelo

def get_escenario(nombre: str) -> ParametrosModelo:
    nombre = nombre.lower()

    base = ParametrosModelo()

    if nombre == "pesimista":
        return ParametrosModelo(
            crecimiento_pib_medio=0.0,
            volatilidad_crecimiento=0.03,
            deficit_primario_medio=-0.05,
            volatilidad_deficit=0.02,
            tasa_interes_deuda=0.06
        )
    elif nombre == "optimista":
        return ParametrosModelo(
            crecimiento_pib_medio=0.04,
            volatilidad_crecimiento=0.015,
            deficit_primario_medio=-0.02,
            volatilidad_deficit=0.01,
            tasa_interes_deuda=0.04
        )
    else:  # base
        return base
