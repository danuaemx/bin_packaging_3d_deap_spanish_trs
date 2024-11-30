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

    def obtener_posiciones_paquetes(self, individuo) -> dict:
        """Obtener las posiciones de los paquetes en un individuo"""
        genes_por_contenedor = 1 + self.num_tipos_paquetes
        resultados = {
            'contenedores': []
        }
        for i in range(self.num_contenedores):
            inicio = i * genes_por_contenedor
            usar_contenedor = individuo[inicio]

            # Usar las dimensiones fijas del contenedor
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
                        'tipo': paq[2],
                        'posicion': (paq[0],),
                        'dimensiones': (paq[1],)
                    } for paq in paquetes_colocados
                ]

            resultados['contenedores'].append(contenedor_info)

        return resultados

    def _generar_rotaciones_paquete(self, paquete: Paquete) -> list[tuple]:
        """Generar todas las posibles rotaciones de un paquete"""
        nombre = paquete.nombre
        x= paquete.dimensiones[0]
        rotaciones_tipo = set()
        rotaciones_tipo.update((nombre, x))
        return list(rotaciones_tipo)

    def _colocar_paquetes_en_contenedor(self, genes_contenedor, indice_contenedor) -> tuple[list, tuple]:
        """Colocar paquetes en un contenedor usando heurística first-fit"""
        paquetes_colocados = []
        dimensiones_contenedor = self.requisitos_contenedores[indice_contenedor].dimensiones
        paso_rejilla = 1

        for i in range(1, len(genes_contenedor)):
            tipo_paquete_idx = i - 1
            cantidad = genes_contenedor[i]

            if cantidad == 0:
                continue

            tipo_paquete = self.tipos_paquetes[tipo_paquete_idx]
            for _ in range(cantidad):
                colocado = False
                for x in range(0, dimensiones_contenedor[0] - tipo_paquete.dimensiones[0] + 1, paso_rejilla):
                    if self._puede_colocar_paquete(paquetes_colocados, tipo_paquete.dimensiones, (x,), dimensiones_contenedor):
                        paquetes_colocados.append((x, tipo_paquete.dimensiones[0], tipo_paquete.nombre))
                        colocado = True
                        break
                if not colocado:
                    return paquetes_colocados, dimensiones_contenedor


        return paquetes_colocados, dimensiones_contenedor

    def _evaluar_aptitud(self, individuo) -> tuple[float]:
        """Evaluar la aptitud de un individuo"""
        aptitud = 0
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

        #Penalizaciones
        #Maximo y minimo global
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
                    nombre_original = paq[2].split('_')[0]
                    cantidad_total[nombre_original] += 1

                # Calcular volúmenes
                volumen_contenedor = np.prod(dimensiones_contenedor)
                volumen_utilizado = sum(paq[1] for paq in paquetes_colocados)

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

    def graficar_resultados(self, resultado: dict) -> None:
        """
        Grafica los resultados del empaquetado usando matplotlib.
        Muestra una visualización de cómo están distribuidos los paquetes en cada contenedor.
        """


        # Configurar el estilo de la gráfica


        # Obtener contenedores en uso
        contenedores_activos = [c for c in resultado['posiciones']['contenedores'] if c['en_uso']]
        num_contenedores = len(contenedores_activos)

        if num_contenedores == 0:
            print("No hay contenedores activos para graficar.")
            return

        # Crear una figura con subplots para cada contenedor
        fig, axs = plt.subplots(num_contenedores, 1, figsize=(15, 4 * num_contenedores))
        # Convertir axs a array si solo hay un contenedor
        if num_contenedores == 1:
            axs = [axs]

        # Colores para diferentes tipos de paquetes
        colores = plt.cm.Set3(np.linspace(0, 1, len(self.tipos_paquetes)))
        color_map = {tipo.nombre: color for tipo, color in zip(self.tipos_paquetes, colores)}

        # Graficar cada contenedor
        for idx, contenedor in enumerate(contenedores_activos):
            ax = axs[idx]
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
                f'Contenedor {contenedor["id"]} - Utilización: {self.analizar_resultados(resultado)["metricas_por_contenedor"][idx]["porcentaje_utilizacion"]:.1f}%')
            ax.set_xlabel('Longitud')
            ax.set_yticks([])

        # Añadir leyenda global
        legend_elements = [patches.Patch(facecolor=color_map[tipo.nombre],
                                         edgecolor='black',
                                         alpha=0.7,
                                         label=f'{tipo.nombre}')
                           for tipo in self.tipos_paquetes]
        fig.legend(handles=legend_elements,
                   loc='center right',
                   bbox_to_anchor=(0.98, 0.5))

        # Ajustar espaciado
        plt.tight_layout(rect=[0, 0, 0.9, 1])

        # Mostrar la gráfica
        plt.show()