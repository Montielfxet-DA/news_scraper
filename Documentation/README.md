# 🏭 Sistema de Análisis de Impacto en la Industria del Acero

Sistema automatizado de análisis de noticias que predice el impacto en indicadores clave de la producción de acero en México mediante NLP y Machine Learning.

## 📋 Descripción del Proyecto

Este sistema utiliza técnicas de **Natural Language Processing (NLP)** y **Text Mining** para:
1. Recolectar noticias sobre la industria del acero en México
2. Analizar sentimiento y extraer información clave (entidades, eventos, magnitudes)
3. Calcular scores de impacto ponderados
4. Estimar cambios en indicadores: producción, exportaciones, precios, empleo
5. Generar reportes automatizados en PDF, Excel y JSON

## 🎯 Componentes del Sistema

### 1. **steel_news_analyzer.py** - Motor de Análisis
Clase `SteelNewsAnalyzer` que incluye:
- ✅ Detección de categorías de eventos (aranceles, subsidios, demanda, etc.)
- ✅ Extracción de entidades (países, empresas, personas, productos)
- ✅ Análisis de sentimiento básico
- ✅ Detección de magnitud de eventos
- ✅ Sistema de ponderación y scoring
- ✅ Estimación de impacto en indicadores

### 2. **steel_impact_system.py** - Sistema Completo
Incluye:
- ✅ Módulo de recolección de noticias (Google News, RSS)
- ✅ Pipeline de análisis automatizado
- ✅ Generación de reportes en PDF y Excel
- ✅ Agregación de métricas

### 3. **analisis_acero_correlacion.py** - Análisis Histórico
- ✅ Análisis de correlación entre búsquedas y producción
- ✅ Visualizaciones profesionales
- ✅ Regresión lineal
- ✅ Reportes en PDF

## 🚀 Instalación

### Requisitos Base
```bash
pip install pandas numpy matplotlib seaborn scipy reportlab openpyxl
```

### Para Scraping de Noticias Reales (Opcional)
```bash
pip install pygooglenews feedparser newspaper3k beautifulsoup4
```

### Para Análisis Avanzado de NLP (Opcional)
```bash
pip install spacy textblob vaderSentiment transformers
python -m spacy download es_core_news_sm  # Modelo de español
```

## 📖 Uso Rápido

### Demo con Noticias de Ejemplo
```bash
python steel_impact_system.py
```

Esto generará:
- `analisis_completo.json` - Datos completos
- `reporte_analisis_acero.pdf` - Reporte ejecutivo
- `reporte_analisis_acero.xlsx` - Excel con detalles

### Análisis de Correlación Histórica
```bash
python analisis_acero_correlacion.py
```

Genera reporte PDF con:
- Matriz de correlaciones
- Series temporales
- Regresión lineal
- 6 visualizaciones profesionales

## 🔧 Uso Programático

### Ejemplo Básico
```python
from steel_news_analyzer import SteelNewsAnalyzer

# Crear analizador
analyzer = SteelNewsAnalyzer()

# Analizar una noticia
analisis = analyzer.analizar_noticia(
    titulo="Gobierno anuncia subsidio para industria del acero",
    contenido="El gobierno federal anunció un paquete de subsidios por $500 millones...",
    fecha=datetime.now()
)

# Ver resultados
print(f"Score de impacto: {analisis['score_impacto']}")
print(f"Sentimiento: {analisis['sentimiento']['clasificacion']}")
print(f"Impacto en producción: {analisis['impacto_indicadores']['produccion']}%")
```

### Recolección Automática de Noticias
```python
from steel_impact_system import NewsCollector

collector = NewsCollector()
noticias = collector.collect_all(dias_atras=7)

# Analizar todas
for noticia in noticias:
    analisis = analyzer.analizar_noticia(
        noticia['titulo'], 
        noticia['contenido']
    )
    print(analisis['score_impacto'])
```

## 📊 Indicadores Estimados

El sistema predice cambios porcentuales en:

| Indicador | Descripción |
|-----------|-------------|
| **Producción** | Toneladas métricas de acero producido |
| **Exportaciones** | Volumen de exportaciones |
| **Precios** | Precio del acero en mercado interno |
| **Empleo** | Empleos en el sector siderúrgico |
| **Importaciones** | Volumen de importaciones |

## 🧠 Metodología

### 1. Análisis de Texto (NLP)
- **Tokenización** y limpieza de texto
- **Named Entity Recognition** para extraer personas, empresas, países
- **Keyword matching** para identificar eventos
- **Sentiment analysis** basado en palabras clave

### 2. Sistema de Ponderación
Cada categoría tiene un peso específico:
- Aranceles: 1.5 (alto impacto)
- Subsidios: 1.3
- Infraestructura: 1.0
- Crisis: 1.4
- etc.

### 3. Cálculo de Score
```python
score_impacto = (sentimiento + categorías_ponderadas) × magnitud
# Normalizado entre -1 (muy negativo) y +1 (muy positivo)
```

### 4. Estimación de Impactos
Basado en:
- Score de impacto general
- Categorías detectadas
- Magnitud del evento
- Reglas específicas por tipo de evento

## 📈 Ejemplos de Output

### Análisis Individual
```
🟢 IMPACTO MUY ALTO - POSITIVO
Noticia: Ternium anuncia inversión de $2,000 millones
Score: 1.00 | Sentimiento: positivo | Magnitud: alto

CATEGORÍAS DETECTADAS:
  • Inversion: 2 menciones (peso: 1.1)
  • Produccion: 2 menciones (peso: 1.1)

IMPACTO ESTIMADO:
  📈 Produccion: +9.6%
  📈 Exportaciones: +4.8%
  📈 Empleo: +4.8%
```

