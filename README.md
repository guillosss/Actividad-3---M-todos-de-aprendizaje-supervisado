# Sistema Inteligente para Encontrar la Mejor Ruta en TransMilenio
## Actividad 5: Aprendizaje supervisado (predicción de congestión por estación)

Componente que entrena un árbol de decisión para predecir el nivel de congestión (bajo/medio/alto)
y lo integra con la búsqueda A* como penalización de costo por estación.

```
data/afluencia_estaciones.csv   dataset (sintético, 12.000 filas)
src/generar_dataset.py          genera el dataset
src/modelo_congestion.py        entrena, evalúa y expone costo_estacion()
src/test_modelo.py              pruebas automatizadas
docs/descripcion_datos.md       descripción de los datos
docs/pruebas.md                 pruebas y resultados
resultados/                     métricas, gráficas, reglas y modelo
```

## Ejecución
```bash
pip install -r requirements.txt
python src/generar_dataset.py
python src/modelo_congestion.py
python -m pytest src/test_modelo.py -v
```

## Integración con A*
```python
from modelo_congestion import costo_estacion
g_nuevo = g_actual + tiempo_tramo + costo_estacion(estacion, hora, dia_semana, festivo, lluvia)
```

Entregables: enlace al video (≤ 10 min) y PDF con los enlaces del repositorio. Agregar al tutor como colaborador.
