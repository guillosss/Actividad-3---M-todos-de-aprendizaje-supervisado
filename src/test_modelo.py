"""Pruebas del componente de congestión. Ejecutar: python -m pytest src/test_modelo.py -v
(requiere haber ejecutado antes generar_dataset.py y modelo_congestion.py)"""
import os, sys
import pandas as pd
import pytest
sys.path.insert(0, os.path.dirname(__file__))
from modelo_congestion import predecir_congestion, costo_estacion, CARACTERISTICAS

DATOS = "data/afluencia_estaciones.csv"


def test_dataset_sin_nulos_y_columnas():
    df = pd.read_csv(DATOS)
    assert df.isna().sum().sum() == 0
    for c in CARACTERISTICAS + ["congestion", "validaciones_hora"]:
        assert c in df.columns


def test_rangos_validos():
    df = pd.read_csv(DATOS)
    assert df["hora"].between(5, 22).all()
    assert df["dia_semana"].between(0, 6).all()
    assert set(df["festivo"].unique()) <= {0, 1}
    assert set(df["congestion"].unique()) == {"bajo", "medio", "alto"}


def test_hora_pico_laboral_es_alta():
    assert predecir_congestion("Portal Norte", 7, 1) == "alto"


def test_madrugada_o_domingo_es_baja():
    assert predecir_congestion("Calle 142", 21, 6) == "bajo"


def test_pico_mas_congestionado_que_valle():
    orden = {"bajo": 0, "medio": 1, "alto": 2}
    pico = orden[predecir_congestion("Av. Jiménez", 18, 2)]
    valle = orden[predecir_congestion("Av. Jiménez", 14, 6)]
    assert pico > valle


def test_costo_en_minutos():
    assert costo_estacion("Portal Norte", 7, 1) == 5
    assert costo_estacion("Calle 142", 21, 6) == 0


def test_estacion_desconocida():
    with pytest.raises(ValueError):
        predecir_congestion("Estacion Inventada", 8, 1)
