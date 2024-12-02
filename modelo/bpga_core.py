import random
from modelo.datos import RequisitosContenedor, Paquete
from deap import base, creator, tools, algorithms
from abc import ABC, abstractmethod
import numpy as np
from matplotlib import pyplot as plt
plt.switch_backend('Qt5Agg')

class OptimizadorEmpaquetadoMultiContenedor(ABC):
    def __init__(self,
                 requisitos_contenedores: list[RequisitosContenedor],
                 tipos_paquetes: list[Paquete] ,
                 rotaciones_permitidas: list[tuple] ,
                 tamano_poblacion: int = 1000,
                 generaciones: int = 55,
                 prob_cruce: float = 0.618,
                 prob_mutacion: float = 0.021) -> None:
  
        self.requisitos_contenedores = requisitos_contenedores
        self.tipos_paquetes = tipos_paquetes
        self.tamano_poblacion = tamano_poblacion
        self.generaciones = generaciones
        self.prob_cruce = prob_cruce
        self.prob_mutacion = prob_mutacion
        self.rotaciones_permitidas = rotaciones_permitidas
        self._configurar()

    def _configurar(self):
        
        # Eliminar clases creadas previamente
        if hasattr(creator, 'FitnessMax'):
            delattr(creator, 'FitnessMax')
        if hasattr(creator, 'Individual'):
            delattr(creator, 'Individual')
        self.num_contenedores = len(self.requisitos_contenedores)
        self.num_tipos_paquetes = len(self.tipos_paquetes)
        self.rotaciones_precalculadas = {
            tipo_paquete.nombre: self._generar_rotaciones_paquete(tipo_paquete, indice)
            for indice, tipo_paquete in enumerate(self.tipos_paquetes)
        }
        self.stats = tools.Statistics(key=lambda ind: ind.fitness.values)
        self.stats.register("desviación", np.std)
        self.stats.register("promedio", np.mean)
        self.stats.register("mínimo", np.min)
        self.stats.register("máximo", np.max)
        self.logbook = tools.Logbook()
        # Inicializar componentes DEAP
        self._configurar_deap()

    def _configurar_deap(self) -> None:
        """Inicializa el creador y toolbox de DEAP para múltiples contenedores"""
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()

        # Registrar generadores para cada contenedor
        atributos = []
        self.registrar_attrs(atributos)

        self.toolbox.register("individual", tools.initCycle, creator.Individual, atributos, n=1)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("evaluate", self._evaluar_aptitud)
        self.toolbox.register("mate", tools.cxUniform, indpb=self.prob_cruce)
        self.toolbox.register("mutate", self._mutar)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def registrar_attrs(self, atributos) -> None:
        for i, requisitos in enumerate(self.requisitos_contenedores):
            # Indicador binario de uso del contenedor - solo si es opcional
            if requisitos.uso_opcional:
                self.toolbox.register(
                    f"attr_usar_contenedor_{i}",
                    random.randint,
                    0, 1
                )
                atributos.append(getattr(self.toolbox, f"attr_usar_contenedor_{i}"))
            else:
                # Si no es opcional, siempre usar el contenedor
                self.toolbox.register(
                    f"attr_usar_contenedor_{i}",
                    lambda: 1
                )
                atributos.append(getattr(self.toolbox, f"attr_usar_contenedor_{i}"))

            # Cantidad de paquetes para este contenedor
            for j, tipo_paquete in enumerate(self.tipos_paquetes):
                self.toolbox.register(
                    f"attr_cantidad_{i}_{j}",
                    random.randint,
                    0,  # Mínimo 0 por contenedor
                    tipo_paquete.cantidad_maxima  # Máximo por contenedor
                )
                atributos.append(getattr(self.toolbox, f"attr_cantidad_{i}_{j}"))

    @abstractmethod
    def _generar_rotaciones_paquete(self, paquete: Paquete, indice) -> list[tuple]:
        """Genera todas las rotaciones posibles para un tipo de paquete"""
        pass

    def optimizar(self, semilla=None) -> dict:
        """Ejecuta la optimización del algoritmo genético para múltiples contenedores"""
        if semilla is not None:
            random.seed(semilla)

        poblacion = self.toolbox.population(n=self.tamano_poblacion)
        mejor_individuo = None
        mejor_aptitud = 0.0
        mejor_resultado = None


        self.logbook.header = "gen", "desviación", "mínimo", "promedio", "máximo"

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
            registro = self.stats.compile(poblacion)
            self.logbook.record(gen=gen, evals=len(poblacion), **registro)

            # Imprimir estadísticas de la generación
            print(self.logbook.stream)
            desviacion = self.logbook.select("desviación")[-1]

            #Parar si ya se ha encontrado la solución
            if mejor_aptitud >= 0.97 or desviacion <= 0.001:
                break

        return {
            'individuo': mejor_individuo,
            'aptitud': mejor_aptitud,
            'posiciones': mejor_resultado
        }

    def _colocar_paquetes_en_contenedor(self, genes_contenedor, indice_contenedor) -> tuple[list, tuple]:
        """Coloca paquetes en un contenedor específico con múltiples rotaciones"""
        paquetes_colocados = []
        dimensiones_contenedor = self.requisitos_contenedores[indice_contenedor].dimensiones
        paso_rejilla = 1

        for i in range(1, len(genes_contenedor)):
            tipo_paquete_idx = i - 1
            cantidad = genes_contenedor[i]

            # Si la cantidad es 0, continuar con el siguiente tipo
            if cantidad == 0:
                continue

            tipo_paquete = self.tipos_paquetes[tipo_paquete_idx]
            # Generar todas las posibles rotaciones para este tipo de paquete
            rotaciones = self.rotaciones_precalculadas[tipo_paquete.nombre]

            for _ in range(cantidad):
                colocado = False
                colocado = self._first_fit(colocado, dimensiones_contenedor, paquetes_colocados, paso_rejilla,
                                           rotaciones)
                if not colocado:
                    break

        return paquetes_colocados, dimensiones_contenedor

    @abstractmethod
    def _first_fit(self, colocado, dimensiones_contenedor, paquetes_colocados, paso_rejilla, rotaciones):
        pass

    @abstractmethod
    def _puede_colocar_paquete(self, paquetes_existentes, nuevo_paquete, posicion, dimensiones_contenedor) -> bool:
        pass

    def _mutar(self, individuo):
        """Operador de mutación para múltiples contenedores"""
        # Aplica mutación severa al 21% de los individuos
        if random.random() < 0.21:
            self.prob_mutacion = 0.21

        genes_por_contenedor = 1 + self.num_tipos_paquetes

        for i, requisitos in enumerate(self.requisitos_contenedores):
            inicio = i * genes_por_contenedor

            # Mutar indicador de uso solo si el contenedor es opcional
            if requisitos.uso_opcional and random.random() < self.prob_mutacion:
                individuo[inicio] = random.randint(0, 1)

            # Solo mutar cantidades si el contenedor está en uso
            if individuo[inicio] == 1:
                for j in range(self.num_tipos_paquetes):
                    idx_cantidad = inicio + 1 + j

                    if random.random() < self.prob_mutacion:
                        individuo[idx_cantidad] = random.randint(
                            0,
                            self.tipos_paquetes[j].cantidad_maxima
                        )
            else:
                # Si el contenedor no está en uso, establecer cantidades en 0
                for j in range(self.num_tipos_paquetes):
                    idx_cantidad = inicio + 1 + j
                    individuo[idx_cantidad] = 0
        self.prob_mutacion = 0.021
        return (individuo,)

    def _evaluar_aptitud(self, individuo) -> tuple[float]:
        """Evalúa la aptitud de un individuo con múltiples contenedores"""
        genes_por_contenedor = 1 + self.num_tipos_paquetes
        cantidad_total = {tipo.nombre: 0 for tipo in self.tipos_paquetes}
        volumen_total_utilizado = 0
        volumen_total_contenedores = 0
        contenedores_usados = 0

        # Procesar cada contenedor
        for i in range(self.num_contenedores):
            inicio = i * genes_por_contenedor
            usar_contenedor = individuo[inicio]

            if usar_contenedor == 1:
                contenedores_usados += 1
                genes_contenedor = individuo[inicio:inicio + genes_por_contenedor]
                paquetes_colocados, dimensiones_contenedor = self._colocar_paquetes_en_contenedor(genes_contenedor, i)

                # Actualizar conteo total de paquetes realmente colocados
                volumen_contenedor, volumen_utilizado = self._conteo_paquetes(cantidad_total, dimensiones_contenedor,
                                                                              paquetes_colocados)

                volumen_total_contenedores += volumen_contenedor
                volumen_total_utilizado += volumen_utilizado

        # Si no hay contenedores usados, retornar aptitud mínima
        if contenedores_usados == 0:
            return (0.0,)

        # Verificar restricciones de cantidad mínima
        penalizacion = 1.0
        for tipo_paquete in self.tipos_paquetes:
            if cantidad_total[tipo_paquete.nombre] < tipo_paquete.cantidad_minima:
                penalizacion *= 0.6
            if cantidad_total[tipo_paquete.nombre] > tipo_paquete.cantidad_maxima:
                penalizacion *= 0.6

        # La aptitud es el porcentaje de volumen utilizado multiplicado por la penalización
        aptitud = (volumen_total_utilizado / volumen_total_contenedores) * penalizacion
        return (aptitud,)

    @abstractmethod
    def _conteo_paquetes(self, cantidad_total, dimensiones_contenedor, paquetes_colocados):
        pass

    def obtener_posiciones_paquetes(self, individuo) -> dict:
        """Obtiene las posiciones de los paquetes y dimensiones de todos los contenedores"""
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

            # Solo procesar paquetes si el contenedor está en uso
            if usar_contenedor:
                genes_contenedor = individuo[inicio:inicio + genes_por_contenedor]
                paquetes_colocados, _ = self._colocar_paquetes_en_contenedor(genes_contenedor, i)

                self._contenedor_info(contenedor_info, paquetes_colocados)

            resultados['contenedores'].append(contenedor_info)

        return resultados

    @abstractmethod
    def _contenedor_info(self, contenedor_info, paquetes_colocados) -> None:
        pass

    def graficar_estadisticas(self) -> None:
        # Extraer generaciones y valores
        logbook = self.logbook
        gen = logbook.select("gen")
        avg = logbook.select("promedio")  # Cambié 'avg' por 'promedio'
        min_ = logbook.select("mínimo")  # Cambié 'min_' por 'mínimo'
        max_ = logbook.select("máximo")  # Cambié 'max_' por 'máximo'
        std = logbook.select("desviación")  # Cambié 'std' por 'desviación'

        # Crear la figura con subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

        # Primer subplot: Aptitud (Promedio, Mínimo, Máximo)
        ax1.plot(gen, avg, label="Promedio", color='blue', linewidth=3, marker='o', markersize=5, alpha=0.7)
        ax1.plot(gen, min_, label="Mínimo", color='red', linewidth=3, marker='s', markersize=5, alpha=0.7)
        ax1.plot(gen, max_, label="Máximo", color='green', linewidth=3, marker='^', markersize=5, alpha=0.7)
        ax1.set_title("Evolución de la Aptitud", fontsize=16, fontweight='bold')
        ax1.set_ylabel("Aptitud", fontsize=12)
        ax1.legend(loc="best", fontsize=10)
        ax1.grid(True, linestyle='--', linewidth=0.5)
        ax1.fill_between(gen, min_, max_, color='gray', alpha=0.1)  # Añadir área sombreada

        # Segundo subplot: Desviación Estándar
        ax2.plot(gen, std, label="Desviación Estándar", color='purple', linewidth=3, marker='d', markersize=5,
                 alpha=0.7)
        ax2.set_title("Desviación Estándar", fontsize=16, fontweight='bold')
        ax2.set_xlabel("Generación", fontsize=12)
        ax2.set_ylabel("Desviación Estándar", fontsize=12)
        ax2.legend(loc="best", fontsize=10)
        ax2.grid(True, linestyle='--', linewidth=0.5)

        plt.tight_layout()
        plt.show()

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
        for contenedor in resultado['posiciones']['contenedores']:
            volumen_contenedor = np.prod(contenedor['dimensiones'])
            volumen_utilizado = sum(np.prod(paq['dimensiones']) for paq in contenedor['paquetes'])

            # Contar paquetes por tipo en este contenedor
            paquetes_por_tipo = {}
            for tipo in self.tipos_paquetes:
                # Contar paquetes cuyo nombre original coincide con el tipo
                paquetes_por_tipo[tipo.nombre] = sum(
                    1 for paq in contenedor['paquetes']
                    if paq['tipo'].split('_')[0] == tipo.nombre
                )
                # Actualizar el conteo global
                analisis['metricas_globales']['paquetes_por_tipo'][tipo.nombre] += paquetes_por_tipo[tipo.nombre]

            # Métricas del contenedor
            metricas_contenedor = {
                'id': contenedor['id'],
                'dimensiones': contenedor['dimensiones'],
                'volumen_total': volumen_contenedor,
                'volumen_utilizado': volumen_utilizado,
                'porcentaje_utilizacion': (
                                                  volumen_utilizado / volumen_contenedor) * 100 if volumen_contenedor > 0 else 0,
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
        ) if analisis['metricas_globales']['volumen_total_contenedores'] > 0 else 0

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
        for contenedor in resultado['posiciones']['contenedores']:
            print(f"\nContenedor {contenedor['id']} - Dimensiones: {contenedor['dimensiones']}")
            if not contenedor['paquetes']:
                print("  No hay paquetes colocados en este contenedor")
            else:
                for i, paquete in enumerate(contenedor['paquetes'], 1):
                    print(f"  Paquete {i}:")
                    print(f"    Tipo: {paquete['tipo']}")  # Incluye la rotación
                    print(f"    Posición (x,y,z): {paquete['posicion']}")
                    print(f"    Dimensiones (l,a,h): {paquete['dimensiones']}")

    @abstractmethod
    def graficar_resultados(self, resultado: dict) -> None:
        pass