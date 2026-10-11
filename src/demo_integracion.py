"""Demo: A* con y sin penalización por congestión (modelo supervisado).
Ejecutar desde la raíz del repo:  python src/demo_integracion.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from astar import astar

if __name__ == "__main__":
    for etiqueta, hora, dia in [("Martes 7:00", 7, 1), ("Domingo 14:00", 14, 6)]:
        for con_ml in (False, True):
            ruta, costo = astar("Portal Norte", "Portal Sur", hora, dia, con_ml=con_ml)
            print(f"{etiqueta} | {'con ML' if con_ml else 'sin ML'}: {' -> '.join(ruta)} | {costo} min")