### Análisis Agregado
```
IMPACTO PROMEDIO (últimos 7 días):
  📈 Produccion: +3.7%
  📈 Exportaciones: +1.4%
  📈 Precios: +1.0%

SCORE GENERAL: 0.36
Tendencia: POSITIVA para la industria
```

## 🔮 Próximos Pasos - Roadmap

### Fase 2: Machine Learning
- [ ] Entrenar modelo predictivo con datos históricos
- [ ] Feature engineering avanzado
- [ ] Validación con indicadores reales
- [ ] Análisis de series temporales (ARIMA/Prophet)

### Fase 3: NLP Avanzado
- [ ] Integrar BERT/Transformers en español
- [ ] Fine-tuning para dominio financiero
- [ ] Named Entity Recognition avanzado
- [ ] Análisis de relaciones entre entidades

### Fase 4: Automatización
- [ ] Pipeline de scraping diario
- [ ] Base de datos PostgreSQL
- [ ] Dashboard web interactivo (Streamlit/Dash)
- [ ] Sistema de alertas automáticas

### Fase 5: Producción
- [ ] API REST
- [ ] Integración con sistemas empresariales
- [ ] Escalabilidad cloud
- [ ] Monitoreo y logging

## 🎓 Conceptos Técnicos

### NLP (Natural Language Processing)
Procesamiento de lenguaje natural para extraer información de texto no estructurado.

### Text Mining
Extracción de patrones y conocimiento desde grandes volúmenes de texto.

### Sentiment Analysis
Determinación de la polaridad emocional (positivo/negativo/neutral) del texto.

### Named Entity Recognition (NER)
Identificación y clasificación de entidades: personas, organizaciones, lugares, fechas, etc.

### Feature Engineering
Creación de variables predictivas desde el texto para modelos de ML.

## 📚 Fuentes de Datos

### Actuales (Demo)
- Noticias de ejemplo predefinidas

### Próximas Implementaciones
- Google News API
- RSS feeds de medios especializados
- Twitter API (análisis de sentimiento social)
- Comunicados oficiales (Canacero, SE)
- INEGI (datos oficiales)

## ⚙️ Configuración

### Agregar Nuevas Palabras Clave
Editar `steel_news_analyzer.py`:
```python
self.keywords = {
    'nueva_categoria': {
        'palabras': ['palabra1', 'palabra2'],
        'peso': 1.2,
        'tipo': 'positivo'  # o 'negativo' o 'neutral'
    }
}
```

### Ajustar Ponderaciones
```python
# En método estimar_impacto_indicadores()
if 'aranceles' in categorias:
    impactos['produccion'] = -10 * factor * mult  # Ajustar -10
```

## 📄 Estructura de Archivos

```
proyecto/
│
├── steel_news_analyzer.py      # Motor de análisis NLP
├── steel_impact_system.py      # Sistema completo con scraping
├── analisis_acero_correlacion.py  # Análisis histórico
│
├── README.md                    # Este archivo
├── requirements.txt             # Dependencias
│
├── data/                        # Datos de entrada
│   ├── steel_keywords_trends.csv
│   └── crude_steel_production.csv
│
└── output/                      # Reportes generados
    ├── analisis_completo.json
    ├── reporte_analisis_acero.pdf
    └── reporte_analisis_acero.xlsx
```

## 🤝 Contribuciones

Para mejorar el sistema:
1. Agregar más fuentes de noticias
2. Mejorar diccionarios de palabras clave
3. Ajustar ponderaciones basado en validación
4. Implementar modelos de ML
5. Crear más visualizaciones

## 📧 Soporte

Para dudas o sugerencias sobre el sistema, documenta:
- Versión de Python
- Librerías instaladas
- Mensaje de error (si aplica)
- Ejemplo de entrada que causa el problema

## 🏆 Casos de Uso

1. **Análisis de Mercado**: Monitorear tendencias del sector
2. **Due Diligence**: Evaluar impacto de eventos en inversiones
3. **Risk Management**: Identificar riesgos tempranos
4. **Trading**: Señales para commodities de acero
5. **Consultoría**: Reportes para clientes del sector

## 📊 Métricas de Desempeño

### Precisión Actual (Fase 1 - MVP)
- Sistema basado en reglas y heurísticas
- Pendiente validación con datos reales

### Objetivo (Fase 3 - ML)
- Accuracy > 75% en dirección de impacto
- R² > 0.6 en predicción de magnitud
- Recall > 80% en detección de eventos críticos

## 🔒 Limitaciones Actuales

1. **Sentimiento básico**: No usa modelos pre-entrenados
2. **Sin contexto temporal**: No considera lags
3. **Reglas fijas**: No aprende de datos históricos
4. **Idioma**: Optimizado solo para español
5. **Sin validación**: Falta comparar vs datos reales

## 💡 Tips de Uso

1. **Filtrar ruido**: Revisar keywords para evitar falsos positivos
2. **Validar manualmente**: Verificar top 10 noticias mensualmente
3. **Combinar fuentes**: Usar múltiples medios para balance
4. **Contexto macro**: Considerar eventos externos (COVID, elecciones)
5. **Umbrales**: Ajustar thresholds de impacto según necesidad

## 📖 Referencias

- spaCy Documentation: https://spacy.io/
- BERT en español: https://github.com/dccuchile/beto
- Financial Sentiment Analysis: FinBERT
- Time Series: Facebook Prophet

---

**Versión**: 1.0.0 (MVP - Fase 1)  
**Última actualización**: Febrero 2026  
**Licencia**: Uso interno - Proyecto empresarial
