# Descripción de los datos

## 1. Origen
No se contó con un archivo público con la granularidad requerida (afluencia por estación, hora y día)
alineada con la red del proyecto, por lo que se construyó un **dataset sintético de muestra**
(`src/generar_dataset.py`, semilla 42, reproducible). Las **estaciones y troncales son reales**
(18 estaciones de 8 troncales/ejes de TransMilenio); las **cifras de demanda son simuladas**.

Fuentes reales identificadas para reemplazar la muestra manteniendo las mismas columnas:
- Datos abiertos de TransMilenio / Datos Abiertos Bogotá: validaciones de acceso por estación y franja horaria.
- GTFS de TransMilenio: estaciones, rutas y coordenadas.
- Calendario oficial de festivos de Colombia.

## 2. Lógica de simulación
- Demanda base = 1500 × factor de la estación × perfil horario × efecto lluvia × ruido (σ = 12 %).
- Perfil día laboral: picos alrededor de las 7:00 y las 18:00. Fin de semana/festivo: perfil plano más bajo.
- Lluvia: +12 % de demanda.
- Ocupación = validaciones_hora / capacidad_hora de la estación.

## 3. Variables (`data/afluencia_estaciones.csv`, 12.000 filas × 10 columnas)

| Variable | Tipo | Rango / valores | Rol |
|---|---|---|---|
| estacion | categórica | 18 estaciones | Entrada |
| troncal | categórica | 8 troncales/ejes | Informativa (redundante con estación) |
| hora | entera | 5 a 22 | Entrada |
| dia_semana | entera | 0 (lunes) a 6 (domingo) | Entrada |
| festivo | binaria | 0 / 1 (≈5 %) | Entrada |
| lluvia | binaria | 0 / 1 (≈25 %) | Entrada |
| validaciones_hora | entera | 50 a ~13.000 | No se usa (genera la etiqueta) |
| capacidad_hora | entera | 3.000 a 6.000 | No se usa (genera la etiqueta) |
| ocupacion | real | validaciones / capacidad | No se usa (genera la etiqueta) |
| **congestion** | categórica | bajo / medio / alto | **Variable objetivo** |

## 4. Variable objetivo
Se discretiza la ocupación: **bajo** ≤ 0,45; **medio** (0,45 – 0,75]; **alto** > 0,75.

Distribución: bajo 6.294 (52,5 %), medio 3.858 (32,2 %), alto 1.848 (15,4 %). Hay desbalance moderado,
por lo que se usa partición estratificada y se reporta precision/recall por clase.

## 5. Calidad y preparación
- Sin valores nulos ni duplicados de interés (se verifica en las pruebas).
- `estacion` se codifica con one-hot; las demás entradas son numéricas.
- **Prevención de fuga de información:** `validaciones_hora`, `capacidad_hora` y `ocupacion` se excluyen de las entradas porque la etiqueta se calcula a partir de ellas.
- Partición 80 % entrenamiento / 20 % prueba, estratificada, semilla 42.

## 6. Limitaciones
Al ser sintéticos, los resultados muestran que el pipeline funciona, pero **no representan el comportamiento real** de la red. Con datos reales se espera menor exactitud y mayor importancia de variables adicionales (clima real, eventos, incidentes).
