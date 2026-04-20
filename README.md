# 🔍 Fuzzy Matching para Cruce de Tablas con Nombres Inconsistentes

Algoritmo en Python que resuelve uno de los problemas más comunes en análisis de datos: cruzar dos tablas cuando los nombres en la tabla de hechos están mal escritos y no generan coincidencias con la tabla de dimensiones.

---

## 🧩 El problema

En un proceso de ventas real, la tabla de hechos (`Ventas.csv`) contenía nombres de empresas con múltiples tipos de errores que impedían hacer un JOIN directo con la tabla de dimensiones (`Vendedores.csv`):

| Tipo de error | Ejemplo en tabla de hechos | Nombre correcto |
|---|---|---|
| Texto invertido | `snoituloS hceT` | `Tech Solutions` |
| Texto invertido con espacios | `hceT neGtxeN` | `NextGen Tech` |
| Error tipográfico | `AI Dvelopments` | `AI Developments` |
| Número por letra | `Inn0vatech` | `Innovatech` |
| Palabras concatenadas | `TechSolutions` | `Tech Solutions` |
| Abreviación | `Tech Solutions Inc` | `Tech Solutions` |
| Mezcla de errores | `AI D3v3lopm3nts` | `AI Developments` |

Un JOIN convencional en SQL o pandas devolvería `NULL` para todos estos registros. Este algoritmo los resuelve todos.

---

## ⚙️ ¿Cómo funciona?

```
Ventas.csv (nombres con errores)
          │
          ▼
    Normalización
  (minúsculas + strip)
          │
          ▼
  ┌───────────────────────────┐
  │   encontrar_mejor_match() │
  │                           │
  │  ① token_sort_ratio       │  ← nombre normal
  │  ② ratio simple           │  ← nombre normal
  │  ③ partial_ratio          │  ← nombre normal
  │  ④ token_sort_ratio       │  ← nombre invertido
  │                           │
  │  Selecciona el mayor score│
  │  Umbral: 60 (normal)      │
  │          40 (invertido)   │
  └───────────────────────────┘
          │
          ▼
  empresa_corregida (columna nueva)
          │
          ▼
  Merge con Vendedores.csv
          │
          ├──→ resultados_cruce.csv      (todos los registros)
          ├──→ registros_sin_cruce.csv   (sin coincidencia)
          └──→ reporte_ventas.pdf        (reporte automático con gráficos)
```

---

## 📁 Estructura del proyecto

```
fuzzy-matching-empresas/
│
├── data/
│   ├── Ventas.csv          # Tabla de hechos (nombres con errores)
│   └── Vendedores.csv      # Tabla de dimensiones (nombres correctos)
│
├── output/                 # Se genera al ejecutar el script
│   ├── resultados_cruce.csv
│   ├── registros_sin_cruce.csv
│   ├── ventas_por_empresa.png
│   ├── ventas_por_vendedor.png
│   └── reporte_ventas.pdf
│
├── Proyecto_Python.py      # Script principal
└── README.md
```

---

## 🚀 Cómo ejecutar

```bash
# 1. Instalar dependencias
pip install pandas thefuzz fpdf matplotlib

# 2. Colocar Ventas.csv y Vendedores.csv en el mismo directorio que el script

# 3. Ejecutar
python Proyecto_Python.py
```

El script genera automáticamente:
- ✅ `resultados_cruce.csv` — tabla final con empresa corregida y vendedor asignado
- ⚠️ `registros_sin_cruce.csv` — registros que no alcanzaron el umbral de confianza
- 📊 `reporte_ventas.pdf` — reporte con tablas y gráficos de ventas por empresa y vendedor

---

## 📦 Dependencias

```
pandas
thefuzz
python-Levenshtein   # opcional, acelera thefuzz significativamente
fpdf
matplotlib
```

---

## 💡 Habilidades demostradas

- Identificación y resolución de problemas de calidad del dato en escenarios reales
- Fuzzy matching con múltiples algoritmos (`token_sort_ratio`, `partial_ratio`, `ratio`)
- Manejo de casos edge: texto invertido, números por letras, concatenaciones
- Lógica de umbrales ajustados por tipo de error para maximizar precisión
- Generación automática de reportes PDF con tablas y gráficos (matplotlib + fpdf)
- Flujo ETL completo: limpieza → cruce → reporte
