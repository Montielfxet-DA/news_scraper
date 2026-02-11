# 🔧 GUÍA DE CONFIGURACIÓN - SCRAPING DE NOTICIAS REALES

## ✅ CHECKLIST DE INSTALACIÓN

### 1. Instalar Librerías Necesarias

Abre tu terminal y ejecuta:

```bash
pip install pygooglenews feedparser requests beautifulsoup4 lxml
```

**Verificar instalación:**
```bash
python -c "import pygooglenews, feedparser, requests; print('✅ Todo instalado correctamente')"
```

---

## 📰 OPCIÓN A: Usar Google News (GRATUITO - RECOMENDADO PARA EMPEZAR)

### Ventajas:
- ✅ Completamente gratuito
- ✅ No requiere API key
- ✅ Fácil de usar
- ✅ Buena cobertura de noticias en español

### Desventajas:
- ⚠️ Límite de requests (no oficial, ~100/día)
- ⚠️ Puede ser bloqueado si se abusa
- ⚠️ Contenido limitado (solo resumen)

### Pasos:

1. **NO requiere configuración adicional**
2. Simplemente ejecuta:
   ```bash
   python steel_impact_system_REAL.py
   ```

3. El sistema automáticamente:
   - Buscará noticias en Google News México
   - Leerá feeds RSS de medios mexicanos
   - Analizará y generará reportes

---

## 📰 OPCIÓN B: Usar NewsAPI (PROFESIONAL - MÁS CONFIABLE)

### Ventajas:
- ✅ Muy confiable
- ✅ Contenido completo de artículos
- ✅ 100 requests/día gratis
- ✅ Mejor calidad de datos
- ✅ Documentación excelente

### Desventajas:
- ⚠️ Requiere registro
- ⚠️ Plan gratis limitado a 100 requests/día
- ⚠️ Noticias de hace máximo 1 mes (plan gratis)

### Pasos:

1. **Registrarte en NewsAPI:**
   - Ve a: https://newsapi.org/register
   - Completa el formulario (nombre, email, uso)
   - Recibirás tu API key por email

2. **Configurar la API Key:**
   
   Abre `steel_impact_system_REAL.py` y busca estas líneas (cerca de la línea 20):
   
   ```python
   # CAMBIAR ESTO:
   NEWSAPI_KEY = "TU_API_KEY_AQUI"
   USE_NEWSAPI = False
   
   # POR ESTO:
   NEWSAPI_KEY = "tu_api_key_real_aqui"  # Pegar tu API key
   USE_NEWSAPI = True  # Cambiar a True
   ```

3. **Ejecutar:**
   ```bash
   python steel_impact_system_REAL.py
   ```

---

## 📰 OPCIÓN C: Combinar Ambas (ÓPTIMO)

Usa **NewsAPI + Google News + RSS Feeds** para máxima cobertura:

1. Configura NewsAPI (Opción B)
2. El sistema automáticamente usará todas las fuentes disponibles
3. Tendrás las noticias más completas y diversas

---

## 🚀 EJECUTAR EL SISTEMA

### Comando básico:
```bash
python steel_impact_system_REAL.py
```

### Lo que verás:
```
================================================================================
SISTEMA DE ANÁLISIS DE IMPACTO - NOTICIAS REALES
Industria del Acero en México
================================================================================

PASO 1: Recolección de Noticias Reales
--------------------------------------------------------------------------------

🔍 RECOLECTANDO NOTICIAS REALES...
================================================================================

📰 Fuente: Google News
  • Buscando: 'acero México'
    ✓ 5 noticias encontradas
  • Buscando: 'industria siderúrgica México'
    ✓ 3 noticias encontradas
  ...

📰 Fuente: Feeds RSS
  • Leyendo: https://www.eleconomista.com.mx/rss/empresas.xml
    ✓ 2 noticias encontradas
  ...

✅ TOTAL: 15 noticias únicas recolectadas
```

---

## 📊 ARCHIVOS GENERADOS

Después de ejecutar, encontrarás:

```
tu_carpeta/
├── analisis_REAL.json      # Datos completos en JSON
├── reporte_REAL.pdf         # Reporte ejecutivo
└── reporte_REAL.xlsx        # Datos en Excel
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "ModuleNotFoundError: No module named 'pygooglenews'"
**Solución:**
```bash
pip install pygooglenews
```

### Error: "requests.exceptions.ConnectionError"
**Causas posibles:**
1. No hay internet
2. Firewall bloqueando
3. VPN/Proxy interfiriendo

**Solución:**
- Verificar conexión a internet
- Desactivar VPN temporalmente
- Verificar configuración de firewall

### Error: "NewsAPI error: apiKeyInvalid"
**Solución:**
1. Verificar que copiaste bien la API key
2. Asegurarte que no tiene espacios extras
3. Verificar que USE_NEWSAPI = True

### Error: "No se pudieron recolectar noticias"
**Solución:**
1. Verificar internet
2. Probar instalar las librerías de nuevo:
   ```bash
   pip install --upgrade pygooglenews feedparser requests
   ```

### Las noticias no son relevantes
**Solución:**
1. Ajustar keywords en el código:
   ```python
   self.keywords_busqueda = [
       'acero México',
       'tu_keyword_personalizada',
       # Agregar más...
   ]
   ```

---

## ⚙️ PERSONALIZACIÓN

### Cambiar días de búsqueda (default: 7 días):
```python
# En main(), cambiar:
noticias = collector.collect_all(dias_atras=14)  # 14 días en vez de 7
```

### Cambiar número de resultados por keyword:
```python
# En main(), cambiar:
noticias = collector.collect_all(
    dias_atras=7, 
    max_por_keyword=10  # 10 en vez de 5
)
```

### Agregar más feeds RSS:
En `RealNewsCollector`, buscar `rss_feeds` y agregar:
```python
rss_feeds = [
    'https://www.eleconomista.com.mx/rss/empresas.xml',
    'TU_FEED_RSS_AQUI',
    # etc...
]
```

---

## 📈 PRÓXIMOS PASOS

Una vez que tengas noticias reales funcionando:

1. **Automatizar ejecución diaria:**
   - Windows: Usar Task Scheduler
   - Linux/Mac: Usar cron
   
2. **Crear base de datos:**
   - Guardar histórico de análisis
   - Permitir análisis de tendencias

3. **Dashboard web:**
   - Visualizar resultados en tiempo real
   - Usar Streamlit o Dash

4. **Sistema de alertas:**
   - Email cuando score > threshold
   - Notificaciones push

---

## 📞 SOPORTE

Si tienes problemas:

1. Verifica que todas las librerías estén instaladas
2. Revisa los mensajes de error completos
3. Prueba con una keyword simple primero
4. Verifica tu conexión a internet

---

## ✅ TESTING RÁPIDO

Para verificar que todo funciona:

```python
# Crear un archivo test.py:
from steel_impact_system_REAL import RealNewsCollector

collector = RealNewsCollector()
noticias = collector.fetch_google_news('acero México', max_results=3)

print(f"✅ Funciona! {len(noticias)} noticias encontradas")
for n in noticias:
    print(f"  - {n['titulo'][:60]}...")
```

```bash
python test.py
```

---

**¡Listo para producción!** 🚀
