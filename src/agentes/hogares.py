"""
Módulo de hogares.

Versión minimal: describe el consumo y los impuestos indirectos asociados.
"""

from dataclasses import dataclass

@dataclass
class Hogares:
    propension_consumo: float = 0.7      # % del ingreso que se consume
    tasa_impuesto_indirecto: float = 0.13  # IVA u otros

    def consumo(self, ingreso_disponible: float) -> float:
        return ingreso_disponible * self.propension_consumo

    def impuestos_indirectos(self, ingreso_disponible: float) -> float:
        cons = self.consumo(ingreso_disponible)
        return cons * self.tasa_impuesto_indirecto
