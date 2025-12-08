import pandas as pd

def analizar_resultados(resumen: pd.DataFrame, umbral: float = 80.0) -> dict:
    """
    resumen: DataFrame con columnas:
      - anio
      - deuda_pib_media
      - deuda_pib_p5
      - deuda_pib_p95
    Devuelve un diccionario con estadísticas para usar en la app.
    """
    ultimo = resumen.iloc[-1]

    estadisticas = {
        "anio_final": int(ultimo["anio"]),
        "ratio_deuda_pib_final": float(ultimo["deuda_pib_media"]),
        "ratio_deuda_pib_p5_final": float(ultimo["deuda_pib_p5"]),
        "ratio_deuda_pib_p95_final": float(ultimo["deuda_pib_p95"]),
        "umbral_sostenibilidad": umbral,
        "es_riesgoso": bool(ultimo["deuda_pib_media"] > umbral),
    }

    return {
        "estadisticas": estadisticas
    }
