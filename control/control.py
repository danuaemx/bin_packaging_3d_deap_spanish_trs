import sys
from PyQt5.QtWidgets import QApplication
from vista.vista_principal import BPGAVista
from modelo.modelo_principal import Modelo
from modelo.datos import RequisitosContenedor, Paquete

class Control:
    def __init__(self):
        self._modelo : Modelo = None
        self._app = QApplication(sys.argv)
        self._vista : BPGAVista = None

    def set_mvc(self,modelo: Modelo,vista: BPGAVista):
        self._modelo = modelo
        self._vista = vista

    def inciar(self):
        self._vista.show()
        sys.exit(self._app.exec_())

    def solicitud(self,contenedores: list[RequisitosContenedor],paquetes: list[Paquete],rotaciones: list[tuple]):
        print(contenedores)
        print(paquetes)
        print(rotaciones)
        print("Solicitud recibida")
        self._modelo.optimizar(contenedores,paquetes,rotaciones)

    def listo(self):
        print("Listo")
