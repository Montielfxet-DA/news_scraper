# 🗄️ SISTEMA DE BASE DE DATOS Y ETIQUETADO

## 🎯 ¿Qué hace este sistema?

**Cada vez que analizas noticias**, el sistema AUTOMÁTICAMENTE:
1. ✅ Guarda TODAS las noticias en una base de datos SQLite
2. ✅ Registra el score del filtro automático
3. ✅ Almacena el análisis de impacto
4. ✅ Deja espacio para tu etiqueta manual

**Con el tiempo**, tendrás:
- 📊 Histórico completo de noticias analizadas
- 🎓 Dataset para entrenar Machine Learning
- 📈 Métricas de precisión del filtro automático

---

## 📁 Archivos Nuevos

### 1. `news_database.py` - Sistema de Base de Datos
Base de datos SQLite que almacena:
- Todas las noticias analizadas
- Scores del filtro automático
- Análisis de impacto
- Etiquetas manuales (cuando las agregues)

### 2. `etiquetador_noticias.py` - Interfaz de Etiquetado
Herramienta para etiquetar noticias manualmente:
- Muestra noticias una por una
- Tú decides: Relevante (1) o No Relevante (0)
- Guarda tus decisiones en la BD
- Genera dataset para ML

### 3. `steel_impact_system_REAL.py` - ACTUALIZADO
Ahora guarda automáticamente en la base de datos.

---

## 🚀 FLUJO DE TRABAJO COMPLETO

### PASO 1: Analizar Noticias (Como siempre)
```bash
python steel_impact_system_REAL.py
```

**Ahora también hace:**
```
✓ 15 noticias analizadas y guardadas en base de datos

📊 ESTADÍSTICAS DE LA BASE DE DATOS
   Total en BD: 15 noticias
   Etiquetadas manualmente: 0
   Pendientes de etiquetar: 15

💡 PRÓXIMO PASO:
   Ejecuta: python etiquetador_noticias.py
```

---

### PASO 2: Etiquetar Noticias Manualmente
```bash
python etiquetador_noticias.py
```

**Te mostrará cada noticia así:**
```
================================================================================
📰 ETIQUETADO DE NOTICIAS (1/15)
================================================================================

🆔 ID: 1
📅 Fecha: 2026-02-05
📍 Fuente: Google News

📌 TÍTULO:
--------------------------------------------------------------------------------
Ternium anuncia inversión de $500 millones en planta de Monterrey
--------------------------------------------------------------------------------

📄 CONTENIDO:
--------------------------------------------------------------------------------
La empresa siderúrgica Ternium anunció una inversión de 500 millones
de dólares para expandir su planta en Monterrey, México...
--------------------------------------------------------------------------------

🤖 CLASIFICACIÓN AUTOMÁTICA:
   Score: 23
   Decisión: RELEVANTE

================================================================================

¿Esta noticia es RELEVANTE para la industria del acero en México?

  [1] ✅ SÍ - Relevante
  [0] ❌ NO - No relevante
  [s] ⏭️  Saltar (etiquetar después)
  [q] 🚪 Salir del etiquetador
  [i] ℹ️  Ver más información

Tu respuesta: _
```

**Tú escribes `1` (relevante) o `0` (no relevante)**

---

### PASO 3: Ver Estadísticas
```bash
python etiquetador_noticias.py --stats
```

```
================================================================================
📊 ESTADÍSTICAS DE LA BASE DE DATOS
================================================================================

📰 NOTICIAS TOTALES: 45
   • Etiquetadas manualmente: 25
   • Pendientes de etiquetar: 20

✅ ETIQUETAS MANUALES:
   • Relevantes: 18
   • No relevantes: 7
   • Balance: 72.0% relevantes

🤖 CLASIFICACIÓN AUTOMÁTICA:
   • Relevantes: 30
   • No relevantes: 10
   • Inciertos: 5

📈 PRECISIÓN DEL FILTRO: 84.0%

💡 PROGRESO: 25/100 noticias etiquetadas.
   Necesitas 75 más para entrenar ML.
================================================================================
```

---

### PASO 4: Exportar para ML (Cuando tengas 100+)
```bash
python etiquetador_noticias.py --export
```

```
✅ Dataset exportado a dataset_ml.csv
   Total: 125 noticias
   Relevantes: 89
   No relevantes: 36
```

---

## 📊 ESTRUCTURA DE LA BASE DE DATOS

### Tabla: `noticias`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER | ID único |
| `titulo` | TEXT | Título de la noticia |
| `contenido` | TEXT | Contenido completo |
| `url` | TEXT | URL original |
| `fuente` | TEXT | Fuente (Google News, etc.) |
| `fecha_publicacion` | DATETIME | Fecha de publicación |
| `fecha_analisis` | DATETIME | Cuando fue analizada |
| **`relevancia_score`** | INTEGER | Score del filtro (ej: 15) |
| **`relevancia_auto`** | TEXT | 'relevante', 'irrelevante', 'incierto' |
| `categorias_detectadas` | JSON | Categorías encontradas |
| `entidades_detectadas` | JSON | Empresas, lugares, etc. |
| `score_impacto` | REAL | Score de impacto (-1 a 1) |
| `sentimiento` | TEXT | positivo/negativo/neutral |
| `magnitud` | TEXT | muy_alto/alto/medio/bajo |
| `impacto_indicadores` | JSON | Impacto en producción, etc. |
| **`etiqueta_manual`** | INTEGER | NULL, 0 (no), 1 (sí) |
| `etiqueta_fecha` | DATETIME | Cuando etiquetaste |
| `etiqueta_usuario` | TEXT | Quién etiquetó |

