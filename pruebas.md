# Pruebas realizadas al componente

Entorno: Python 3.12, scikit-learn 1.8.0. Comando: `python src/modelo_congestion.py` y `python -m pytest src/test_modelo.py -v`.

## 1. Evaluación del modelo (conjunto de prueba, 2.400 registros)

| Modelo | Exactitud (test) |
|---|---|
| Línea base (clase mayoritaria) | 0,5246 |
| **Árbol de decisión (max_depth = 8)** | **0,7900** |

### Selección de profundidad (validación cruzada de 5 folds sobre entrenamiento)

| max_depth | acc. entrenamiento | acc. CV | acc. test |
|---|---|---|---|
| 2 | 0,5765 | 0,5765 | 0,5733 |
| 3 | 0,6652 | 0,6652 | 0,6458 |
| 4 | 0,7376 | 0,7376 | 0,7238 |
| 5 | 0,7522 | 0,7483 | 0,7475 |
| 6 | 0,7953 | 0,7866 | 0,7817 |
| **8** | 0,8148 | **0,7968** | 0,7900 |
| 10 | 0,8281 | 0,7908 | 0,7887 |
| 15 | 0,8530 | 0,7804 | 0,7854 |
| None | 0,8814 | 0,7674 | 0,7825 |

Lectura: con profundidades 2–4 hay **subajuste**; desde 10 la brecha entrenamiento–CV crece (**sobreajuste**: 0,88 vs 0,77 sin límite). Se elige 8 por mejor exactitud en CV.

### Métricas por clase

| Clase | Precision | Recall | F1 |
|---|---|---|---|
| bajo | 0,849 | 0,882 | 0,865 |
| medio | 0,732 | 0,546 | 0,626 |
| alto | 0,705 | 0,984 | 0,822 |

### Matriz de confusión (filas = real, columnas = predicho; orden bajo, medio, alto)

|  | bajo | medio | alto |
|---|---|---|---|
| bajo | 1111 | 148 | 0 |
| medio | 198 | 421 | 152 |
| alto | 0 | 6 | 364 |

Los errores se concentran entre clases vecinas; **nunca se confunde bajo con alto** (0 casos) y solo 6 de 370 "alto" se subestiman como "medio". La clase "medio" es la más difícil, por estar en la zona de transición.

### Variables más importantes
hora 0,707 · dia_semana 0,104 · festivo 0,090 · lluvia 0,064; las estaciones individuales aportan menos de 0,01 cada una.

Evidencias: `resultados/metricas.json`, `matriz_confusion.png`, `importancias.png`, `arbol_profundidad3.png`, `reglas_arbol.txt`.

## 2. Pruebas automatizadas (`src/test_modelo.py`): 7/7 aprobadas

| Prueba | Verifica | Resultado |
|---|---|---|
| test_dataset_sin_nulos_y_columnas | Sin nulos; columnas esperadas presentes | OK |
| test_rangos_validos | hora 5–22, día 0–6, binarias, 3 clases | OK |
| test_hora_pico_laboral_es_alta | Portal Norte, martes 7:00 → alto | OK |
| test_madrugada_o_domingo_es_baja | Calle 142, domingo 21:00 → bajo | OK |
| test_pico_mas_congestionado_que_valle | Pico laboral > domingo a mediodía | OK |
| test_costo_en_minutos | Penalización 5 min (alto) y 0 min (bajo) | OK |
| test_estacion_desconocida | Lanza ValueError ante estación inexistente | OK |

## 3. Prueba de integración con A*
Completar con su `astar.py`: ejecutar la misma ruta (ej. Portal Norte → Portal Sur) a las 7:00 de un martes y a las 14:00 de un domingo, y registrar si cambia la ruta/tiempo al sumar `costo_estacion(...)` al costo g(n).
