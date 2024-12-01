from modelo.datos import *
from modelo.bpga_3d import OptimizadorEmpaquetadoMultiContenedor3D
from modelo.bpga_2d import OptimizadorEmpaquetadoMultiContenedor2D
from modelo.bpga_1d import OptimizadorEmpaquetadoMultiContenedor1D


def prueba_1d() -> None:
    requisitos_contenedores = [
        RequisitosContenedor(
            dimensiones=(191,),  # Dimensiones para el primer contenedor
            id="Contenedor_1",
            uso_opcional=False  # Este contenedor siempre se usa
        ),
        RequisitosContenedor(
            dimensiones=(129,),
            id="Contenedor_2",
            uso_opcional=False
        ),
        RequisitosContenedor(
            dimensiones=(72,),
            id="Contenedor_3",
            uso_opcional=False
        ),
        RequisitosContenedor(
            dimensiones=(51,),
            id="Contenedor_4",
            uso_opcional=False
        ),
    ]

    # Crear y ejecutar el optimizador
    optimizador = OptimizadorEmpaquetadoMultiContenedor1D(
        requisitos_contenedores=requisitos_contenedores,
        tipos_paquetes=[
            Paquete('P1', (3,), 1, 3),
            Paquete('P2', (2,), 1, 5),
            Paquete('P3', (5,), 1, 3),
            Paquete('P4', (7,), 1, 4),
            Paquete('P5', (13,), 1, 2),
            Paquete('P6', (6,), 2, 3),
            Paquete('P7', (4,), 3, 10),
            Paquete('P8', (9,), 1, 3),
            Paquete('P9', (15,), 1, 5),
            Paquete('P10', (11,), 1, 6),
            Paquete('P11', (17,), 2, 4),
            Paquete('P11', (19,), 1, 4),
        ],
        tamano_poblacion=2000,
        generaciones=20
    )

    # Ejecutar la optimización
    resultado = optimizador.optimizar()

    # Analizar y mostrar resultados
    analisis = optimizador.analizar_resultados(resultado)
    optimizador.imprimir_resultados(resultado, analisis)
    optimizador.graficar_estadisticas()
    optimizador.graficar_resultados(resultado)

def prueba_2d() -> None:

        requisitos_contenedores = [
            RequisitosContenedor(
                dimensiones=(20, 20),  # Dimensiones fijas para el primer contenedor
                id="Contenedor_1",
                uso_opcional=True  # Este contenedor puede o no usarse
            ),
            RequisitosContenedor(
                dimensiones=(13, 19),
                id="Contenedor_2",
                uso_opcional=True
            ),
            RequisitosContenedor(
                dimensiones=(10, 17),
                id="Contenedor_3",
                uso_opcional=False # Este contenedor siempre se usa
            ),
            RequisitosContenedor(
                dimensiones=(20, 10),
                id="Contenedor_4",
                uso_opcional=True
            ),
            RequisitosContenedor(
                dimensiones=(15, 10),
                id="Contenedor_5",
                uso_opcional=True
            ),

        ]

        # Crear y ejecutar el optimizador
        optimizador = OptimizadorEmpaquetadoMultiContenedor2D(
            requisitos_contenedores=requisitos_contenedores,
            tipos_paquetes=[
                Paquete('P1', (6,2), 1, 30),
                Paquete('P2', (3, 3), 2, 30),
                Paquete('P3', (2, 5), 2, 30),
                Paquete('P4', (7, 1), 3, 30),
                Paquete('P5', (13, 2), 1, 30),
                Paquete('P6', (6, 6), 3, 30),  # Nuevo paquete
                Paquete('P7', (4, 4), 2, 30),  # Nuevo paquete
                Paquete('P8', (9, 1), 3, 30),  # Nuevo paquete
            ],
            tamano_poblacion=1000,
            generaciones=20,
            rotaciones_permitidas=[
                (True,),
                (False,),
                (True,),
                (True,),
                (True,),
                (True,),
                (True,),
                (False,),
            ]
        )

        # Ejecutar la optimización
        resultado = optimizador.optimizar()

        # Analizar y mostrar
        analisis = optimizador.analizar_resultados(resultado)
        optimizador.imprimir_resultados(resultado, analisis)
        optimizador.graficar_resultados(resultado)
        optimizador.graficar_estadisticas()

def prueba_3d() -> None:
    requisitos_contenedores = [
        RequisitosContenedor(
            dimensiones=(13, 13, 13),
            id="Contenedor_1",
            uso_opcional=False  # Siempre se usa
        ),
        RequisitosContenedor(
            dimensiones=(5, 7, 11),
            id="Contenedor_2",
            uso_opcional=False
        ),
        RequisitosContenedor(
            dimensiones=(13, 17, 19),
            id="Contenedor_3",
            uso_opcional=False

        ),
        RequisitosContenedor(
            dimensiones=(12, 11, 5),
            id="Contenedor_4",
            uso_opcional=False

        ),
    ]

    # Crear y ejecutar el optimizador
    optimizador = OptimizadorEmpaquetadoMultiContenedor3D(
        requisitos_contenedores=requisitos_contenedores,
        tipos_paquetes=[
            Paquete('P1', (2, 3, 5), 10, 45),
            Paquete('P2', (3, 3, 7), 5, 40),
            Paquete('P3', (5, 11, 13), 1, 4),
            Paquete('P4', (2, 3, 3), 3, 45),
            Paquete('P5', (7, 7, 7), 3, 10),

        ],
        tamano_poblacion=100,
        generaciones=20,
        rotaciones_permitidas=[
            (True, True, True, True, True),
            (True, False, True, False, True),
            (True, True, True, False, False),
            (True, True, True, True, True),
            (True, False, True, False, True),
        ]
    )

    # Ejecutar la optimización
    resultado = optimizador.optimizar()

    # Analizar y mostrar resultados
    analisis = optimizador.analizar_resultados(resultado)
    optimizador.imprimir_resultados(resultado, analisis)
    optimizador.graficar_resultados(resultado)
    optimizador.graficar_estadisticas()

def main() -> None:

    prueba_1d()
    prueba_2d()
    prueba_3d()

if __name__ == "__main__":
    main()