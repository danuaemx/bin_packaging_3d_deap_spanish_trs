from dataclasses import dataclass
"""
    Las estructuras de datos que se usaron
    solo para facilitar el modelo
"""

@dataclass
class Paquete:

    nombre: str
    dimensiones: tuple[int, int, int]
    cantidad_minima: int
    cantidad_maxima: int

@dataclass
class RequisitosPaquete:
    paquete: Paquete
    rotaciones_permitidas: tuple[bool, bool, bool, bool, bool]

@dataclass
class RequisitosContenedor:
    dimensiones_minimas: tuple[int, int, int]
    dimensiones_maximas: tuple[int, int, int]
    id: str = "default"  # Añadido para identificar el contenedor

@dataclass
class DatosEmpaquetado:
    requisitos_paquetes: list[RequisitosPaquete]
    contenedores: list[RequisitosContenedor]