"""
LOAD — Quality checks y persistencia   *** PARCIALMENTE RESUELTO ***
=====================================================================

Dos responsabilidades, en este orden:

  1. CHEQUEAR: validar el dataset antes de publicarlo.
  2. GUARDAR: escribir CSV, JSON y log.
"""

import csv
import json
import logging
import os
from datetime import datetime

import config
from transform import COLUMNAS


# ======================================================================
# QUALITY CHECKS
# ======================================================================

def chequear_cantidad(filas, minimo=None):
    """Verifica que haya como mínimo la cantidad esperada de filas."""
    if minimo is None:
        minimo = config.MINIMO_FILAS_ESPERADAS

    ok = len(filas) >= minimo

    return ok, f"cantidad: {len(filas)} filas (mínimo esperado {minimo})"


def chequear_columnas(filas):
    """Verifica que todas las filas tengan las columnas del contrato."""
    esperadas = set(COLUMNAS)

    for fila in filas:
        if set(fila.keys()) != esperadas:
            faltan = esperadas - set(fila.keys())

            return (
                False,
                f"columnas: una fila no cumple el esquema "
                f"(faltan {faltan})"
            )

    return (
        True,
        f"columnas: las {len(COLUMNAS)} del contrato en todas las filas"
    )


def chequear_unicidad(filas):
    """Verifica que no existan duplicados."""
    claves = [
        (
            fila["provincia"],
            fila["anio"],
            fila["destino"]
        )
        for fila in filas
    ]

    ok = len(claves) == len(set(claves))

    if ok:
        mensaje = f"unicidad: {len(claves)} claves únicas"
    else:
        duplicados = len(claves) - len(set(claves))
        mensaje = f"unicidad: hay {duplicados} filas duplicadas"

    return ok, mensaje


def chequear_rangos(filas):
    """Verifica que los valores de exportación sean plausibles."""
    fuera_de_rango = [
        fila
        for fila in filas
        if (
            fila["valor_musd"] is not None
            and (
                fila["valor_musd"] < 0
                or fila["valor_musd"] > config.VALOR_MAXIMO_RAZONABLE
            )
        )
    ]

    ok = len(fuera_de_rango) == 0

    mensaje = (
        f"rangos: {len(fuera_de_rango)} valores fuera de rango "
        f"(0–{config.VALOR_MAXIMO_RAZONABLE})"
    )

    return ok, mensaje


def chequear_cobertura(filas):
    """Verifica la cobertura de las columnas derivadas."""
    sin_variacion = sum(
        1
        for f in filas
        if f["var_interanual_pct"] is None
    )

    sin_rubro = sum(
        1
        for f in filas
        if f["rubro_principal"] is None
    )

    ok = sin_rubro == 0

    return ok, (
        f"cobertura: {sin_variacion} filas sin variación interanual "
        f"(esperable en el primer año), {sin_rubro} sin rubro"
    )


def validar(filas):
    """Corre todos los quality checks y detiene el proceso si falla uno."""
    criticos = [
        chequear_cantidad(filas),
        chequear_columnas(filas),
        chequear_unicidad(filas),
        chequear_rangos(filas),
    ]

    detalle = []

    for ok, mensaje in criticos:
        detalle.append({
            "check": mensaje,
            "estado": "OK" if ok else "FALLO"
        })

        if ok:
            logging.info("  check OK    | %s", mensaje)
        else:
            logging.error("  check FALLO | %s", mensaje)
            raise ValueError(
                f"Quality check crítico falló -> {mensaje}"
            )

    ok, mensaje = chequear_cobertura(filas)

    detalle.append({
        "check": mensaje,
        "estado": "OK" if ok else "AVISO"
    })

    if ok:
        logging.info("  check OK    | %s", mensaje)
    else:
        logging.warning("  check AVISO | %s", mensaje)

    return detalle


# ======================================================================
# PERSISTENCIA
# ======================================================================

def guardar_csv(filas, carpeta=None, nombre=None):
    """Escribe el dataset final en CSV."""
    carpeta = carpeta or config.DIR_PROCESSED
    nombre = nombre or config.ARCHIVO_SALIDA_CSV

    os.makedirs(carpeta, exist_ok=True)

    ruta = os.path.join(carpeta, nombre)

    with open(
        ruta,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:
        escritor = csv.DictWriter(
            f,
            fieldnames=COLUMNAS
        )

        escritor.writeheader()
        escritor.writerows(filas)

    logging.info(
        "  CSV: %s (%s filas)",
        ruta,
        len(filas)
    )

    return ruta


def construir_resumen(filas, detalle_checks):
    """Construye el resumen técnico del dataset."""
    valores = [
        fila["valor_musd"]
        for fila in filas
        if fila["valor_musd"] is not None
    ]

    anios = [
        fila["anio"]
        for fila in filas
        if fila["anio"] is not None
    ]

    provincias = sorted({
        fila["provincia"]
        for fila in filas
        if fila["provincia"] is not None
    })

    if valores:
        minimo = round(min(valores), 2)
        maximo = round(max(valores), 2)
        promedio = round(sum(valores) / len(valores), 2)
    else:
        minimo = None
        maximo = None
        promedio = None

    if anios:
        anio_min = min(anios)
        anio_max = max(anios)
    else:
        anio_min = None
        anio_max = None

    resumen = {
        "dataset": "Exportaciones del NEA por provincia y destino",
        "fuente": "API de Series de Tiempo de datos.gob.ar / INDEC",
        "unidad": "millones de dólares FOB",
        "generado": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "filas": len(filas),
        "columnas": len(COLUMNAS),
        "periodo": {
            "desde": anio_min,
            "hasta": anio_max,
        },
        "provincias": provincias,
        "valor_musd": {
            "minimo": minimo,
            "maximo": maximo,
            "promedio": promedio,
        },
        "quality_checks": detalle_checks,
    }

    return resumen


def guardar_resumen(resumen, carpeta=None, nombre=None):
    """Guarda el resumen técnico en formato JSON."""
    carpeta = carpeta or config.DIR_PROCESSED
    nombre = nombre or config.ARCHIVO_SALIDA_JSON

    os.makedirs(carpeta, exist_ok=True)

    ruta = os.path.join(carpeta, nombre)

    with open(
        ruta,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            resumen,
            f,
            ensure_ascii=False,
            indent=2
        )

    logging.info("  JSON: %s", ruta)

    return ruta


def escribir_log_corrida(resumen, carpeta=None, nombre=None):
    """Agrega una línea al historial del pipeline."""
    carpeta = carpeta or config.DIR_LOGS
    nombre = nombre or config.ARCHIVO_LOG

    os.makedirs(carpeta, exist_ok=True)

    ruta = os.path.join(carpeta, nombre)

    periodo = resumen["periodo"]

    linea = (
        f'{resumen["generado"]} | OK | '
        f'{resumen["filas"]} filas | '
        f'{periodo["desde"]}-{periodo["hasta"]}\n'
    )

    with open(
        ruta,
        "a",
        encoding="utf-8"
    ) as f:
        f.write(linea)

    logging.info("  LOG: %s", ruta)

    return ruta


def cargar(filas):
    """Valida y persiste las tres salidas."""
    logging.info("LOAD: validando")

    detalle = validar(filas)

    logging.info("LOAD: guardando")

    guardar_csv(filas)

    resumen = construir_resumen(
        filas,
        detalle
    )

    guardar_resumen(resumen)
    escribir_log_corrida(resumen)

    logging.info("LOAD OK")

    return resumen