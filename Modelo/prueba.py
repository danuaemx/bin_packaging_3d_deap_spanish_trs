from bpga_3d import OptimizadorEmpaquetadoMultiContenedor
from datos import *

def main() -> None:
    # Definir requisitos específicos para cada contenedor

    paquetes = [RequisitosPaquete(Paquete('P1', (1, 1, 1), 10, 15), (True, True, True, True, True)),
                RequisitosPaquete(Paquete('P2', (3, 3, 3), 15, 100), (True, True, True, True, True)),
                RequisitosPaquete(Paquete('P3', (5, 5, 5), 2, 3), (True, True, True, False, False))
    ]

    requisitos_contenedores = [
        RequisitosContenedor(
            dimensiones_minimas=(5, 5, 5),
            dimensiones_maximas=(5, 5, 5),
            id="Contenedor_1"
        ),
        RequisitosContenedor(
            dimensiones_minimas=(11, 11, 11),
            dimensiones_maximas=(11,11,11),
            id="Contenedor_2"
        ),
        RequisitosContenedor(
            dimensiones_minimas=(4, 4, 4),
            dimensiones_maximas=(6, 6, 6),
            id="Contenedor_3"
        ),
        RequisitosContenedor(
            dimensiones_minimas=(2, 2, 2),
            dimensiones_maximas=(2, 2, 2),
            id="Contenedor_4"
        )
    ]

    datos_empaquetado = DatosEmpaquetado(paquetes,requisitos_contenedores)

    # Crear y ejecutar el optimizador
    optimizador = OptimizadorEmpaquetadoMultiContenedor(
        datos_empaquetado=datos_empaquetado,
        generaciones=61
    )

    # Ejecutar la optimización
    resultado = optimizador.optimizar()

    # Analizar y mostrar resultados
    analisis = optimizador.analizar_resultados(resultado)
    optimizador.imprimir_resultados(resultado, analisis)


if __name__ == "__main__":
    main()