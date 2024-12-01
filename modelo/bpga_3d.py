from datos import *
import numpy as np
from modelo.bpga_core import OptimizadorEmpaquetadoMultiContenedor
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def vertices_caja(pos, dims):
    """Crea los vértices de una caja 3D dada su posición y dimensiones"""
    x, y, z = pos
    l, w, h = dims
    vertices = np.array([
        [x, y, z], [x + l, y, z], [x + l, y + w, z], [x, y + w, z],
        [x, y, z + h], [x + l, y, z + h], [x + l, y + w, z + h], [x, y + w, z + h]
    ])
    return vertices

def caras_caja(vertices):
    """Crea las caras de una caja 3D a partir de sus vértices"""
    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],  # Inferior
        [vertices[4], vertices[5], vertices[6], vertices[7]],  # Superior
        [vertices[0], vertices[1], vertices[5], vertices[4]],  # Atraz
        [vertices[2], vertices[3], vertices[7], vertices[6]],  # Frente
        [vertices[0], vertices[3], vertices[7], vertices[4]],  # Izquierda
        [vertices[1], vertices[2], vertices[6], vertices[5]]  # Derecha
    ]
    return faces

class OptimizadorEmpaquetadoMultiContenedor3D(OptimizadorEmpaquetadoMultiContenedor):
    def __init__(self,
                 requisitos_contenedores: list[RequisitosContenedor],
                 tipos_paquetes: list[Paquete] ,
                 rotaciones_permitidas: list[tuple[bool, bool, bool, bool, bool]] ,
                 tamano_poblacion: int = 1000,
                 generaciones: int = 55,
                 prob_cruce: float = 0.618,
                 prob_mutacion: float = 0.021) -> None:

        super().__init__(requisitos_contenedores, tipos_paquetes, rotaciones_permitidas, tamano_poblacion, generaciones,
                         prob_cruce, prob_mutacion)

    def _generar_rotaciones_paquete(self, paquete: Paquete, indice : int) -> list[tuple]:
        """Genera todas las rotaciones únicas permitidas para un paquete"""
        nombre = paquete.nombre
        x, y, z = paquete.dimensiones
        rotaciones_tipo = [(nombre, x, y, z),]

        permisos = self.rotaciones_permitidas[indice]

        if permisos[0] and x != y:
            rotaciones_tipo.append((f"{nombre}_rxy", y, x, z))
        if permisos[1] and x != z:
            rotaciones_tipo.append((f"{nombre}_rxz", z, y, x))
        if permisos[2] and y != z:
            rotaciones_tipo.append((f"{nombre}_ryz", x, z, y))
        if permisos[3] and not (x == y == z):
            rotaciones_tipo.append((f"{nombre}_rxy_rxz", z, x, y))
        if permisos[4] and not (x == y == z):
            rotaciones_tipo.append((f"{nombre}_rxy_ryz", y, z, x))

        return rotaciones_tipo

    def _first_fit(self, colocado, dimensiones_contenedor, paquetes_colocados, paso_rejilla, rotaciones):
        for rotacion in rotaciones:
            nombre_rot, l_rot, a_rot, h_rot = rotacion

            for x in range(0, dimensiones_contenedor[0] - l_rot + 1, paso_rejilla):
                for y in range(0, dimensiones_contenedor[1] - a_rot + 1, paso_rejilla):
                    for z in range(0, dimensiones_contenedor[2] - h_rot + 1, paso_rejilla):
                        if self._puede_colocar_paquete(paquetes_colocados,
                                                       (nombre_rot, l_rot, a_rot, h_rot), (x, y, z),
                                                       dimensiones_contenedor):
                            paquetes_colocados.append(
                                (x, y, z, l_rot, a_rot, h_rot, nombre_rot)
                            )
                            colocado = True
                            break
                    if colocado:
                        break
                if colocado:
                    break
            if colocado:
                break
        return colocado

    def _puede_colocar_paquete(self, paquetes_existentes, nuevo_paquete, posicion, dimensiones_contenedor) -> bool:
        """Verifica si un paquete puede ser colocado en la posición dada"""
        x, y, z = posicion
        l, a, h = nuevo_paquete[1:4]

        if (x + l > dimensiones_contenedor[0] or
                y + a > dimensiones_contenedor[1] or
                z + h > dimensiones_contenedor[2]):
            return False

        for paq in paquetes_existentes:
            px, py, pz, pl, pa, ph, _ = paq
            if not (x + l <= px or px + pl <= x or
                    y + a <= py or py + pa <= y or
                    z + h <= pz or pz + ph <= z):
                return False
        return True

    def _conteo_paquetes(self, cantidad_total, dimensiones_contenedor, paquetes_colocados):
        for paq in paquetes_colocados:
            # Extraer el nombre original del paquete sin la rotación
            nombre_original = paq[6].split('_')[0]
            cantidad_total[nombre_original] += 1
        # Calcular volúmenes
        volumen_contenedor = np.prod(dimensiones_contenedor)
        volumen_utilizado = sum(paq[3] * paq[4] * paq[5] for paq in paquetes_colocados)
        return volumen_contenedor, volumen_utilizado

    def _contenedor_info(self, contenedor_info, paquetes_colocados):
        contenedor_info['paquetes'] = [
            {
                'tipo': paq[6],  # Nombre con rotación incluida
                'posicion': (paq[0], paq[1], paq[2]),
                'dimensiones': (paq[3], paq[4], paq[5])
            } for paq in paquetes_colocados
        ]

    def graficar_resultados(self, resultado: dict) -> None:
        """
        Visualiza los resultados del empaquetado en 3D usando matplotlib.
        Muestra cada contenedor en uso con los paquetes colocados en diferentes colores.

        Args:
            resultado (dict): Diccionario con los resultados de la optimización
        """

        # Crear una figura para cada contenedor en uso
        contenedores_en_uso = [cont for cont in resultado['posiciones']['contenedores'] if cont['en_uso']]

        if not contenedores_en_uso:
            print("No hay contenedores en uso para visualizar.")
            return

        # Configurar el diseño de la cuadrícula para los subplots
        n_contenedores = len(contenedores_en_uso)
        cols = min(3, n_contenedores)  # Máximo 3 columnas
        rows = (n_contenedores + cols - 1) // cols

        fig = plt.figure(figsize=(6 * cols, 6 * rows))

        # Generar colores únicos para cada tipo de paquete
        tipos_unicos = set()
        for cont in contenedores_en_uso:
            for paq in cont['paquetes']:
                tipos_unicos.add(paq['tipo'].split('_')[0])  # Usar nombre base sin rotación

        colores = plt.cm.get_cmap('tab20')(np.linspace(0, 1, len(tipos_unicos)))
        color_map = dict(zip(tipos_unicos, colores))

        for idx, contenedor in enumerate(contenedores_en_uso, 1):
            ax = fig.add_subplot(rows, cols, idx, projection='3d')

            # Dibujar el contenedor (transparente)
            vertices_cont = vertices_caja((0, 0, 0), contenedor['dimensiones'])
            faces_cont = caras_caja(vertices_cont)
            cont_poly = Poly3DCollection(faces_cont, alpha=0.1, facecolor='gray')
            ax.add_collection3d(cont_poly)

            # Dibujar cada paquete
            for paquete in contenedor['paquetes']:
                vertices_paq = vertices_caja(paquete['posicion'], paquete['dimensiones'])
                faces_paq = caras_caja(vertices_paq)
                tipo_base = paquete['tipo'].split('_')[0]
                color = color_map[tipo_base]
                paq_poly = Poly3DCollection(faces_paq, alpha=0.6, facecolor=color)
                ax.add_collection3d(paq_poly)

            # Configurar los límites y etiquetas
            ax.set_xlim([0, contenedor['dimensiones'][0]])
            ax.set_ylim([0, contenedor['dimensiones'][1]])
            ax.set_zlim([0, contenedor['dimensiones'][2]])
            ax.set_xlabel('Largo (x)')
            ax.set_ylabel('Ancho (y)')
            ax.set_zlabel('Alto (z)')
            ax.set_title(f'Contenedor {contenedor["id"]}')

        # Agregar leyenda
        legend_elements = [plt.Rectangle((0, 0), 1, 1, facecolor=color_map[tipo])
                           for tipo in tipos_unicos]
        fig.legend(legend_elements, list(tipos_unicos),
                   loc='center left', bbox_to_anchor=(1, 0.5))

        plt.tight_layout()
        plt.show()