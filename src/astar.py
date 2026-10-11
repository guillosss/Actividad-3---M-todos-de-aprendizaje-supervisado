"""A* sobre una red de estaciones de TransMilenio, con penalización por congestión
predicha por el modelo supervisado (árbol de decisión).

Costo al pasar a un vecino:  g_nuevo = g_actual + tiempo_tramo + penalización(vecino)
donde la penalización (0, 2 o 5 minutos) sale de costo_estacion() según la hora,
el día, si es festivo y si llueve.

Con la heurística por defecto (h = 0) A* se comporta como Dijkstra; para usar una
heurística real pase una función h(nodo, destino) en el parámetro `heuristica`.

Ejecutar desde la raíz del repo:  python src/demo_integracion.py
"""
import heapq
import os
import sys
from functools import lru_cache

sys.path.insert(0, os.path.dirname(__file__))
from modelo_congestion import costo_estacion

# Grafo de ejemplo: estación -> [(vecino, minutos del tramo)]
GRAFO = {
    "Portal Norte": [("Calle 100", 8), ("Toberín", 6)],
    "Toberín": [("Calle 100", 7)],
    "Calle 100": [("Calle 72", 5), ("Av. Jiménez", 11)],
    "Calle 72": [("Av. Jiménez", 4)],
    "Av. Jiménez": [("Ricaurte", 6), ("Portal Sur", 14)],
    "Ricaurte": [("Portal Sur", 8)],
    "Portal Sur": [],
}


@lru_cache(maxsize=None)          # evita recargar el modelo en cada llamada
def penalizacion(estacion, hora, dia_semana, festivo, lluvia):
    return costo_estacion(estacion, hora, dia_semana, festivo, lluvia)


def astar(origen, destino, hora, dia_semana, festivo=0, lluvia=0,
          con_ml=True, heuristica=None, grafo=None):
    """Devuelve (camino, costo_total_en_minutos); (None, inf) si no hay ruta."""
    grafo = GRAFO if grafo is None else grafo
    for e in (origen, destino):
        if e not in grafo:
            raise ValueError(f"Estación desconocida: {e}")
    h = heuristica or (lambda nodo, meta: 0)
    abierta = [(h(origen, destino), 0, origen, [origen])]
    mejor = {origen: 0}
    while abierta:
        _, g_actual, nodo, camino = heapq.heappop(abierta)
        if nodo == destino:
            return camino, g_actual
        if g_actual > mejor.get(nodo, float("inf")):
            continue
        for vecino, tiempo_tramo in grafo[nodo]:
            extra = penalizacion(vecino, hora, dia_semana, festivo, lluvia) if con_ml else 0
            g_nuevo = g_actual + tiempo_tramo + extra          # <- línea clave de la integración
            if g_nuevo < mejor.get(vecino, float("inf")):
                mejor[vecino] = g_nuevo
                heapq.heappush(abierta, (g_nuevo + h(vecino, destino), g_nuevo, vecino, camino + [vecino]))
    return None, float("inf")
