from modelo.bpga_core import OptimizadorEmpaquetadoMultiContenedor
from modelo.datos import Paquete, RequisitosContenedor
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
plt.switch_backend('Qt5Agg')

class OptimizadorEmpaquetadoMultiContenedor1D(OptimizadorEmpaquetadoMultiContenedor):

    def __init__(self, requisitos_contenedores: list[RequisitosContenedor],
                 tipos_paquetes: list[Paquete],
                 rotaciones_permitidas: list[tuple] = [],
                 tamano_poblacion: int = 1000,
                 generaciones: int = 55,
                 prob_cruce: float = 0.618,
                 prob_mutacion: float = 0.021) -> None:

        super().__init__(requisitos_contenedores, tipos_paquetes, rotaciones_permitidas, tamano_poblacion, generaciones,
                         prob_cruce, prob_mutacion)

    def _generar_rotaciones_paquete(self, paquete: Paquete, indice: int) -> list[tuple]:
        """Generar todas las posibles rotaciones de un paquete"""
        nombre = paquete.nombre
        x = paquete.dimensiones[0]
        rotaciones_tipo = [(x, nombre), ]
        return rotaciones_tipo

    def _puede_colocar_paquete(self, paquetes_existentes, nuevo_paquete, posicion, dimensiones_contenedor) -> bool:
        """Determinar si un nuevo paquete puede ser colocado en una posición dada"""
        x = posicion[0]
        l = nuevo_paquete[0]

        if x + l > dimensiones_contenedor[0]:
            return False

        for pkg in paquetes_existentes:
            px, pl, _ = pkg
            if not (x + l <= px or px + pl <= x):
                return False

        return True

    def _first_fit(self, colocado, dimensiones_contenedor, paquetes_colocados, paso_rejilla, rotaciones):
        for rotacion in rotaciones:
            l_rot, nombre_rot = rotacion
            for x in range(0, dimensiones_contenedor[0] - l_rot + 1, paso_rejilla):
                if self._puede_colocar_paquete(paquetes_colocados, (l_rot,), (x,), dimensiones_contenedor):
                    paquetes_colocados.append((x, l_rot, nombre_rot))
                    colocado = True
                    break
            if colocado:
                break
        return colocado

    def _conteo_paquetes(self, cantidad_total, dimensiones_contenedor, paquetes_colocados):
        for paq in paquetes_colocados:
            # Extraer el nombre original del paquete sin la rotación
            nombre_original = paq[2].split('_')[0]
            cantidad_total[nombre_original] += 1
        # Calcular volúmenes
        volumen_contenedor = np.prod(dimensiones_contenedor)
        volumen_utilizado = sum(paq[1] for paq in paquetes_colocados)
        return volumen_contenedor, volumen_utilizado

    def _contenedor_info(self, contenedor_info, paquetes_colocados):
        contenedor_info['paquetes'] = [
            {
                'tipo': paq[2],
                'posicion': (paq[0],),
                'dimensiones': (paq[1],)
            } for paq in paquetes_colocados
        ]

    def graficar_resultados(self, resultado: dict) -> None:
        """
        Grafica los resultados del empaquetado usando matplotlib con navegación entre contenedores.
        Muestra una visualización de cómo están distribuidos los paquetes en cada contenedor.
        """
        # Obtener contenedores en uso
        contenedores_activos = [c for c in resultado['posiciones']['contenedores'] if c['en_uso']]
        num_contenedores = len(contenedores_activos)

        if num_contenedores == 0:
            print("No hay contenedores activos para graficar.")
            return

        colores = plt.cm.Set3(np.linspace(0, 1, len(self.tipos_paquetes)))
        color_map = {tipo.nombre: color for tipo, color in zip(self.tipos_paquetes, colores)}

        # Crear figura
        fig, ax = plt.subplots(figsize=(15, 6))
        plt.subplots_adjust(bottom=0.2)  # Espacio para botones de navegación

        # Estado para seguimiento
        estado_actual = {'indice_contenedor': 0}

        def dibujar_contenedor(indice):
            # Limpiar el eje anterior
            ax.clear()
            contenedor = contenedores_activos[indice]
            longitud_contenedor = contenedor['dimensiones'][0]

            # Configurar el área de visualización
            ax.set_xlim(-longitud_contenedor * 0.05, longitud_contenedor * 1.05)
            ax.set_ylim(-0.5, 1.5)

            # Dibujar el contenedor
            contenedor_rect = patches.Rectangle(
                (0, 0), longitud_contenedor, 1,
                linewidth=2, edgecolor='black', facecolor='none'
            )
            ax.add_patch(contenedor_rect)

            # Dibujar cada paquete
            for paquete in contenedor['paquetes']:
                x = paquete['posicion'][0]
                longitud = paquete['dimensiones'][0]
                tipo_base = paquete['tipo'].split('_')[0]  # Obtener tipo base sin rotación

                # Crear y añadir el rectángulo del paquete
                paquete_rect = patches.Rectangle(
                    (x, 0), longitud, 1,
                    facecolor=color_map[tipo_base],
                    edgecolor='black',
                    alpha=0.7,
                    linewidth=1
                )
                ax.add_patch(paquete_rect)

                # Añadir texto con el tipo de paquete si hay espacio suficiente
                if longitud > longitud_contenedor * 0.05:
                    ax.text(x + longitud / 2, 0.5, tipo_base,
                            ha='center', va='center')

            # Configurar título y etiquetas
            ax.set_title(
                f'Contenedor {contenedor["id"]} - Utilización: {self.analizar_resultados(resultado)["metricas_por_contenedor"][indice]["porcentaje_utilizacion"]:.1f}%')
            ax.set_xlabel('Longitud')
            ax.set_yticks([])

            # Añadir leyenda
            legend_elements = [patches.Patch(facecolor=color_map[tipo.nombre],
                                             edgecolor='black',
                                             alpha=0.7,
                                             label=f'{tipo.nombre}')
                               for tipo in self.tipos_paquetes]
            ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.15),
                      ncol=len(self.tipos_paquetes))

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

        plt.show()