---

## 🎓 ETIQUETADO: GUÍA RÁPIDA

### ✅ MARCA COMO RELEVANTE (1) SI:
- Habla de producción/venta de acero
- Menciona empresas del sector
- Trata sobre políticas que afectan la industria
- Incluye datos económicos del sector
- Impacta a México

### ❌ MARCA COMO NO RELEVANTE (0) SI:
- Usa "acero" como metáfora ("nervios de acero")
- Es de otro sector (deportes, entretenimiento)
- No menciona México
- Habla de productos de consumo (sartenes)

---

## 🔧 COMANDOS ÚTILES

### Ver estadísticas:
```bash
python etiquetador_noticias.py --stats
```

### Etiquetar hasta 20 noticias:
```bash
python etiquetador_noticias.py --max 20
```

### Exportar dataset:
```bash
python etiquetador_noticias.py --export
```

### Ver estadísticas desde Python:
```python
from news_database import mostrar_estadisticas
mostrar_estadisticas()
```

---

## 📈 PROGRESO HACIA ML

| Etiquetadas | Estado | Siguiente Paso |
|-------------|--------|----------------|
| **0-49** | 🌱 Iniciando | Sigue etiquetando |
| **50-99** | 💪 Progreso | Ya casi puedes entrenar |
| **100-199** | ✅ Listo | ¡Entrena modelo básico! |
| **200-499** | 🚀 Excelente | Entrena modelo robusto |
| **500+** | 🏆 Óptimo | Prueba BERT/Transformers |

---

## 🤖 ENTRENAR ML (Cuando tengas 100+)

```bash
# Exportar datos
python etiquetador_noticias.py --export

# Entrenar modelo (próximo archivo a crear)
python train_ml_classifier.py

# El modelo aprenderá de tus etiquetas y mejorará
# la clasificación automática
```

---

## 💡 CONSEJOS

### 1. **Sesiones cortas**
Etiqueta 10-20 noticias por sesión para no cansarte.

### 2. **Consistencia**
Mantén el mismo criterio. Si tienes duda, usa la ayuda (`i`).

### 3. **Balance**
Intenta que ~50% sean relevantes y ~50% no relevantes.

### 4. **Revisar rechazadas**
Revisa `noticias_rechazadas.json` para mejorar el filtro.

### 5. **Frecuencia**
Ejecuta el sistema 2-3 veces por semana para acumular datos.

---

## 🗃️ UBICACIÓN DE LA BASE DE DATOS

```
tu_carpeta/
├── noticias_database.db       ← Aquí se guarda TODO
├── etiquetador_noticias.py    ← Interfaz de etiquetado
├── news_database.py            ← Sistema de BD
└── steel_impact_system_REAL.py ← Sistema principal
```

**IMPORTANTE:** 
- La BD es un archivo `.db` que puedes respaldar
- Se puede abrir con herramientas como DB Browser for SQLite
- Nunca borres este archivo o perderás todo el progreso

---

## 🔄 FLUJO AUTOMÁTICO SUGERIDO

### Diario/Semanal:
```bash
# 1. Recolectar y analizar noticias
python steel_impact_system_REAL.py

# 2. Etiquetar 10-20 noticias
python etiquetador_noticias.py --max 20

# 3. Ver progreso
python etiquetador_noticias.py --stats
```

### Cada 2-3 semanas (cuando tengas 100+):
```bash
# Exportar y entrenar modelo
python etiquetador_noticias.py --export
python train_ml_classifier.py
```

---

## ⚠️ SOLUCIÓN DE PROBLEMAS

### Error: "database is locked"
Cierra otros programas que puedan estar usando la BD.

### Error: "table noticias already exists"
Normal, la BD ya existe. El sistema la reutiliza.

### Perder progreso de etiquetado
Haz backup del archivo `noticias_database.db` regularmente.

### Ver qué hay en la BD
Usa DB Browser for SQLite (gratis): https://sqlitebrowser.org/

---

## 📊 PRÓXIMOS ARCHIVOS QUE CREARÉ

Una vez que tengas 100+ noticias etiquetadas:

1. **`train_ml_classifier.py`**
   - Entrena modelo de ML
   - Evalúa precisión
   - Guarda modelo entrenado

2. **`ml_filter.py`**
   - Usa modelo entrenado en producción
   - Combina con filtro de reglas
   - Mejor precisión

3. **`dashboard.py`** (opcional)
   - Visualiza estadísticas
   - Gráficas de progreso
   - Interface web con Streamlit

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [x] Base de datos creada (`news_database.py`)
- [x] Sistema guarda automáticamente
- [x] Interfaz de etiquetado lista
- [x] Estadísticas funcionando
- [ ] Etiquetar primeras 100 noticias (tu trabajo)
- [ ] Entrenar primer modelo ML (cuando tengas 100+)
- [ ] Integrar ML al sistema (Fase 3)

---

## 🎯 OBJETIVO FINAL

**En 2-4 semanas:**
- 200+ noticias etiquetadas
- Modelo ML entrenado
- Precisión >85% automática
- Sistema autónomo funcionando

**Beneficio:**
- Ya no necesitas etiquetar manualmente
- El sistema aprende continuamente
- Filtrado inteligente automático

---

¿Preguntas? ¿Listo para empezar a etiquetar? 🚀
