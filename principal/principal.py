from control.control import Control
from vista.vista_principal import BPGAVista
from modelo.modelo_principal import Modelo

def main():

    control = Control()
    modelo = Modelo(control)
    vista = BPGAVista(control)
    control.set_mvc(modelo,vista)
    control.inciar()


if __name__ == "__main__":
    main()