from modelo.datos import *
from modelo.bpga_3d import OptimizadorEmpaquetadoMultiContenedor3D
from modelo.bpga_2d import OptimizadorEmpaquetadoMultiContenedor2D
from modelo.bpga_1d import OptimizadorEmpaquetadoMultiContenedor1D


def prueba_1d() -> None:
    requisitos_contenedores = [
        RequisitosContenedor(
            dimensiones=(10,),  # Dimensiones fijas para el primer contenedor
            id="Contenedor_1",
            uso_opcional=False  # Este contenedor SIEMPRE se usa
        ),
        RequisitosContenedor(
            dimensiones=(20,),  # Dimensiones fijas para el segundo contenedor
            id="Contenedor_2",
            uso_opcional=False  # Este contenedor puede o no usarse
        ),
    ]

    # Crear y ejecutar el optimizador
    optimizador = OptimizadorEmpaquetadoMultiContenedor1D(
        requisitos_contenedores=requisitos_contenedores,
        tipos_paquetes=[
            Paquete('P3', (1,), 1, 100),
            Paquete('P1', (2,), 1, 100),
            Paquete('P2', (5,), 1, 100),
        ],
        tamano_poblacion=10000,
        generaciones=10
    )

    # Ejecutar la optimización
    resultado = optimizador.optimizar()

    # Analizar y mostrar resultados
    analisis = optimizador.analizar_resultados(resultado)
    optimizador.imprimir_resultados(resultado, analisis)
    optimizador.graficar_resultados(resultado)

def prueba_2d() -> None:

        requisitos_contenedores = [
            RequisitosContenedor(
                dimensiones=(10, 10),  # Dimensiones fijas para el primer contenedor
                id="Contenedor_1",
                uso_opcional=False  # Este contenedor SIEMPRE se usa
            ),
            RequisitosContenedor(
                dimensiones=(20, 20),  # Dimensiones fijas para el segundo contenedor
                id="Contenedor_2",
                uso_opcional=False  # Este contenedor puede o no usarse
            ),
        ]

        # Crear y ejecutar el optimizador
        optimizador = OptimizadorEmpaquetadoMultiContenedor2D(
            requisitos_contenedores=requisitos_contenedores,
            tipos_paquetes=[
                Paquete('P3', (3, 1), 1, 30),
                Paquete('P1', (2, 2), 1, 30),
                Paquete('P2', (5, 7), 1, 30),
            ],
            tamano_poblacion=10000,
            generaciones=10,
            rotaciones_permitidas=[
                (True,),
                (False,),
                (True,),
            ]
        )

        # Ejecutar la optimización
        resultado = optimizador.optimizar()

        # Analizar y mostrar
        analisis = optimizador.analizar_resultados(resultado)
        optimizador.imprimir_resultados(resultado, analisis)
        optimizador.graficar_resultados(resultado)

def prueba_3d() -> None:

    requisitos_contenedores = [
        RequisitosContenedor(
            dimensiones=(4, 4, 4),  # Dimensiones fijas para el primer contenedor
            id="Contenedor_1",
            uso_opcional=False  # Este contenedor SIEMPRE se usa
        ),
        RequisitosContenedor(
            dimensiones=(5, 5, 5),  # Dimensiones fijas para el segundo contenedor
            id="Contenedor_2",
            uso_opcional=False  # Este contenedor puede o no usarse
        ),
    ]

    # Crear y ejecutar el optimizador
    optimizador = OptimizadorEmpaquetadoMultiContenedor3D(
        requisitos_contenedores=requisitos_contenedores,
        tipos_paquetes=[
            Paquete('P3', (1, 1, 1), 1, 100),
            Paquete('P1', (2, 2, 2), 1, 100),
            Paquete('P2', (5, 5, 5), 1, 100),
        ],
        tamano_poblacion=10000,
        generaciones=10,
        rotaciones_permitidas=[
        (True, True, True, True, True),
        (True, False, True, False, True),
        (True, True, True, False, False),
        ]
    )

    # Ejecutar la optimización
    resultado = optimizador.optimizar()

    # Analizar y mostrar resultados
    analisis = optimizador.analizar_resultados(resultado)
    optimizador.imprimir_resultados(resultado, analisis)
    optimizador.graficar_resultados(resultado)



def main() -> None:

    prueba_1d()
    prueba_2d()
    prueba_3d()




if __name__ == "__main__":
    main()