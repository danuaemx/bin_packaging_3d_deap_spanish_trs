from datos import *
import numpy as np
from modelo.bpga_core import OptimizadorEmpaquetadoMultiContenedor
import matplotlib.pyplot as plt
import matplotlib.patches as patches
plt.switch_backend('Qt5Agg')

class OptimizadorEmpaquetadoMultiContenedor2D(OptimizadorEmpaquetadoMultiContenedor):
    def __init__(self,
                 requisitos_contenedores: list[RequisitosContenedor],
                 tipos_paquetes: list[Paquete],
                 rotaciones_permitidas: list[tuple[bool,]],
                 tamano_poblacion: int = 1000,
                 generaciones: int = 55,
                 prob_cruce: float = 0.618,
                 prob_mutacion: float = 0.021) -> None:

        super().__init__(requisitos_contenedores, tipos_paquetes, rotaciones_permitidas, tamano_poblacion, generaciones,
                         prob_cruce, prob_mutacion)

    def _generar_rotaciones_paquete(self, paquete: Paquete) -> list[tuple]:
        """Genera todas las rotaciones únicas permitidas para un paquete"""
        nombre = paquete.nombre
        x, y = paquete.dimensiones
        rotaciones_tipo = set()

        for permisos in self.rotaciones_permitidas:

            current_rotations = []


            if permisos[0] and x != y:
                current_rotations.append((f"{nombre}_rxy", y, x))


            current_rotations.append((nombre, x, y))


            rotaciones_tipo.update(current_rotations)

        return list(rotaciones_tipo)

    def _puede_colocar_paquete(self, paquetes_existentes, nuevo_paquete, posicion, dimensiones_contenedor) -> bool:
        """Verifica si un paquete puede ser colocado en la posición dada"""
        x, y = posicion
        l, a = nuevo_paquete

        if (x + l > dimensiones_contenedor[0] or
                y + a > dimensiones_contenedor[1]):
            return False

        for paq in paquetes_existentes:
            px, py, pl, pa, _ = paq
            if not (x + l <= px or px + pl <= x or
                    y + a <= py or py + pa <= y):
                return False
        return True

    def _colocar_paquetes_en_contenedor(self, genes_contenedor, indice_contenedor) -> tuple[list, tuple]:
        """Colocar paquetes en el contenedor usando heurística first-fit"""
        paquetes_colocados = []
        dimensiones_contenedor = self.requisitos_contenedores[indice_contenedor].dimensiones
        paso_rejilla = 1

        for i in range(1, len(genes_contenedor)):
            tipo_paquete_idx = i - 1
            cantidad = genes_contenedor[i]

            if cantidad == 0:
                continue

            tipo_paquete = self.tipos_paquetes[tipo_paquete_idx]
            rotaciones = self.rotaciones_precalculadas[tipo_paquete.nombre]
            for _ in range(cantidad):
                colocado = False
                for rotacion in rotaciones:
                    nombre_rot, l_rot, a_rot = rotacion
                    for x in range(0, dimensiones_contenedor[0] - l_rot + 1, paso_rejilla):
                        for y in range(0, dimensiones_contenedor[1] - a_rot + 1, paso_rejilla):
                            if self._puede_colocar_paquete(paquetes_colocados, (l_rot, a_rot), (x, y),
                                                           dimensiones_contenedor):
                                paquetes_colocados.append(
                                    (x, y, l_rot, a_rot, nombre_rot)
                                )
                                colocado = True
                                break
                        if colocado:
                            break

        return paquetes_colocados, dimensiones_contenedor

    def _evaluar_aptitud(self, individuo) -> tuple[float]:
        """Evaluar la aptitud de un individuo"""
        genes_por_contenedor = 1 + self.num_tipos_paquetes
        cantidad_total = {tipo.nombre: 0 for tipo in self.tipos_paquetes}
        volumen_total_utilizado = 0
        volumen_total_contenedores = 0
        contenedores_usados = 0

        for i in range(self.num_contenedores):
            inicio = i * genes_por_contenedor
            usar_contenedor = individuo[inicio]

            if usar_contenedor == 1:
                # Sumar las cantidades de cada tipo de paquete en este contenedor
                for j, tipo_paquete in enumerate(self.tipos_paquetes):
                    idx_cantidad = inicio + 1 + j
                    cantidad = individuo[idx_cantidad]
                    cantidad_total[tipo_paquete.nombre] += cantidad

        # Penalizaciones
        # Maximo y minimo global
        for tipo_paquete in self.tipos_paquetes:
            if cantidad_total[tipo_paquete.nombre] > tipo_paquete.cantidad_maxima:
                return (0.0,)  # Penalización máxima si se excede el límite global

        cantidad_total = {tipo.nombre: 0 for tipo in self.tipos_paquetes}

        for i in range(self.num_contenedores):
            inicio = i * genes_por_contenedor
            usar_contenedor = individuo[inicio]

            if usar_contenedor == 1:
                contenedores_usados += 1
                genes_contenedor = individuo[inicio:inicio + genes_por_contenedor]
                paquetes_colocados, dimensiones_contenedor = self._colocar_paquetes_en_contenedor(genes_contenedor, i)

                # Actualizar conteo total de paquetes realmente colocados
                for paq in paquetes_colocados:
                    # Extraer el nombre original del paquete sin la rotación
                    nombre_original = paq[4].split('_')[0]
                    cantidad_total[nombre_original] += 1

                # Calcular volúmenes
                volumen_contenedor = np.prod(dimensiones_contenedor)
                volumen_utilizado = sum(paq[2]*paq[3] for paq in paquetes_colocados)

                volumen_total_contenedores += volumen_contenedor
                volumen_total_utilizado += volumen_utilizado

        # Si no hay contenedores usados, retornar aptitud mínima
        if contenedores_usados == 0:
            return (0.0,)

        # Verificar restricciones de cantidad mínima
        penalizacion = 1.0
        for tipo_paquete in self.tipos_paquetes:
            if cantidad_total[tipo_paquete.nombre] < tipo_paquete.cantidad_minima:
                penalizacion *= 0.4

        aptitud = volumen_total_utilizado / volumen_total_contenedores * penalizacion
        return (aptitud,)

    def obtener_posiciones_paquetes(self, individuo) -> dict:
        """Obtener las posiciones de los paquetes en un individuo"""
        genes_por_contenedor = 1 + self.num_tipos_paquetes
        resultados = {
            'contenedores': []
        }
        for i in range(self.num_contenedores):
            inicio = i * genes_por_contenedor
            usar_contenedor = individuo[inicio]

            dimensiones = self.requisitos_contenedores[i].dimensiones

            contenedor_info = {
                'id': i + 1,
                'en_uso': bool(usar_contenedor),
                'dimensiones': dimensiones,
                'paquetes': []
            }
            if usar_contenedor:
                genes_contenedor = individuo[inicio:inicio + genes_por_contenedor]
                paquetes_colocados, _ = self._colocar_paquetes_en_contenedor(genes_contenedor, i)

                contenedor_info['paquetes'] = [
                    {
                        'tipo': paq[4],
                        'posicion': (paq[0],paq[1]),
                        'dimensiones': (paq[2],paq[3])
                    } for paq in paquetes_colocados
                ]

            resultados['contenedores'].append(contenedor_info)

        return resultados

    def graficar_resultados(self, resultado: dict) -> None:
        """
        Grafica la disposición de los paquetes en cada contenedor usando matplotlib.
        Crea una figura separada para cada contenedor en uso.

        Args:
            resultado (dict): Diccionario con los resultados de la optimización
        """
        # Crear un mapa de colores para cada tipo de paquete
        tipos_unicos = {paquete.nombre for paquete in self.tipos_paquetes}
        colores = plt.cm.get_cmap('tab20')(np.linspace(0, 1, len(tipos_unicos)))
        mapa_colores = dict(zip(tipos_unicos, colores))

        for contenedor in resultado['posiciones']['contenedores']:
            if not contenedor['en_uso'] or not contenedor['paquetes']:
                continue

            # Crear una nueva figura para cada contenedor
            fig, ax = plt.subplots(figsize=(12, 8))

            # Configurar los límites del gráfico según las dimensiones del contenedor
            ancho_contenedor, alto_contenedor = contenedor['dimensiones']
            ax.set_xlim(-1, ancho_contenedor + 1)
            ax.set_ylim(-1, alto_contenedor + 1)

            # Dibujar el contenedor
            rect_contenedor = patches.Rectangle((0, 0), ancho_contenedor, alto_contenedor,
                                                fill=False, color='black', linewidth=2)
            ax.add_patch(rect_contenedor)

            # Dibujar cada paquete
            for paquete in contenedor['paquetes']:
                # Obtener el tipo base del paquete (sin la rotación)
                tipo_base = paquete['tipo'].split('_')[0]
                color = mapa_colores[tipo_base]

                x, y = paquete['posicion']
                ancho, alto = paquete['dimensiones']

                # Crear y añadir el rectángulo del paquete
                rect = patches.Rectangle((x, y), ancho, alto,
                                         fill=True, facecolor=color, alpha=0.5,
                                         edgecolor='black', linewidth=1)
                ax.add_patch(rect)

                # Añadir texto con el tipo de paquete
                ax.text(x + ancho / 2, y + alto / 2, tipo_base,
                        horizontalalignment='center',
                        verticalalignment='center')

            # Configurar el título y etiquetas
            ax.set_title(f'Contenedor {contenedor["id"]} - {ancho_contenedor}x{alto_contenedor}')
            ax.set_xlabel('Ancho')
            ax.set_ylabel('Alto')

            # Ajustar la escala para que sea igual en ambos ejes
            ax.set_aspect('equal')

            # Añadir una cuadrícula
            ax.grid(True, linestyle='--', alpha=0.7)

            # Crear leyenda
            legend_elements = [patches.Patch(facecolor=mapa_colores[tipo],
                                             alpha=0.5,
                                             edgecolor='black',
                                             label=tipo)
                               for tipo in tipos_unicos]
            ax.legend(handles=legend_elements, title="Tipos de Paquetes",
                      loc='center left', bbox_to_anchor=(1, 0.5))

            # Ajustar el layout para que no se solapen los elementos
            plt.tight_layout()

        # Mostrar todas las figuras
        plt.show()