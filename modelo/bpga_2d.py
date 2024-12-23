from modelo.datos import RequisitosContenedor, Paquete
import numpy as np
from modelo.bpga_core import OptimizadorEmpaquetadoMultiContenedor
import matplotlib.pyplot as plt
import matplotlib.patches as patches


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

    def _generar_rotaciones_paquete(self, paquete: Paquete, indice : int) -> list[tuple]:
        """Genera todas las rotaciones únicas permitidas para un paquete"""
        nombre = paquete.nombre
        x, y = paquete.dimensiones
        rotaciones_tipo = [(nombre, x, y),]

        permiso = self.rotaciones_permitidas[indice][0]
        if permiso and x != y:
            rotaciones_tipo.append((f"{nombre}_rxy", y, x))

        return rotaciones_tipo

    def _first_fit(self, colocado, dimensiones_contenedor, paquetes_colocados, paso_rejilla, rotaciones):
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
            if colocado:
                break
        return colocado

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

    def _conteo_paquetes(self, cantidad_total, dimensiones_contenedor, paquetes_colocados):
        for paq in paquetes_colocados:
            # Extraer el nombre original del paquete sin la rotación
            nombre_original = paq[4].split('_')[0]
            cantidad_total[nombre_original] += 1
        # Calcular volúmenes
        volumen_contenedor = np.prod(dimensiones_contenedor)
        volumen_utilizado = sum(paq[2] * paq[3] for paq in paquetes_colocados)
        return volumen_contenedor, volumen_utilizado

    def _contenedor_info(self, contenedor_info, paquetes_colocados):
        contenedor_info['paquetes'] = [
            {
                'tipo': paq[4],
                'posicion': (paq[0], paq[1]),
                'dimensiones': (paq[2], paq[3])
            } for paq in paquetes_colocados
        ]


    def graficar_resultados(self, resultado: dict) -> None:
        """
        Grafica la disposición de los paquetes en cada contenedor usando matplotlib con navegación.
        Crea una figura única con capacidad de navegar entre contenedores.

        Args:
            resultado (dict): Diccionario con los resultados de la optimización
        """
        # Filtrar contenedores en uso
        contenedores_activos = [c for c in resultado['posiciones']['contenedores'] if c['en_uso'] and c['paquetes']]
        num_contenedores = len(contenedores_activos)

        if num_contenedores == 0:
            print("No hay contenedores activos para graficar.")
            return

        # Crear un mapa de colores para cada tipo de paquete
        tipos_unicos = {paquete.nombre for paquete in self.tipos_paquetes}
        colores = plt.cm.get_cmap('tab20')(np.linspace(0, 1, len(tipos_unicos)))
        mapa_colores = dict(zip(tipos_unicos, colores))

        # Crear figura única para navegación
        fig, ax = plt.subplots(figsize=(15, 8))
        plt.subplots_adjust(bottom=0.2)  # Espacio para instrucciones

        # Estado para seguimiento
        estado_actual = {'indice_contenedor': 0}

        def dibujar_contenedor(indice):
            # Limpiar el eje anterior
            ax.clear()

            contenedor = contenedores_activos[indice]
            ancho_contenedor, alto_contenedor = contenedor['dimensiones']

            # Configurar los límites del gráfico
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

            # Actualizar la figura
            fig.canvas.draw_idle()

        def on_key(event):
            if event.key == 'left':
                # Ir al contenedor anterior
                estado_actual['indice_contenedor'] = (estado_actual['indice_contenedor'] - 1) % num_contenedores
                dibujar_contenedor(estado_actual['indice_contenedor'])
            elif event.key == 'right':
                # Ir al contenedor siguiente
                estado_actual['indice_contenedor'] = (estado_actual['indice_contenedor'] + 1) % num_contenedores
                dibujar_contenedor(estado_actual['indice_contenedor'])

        # Conectar el evento de teclas
        fig.canvas.mpl_connect('key_press_event', on_key)

        # Dibujar el primer contenedor
        dibujar_contenedor(0)

        # Mostrar instrucciones
        plt.figtext(0.5, 0.02,
                    'Usa ← y → para navegar entre contenedores',
                    ha='center', fontsize=10,
                    bbox=dict(facecolor='white', alpha=0.5))

        plt.tight_layout()
        plt.show()