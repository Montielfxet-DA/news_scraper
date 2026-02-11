# 🤖 PLAN PARA MACHINE LEARNING - FASE 2
## Sistema de Clasificación Inteligente de Noticias

---

## 📋 OBJETIVO

Entrenar un modelo de Machine Learning que **aprenda automáticamente** a identificar noticias relevantes basándose en ejemplos que tú etiquetes manualmente.

### ¿Por qué necesitamos ML?

El filtro actual (Fase 1) funciona con **reglas fijas**:
- ✅ Bueno: Fácil de entender y ajustar
- ❌ Limitado: Solo detecta lo que programamos explícitamente
- ❌ No aprende: Requiere ajustes manuales constantes

El ML puede:
- ✅ **Aprender patrones** que no vimos
- ✅ **Mejorar con el tiempo** conforme procesa más noticias
- ✅ **Capturar matices** complejos del lenguaje
- ✅ **Adaptarse** a cambios en cómo se escriben las noticias

---

## 🗺️ ROADMAP COMPLETO

### FASE 2A: Recolección de Datos (2-3 semanas)
**Objetivo:** Obtener 200-500 noticias etiquetadas manualmente

### FASE 2B: Feature Engineering (1 semana)
**Objetivo:** Convertir texto en variables que el modelo pueda procesar

### FASE 2C: Entrenamiento de Modelos (1-2 semanas)
**Objetivo:** Probar diferentes algoritmos y elegir el mejor

### FASE 2D: Evaluación y Deploy (1 semana)
**Objetivo:** Validar performance y poner en producción

---

## 📊 FASE 2A: RECOLECCIÓN Y ETIQUETADO DE DATOS

### Paso 1: Herramienta de Etiquetado

Voy a crear una interfaz simple para que etiquetes noticias:

```python
# etiquetador.py
# Lee noticias del sistema
# Te las muestra una por una
# Tú decides: Relevante (1) o No Relevante (0)
# Guarda el resultado en CSV
```

### Paso 2: ¿Cuántas noticias necesitas etiquetar?

| Objetivo | Noticias Mínimas | Recomendado | Tiempo Estimado |
|----------|------------------|-------------|-----------------|
| **Prototipo** | 100 | 150 | 2-3 horas |
| **Producción básica** | 200 | 300 | 4-6 horas |
| **Alta precisión** | 500 | 1000 | 10-15 horas |

### Paso 3: Distribución Ideal

- **50% Relevantes** (mitad sí)
- **50% No Relevantes** (mitad no)

Importante: Si tienes 80% relevantes y 20% no relevantes, el modelo aprenderá mal.

### Paso 4: Tips para Etiquetar

**✅ RELEVANTE si:**
- Habla directamente de producción/venta de acero
- Menciona empresas del sector
- Trata sobre políticas que afectan la industria
- Incluye datos económicos del sector
- Afecta directamente a México

**❌ NO RELEVANTE si:**
- Usa "acero" como metáfora
- Es de otro sector (deportes, entretenimiento)
- No menciona México o empresas mexicanas
- Es sobre productos de consumo (sartenes, etc.)

---

## 🔧 FASE 2B: FEATURE ENGINEERING

### ¿Qué son "features"?

Son variables numéricas que representan el texto. El ML no puede leer texto directamente, necesita números.

### Features que extraeremos:

#### 1. **TF-IDF (Term Frequency - Inverse Document Frequency)**
Importancia de cada palabra en el documento.

```python
from sklearn.feature_extraction.text import TfidfVectorizer

# Ejemplo
texts = ["acero ternium méxico", "futbol gol partido"]
vectorizer = TfidfVectorizer(max_features=100)
X = vectorizer.fit_transform(texts)
# Resultado: matriz de números representando cada texto
```

#### 2. **Features Estructurales**
- Longitud del título
- Longitud del contenido
- Número de números/porcentajes
- Tiene URL de empresa
- Día de la semana publicado

#### 3. **Named Entities**
- ¿Menciona empresas del sector? (1/0)
- ¿Menciona México? (1/0)
- ¿Menciona cifras? (1/0)
- Número de entidades detectadas

#### 4. **Keywords del Filtro Actual**
- Score del filtro de reglas
- Puntos de sector
- Puntos de México
- Puntos de exclusión

---

## 🧠 FASE 2C: MODELOS A PROBAR

### 1. **Logistic Regression** (Baseline simple)
```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression()
model.fit(X_train, y_train)
```

**Ventajas:**
- Muy rápido
- Fácil de interpretar
- Funciona bien con texto

