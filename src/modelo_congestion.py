"""Modelo supervisado (árbol de decisión) que predice el nivel de congestión
(bajo / medio / alto) de una estación de TransMilenio según estación, hora,
día de la semana, festivo y lluvia.

Uso:  python src/modelo_congestion.py
"""
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, ConfusionMatrixDisplay)

SEMILLA = 42
ETIQUETAS = ["bajo", "medio", "alto"]
# Variables de entrada. NO se usan validaciones_hora, capacidad_hora ni ocupacion
# porque con ellas se calcula la etiqueta (fuga de información / data leakage).
CARACTERISTICAS = ["estacion", "hora", "dia_semana", "festivo", "lluvia"]


def cargar_datos(ruta="data/afluencia_estaciones.csv"):
    df = pd.read_csv(ruta)
    X = pd.get_dummies(df[CARACTERISTICAS], columns=["estacion"])
    y = df["congestion"]
    return df, X, y


def entrenar():
    df, X, y = cargar_datos()
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEMILLA)

    resultados = {}

    # 1) Línea base: siempre predice la clase mayoritaria
    base = DummyClassifier(strategy="most_frequent").fit(X_tr, y_tr)
    resultados["baseline_accuracy"] = round(accuracy_score(y_te, base.predict(X_te)), 4)

    # 2) Selección de profundidad con validación cruzada (5 folds) sobre entrenamiento
    profundidades = [2, 3, 4, 5, 6, 8, 10, 15, None]
    tabla = []
    for d in profundidades:
        m = DecisionTreeClassifier(max_depth=d, random_state=SEMILLA)
        cv = cross_val_score(m, X_tr, y_tr, cv=5).mean()
        m.fit(X_tr, y_tr)
        tabla.append({"max_depth": "None" if d is None else d,
                      "acc_train": round(m.score(X_tr, y_tr), 4),
                      "acc_cv": round(cv, 4),
                      "acc_test": round(m.score(X_te, y_te), 4)})
    resultados["comparacion_profundidad"] = tabla
    mejor = max(tabla, key=lambda t: t["acc_cv"])
    d_opt = None if mejor["max_depth"] == "None" else mejor["max_depth"]
    resultados["max_depth_elegido"] = mejor["max_depth"]

    # 3) Modelo final
    modelo = DecisionTreeClassifier(max_depth=d_opt, random_state=SEMILLA).fit(X_tr, y_tr)
    pred = modelo.predict(X_te)
    resultados["accuracy_test"] = round(accuracy_score(y_te, pred), 4)
    resultados["reporte"] = classification_report(
        y_te, pred, labels=ETIQUETAS, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_te, pred, labels=ETIQUETAS)
    resultados["matriz_confusion"] = cm.tolist()

    imp = pd.Series(modelo.feature_importances_, index=X.columns).sort_values(ascending=False)
    resultados["top_importancias"] = imp.head(8).round(4).to_dict()

    # 4) Artefactos
    ConfusionMatrixDisplay(cm, display_labels=ETIQUETAS).plot(cmap="Blues")
    plt.title("Matriz de confusión (test)")
    plt.savefig("resultados/matriz_confusion.png", dpi=130, bbox_inches="tight"); plt.close()

    plt.figure(figsize=(8, 4))
    imp.head(8).iloc[::-1].plot(kind="barh")
    plt.title("Importancia de variables"); plt.tight_layout()
    plt.savefig("resultados/importancias.png", dpi=130); plt.close()

    d_plot = DecisionTreeClassifier(max_depth=3, random_state=SEMILLA).fit(X_tr, y_tr)
    plt.figure(figsize=(18, 8))
    plot_tree(d_plot, feature_names=list(X.columns), class_names=d_plot.classes_,
              filled=True, fontsize=8)
    plt.savefig("resultados/arbol_profundidad3.png", dpi=130, bbox_inches="tight"); plt.close()

    with open("resultados/reglas_arbol.txt", "w", encoding="utf-8") as f:
        f.write(export_text(d_plot, feature_names=list(X.columns)))
    with open("resultados/metricas.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    joblib.dump({"modelo": modelo, "columnas": list(X.columns)}, "resultados/modelo.joblib")
    return modelo, list(X.columns), resultados


PENALIZACION_MIN = {"bajo": 0, "medio": 2, "alto": 5}   # minutos extra por estación


def predecir_congestion(estacion, hora, dia_semana, festivo=0, lluvia=0,
                        ruta_modelo="resultados/modelo.joblib"):
    """Devuelve 'bajo', 'medio' o 'alto' para una estación y momento dados."""
    art = joblib.load(ruta_modelo)
    fila = pd.DataFrame([{c: 0 for c in art["columnas"]}])
    fila.loc[0, ["hora", "dia_semana", "festivo", "lluvia"]] = [hora, dia_semana, festivo, lluvia]
    col = f"estacion_{estacion}"
    if col not in fila.columns:
        raise ValueError(f"Estación desconocida: {estacion}")
    fila.loc[0, col] = 1
    return art["modelo"].predict(fila)[0]


def costo_estacion(estacion, hora, dia_semana, festivo=0, lluvia=0):
    """Penalización (minutos) que se suma al costo g(n) del algoritmo A*."""
    return PENALIZACION_MIN[predecir_congestion(estacion, hora, dia_semana, festivo, lluvia)]


if __name__ == "__main__":
    _, _, r = entrenar()
    print(json.dumps({k: r[k] for k in ["baseline_accuracy", "max_depth_elegido",
                                        "accuracy_test"]}, indent=2))
    print(pd.DataFrame(r["comparacion_profundidad"]).to_string(index=False))
    print("Matriz de confusión:", r["matriz_confusion"])
    print("Importancias:", r["top_importancias"])
    for lab in ETIQUETAS:
        p = r["reporte"][lab]
        print(f"{lab}: precision={p['precision']:.3f} recall={p['recall']:.3f} f1={p['f1-score']:.3f}")
