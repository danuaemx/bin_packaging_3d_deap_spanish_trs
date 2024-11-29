from dataclasses import dataclass
"""
    Las estructuras de datos que se usaron
    solo para facilitar el modelo
"""

@dataclass
class Paquete:
    """
    Clase para representar un paquete
    :param nombre: Nombre del paquete
    :param dimensiones: Dimensiones del paquete
    :param cantidad_minima: Cantidad mínima de paquetes en todos los contenedores
    :param cantidad_maxima: Cantidad máxima de paquetes en todos los contenedores
    """

    nombre: str
    dimensiones: tuple[int, int, int]
    cantidad_minima: int
    cantidad_maxima: int

@dataclass
class RequisitosContenedor:
    """
    Clase para representar los requisitos de un contenedor
    :param dimensiones_minimas: Dimensiones mínimas del contenedor
    :param dimensiones_maximas: Dimensiones máximas del contenedor
    :param id: Identificador del contenedor
    """
    dimensiones_minimas: tuple[int, int, int]
    dimensiones_maximas: tuple[int, int, int]
    id: str   # Añadido para identificar el contenedor

@dataclass
class DatosEmpaquetado:
    """
    Clase para representar los datos de empaquetado
    :param tipos_paquetes: Lista de tipos de paquetes
    :param contenedores: Lista de requisitos de contenedores
    :param rotaciones_permitidas: Lista de rotaciones permitidas para los paquetes
    """
    tipos_paquetes: list[Paquete]
    contenedores: list[RequisitosContenedor]
    rotaciones_permitidas: list[tuple[bool, bool, bool, bool, bool]]