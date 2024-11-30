import random
from datos import *
from deap import base, creator, tools, algorithms
from abc import ABC, abstractmethod
import numpy as np


class OptimizadorEmpaquetadoMultiContenedor(ABC):
    def __init__(self,
                 requisitos_contenedores: list[RequisitosContenedor],
                 tipos_paquetes: list[Paquete] ,
                 rotaciones_permitidas: list[tuple] ,
                 tamano_poblacion: int = 1000,
                 generaciones: int = 55,
                 prob_cruce: float = 0.618,
                 prob_mutacion: float = 0.021) -> None:

        self.num_contenedores = len(requisitos_contenedores)
        self.requisitos_contenedores = requisitos_contenedores
        self.tipos_paquetes = tipos_paquetes
        self.tamano_poblacion = tamano_poblacion
        self.generaciones = generaciones
        self.prob_cruce = prob_cruce
        self.prob_mutacion = prob_mutacion
        self.rotaciones_permitidas = rotaciones_permitidas
        self.num_tipos_paquetes = len(tipos_paquetes)
        self.rotaciones_precalculadas = {
            tipo_paquete.nombre: self._generar_rotaciones_paquete(tipo_paquete)
            for tipo_paquete in self.tipos_paquetes
        }

        # Inicializar componentes DEAP
        self._configurar_deap()

    def _configurar_deap(self) -> None:
        """Inicializa el creador y toolbox de DEAP para múltiples contenedores"""
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()

        # Registrar generadores para cada contenedor
        atributos = []
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

        self.toolbox.register("individual", tools.initCycle, creator.Individual, atributos, n=1)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("evaluate", self._evaluar_aptitud)
        self.toolbox.register("mate", tools.cxUniform, indpb=0.5)
        self.toolbox.register("mutate", self._mutar)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def _mutar(self, individuo):
        """Operador de mutación para múltiples contenedores"""
        # Aplica mutación severa al 21% de los individuos
        if random.random() < self.prob_mutacion * 10:
            self.prob_mutacion *= 10

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
            'posiciones': mejor_resultado
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
    def _generar_rotaciones_paquete(self, paquete: Paquete) -> list[tuple]:
        """Genera todas las rotaciones posibles para un tipo de paquete"""
        pass

    @abstractmethod
    def _puede_colocar_paquete(self, paquetes_existentes, nuevo_paquete, posicion, dimensiones_contenedor) -> bool:
        pass

    @abstractmethod
    def _colocar_paquetes_en_contenedor(self, genes_contenedor, indice_contenedor) -> tuple[list, tuple]:
        pass

    @abstractmethod
    def _evaluar_aptitud(self, individuo) -> tuple[float]:
        pass

    @abstractmethod
    def obtener_posiciones_paquetes(self, individuo) -> dict:
        pass

    @abstractmethod
    def graficar_resultados(self, resultado: dict) -> None:
        pass