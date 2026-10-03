"""
TRANSFORM — De datos crudos a un dataset analítico   *** ACÁ TRABAJÁS VOS ***
=============================================================================

Este es el corazón del TP. El Extract ya te trae los datos y el Load ya
sabe guardarlos: lo que falta es convertir lo crudo en algo analizable.

El recorrido es:

    formato ANCHO (como llega de la API)
        fecha        China   Brasil   ...   __TOTAL__
        1993-01-01    12.3     45.6   ...      120.0

              |  ancho_a_largo()          <- TODO 1
              v

    formato LARGO / "tidy" (una fila por observación)
        anio  provincia  destino  valor_musd  total_provincia_musd
        1993  Chaco      China          12.3                 120.0
        1993  Chaco      Brasil         45.6                 120.0

              |  + columnas derivadas     <- TODO 2, 3, 4, 5, 6
              |  + join con rubros        <- TODO 7, 8
              v

    dataset final de 13 columnas
"""

import logging

import config


CLAVE_TOTAL = "__TOTAL__"


COLUMNAS = [
    "anio",
    "provincia",
    "destino",
    "region_destino",
    "valor_musd",
    "total_provincia_musd",
    "participacion_pct",
    "var_interanual_pct",
    "decada",
    "ranking_destino",
    "es_top3",
    "rubro_principal",
    "pp_participacion_pct",
]


# ======================================================================
# 1) ANCHO -> LARGO
# ======================================================================

def extraer_anio(fecha_texto):
    """Convierte '1993-01-01' en el entero 1993."""
    return int(fecha_texto[:4])


def ancho_a_largo(paquetes_destino):
    """Convierte los datos de formato ancho a formato largo."""
    filas = []

    for paquete in paquetes_destino:
        provincia = paquete["provincia"]
        columnas = paquete["orden_columnas"]
        posicion_total = columnas.index(CLAVE_TOTAL)

        for fila_cruda in paquete["data"]:
            fecha = fila_cruda[0]
            valores = fila_cruda[1:]

            anio = extraer_anio(fecha)
            total = valores[posicion_total]

            for posicion, nombre in enumerate(columnas):
                if nombre == CLAVE_TOTAL:
                    continue

                valor = valores[posicion]

                if valor is None:
                    continue

                filas.append({
                    "anio": anio,
                    "provincia": provincia,
                    "destino": nombre,
                    "valor_musd": round(valor, 2),
                    "total_provincia_musd": round(total, 2),
                })

    logging.info("  ancho_a_largo: %s filas", len(filas))
    return filas


# ======================================================================
# 2) COLUMNAS DERIVADAS SIMPLES
# ======================================================================

def clasificar_region(destino):
    """Devuelve la región geoeconómica de un país de destino."""
    return config.REGIONES.get(destino, config.REGION_POR_DEFECTO)


