from bpga_3d import OptimizadorEmpaquetadoMultiContenedor
from datos import *

def main() -> None:
    # Definir requisitos específicos para cada contenedor

    paquetes = [Paquete('P1', (3, 3, 1), 1, 10),
                Paquete('P2', (3, 3, 3), 1, 20),
                Paquete('P3', (5, 5, 5), 1, 20)
    ]
    rotaciones_pertmitidas  = [
    (True, True, True, True, True),
    (True, False, True, False, True),
    (True, True, True, False, False),
    ]
    requisitos_contenedores = [
        RequisitosContenedor(
            dimensiones_minimas=(15, 15, 15),
            dimensiones_maximas=(15, 15, 15),
            id="Contenedor_1"
        ),
        RequisitosContenedor(
            dimensiones_minimas=(4, 4, 4),
            dimensiones_maximas=(10, 10, 10),
            id="Contenedor_3"
        )
    ]

    datos_empaquetado = DatosEmpaquetado(paquetes,requisitos_contenedores,rotaciones_pertmitidas)

    # Crear y ejecutar el optimizador
    optimizador = OptimizadorEmpaquetadoMultiContenedor(
        datos_empaquetado=datos_empaquetado,
        generaciones=10
    )

    # Ejecutar la optimización
    resultado = optimizador.optimizar()

    # Analizar y mostrar resultados
    analisis = optimizador.analizar_resultados(resultado)
    optimizador.imprimir_resultados(resultado, analisis)


if __name__ == "__main__":
    main()