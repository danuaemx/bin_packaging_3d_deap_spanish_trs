from dataclasses import dataclass
"""
    Las estructuras de datos que se usaron
    solo para facilitar el modelo
"""


@dataclass
class Paquete:
    nombre: str
    dimensiones: tuple
    cantidad_minima: int
    cantidad_maxima: int


@dataclass
class RequisitosContenedor:
    dimensiones: tuple  # Dimensiones fijas
    id: str
    uso_opcional: bool = False  # New flag to indicate if container usage can be modified


@dataclass
class DatosEmpaquetado:
    paquetes: list[Paquete]
    contenedores: list[RequisitosContenedor]