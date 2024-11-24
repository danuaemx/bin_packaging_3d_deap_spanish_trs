from bpga_3d import OptimizadorEmpaquetadoMultiContenedor
from datos import *

def main() -> None:
    # Definir requisitos específicos para cada contenedor

    paquetes = [RequisitosPaquete(Paquete('P3', (3, 3, 3), 1, 100), (True, True, True, True, True)),
                RequisitosPaquete(Paquete('P1', (3, 1, 7), 2, 100), (True, True, True, True, True)),
                RequisitosPaquete(Paquete('P2', (5, 5, 5), 1, 100), (True, True, True, False, False))
    ]

    requisitos_contenedores = [
        RequisitosContenedor(
            dimensiones_minimas=(11, 7, 13),
            dimensiones_maximas=(11, 7, 13),
            id="Contenedor_1"
        ),
        RequisitosContenedor(
            dimensiones_minimas=(11, 11, 11),
            dimensiones_maximas=(11,11,11),
            id="Contenedor_2"
        )
    ]

    datos_empaquetado = DatosEmpaquetado(paquetes,requisitos_contenedores)

    # Crear y ejecutar el optimizador
    optimizador = OptimizadorEmpaquetadoMultiContenedor(
        datos_empaquetado=datos_empaquetado,
        generaciones=21
    )

    # Ejecutar la optimización
    resultado = optimizador.optimizar()

    # Analizar y mostrar resultados
    analisis = optimizador.analizar_resultados(resultado)
    optimizador.imprimir_resultados(resultado, analisis)


if __name__ == "__main__":
    main()