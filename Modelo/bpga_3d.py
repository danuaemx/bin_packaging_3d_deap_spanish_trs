import random
from datos import *
from deap import base, creator, tools, algorithms
import numpy as np

"""
    Implementación de GA con DEAP para resolver:
    -Maximizar volumen ocupado de Empaquetado multi contenedor
    
"""

class OptimizadorEmpaquetadoMultiContenedor:
    def __init__(self,
                 datos_empaquetado : DatosEmpaquetado,
                 tamano_poblacion: int = 1000,
                 generaciones: int = 55,
                 prob_cruce: float = 0.618,
                 prob_mutacion: float = 0.021) -> None:

        self.num_contenedores = len(datos_empaquetado.contenedores)
        self.num_tipos_paquetes = len(datos_empaquetado.requisitos_paquetes)
        self.requisitos_contenedores = datos_empaquetado.contenedores
        self.tipos_paquetes = [req_paquetes.paquete for req_paquetes in datos_empaquetado.requisitos_paquetes]
        self.rotaciones_permitidas = [req_paquetes.rotaciones_permitidas for req_paquetes in datos_empaquetado.requisitos_paquetes]


        self.tipos_paquetes_rotados = self._generar_rotaciones()
        self.tamano_poblacion = tamano_poblacion
        self.generaciones = generaciones
        self.prob_cruce = prob_cruce
        self.prob_mutacion = prob_mutacion

        # Inicializar componentes DEAP
        self._configurar_deap()

    def _generar_rotaciones(self) -> dict[int, list[tuple[str, int, int, int]]]:
        """Genera un diccionario con todas las rotaciones posibles para cada tipo de paquete"""
        rotaciones = {}
        for idx, tipo_paquete in enumerate(self.tipos_paquetes):
            nombre, (x, y, z) = tipo_paquete.nombre, tipo_paquete.dimensiones
            rotaciones_tipo = [(nombre, x, y, z)]
            if idx < len(self.rotaciones_permitidas):
                permisos = self.rotaciones_permitidas[idx]
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
            rotaciones[idx] = rotaciones_tipo
        return rotaciones

    def _configurar_deap(self) -> None:
        """Inicializa el creador y toolbox de DEAP para múltiples contenedores"""
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()

        # Registrar generadores para cada contenedor
        atributos = []
        for i, requisitos in enumerate(self.requisitos_contenedores):
            # Indicador binario de uso del contenedor
            self.toolbox.register(
                f"attr_usar_contenedor_{i}",
                #Inicia con todos en uso
                lambda: 1
            )
            atributos.append(getattr(self.toolbox, f"attr_usar_contenedor_{i}"))

            # Dimensiones del contenedor (siempre presentes)
            for dim in range(3):
                self.toolbox.register(
                    f"attr_contenedor_{i}_{dim}",
                    random.randint,
                    requisitos.dimensiones_minimas[dim],
                    requisitos.dimensiones_maximas[dim]
                )
                atributos.append(getattr(self.toolbox, f"attr_contenedor_{i}_{dim}"))

            # Cantidad y rotación de paquetes para este contenedor
            for j, tipo_paquete in enumerate(self.tipos_paquetes):
                self.toolbox.register(
                    f"attr_cantidad_{i}_{j}",
                    random.randint,
                    0,  # Mínimo 0 por contenedor
                    tipo_paquete.cantidad_maxima  # Máximo por contenedor
                )
                self.toolbox.register(
                    f"attr_rotacion_{i}_{j}",
                    random.randint,
                    0,
                    len(self.tipos_paquetes_rotados[j]) - 1
                )
                atributos.extend([
                    getattr(self.toolbox, f"attr_cantidad_{i}_{j}"),
                    getattr(self.toolbox, f"attr_rotacion_{i}_{j}")
                ])

        self.toolbox.register("individual", tools.initCycle, creator.Individual, atributos, n=1)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("evaluate", self._evaluar_aptitud)
        self.toolbox.register("mate", tools.cxUniform, indpb=0.5)
        self.toolbox.register("mutate", self._mutar)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def _mutar(self, individuo):
        """Operador de mutación para múltiples contenedores"""
        genes_por_contenedor = 1 + 3 + (
                    self.num_tipos_paquetes * 2)  # indicador + dimensiones + (cantidad + rotación) por tipo

        for i, requisitos in enumerate(self.requisitos_contenedores):
            inicio = i * genes_por_contenedor

            # Mutar indicador de uso del contenedor
            if random.random() < self.prob_mutacion:
                individuo[inicio] = random.randint(0, 1)

            # Mutar dimensiones del contenedor (siempre, para mantenerlas válidas)
            for j in range(3):
                if random.random() < self.prob_mutacion:
                    individuo[inicio + 1 + j] = random.randint(
                        requisitos.dimensiones_minimas[j],
                        requisitos.dimensiones_maximas[j]
                    )

            # Solo mutar cantidades y incluyendo rotaciones si el contenedor está en uso
            if individuo[inicio] == 1:
                for j in range(self.num_tipos_paquetes):
                    idx_cantidad = inicio + 4 + (j * 2)
                    idx_rotacion = idx_cantidad + 1

                    if random.random() < self.prob_mutacion:
                        individuo[idx_cantidad] = random.randint(
                            0,
                            self.tipos_paquetes[j].cantidad_maxima
                        )

                    if random.random() < self.prob_mutacion:
                        individuo[idx_rotacion] = random.randint(
                            0,
                            len(self.tipos_paquetes_rotados[j]) - 1
                        )
            else:
                # Si el contenedor no está en uso, establecer cantidades en 0
                for j in range(self.num_tipos_paquetes):
                    idx_cantidad = inicio + 4 + (j * 2)
                    individuo[idx_cantidad] = 0

        return (individuo,)

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

    def _colocar_paquetes_en_contenedor(self, genes_contenedor, indice_contenedor) -> tuple[list, tuple]:
        """Coloca paquetes en un contenedor específico usando sus restricciones individuales"""
        dimensiones_contenedor = tuple(genes_contenedor[:3])
        requisitos = self.requisitos_contenedores[indice_contenedor]

        # Verificar que las dimensiones estén dentro de los límites del contenedor específico
        for i in range(3):
            if (dimensiones_contenedor[i] < requisitos.dimensiones_minimas[i] or
                    dimensiones_contenedor[i] > requisitos.dimensiones_maximas[i]):
                return [], dimensiones_contenedor

        paquetes_colocados = []
        paso_rejilla = 1

        for i in range(3, len(genes_contenedor), 2):
            tipo_paquete_idx = (i - 3) // 2
            cantidad = genes_contenedor[i]
            # Si la cantidad es 0, continuar con el siguiente tipo
            if cantidad == 0:
                continue

            rotacion_idx = genes_contenedor[i + 1]
            tipo_paquete = self.tipos_paquetes_rotados[tipo_paquete_idx][rotacion_idx]

            for _ in range(cantidad):
                colocado = False
                for x in range(0, dimensiones_contenedor[0] - tipo_paquete[1] + 1, paso_rejilla):
                    for y in range(0, dimensiones_contenedor[1] - tipo_paquete[2] + 1, paso_rejilla):
                        for z in range(0, dimensiones_contenedor[2] - tipo_paquete[3] + 1, paso_rejilla):
                            if self._puede_colocar_paquete(paquetes_colocados, tipo_paquete, (x, y, z),
                                                           dimensiones_contenedor):
                                paquetes_colocados.append(
                                    (x, y, z, tipo_paquete[1], tipo_paquete[2], tipo_paquete[3], tipo_paquete[0])
                                )
                                colocado = True
                                break
                        if colocado:
                            break
                    if colocado:
                        break
                if not colocado:
                    break

        return paquetes_colocados, dimensiones_contenedor

    def _evaluar_aptitud(self, individuo) -> tuple[float]:
        """Evalúa la aptitud de un individuo con múltiples contenedores"""
        genes_por_contenedor = 1 + 3 + (self.num_tipos_paquetes * 2)
        cantidad_total = {tipo.nombre: 0 for tipo in self.tipos_paquetes}
        volumen_total_utilizado = 0
        volumen_total_contenedores = 0
        contenedores_usados = 0

        # Verificar restricciones globales de cantidad máxima
        for i in range(self.num_contenedores):
            inicio = i * genes_por_contenedor
            usar_contenedor = individuo[inicio]

            if usar_contenedor == 1:
                # Sumar las cantidades de cada tipo de paquete en este contenedor
                for j, tipo_paquete in enumerate(self.tipos_paquetes):
                    idx_cantidad = inicio + 4 + (j * 2)
                    cantidad = individuo[idx_cantidad]
                    cantidad_total[tipo_paquete.nombre] += cantidad

        # Verificar si se exceden los máximos globales
        for tipo_paquete in self.tipos_paquetes:
            if cantidad_total[tipo_paquete.nombre] > tipo_paquete.cantidad_maxima:
                return (0.0,)  # Penalización máxima si se excede el límite global

        # Reiniciar contadores para el cálculo normal de aptitud
        cantidad_total = {tipo.nombre: 0 for tipo in self.tipos_paquetes}

        # Procesar cada contenedor
        for i in range(self.num_contenedores):
            inicio = i * genes_por_contenedor
            usar_contenedor = individuo[inicio]

            if usar_contenedor == 1:
                contenedores_usados += 1
                genes_contenedor = individuo[inicio + 1:inicio + genes_por_contenedor]
                paquetes_colocados, dimensiones_contenedor = self._colocar_paquetes_en_contenedor(genes_contenedor, i)

                # Actualizar conteo total de paquetes realmente colocados
                for paq in paquetes_colocados:
                    nombre_base = paq[6].split('_')[0]
                    cantidad_total[nombre_base] += 1

                # Calcular volúmenes
                volumen_contenedor = np.prod(dimensiones_contenedor)
                volumen_utilizado = sum(paq[3] * paq[4] * paq[5] for paq in paquetes_colocados)

                volumen_total_contenedores += volumen_contenedor
                volumen_total_utilizado += volumen_utilizado

        # Si no hay contenedores usados, retornar aptitud mínima
        if contenedores_usados == 0:
            return (0.0,)

        # Verificar restricciones de cantidad mínima
        penalizacion = 1.0
        for tipo_paquete in self.tipos_paquetes:
            if cantidad_total[tipo_paquete.nombre] < tipo_paquete.cantidad_minima:
                penalizacion *= 0.5

        # La aptitud es el porcentaje de volumen utilizado multiplicado por la penalización
        aptitud = (volumen_total_utilizado / volumen_total_contenedores) * penalizacion
        return (aptitud,)

    def obtener_posiciones_paquetes(self, individuo) -> dict:
        """Obtiene las posiciones de los paquetes y dimensiones de todos los contenedores"""
        genes_por_contenedor = 1 + 3 + (self.num_tipos_paquetes * 2)
        resultados = {
            'contenedores': []
        }

        for i in range(self.num_contenedores):
            inicio = i * genes_por_contenedor
            usar_contenedor = individuo[inicio]

            # Siempre incluir las dimensiones del contenedor
            dimensiones = tuple(individuo[inicio + 1:inicio + 4])

            contenedor_info = {
                'id': i + 1,
                'en_uso': bool(usar_contenedor),
                'dimensiones': dimensiones,
                'paquetes': []
            }

            # Solo procesar paquetes si el contenedor está en uso
            if usar_contenedor:
                genes_contenedor = individuo[inicio + 1:inicio + genes_por_contenedor]
                paquetes_colocados, _ = self._colocar_paquetes_en_contenedor(genes_contenedor, i)

                contenedor_info['paquetes'] = [
                    {
                        'tipo': paq[6],
                        'posicion': (paq[0], paq[1], paq[2]),
                        'dimensiones': (paq[3], paq[4], paq[5])
                    } for paq in paquetes_colocados
                ]

            resultados['contenedores'].append(contenedor_info)

        return resultados

    def optimizar(self, semilla=None) -> dict:
        """Ejecuta la optimización del algoritmo genético para múltiples contenedores"""
        if semilla is not None:
            random.seed(semilla)

        poblacion = self.toolbox.population(n=self.tamano_poblacion)
        mejor_individuo = None
        mejor_aptitud = 0.0
        mejor_resultado = None

        for gen in range(self.generaciones):
            descendencia = algorithms.varAnd(poblacion, self.toolbox, self.prob_cruce, self.prob_mutacion)

            aptitudes = map(self.toolbox.evaluate, descendencia)
            for aptitud, ind in zip(aptitudes, descendencia):
                ind.fitness.values = aptitud
                if aptitud[0] > mejor_aptitud:
                    mejor_aptitud = aptitud[0]
                    mejor_individuo = ind.copy()
                    mejor_resultado = self.obtener_posiciones_paquetes(ind)

            poblacion = self.toolbox.select(descendencia, k=len(poblacion))
            print(f"Generación {gen + 1}: Mejor Aptitud = {mejor_aptitud:.4f}")


        return {
            'individuo': mejor_individuo,
            'aptitud': mejor_aptitud,
            'resultados': mejor_resultado
        }

    def analizar_resultados(self, resultado: dict) -> dict:
        """Analiza los resultados de la optimización proporcionando métricas detalladas"""
        analisis = {
            'aptitud_global': resultado['aptitud'],
            'metricas_por_contenedor': [],
            'metricas_globales': {
                'total_paquetes': 0,
                'volumen_total_contenedores': 0,
                'volumen_total_utilizado': 0,
                'paquetes_por_tipo': {}
            }
        }

        # Inicializar conteo de paquetes por tipo
        for tipo in self.tipos_paquetes:
            analisis['metricas_globales']['paquetes_por_tipo'][tipo.nombre] = 0

        # Analizar cada contenedor
        for contenedor in resultado['resultados']['contenedores']:
            volumen_contenedor = np.prod(contenedor['dimensiones'])
            volumen_utilizado = sum(np.prod(paq['dimensiones']) for paq in contenedor['paquetes'])

            # Contar paquetes por tipo en este contenedor
            paquetes_por_tipo = {}
            for tipo in self.tipos_paquetes:
                paquetes_por_tipo[tipo.nombre] = sum(
                    1 for paq in contenedor['paquetes']
                    if paq['tipo'].split('_')[0] == tipo.nombre
                )
                analisis['metricas_globales']['paquetes_por_tipo'][tipo.nombre] += paquetes_por_tipo[tipo.nombre]

            # Métricas del contenedor
            metricas_contenedor = {
                'id': contenedor['id'],
                'dimensiones': contenedor['dimensiones'],
                'volumen_total': volumen_contenedor,
                'volumen_utilizado': volumen_utilizado,
                'porcentaje_utilizacion': (volumen_utilizado / volumen_contenedor) * 100,
                'num_paquetes': len(contenedor['paquetes']),
                'paquetes_por_tipo': paquetes_por_tipo
            }
            analisis['metricas_por_contenedor'].append(metricas_contenedor)

            # Actualizar métricas globales
            analisis['metricas_globales']['total_paquetes'] += metricas_contenedor['num_paquetes']
            analisis['metricas_globales']['volumen_total_contenedores'] += volumen_contenedor
            analisis['metricas_globales']['volumen_total_utilizado'] += volumen_utilizado

        # Calcular porcentaje de utilización global
        analisis['metricas_globales']['porcentaje_utilizacion_global'] = (
                analisis['metricas_globales']['volumen_total_utilizado'] /
                analisis['metricas_globales']['volumen_total_contenedores'] * 100
        )

        # Verificar cumplimiento de restricciones
        analisis['cumplimiento_restricciones'] = {
            'cantidad_minima_cumplida': all(
                analisis['metricas_globales']['paquetes_por_tipo'][tipo.nombre] >= tipo.cantidad_minima
                for tipo in self.tipos_paquetes
            ),
            'cantidad_maxima_cumplida': all(
                analisis['metricas_globales']['paquetes_por_tipo'][tipo.nombre] <= tipo.cantidad_maxima
                for tipo in self.tipos_paquetes
            )
        }

        return analisis

    #Metodo auxiliar
    def imprimir_resultados(self, resultado: dict, analisis: dict) -> None:
        """Imprime un resumen detallado de los resultados de la optimización"""
        print("\n=== RESULTADOS DE LA OPTIMIZACIÓN ===")
        print(f"Aptitud global: {analisis['aptitud_global']:.4f}")

        print("\n=== MÉTRICAS GLOBALES ===")
        print(f"Total de paquetes colocados: {analisis['metricas_globales']['total_paquetes']}")
        print(f"Volumen total de contenedores: {analisis['metricas_globales']['volumen_total_contenedores']}")
        print(f"Volumen total utilizado: {analisis['metricas_globales']['volumen_total_utilizado']:.2f}")
        print(
            f"Porcentaje de utilización global: {analisis['metricas_globales']['porcentaje_utilizacion_global']:.2f}%")

        print("\nDistribución total de paquetes por tipo:")
        for tipo, cantidad in analisis['metricas_globales']['paquetes_por_tipo'].items():
            print(f"  {tipo}: {cantidad}")

        print("\n=== CUMPLIMIENTO DE RESTRICCIONES ===")
        print(
            f"Cantidades mínimas cumplidas: {'Sí' if analisis['cumplimiento_restricciones']['cantidad_minima_cumplida'] else 'No'}")
        print(
            f"Cantidades máximas cumplidas: {'Sí' if analisis['cumplimiento_restricciones']['cantidad_maxima_cumplida'] else 'No'}")

        print("\n=== DETALLES POR CONTENEDOR ===")
        for contenedor in analisis['metricas_por_contenedor']:
            print(f"\nContenedor {contenedor['id']}:")
            print(f"  Dimensiones: {contenedor['dimensiones']}")
            print(f"  Volumen total: {contenedor['volumen_total']}")
            print(f"  Volumen utilizado: {contenedor['volumen_utilizado']:.2f}")
            print(f"  Porcentaje de utilización: {contenedor['porcentaje_utilizacion']:.2f}%")
            print(f"  Número de paquetes: {contenedor['num_paquetes']}")
            print("  Distribución de paquetes:")
            for tipo, cantidad in contenedor['paquetes_por_tipo'].items():
                print(f"    {tipo}: {cantidad}")

        print("\n=== POSICIÓN DE PAQUETES POR CONTENEDOR ===")
        for contenedor in resultado['resultados']['contenedores']:
            print(f"\nContenedor {contenedor['id']} - Dimensiones: {contenedor['dimensiones']}")
            if not contenedor['paquetes']:
                print("  No hay paquetes colocados en este contenedor")
            else:
                for i, paquete in enumerate(contenedor['paquetes'], 1):
                    print(f"  Paquete {i}:")
                    print(f"    Tipo: {paquete['tipo']}")
                    print(f"    Posición (x,y,z): {paquete['posicion']}")
                    print(f"    Dimensiones (l,a,h): {paquete['dimensiones']}")