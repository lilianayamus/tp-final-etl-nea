# TP Final — Pipeline ETL de exportaciones del NEA

**Unidad II · Fundamentos de la Programación**
Diplomatura en Data Analytics e IA Aplicada — UNNE / Extender

---

## Qué vas a construir

Un pipeline **ETL** que se conecta a una API pública, transforma los datos
y produce un dataset analítico listo para usar.

```
   API datos.gob.ar          data/raw/*.json         data/processed/
   (INDEC, 8 llamadas)  -->  (crudo, sin tocar) -->  exportaciones_nea.csv
                                                     resumen.json
        EXTRACT                  TRANSFORM              CHEQUEAR + LOAD
```

**Los datos:** exportaciones de Chaco, Corrientes, Formosa y Misiones por
país de destino y por rubro, 1993–2024, en millones de dólares.
Fuente: INDEC vía la [API de Series de Tiempo](https://apis.datos.gob.ar/series/api/)
de datos.gob.ar (datasets 357.1 y 350.1).

**El resultado esperado:** un CSV de **1.408 filas × 13 columnas**.

Ese CSV no se termina acá: lo vas a volver a usar en el módulo de
**estadística descriptiva**. Por eso importa que quede bien.

---

## Instalación

Necesitás **Python 3.8 o superior**. Nada más: el proyecto usa solo la
biblioteca estándar.

En la **terminal de VS Code**, parado en la carpeta del proyecto:

```bash
python --version          # verificá que sea 3.8+
python src/main.py        # corré el pipeline
```

La primera corrida descarga los datos de la API (necesitás internet) y los
deja en `data/raw/`. A partir de ahí podés trabajar sin conexión:

```bash
python src/main.py --sin-internet    # reutiliza lo que ya bajaste
```

Correr los tests:

```bash
python tests/test_transform.py
```

---

## Estructura del proyecto

```
├── config.py              Configuración: IDs de series, rutas, mapeos.
│                          El código dice CÓMO; esto dice CON QUÉ.
├── src/
│   ├── extract.py         [RESUELTO]  Descarga de la API -> data/raw/
│   ├── transform.py       [TU TRABAJO] TODOs 1 a 8
│   ├── load.py            [PARCIAL]    TODOs 9 a 12
│   └── main.py            [RESUELTO]  Orquesta E -> T -> L
├── tests/
│   └── test_transform.py  17 tests que definen qué se espera de vos
│                          (+ 2 en blanco para que escribas vos)
├── data/
│   ├── raw/               Datos crudos (no se versionan)
│   └── processed/         Salidas finales (no se versionan)
└── logs/                  Historial de corridas
```

---

## Lo que tenés que completar

Hay **13 TODOs**. Hacelos **en orden**: cada uno se apoya en el anterior.
Después de cada uno, corré los tests para ver si vas bien.

### `src/transform.py` — el corazón del TP

| TODO | Función | Qué aplica de la cursada |
|:---:|---|---|
| 1 | `ancho_a_largo()` | Bucles anidados sobre listas y diccionarios |
| 2 | `clasificar_region()` | Diccionario de mapeo + `.get()` con default |
| 3 | `calcular_decada()` | División entera `//` y f-strings |
| 4 | `calcular_participacion()` | Función con `return` + evitar división por cero |
| 5 | `calcular_variacion()` | Función con `return` + manejo de `None` |
| 6 | `agregar_variacion_interanual()` | Diccionario como índice de búsqueda |
| 7 | `agregar_ranking()` | `sorted()`, `enumerate()`, booleanos |
| 8 | `construir_indice_rubros()` y `unir_con_rubros()` | JOIN por clave compuesta |

### `src/load.py` — validar y guardar

| TODO | Función | Qué aplica |
|:---:|---|---|
| 9 | `chequear_unicidad()` | Sets para detectar duplicados |
| 10 | `chequear_rangos()` | Comprensión de listas con filtro |
| 11 | `construir_resumen()` | Diccionarios anidados, `min`/`max`/`sum` |
| 12 | `guardar_resumen()` y `escribir_log_corrida()` | `json.dump`, modos `"w"` vs `"a"` |

### `tests/test_transform.py`

| TODO | Qué hacer |
|:---:|---|
| 13 | **(Bonus)** Escribí dos tests propios |

---

## El dataset que tenés que producir

`data/processed/exportaciones_nea.csv` — **13 columnas, en este orden exacto**:

| # | Columna | Tipo | Descripción |
|:---:|---|---|---|
| 1 | `anio` | int | Año de la observación (1993–2024) |
| 2 | `provincia` | str | Chaco, Corrientes, Formosa o Misiones |
| 3 | `destino` | str | País de destino (o "Resto") |
| 4 | `region_destino` | str | Región geoeconómica del destino |
| 5 | `valor_musd` | float | Exportado a ese destino, en millones de USD |
| 6 | `total_provincia_musd` | float | Total exportado por la provincia ese año |
| 7 | `participacion_pct` | float | `valor / total * 100` |
| 8 | `var_interanual_pct` | float | Variación vs. el año anterior (nulo el 1er año) |
| 9 | `decada` | str | 1990s, 2000s, 2010s o 2020s |
| 10 | `ranking_destino` | int | Posición del destino ese año (1 = el mayor) |
| 11 | `es_top3` | bool | Si está entre los 3 principales |
| 12 | `rubro_principal` | str | Rubro más exportado ese año (del join) |
| 13 | `pp_participacion_pct` | float | % de productos primarios ese año (del join) |

Dos filas de ejemplo (valores reales de la API):

```csv
anio,provincia,destino,region_destino,valor_musd,total_provincia_musd,participacion_pct,var_interanual_pct,decada,ranking_destino,es_top3,rubro_principal,pp_participacion_pct
2024,Chaco,China,Asia,110.93,401.74,27.61,46.36,2020s,1,True,Productos primarios,81.3
2024,Chaco,Brasil,Mercosur,18.12,401.74,4.51,30.45,2020s,6,False,Productos primarios,81.3
```

---

## Cómo saber si terminaste

1. `python tests/test_transform.py` → los 17 tests en verde
   (los 2 del TODO 13 quedan en *skipped* hasta que los escribas).
2. `python src/main.py` → corre sin errores de punta a punta.
3. `data/processed/exportaciones_nea.csv` existe y tiene **1.408 filas**
   (más la de encabezado) y **13 columnas**.
4. `data/processed/resumen.json` y `logs/pipeline.log` existen.
5. Corré el pipeline **dos veces**: el CSV tiene que quedar igual
   (idempotencia) y el log tiene que tener **dos** líneas.

Para contar las filas rápido:

```bash
wc -l data/processed/exportaciones_nea.csv     # debería dar 1409
```

---

## Consejos

- **Leé los contratos.** Cada función tiene un docstring que dice qué
  recibe y qué devuelve. El resto del pipeline cuenta con eso.
- **Un TODO por vez.** Implementá, corré los tests, y recién ahí seguí.
- **Los errores son información.** Leé el traceback de abajo hacia arriba:
  la última línea dice qué pasó, las de arriba dónde.
- **No toques `COLUMNAS`** en `transform.py`: es el contrato de salida.
- **Commiteá seguido.** Un commit por TODO resuelto es un buen ritmo, y
  se evalúa. `version_final_v3_DEFINITIVA.py` no es control de versiones.
- **Si algo del enunciado no se entiende, preguntá** en el foro de la
  materia antes de asumir.

---

## Entrega

1. Creá tu **propio repositorio** en GitHub con este proyecto.
2. Completá los TODOs, commiteando a medida que avanzás.
3. Actualizá este README: sacá las secciones de TODOs y contá **vos** qué
   hace tu pipeline, cómo se corre y qué encontraste en los datos.
4. Entregá el **link a tu repositorio**.

La guía paso a paso está en `docs/guia-git.md`, dentro de la carpeta
`tp-final/` del repositorio de la materia.

---

*Fuente de datos: INDEC, vía el portal de datos abiertos del Estado
argentino (datos.gob.ar). IDs de series verificados el 2026-08-02.*



# TP Final — Pipeline ETL de Exportaciones del NEA

**Diplomatura en Data Analytics e IA Aplicada — UNNE / Extender**
**Unidad II — Fundamentos de la Programación**

---

## 📌 Descripción del proyecto

Este proyecto implementa un **pipeline ETL (Extract, Transform, Load)** para obtener, transformar, validar y almacenar información sobre las exportaciones de las provincias del **NEA argentino**.

El pipeline utiliza datos públicos provenientes de la **API de Series de Tiempo de datos.gob.ar / INDEC** y genera un dataset analítico con información de:

* Chaco
* Corrientes
* Formosa
* Misiones

El período analizado comprende los años **1993 a 2024** y la unidad de medida es **millones de dólares FOB (MUSD)**.

El resultado final permite analizar la evolución de las exportaciones por provincia y destino, incorporando indicadores derivados para facilitar posteriores análisis y visualizaciones.

---

## 🎯 Objetivo

Construir un proceso automatizado que permita:

1. Extraer datos desde una API pública.
2. Guardar los datos originales en formato JSON.
3. Transformar los datos desde un formato ancho a uno analítico.
4. Estandarizar regiones y categorías.
5. Calcular indicadores derivados.
6. Integrar información de exportaciones por rubro.
7. Validar la calidad del dataset.
8. Generar archivos finales en formatos CSV y JSON.
9. Registrar cada ejecución del pipeline mediante un archivo de log.

---

## 🔄 Arquitectura del pipeline

El proyecto está organizado en tres etapas principales:

```text
              API datos.gob.ar / INDEC
                       │
                       ▼
                 ┌───────────┐
                 │  EXTRACT  │
                 │           │
                 │ src/      │
                 │ extract.py│
                 └─────┬─────┘
                       │
                       ▼
                  data/raw/
                       │
                       ▼
                 ┌───────────┐
                 │ TRANSFORM │
                 │           │
                 │ src/      │
                 │transform.py
                 └─────┬─────┘
                       │
                       ▼
              Dataset analítico
                       │
                       ▼
                 ┌───────────┐
                 │   LOAD    │
                 │           │
                 │ src/      │
                 │  load.py  │
                 └─────┬─────┘
                       │
              ┌────────┼─────────┐
              ▼        ▼         ▼
             CSV      JSON      LOG
```

La ejecución completa se realiza desde:

```bash
python src/main.py
```

---

## 📁 Estructura del proyecto

```text
tp-final-etl/
│
├── data/
│   ├── raw/
│   │   └── Datos originales descargados desde la API
│   │
│   └── processed/
│       ├── exportaciones_nea.csv
│       └── resumen.json
│
├── logs/
│   └── pipeline.log
│
├── src/
│   ├── config.py
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── main.py
│
├── tests/
│   └── test_transform.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 📊 Fuente de datos

Los datos se obtienen de la **API de Series de Tiempo de datos.gob.ar**, utilizando información del **INDEC** sobre exportaciones provinciales.

Se utilizan dos conjuntos de información:

### Exportaciones por provincia y país de destino

Permite obtener el valor de las exportaciones de cada provincia hacia diferentes destinos.

### Exportaciones por provincia y rubro

Permite identificar el rubro principal de exportación y calcular la participación de los **Productos primarios** sobre el total correspondiente a cada provincia y año.

---

## 🗺️ Cobertura del dataset

| Característica    | Valor                                 |
| ----------------- | ------------------------------------- |
| Provincias        | Chaco, Corrientes, Formosa y Misiones |
| Período           | 1993–2024                             |
| Años              | 32                                    |
| Unidad            | Millones de dólares FOB               |
| Destinos          | 11 categorías                         |
| Registros finales | 1.408                                 |
| Columnas finales  | 13                                    |

La estructura esperada surge de:

```text
4 provincias × 11 destinos × 32 años = 1.408 registros
```

---

## 🔧 Etapa 1 — Extract

El módulo `src/extract.py` se encarga de:

* Conectarse a la API.
* Descargar los datos correspondientes a las provincias.
* Obtener información por destino y por rubro.
* Manejar errores de conexión o ausencia de datos.
* Guardar los datos originales en `data/raw/`.

Para cada provincia se descargan:

* 12 series relacionadas con destinos.
* 4 series relacionadas con rubros.

En total:

```text
4 provincias × 2 tipos de información = 8 descargas
```

La ejecución final confirmó:

```text
EXTRACT OK: 8 de 8 descargas
```

---

## 🔄 Etapa 2 — Transform

El módulo `src/transform.py` realiza las principales transformaciones del proyecto.

### Conversión de formato ancho a largo

Los datos originales se encuentran en formato ancho.

Se transforman a una estructura donde cada registro representa:

```text
Año + Provincia + Destino + Valor
```

Los registros correspondientes al total (`__TOTAL__`) no se consideran destinos.

El total provincial se conserva para utilizarlo posteriormente en los cálculos.

---

### Clasificación regional

Cada destino se asigna a una región utilizando la configuración definida en `config.py`.

Ejemplos:

| Destino        | Región            |
| -------------- | ----------------- |
| Brasil         | Mercosur          |
| Paraguay       | Mercosur          |
| China          | Asia              |
| Estados Unidos | América del Norte |
| España         | Europa            |
| Resto          | Otros             |

Los destinos que no poseen una clasificación específica utilizan la región definida como predeterminada.

---

### Cálculo de década

A partir del año se genera la columna:

```text
decada
```

Ejemplos:

```text
1993 → 1990s
2007 → 2000s
2024 → 2020s
```

---

### Participación sobre el total provincial

Se calcula qué porcentaje representa cada destino sobre el total de exportaciones de la provincia:

```text
participacion_pct =
(valor_musd / total_provincia_musd) × 100
```

Se contempla el caso de valores nulos o de un total igual a cero para evitar divisiones inválidas.

---

### Variación interanual

Se calcula la variación porcentual respecto del año anterior para cada combinación de:

```text
Provincia + Destino
```

La fórmula utilizada es:

```text
((valor_actual - valor_anterior) / valor_anterior) × 100
```

Cuando no existe un año anterior o el valor anterior es cero, la variación no se calcula.

---

### Ranking de destinos

Los destinos se ordenan según su valor de exportación para cada:

```text
Provincia + Año
```

Se genera:

```text
ranking_destino
```

También se genera:

```text
es_top3
```

que indica si el destino se encuentra entre los tres primeros.

---

### Integración de información por rubro

La información de exportaciones por rubro se transforma en un índice por:

```text
Provincia + Año
```

A partir de este índice se obtiene:

* `rubro_principal`
* `pp_participacion_pct`

`rubro_principal` identifica el rubro con mayor participación.

`pp_participacion_pct` representa la participación de **Productos primarios** en el total de exportaciones de la provincia y año correspondiente.

---

## 📋 Dataset final

El archivo generado es:

```text
data/processed/exportaciones_nea.csv
```

Contiene las siguientes 13 columnas:

| Columna                | Descripción                                         |
| ---------------------- | --------------------------------------------------- |
| `anio`                 | Año de la exportación                               |
| `provincia`            | Provincia del NEA                                   |
| `destino`              | País o categoría de destino                         |
| `region_destino`       | Región a la que pertenece el destino                |
| `valor_musd`           | Valor exportado en millones de dólares FOB          |
| `total_provincia_musd` | Total de exportaciones de la provincia              |
| `participacion_pct`    | Participación del destino sobre el total provincial |
| `var_interanual_pct`   | Variación porcentual respecto del año anterior      |
| `decada`               | Década correspondiente al año                       |
| `ranking_destino`      | Posición del destino dentro de la provincia y año   |
| `es_top3`              | Indica si el destino pertenece al Top 3             |
| `rubro_principal`      | Principal rubro de exportación                      |
| `pp_participacion_pct` | Participación de Productos primarios                |

---

## 🧪 Etapa 3 — Load y controles de calidad

El módulo `src/load.py` valida el dataset antes de guardarlo.

Se implementaron controles para:

### 1. Cantidad de registros

Se verifica que el dataset tenga como mínimo la cantidad de filas esperada.

Resultado final:

```text
1408 filas
```

---

### 2. Estructura de columnas

Se verifica que estén presentes las 13 columnas definidas por el contrato de salida.

Resultado:

```text
13 columnas correctas
```

---

### 3. Unicidad

Se verifica que no existan registros duplicados para la combinación de:

```text
Provincia + Año + Destino
```

Resultado:

```text
1408 claves únicas
```

---

### 4. Rangos

Se controlan valores fuera de rangos razonables.

Resultado:

```text
0 valores fuera de rango
```

---

### 5. Cobertura

También se verifica la presencia de datos necesarios para los cálculos derivados.

En la ejecución final:

```text
91 filas sin variación interanual
```

Esto es esperable porque corresponden a los primeros registros de cada serie, donde no existe un año anterior para realizar la comparación.

No se detectaron filas sin información de rubro.

---

## 📈 Resultados de la ejecución

La ejecución final del pipeline produjo:

```text
TRANSFORM OK: 1408 filas x 13 columnas

LOAD:
check OK | cantidad: 1408 filas
check OK | columnas: las 13 del contrato
check OK | unicidad: 1408 claves únicas
check OK | rangos: 0 valores fuera de rango
check OK | cobertura: 0 sin rubro
```

El dataset generado presenta:

```text
Valor mínimo: 0,00 MUSD
Valor máximo: 399,14 MUSD
Promedio:     20,17 MUSD
```

---

## 🔎 Ejemplo de resultado

Para **Chaco — 2024** se obtuvieron, entre otros, los siguientes resultados:

### China

```text
Valor:             110,93 MUSD
Total provincial:  401,74 MUSD
Participación:      27,61 %
Variación anual:    +46,36 %
Ranking:             2
Top 3:              Sí
Región:             Asia
Rubro principal:    Productos primarios
```

### Brasil

```text
Valor:              18,12 MUSD
Total provincial:  401,74 MUSD
Participación:       4,51 %
Variación anual:    +30,45 %
Ranking:             4
Top 3:              No
Región:             Mercosur
Rubro principal:    Productos primarios
```

Estos indicadores permiten analizar no solamente cuánto exporta cada provincia, sino también **hacia dónde exporta, qué importancia tiene cada destino y cómo evoluciona en el tiempo**.

---

## 🧪 Tests

El proyecto incluye pruebas automatizadas en:

```text
tests/test_transform.py
```

La ejecución se realiza mediante:

```bash
python tests/test_transform.py
```

Resultado final:

```text
Ran 19 tests

OK (skipped=2)
```

Se obtuvieron:

* **17 tests aprobados**
* **2 tests opcionales omitidos**

Los tests cubren, entre otros aspectos:

* Conversión de formato.
* Exclusión del total como destino.
* Tratamiento de faltantes.
* Conservación del total provincial.
* Clasificación regional.
* Cálculo de década.
* Participación porcentual.
* Variación interanual.
* Ranking.
* Identificación del Top 3.
* Integración de información por rubro.

---

## ▶️ Ejecución

Para ejecutar el pipeline completo:

```bash
python src/main.py
```

Para ejecutar las pruebas:

```bash
python tests/test_transform.py
```

El pipeline genera automáticamente:

```text
data/processed/exportaciones_nea.csv
data/processed/resumen.json
logs/pipeline.log
```

---

## 📄 Resumen JSON

Además del CSV, se genera:

```text
data/processed/resumen.json
```

Este archivo contiene información resumida de la ejecución:

* Dataset.
* Fuente.
* Unidad de medida.
* Fecha de generación.
* Cantidad de filas.
* Cantidad de columnas.
* Período.
* Provincias.
* Estadísticas del valor exportado.
* Resultado de los controles de calidad.

---

## 📝 Registro de ejecuciones

Cada ejecución queda registrada en:

```text
logs/pipeline.log
```

Se comprobó la ejecución del pipeline dos veces de manera exitosa, quedando registradas ambas corridas.

---

## ⚙️ Configuración

Los parámetros generales del proyecto se encuentran centralizados en:

```text
src/config.py
```

Entre ellos:

* URL base de la API.
* Tiempo máximo de espera.
* Directorios.
* Nombres de archivos de salida.
* Regiones.
* Cantidad de destinos para el Top N.
* Período analizado.
* Cantidad mínima esperada de registros.
* Rangos razonables de valores.

Esto permite separar la configuración de la lógica del pipeline y facilita futuras modificaciones.

---

## 🛡️ Manejo de errores

El proyecto contempla situaciones como:

* Falta de datos.
* Errores de conexión con la API.
* Valores nulos.
* División por cero.
* Datos fuera de rangos razonables.
* Registros duplicados.
* Estructura incorrecta del dataset.

Los controles críticos detienen el proceso cuando se detecta una condición que compromete la calidad del resultado.

---
Nota sobre el ranking: el ranking se calcula ordenando los destinos por valor exportado de mayor a menor dentro de cada provincia y año, según la lógica definida en los tests. En el ejemplo de referencia de la consigna se muestran valores de ranking que no coinciden con ese criterio para Chaco 2024; el pipeline mantiene el criterio definido por la función y validado por test_ranking_por_provincia_y_anio.


## 💡 Posibles usos del dataset

El dataset final puede utilizarse como base para análisis y visualizaciones sobre:

* Evolución de las exportaciones del NEA.
* Comparación entre provincias.
* Principales destinos de exportación.
* Participación de cada destino.
* Evolución interanual.
* Ranking de destinos.
* Identificación de destinos Top 3.
* Distribución regional de los destinos.
* Importancia de los Productos primarios.
* Análisis histórico por década.

---

## 👩‍💻 Autora

**Liliana Yamus**

Diplomatura en Data Analytics e IA Aplicada
UNNE / Extender

Proyecto Final — Unidad II: Fundamentos de la Programación