def calcular_decada(anio):
    """Devuelve la década de un año como texto."""
    decada = (anio // 10) * 10
    return f"{decada}s"


def calcular_participacion(valor, total):
    """Calcula qué porcentaje del total representa un destino."""
    if total is None or total == 0:
        return None

    return round((valor / total) * 100, 2)


def agregar_derivadas_simples(filas):
    """Agrega región, década y participación porcentual."""
    for fila in filas:
        fila["region_destino"] = clasificar_region(fila["destino"])
        fila["decada"] = calcular_decada(fila["anio"])
        fila["participacion_pct"] = calcular_participacion(
            fila["valor_musd"],
            fila["total_provincia_musd"]
        )

    return filas


# ======================================================================
# 3) VARIACIÓN INTERANUAL
# ======================================================================

def calcular_variacion(actual, anterior):
    """Calcula la variación porcentual entre dos valores."""
    if anterior is None or anterior == 0:
        return None

    return round(((actual - anterior) / anterior) * 100, 2)


def agregar_variacion_interanual(filas):
    """Agrega la variación interanual por provincia y destino."""
    indice = {}

    for fila in filas:
        clave = (
            fila["provincia"],
            fila["destino"],
            fila["anio"],
        )
        indice[clave] = fila["valor_musd"]

    for fila in filas:
        clave_anterior = (
            fila["provincia"],
            fila["destino"],
            fila["anio"] - 1,
        )

        anterior = indice.get(clave_anterior)

        fila["var_interanual_pct"] = calcular_variacion(
            fila["valor_musd"],
            anterior
        )

    return filas


# ======================================================================
# 4) RANKING DE DESTINOS
# ======================================================================

def agregar_ranking(filas, top_n=None):
    """Agrega ranking y determina si cada destino está en el top N."""
    if top_n is None:
        top_n = config.TOP_N

    grupos = {}

    for fila in filas:
        clave = (fila["provincia"], fila["anio"])
        grupos.setdefault(clave, []).append(fila)

    for grupo in grupos.values():
        grupo_ordenado = sorted(
            grupo,
            key=lambda f: f["valor_musd"],
            reverse=True
        )

        for posicion, fila in enumerate(grupo_ordenado, start=1):
            fila["ranking_destino"] = posicion
            fila["es_top3"] = posicion <= top_n

    return filas


# ======================================================================
# 5) JOIN CON LOS RUBROS
# ======================================================================

def construir_indice_rubros(paquetes_rubro):
    """Construye un índice de rubro principal y participación de PP."""
    indice = {}

    for paquete in paquetes_rubro:
        provincia = paquete["provincia"]
        columnas = paquete["orden_columnas"]

        for fila_cruda in paquete["data"]:
            fecha = fila_cruda[0]
            valores = fila_cruda[1:]

            anio = extraer_anio(fecha)

            rubros = {}

            for posicion, nombre in enumerate(columnas):
                valor = valores[posicion]

                if valor is not None:
                    rubros[nombre] = valor

            if not rubros:
                indice[(provincia, anio)] = {
                    "rubro_principal": None,
                    "pp_participacion_pct": None,
                }
                continue

            rubro_principal = max(
                rubros,
                key=rubros.get
            )

            total = sum(rubros.values())
            valor_pp = rubros.get("Productos primarios")

            if valor_pp is None or total == 0:
                pp_participacion = None
            else:
                pp_participacion = round(
                    (valor_pp / total) * 100,
                    2
                )

            indice[(provincia, anio)] = {
                "rubro_principal": rubro_principal,
                "pp_participacion_pct": pp_participacion,
            }

    logging.info(
        "  índice de rubros: %s claves (provincia, año)",
        len(indice)
    )

    return indice


def unir_con_rubros(filas, indice_rubros):
    """Une las filas de destinos con la información de rubros."""
    for fila in filas:
        clave = (
            fila["provincia"],
            fila["anio"],
        )

        datos_rubro = indice_rubros.get(clave)

        if datos_rubro is None:
            fila["rubro_principal"] = None
            fila["pp_participacion_pct"] = None
        else:
            fila["rubro_principal"] = datos_rubro["rubro_principal"]
            fila["pp_participacion_pct"] = datos_rubro[
                "pp_participacion_pct"
            ]

    return filas


# ======================================================================
# ORQUESTACIÓN DEL TRANSFORM
# ======================================================================

def ordenar_columnas(filas):
    """Devuelve las filas con las claves en el orden definido por COLUMNAS."""
    return [
        {columna: fila.get(columna) for columna in COLUMNAS}
        for fila in filas
    ]


def transformar(datos_crudos):
    """Transforma los datos crudos en las 13 columnas finales."""
    logging.info("TRANSFORM: iniciando")

    filas = ancho_a_largo(datos_crudos["destino"])
    filas = agregar_derivadas_simples(filas)
    filas = agregar_variacion_interanual(filas)
    filas = agregar_ranking(filas)

    indice = construir_indice_rubros(datos_crudos["rubro"])
    filas = unir_con_rubros(filas, indice)

    filas.sort(
        key=lambda f: (
            f["provincia"],
            f["anio"],
            f["ranking_destino"]
        )
    )

    filas = ordenar_columnas(filas)

    logging.info(
        "TRANSFORM OK: %s filas x %s columnas",
        len(filas),
        len(COLUMNAS)
    )

    return filas