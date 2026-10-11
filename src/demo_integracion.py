"""Demo mínima: A* sobre un grafo pequeño, con y sin penalización por congestión.
Ejecutar desde la raíz del repo:  python src/demo_integracion.py
Reemplazar GRAFO y la heurística por los de su astar.py real."""
import heapq
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from functools import lru_cache
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
def penalizacion(estacion, hora, dia, festivo, lluvia):
    return costo_estacion(estacion, hora, dia, festivo, lluvia)

def astar(origen, destino, hora, dia, festivo=0, lluvia=0, con_ml=True):
    h = lambda n: 0               # heurística nula (use la suya)
    abierta = [(0, 0, origen, [origen])]
    mejor = {origen: 0}
    while abierta:
        _, g, nodo, camino = heapq.heappop(abierta)
        if nodo == destino:
            return camino, g
        for vecino, t in GRAFO[nodo]:
            extra = penalizacion(vecino, hora, dia, festivo, lluvia) if con_ml else 0
            g2 = g + t + extra
            if g2 < mejor.get(vecino, float("inf")):
                mejor[vecino] = g2
                heapq.heappush(abierta, (g2 + h(vecino), g2, vecino, camino + [vecino]))
    return None, float("inf")

if __name__ == "__main__":
    for etiqueta, hora, dia in [("Martes 7:00", 7, 1), ("Domingo 14:00", 14, 6)]:
        for con_ml in (False, True):
            ruta, costo = astar("Portal Norte", "Portal Sur", hora, dia, con_ml=con_ml)
            print(f"{etiqueta} | {'con ML' if con_ml else 'sin ML'}: {' -> '.join(ruta)} | {costo} min")
