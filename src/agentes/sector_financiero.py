"""
Sector financiero: determina tasa de interés efectiva para la deuda.
"""

from dataclasses import dataclass

@dataclass
class SectorFinanciero:
    tasa_base_internacional: float = 0.02   # 2%
    prima_riesgo: float = 0.03              # 3%

    def tasa_interes_efectiva(self) -> float:
        return self.tasa_base_internacional + self.prima_riesgo