**Desventajas:**
- Modelo simple
- No captura patrones muy complejos

**Precisión esperada:** 75-80%

---

### 2. **Random Forest** (Ensemble poderoso)
```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)
```

**Ventajas:**
- Maneja bien features mixtos
- Resistente a overfitting
- Puede mostrar importancia de features

**Desventajas:**
- Más lento que Logistic Regression
- Requiere más datos

**Precisión esperada:** 80-85%

---

### 3. **Gradient Boosting (XGBoost/LightGBM)** (Estado del arte)
```python
from xgboost import XGBClassifier

model = XGBClassifier()
model.fit(X_train, y_train)
```

**Ventajas:**
- Mejor performance general
- Maneja bien desbalance de clases
- Optimización avanzada

**Desventajas:**
- Más complejo de tunear
- Puede hacer overfitting

**Precisión esperada:** 85-90%

---

### 4. **BERT (Transformers)** (Deep Learning - Opcional)
```python
from transformers import BertTokenizer, BertForSequenceClassification

# Usar modelo pre-entrenado en español
model_name = 'dccuchile/bert-base-spanish-wwm-uncased'
```

**Ventajas:**
- Estado del arte en NLP
- Entiende contexto profundo
- Mejor con textos complejos

**Desventajas:**
- Requiere GPU
- Mucho más lento
- Necesita más datos (500+)
- Más difícil de debuggear

**Precisión esperada:** 88-95%

**Recomendación:** Solo si tienes 500+ noticias etiquetadas y GPU disponible.

---

## 📈 FASE 2D: EVALUACIÓN

### Métricas Clave

#### 1. **Accuracy (Precisión General)**
```
Accuracy = (Correctas) / (Total)
```
Objetivo: > 85%

#### 2. **Precision (Precisión de Positivos)**
```
Precision = (Verdaderos Positivos) / (Todos los que predije como Positivos)
```
¿De las que marqué como relevantes, cuántas realmente lo son?

#### 3. **Recall (Exhaustividad)**
```
Recall = (Verdaderos Positivos) / (Todos los Positivos reales)
```
¿De todas las relevantes, cuántas logré encontrar?

#### 4. **F1-Score (Balance)**
```
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```
Objetivo: > 0.80

### Matriz de Confusión

```
                    Predicción
                Relevante  No Relevante
Real Relevante      TP          FN       
     No Relev.      FP          TN
```

**Ideal para este caso:**
- **Alta Precision**: No queremos analizar noticias irrelevantes (desperdicio)
- **Alta Recall**: No queremos perder noticias importantes

---

## 🚀 IMPLEMENTACIÓN PRÁCTICA

### Script de Entrenamiento Completo

```python
# train_classifier.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# 1. Cargar datos etiquetados
df = pd.read_csv('noticias_etiquetadas.csv')
# Columnas: titulo, contenido, relevante (1/0)

# 2. Preparar textos
df['texto_completo'] = df['titulo'] + ' ' + df['contenido']

# 3. Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    df['texto_completo'], 
    df['relevante'],
    test_size=0.2,
    stratify=df['relevante'],  # Mantener proporción
    random_state=42
)

# 4. Vectorizar texto
vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1,2))
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# 5. Entrenar modelo
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_vec, y_train)

# 6. Evaluar
y_pred = model.predict(X_test_vec)
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))

# 7. Guardar modelo
joblib.dump(model, 'modelo_relevancia.pkl')
joblib.dump(vectorizer, 'vectorizador.pkl')

print("✅ Modelo entrenado y guardado")
```

### Usar el Modelo en Producción

```python
# En steel_impact_system_REAL.py

import joblib

# Cargar modelo entrenado
modelo = joblib.load('modelo_relevancia.pkl')
vectorizador = joblib.load('vectorizador.pkl')

def es_relevante_ml(titulo, contenido):
    texto = titulo + ' ' + contenido
    texto_vec = vectorizador.transform([texto])
    prediccion = modelo.predict(texto_vec)[0]
    probabilidad = modelo.predict_proba(texto_vec)[0]
    
    return {
        'relevante': bool(prediccion),
        'confianza': float(probabilidad[1])  # Probabilidad de ser relevante
    }

# Usar
resultado = es_relevante_ml(
    "Ternium invierte en México",
    "La empresa anuncia $500M..."
)
# {'relevante': True, 'confianza': 0.89}
```

---

## 📊 COMPARACIÓN: REGLAS vs ML

