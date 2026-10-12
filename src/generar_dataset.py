"""Genera un dataset SINTÉTICO de muestra de afluencia por estación de TransMilenio.

Las estaciones y troncales son reales; las cifras de demanda son simuladas con
patrones plausibles (picos de 6-8 am y 5-7 pm, menor demanda en fines de semana
y festivos, ligero aumento con lluvia). Reemplazable por datos abiertos reales
manteniendo las mismas columnas.
"""
import numpy as np
import pandas as pd

SEMILLA = 42
rng = np.random.default_rng(SEMILLA)

# estacion: (troncal, factor de demanda base, capacidad horaria aprox. en validaciones)
ESTACIONES = {
    "Portal Norte":     ("Autonorte",      1.55, 6000),
    "Toberín":          ("Autonorte",      0.95, 3500),
    "Calle 142":        ("Autonorte",      0.80, 3000),
    "Calle 100":        ("Autonorte",      1.05, 4000),
    "Calle 72":         ("Caracas",        1.15, 4500),
    "Marly":            ("Caracas",        1.00, 4000),
    "Av. Jiménez":      ("Caracas",        1.35, 5000),
    "Ricaurte":         ("Caracas",        1.00, 4000),
    "Portal Sur":       ("Caracas",        1.50, 6000),
    "Portal Américas":  ("Américas",       1.50, 6000),
    "Banderas":         ("Américas",       0.90, 3500),
    "Portal 80":        ("Calle 80",       1.55, 6000),
    "Av. Chile":        ("Calle 80",       0.85, 3500),
    "Portal Tunal":     ("Tunal",          1.45, 5500),
    "Museo del Oro":    ("Eje Ambiental",  0.95, 3500),
    "Universidades":    ("Eje Ambiental",  1.10, 4000),
    "Portal Suba":      ("Suba",           1.45, 5500),
    "Portal Eldorado":  ("Eldorado",       1.35, 5000),
}

N = 12000
est = rng.choice(list(ESTACIONES), size=N)
hora = rng.integers(5, 23, size=N)            # 5:00 a 22:00
dia = rng.integers(0, 7, size=N)              # 0=lunes ... 6=domingo
festivo = (rng.random(N) < 0.05).astype(int)
lluvia = (rng.random(N) < 0.25).astype(int)

def perfil_hora(h, es_laboral):
    if es_laboral:
        return 1.0 + 1.5 * np.exp(-((h - 7) ** 2) / 2.0) + 1.4 * np.exp(-((h - 18) ** 2) / 2.5)
    return 0.8 + 0.5 * np.exp(-((h - 13) ** 2) / 12.0)

laboral = (dia < 5) & (festivo == 0)
factor_h = np.array([perfil_hora(h, l) for h, l in zip(hora, laboral)])
base = np.array([ESTACIONES[e][1] for e in est])
cap = np.array([ESTACIONES[e][2] for e in est])
troncal = [ESTACIONES[e][0] for e in est]

demanda = 1500 * base * factor_h * np.where(lluvia == 1, 1.12, 1.0)
demanda = demanda * rng.normal(1.0, 0.12, size=N)          # ruido
demanda = np.clip(demanda, 50, None).round().astype(int)

ocupacion = demanda / cap
congestion = pd.cut(ocupacion, bins=[-np.inf, 0.45, 0.75, np.inf],
                    labels=["bajo", "medio", "alto"])

df = pd.DataFrame({
    "estacion": est, "troncal": troncal, "hora": hora, "dia_semana": dia,
    "festivo": festivo, "lluvia": lluvia, "validaciones_hora": demanda,
    "capacidad_hora": cap, "ocupacion": ocupacion.round(3), "congestion": congestion,
})
df.to_csv("data/afluencia_estaciones.csv", index=False)
print(f"Dataset generado: {df.shape[0]} filas x {df.shape[1]} columnas")
print(df["congestion"].value_counts().to_string())
