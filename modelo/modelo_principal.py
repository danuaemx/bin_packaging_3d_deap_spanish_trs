from modelo.datos import RequisitosContenedor, Paquete
from modelo.bpga_3d import OptimizadorEmpaquetadoMultiContenedor3D
from modelo.bpga_2d import OptimizadorEmpaquetadoMultiContenedor2D
from modelo.bpga_1d import OptimizadorEmpaquetadoMultiContenedor1D

class Modelo:
    def __init__(self, control):
        self.control = control

    def optimizar(self,contenedores: list[RequisitosContenedor],paquetes: list[Paquete],rotaciones,
                  poblacion: int,
                  generaciones: int) -> dict:

        if len(contenedores[0].dimensiones) == 1:
            print(contenedores)
            print(paquetes[0].dimensiones)
            optimizador = OptimizadorEmpaquetadoMultiContenedor1D(
                requisitos_contenedores=contenedores,
                tipos_paquetes=paquetes,
                rotaciones_permitidas=rotaciones,
                tamano_poblacion= poblacion,
                generaciones= generaciones)

        elif len(contenedores[0].dimensiones) == 2:
            optimizador = OptimizadorEmpaquetadoMultiContenedor2D(
                requisitos_contenedores=contenedores,
                tipos_paquetes=paquetes,
                rotaciones_permitidas=rotaciones,
                tamano_poblacion=poblacion,
                generaciones=generaciones
            )
        else:
            optimizador = OptimizadorEmpaquetadoMultiContenedor3D(
                requisitos_contenedores=contenedores,
                tipos_paquetes=paquetes,
                rotaciones_permitidas=rotaciones,
                tamano_poblacion=poblacion,
                generaciones=generaciones
            )
        resultado = optimizador.optimizar()
        optimizador.analizar_resultados(resultado)
        optimizador.imprimir_resultados(resultado, optimizador.analizar_resultados(resultado))
        optimizador.graficar_estadisticas()
        optimizador.graficar_resultados(resultado)
        self.control.listo()