| Aspecto | Filtro de Reglas (Actual) | Machine Learning |
|---------|---------------------------|------------------|
| **Setup** | Inmediato | 2-4 semanas |
| **Precisión** | 70-80% | 85-95% |
| **Mantenimiento** | Manual (ajustar reglas) | Automático (re-entrenar) |
| **Explicabilidad** | Total (vemos las reglas) | Parcial (caja negra) |
| **Adaptabilidad** | Baja | Alta |
| **Datos necesarios** | 0 | 200-500 noticias |
| **Tiempo de ejecución** | Muy rápido | Rápido |

---

## 🎯 ESTRATEGIA HÍBRIDA RECOMENDADA

**Mejor de ambos mundos:**

```python
def filtrar_noticia_hibrido(titulo, contenido):
    # 1. Primero filtro de reglas (rápido)
    score_reglas = filtro_reglas(titulo, contenido)
    
    if score_reglas < -10:
        # Muy claramente irrelevante (futbol, cocina, etc)
        return False, "rechazado_por_reglas"
    
    if score_reglas > 15:
        # Muy claramente relevante (empresas, cifras, etc)
        return True, "aceptado_por_reglas"
    
    # 2. Casos ambiguos: usar ML
    resultado_ml = modelo_ml.predict(titulo, contenido)
    
    if resultado_ml['confianza'] > 0.7:
        return resultado_ml['relevante'], "decidido_por_ml"
    
    # 3. Si ML no está seguro, ser conservador
    return score_reglas > 5, "decision_conservadora"
```

**Ventajas:**
- ✅ Casos obvios se resuelven rápido
- ✅ ML solo para casos difíciles
- ✅ Mejor uso de recursos computacionales

---

## 📅 TIMELINE SUGERIDO

### Semana 1-2: Etiquetado
- Etiquetar 50 noticias/día
- Meta: 200+ noticias

### Semana 3: Feature Engineering
- Implementar extracción de features
- Crear dataset de entrenamiento

### Semana 4: Entrenamiento
- Probar 3-4 modelos
- Validar con cross-validation
- Elegir mejor modelo

### Semana 5: Integración
- Integrar modelo al sistema
- Testing en producción
- Monitorear resultados

### Ongoing: Mejora Continua
- Cada mes: etiquetar 50 noticias nuevas
- Cada 3 meses: re-entrenar modelo
- Monitorear drift (cambios en distribución)

---

## 🛠️ HERRAMIENTAS QUE NECESITARÁS

```bash
# Para ML básico
pip install scikit-learn joblib

# Para ML avanzado
pip install xgboost lightgbm

# Para Deep Learning (opcional)
pip install transformers torch

# Para análisis
pip install matplotlib seaborn jupyter
```

---

## 🎓 RECURSOS DE APRENDIZAJE

### Tutoriales Recomendados:
1. **scikit-learn Text Classification**: https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html
2. **TF-IDF explicado**: https://monkeylearn.com/blog/what-is-tf-idf/
3. **BERT en español**: https://github.com/dccuchile/beto

### Cursos (opcionales):
- Coursera: "Machine Learning" by Andrew Ng
- fast.ai: "Practical Deep Learning for Coders"

---

## ✅ CHECKLIST ANTES DE EMPEZAR ML

- [ ] Sistema de reglas funcionando bien
- [ ] Al menos 100 noticias recolectadas
- [ ] Tiempo disponible para etiquetar (5-10 horas)
- [ ] Python y librerías ML instaladas
- [ ] Espacio para experimentar y validar

---

## 🚦 ¿CUÁNDO EMPEZAR CON ML?

### EMPEZAR YA si:
- ✅ Tienes >100 noticias para etiquetar
- ✅ El filtro de reglas rechaza muchas noticias correctas
- ✅ Quieres automatización a largo plazo
- ✅ Tienes tiempo para experimentar

### ESPERAR si:
- ⏸️ El filtro de reglas funciona bien (>85% precisión)
- ⏸️ Tienes <50 noticias
- ⏸️ No tienes tiempo para etiquetar
- ⏸️ El proyecto es de corto plazo

---

## 💬 SIGUIENTE PASO

**Dime cuando estés listo y te crearé:**

1. **etiquetador.py** - Interfaz para etiquetar noticias
2. **train_classifier.py** - Script de entrenamiento
3. **ml_filter.py** - Integración con el sistema

**O primero validamos que el filtro de reglas actual funcione bien para ti.**

---

**¿Preguntas? ¿Empezamos con el etiquetado o ajustamos más el filtro de reglas primero?** 🤔
