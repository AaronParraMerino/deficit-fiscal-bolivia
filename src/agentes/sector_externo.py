"""
Sector externo: exportaciones, importaciones y cuenta corriente simplificada.
"""

from dataclasses import dataclass

@dataclass
class SectorExterno:
    def balanza_comercial(self, exportaciones: float, importaciones: float) -> float:
        """Exportaciones - Importaciones."""
        return exportaciones - importaciones

    def cuenta_corriente(self, exportaciones: float, importaciones: float, renta_neta: float = 0.0) -> float:
        """Cuenta corriente simplificada."""
        return self.balanza_comercial(exportaciones, importaciones) + renta_neta
