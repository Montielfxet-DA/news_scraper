"""
Sistema de Análisis de Impacto en la Industria del Acero
VERSIÓN CON SCRAPING REAL DE NOTICIAS
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
import json
import warnings
import os

warnings.filterwarnings('ignore')

import sys

sys.path.append(r'D:\Data Documents\Python Projects\news_scraper\Core')

from steel_news_analyzer import SteelNewsAnalyzer
from news_relevance_filter import NewsRelevanceFilter
from news_database import NewsDatabase, mostrar_estadisticas

NEWSAPI_KEY = "e9a1a7c23b694a419fca45af9bfe3994"
USE_NEWSAPI = True

# Directorio de salida
OUTPUT_DIR = r'D:\Data Documents\Python Projects\news_scraper\Output'

# Crear carpeta si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

class RealNewsCollector:
    """Recolector de noticias reales desde múltiples fuentes"""

    def __init__(self, newsapi_key=None):
        self.newsapi_key = newsapi_key
        self.keywords_busqueda = [
            'acero México', 'industria siderúrgica México', 'Ternium',
            'aranceles acero', 'exportación acero México', 'precio acero',
            'construcción México acero', 'CANACERO', 'lámina acero México',
            'varilla construcción México', 'siderurgia México', 'importación acero',
            'dumping acero', 'T-MEC acero', 'DeAcero', 'Simec', 'Gerdau México',
            'sector construcción México', 'infraestructura México', 'metalúrgica México',
            'regulación acero', 'recesión', 'regulación', 'demanda acero', 'importación',
            'chatarra', 'chatarra de acero', 'minas de acero', 'HMS', 'Bushelin',
        ]

    def fetch_newsapi(self, keyword, dias_atras=7):
        """
        Obtiene noticias de NewsAPI
        Documentación: https://newsapi.org/docs/endpoints/everything
        """
        if not self.newsapi_key or self.newsapi_key == "TU_API_KEY_AQUI":
            print("  ⚠️ NewsAPI key no configurada. Saltando NewsAPI...")
            return []

        try:
            import requests

            fecha_desde = (datetime.now() - timedelta(days=dias_atras)).strftime('%Y-%m-%d')

            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': keyword,
                'from': fecha_desde,
                'language': 'es',
                'sortBy': 'publishedAt',
                'apiKey': self.newsapi_key,
                'pageSize': 10
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
                print(f"  ❌ Error NewsAPI ({response.status_code}): {response.text[:100]}")
                return []

            data = response.json()

            if data['status'] != 'ok':
                print(f"  ❌ NewsAPI error: {data.get('message', 'Unknown error')}")
                return []

            noticias = []
            for article in data.get('articles', []):
                # Filtrar noticias sin contenido
                if not article.get('description') and not article.get('content'):
                    continue

                noticias.append({
                    'titulo': article.get('title', ''),
                    'contenido': article.get('description', '') + ' ' + article.get('content', ''),
                    'url': article.get('url', ''),
                    'fecha': datetime.strptime(article['publishedAt'][:10], '%Y-%m-%d'),
                    'fuente': article.get('source', {}).get('name', 'NewsAPI')
                })

            return noticias

        except ImportError:
            print("  ⚠️ requests no instalado: pip install requests")
            return []
        except Exception as e:
            print(f"  ❌ Error en NewsAPI: {e}")
            return []

    def fetch_google_news(self, keyword, max_results=20):
        """
        Obtiene noticias de Google News
        Requiere: pip install pygooglenews
        """
        try:
            from pygooglenews import GoogleNews

            gn = GoogleNews(lang='es', country='MX')
            search = gn.search(keyword, when='7d')

            noticias = []
            for entry in search['entries'][:max_results]:
                try:
                    noticias.append({
                        'titulo': entry.title,
                        'contenido': entry.get('summary', entry.get('description', '')),
                        'url': entry.link,
                        'fecha': datetime(*entry.published_parsed[:6]) if hasattr(entry,
                                                                                  'published_parsed') else datetime.now(),
                        'fuente': entry.get('source', {}).get('title', 'Google News')
                    })
                except Exception as e:
                    continue

            return noticias

        except ImportError:
            print("  ⚠️ pygooglenews no instalado: pip install pygooglenews")
            return []
        except Exception as e:
            print(f"  ❌ Error en Google News: {e}")
            return []

    def fetch_rss_feed(self, url):
        """
        Obtiene noticias de un feed RSS
        Requiere: pip install feedparser
        """
        try:
            import feedparser

            feed = feedparser.parse(url)
            noticias = []

            for entry in feed.entries[:15]:
                try:
                    texto = entry.title + ' ' + entry.get('summary', entry.get('description', ''))

                    # Filtrar solo noticias relacionadas con acero
                    if any(kw in texto.lower() for kw in ['acero', 'siderúrgica', 'ternium', 'tyasa',
                                                          'metalúrgica', 'siderurgia', 'fundición', 'chatarra']):

                        fecha = datetime.now()
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            try:
                                fecha = datetime(*entry.published_parsed[:6])
                            except:
                                pass

                        noticias.append({
                            'titulo': entry.title,
                            'contenido': entry.get('summary', entry.get('description', '')),
                            'url': entry.get('link', ''),
                            'fecha': fecha,
                            'fuente': feed.feed.get('title', 'RSS Feed')
                        })
                except Exception as e:
                    continue

            return noticias

        except ImportError:
            print("  ⚠️ feedparser no instalado: pip install feedparser")
            return []
        except Exception as e:
            print(f"  ❌ Error en RSS {url}: {e}")
            return []

    def scrape_web_simple(self, url):
        """
        Scraping simple de una URL específica
        Requiere: pip install beautifulsoup4 requests
        """
        try:
            import requests
            from bs4 import BeautifulSoup

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Buscar título
            titulo = soup.find('h1')
            titulo = titulo.get_text().strip() if titulo else ''

            # Buscar contenido (común en artículos)
            contenido_tags = soup.find_all(['p', 'article'])
            contenido = ' '.join([tag.get_text().strip() for tag in contenido_tags[:10]])

            if titulo and contenido:
                return {
                    'titulo': titulo,
                    'contenido': contenido[:1000],  # Primeros 1000 caracteres
                    'url': url,
                    'fecha': datetime.now(),
                    'fuente': 'Web Scraping'
                }

            return None

        except Exception as e:
            print(f"  ❌ Error scraping {url}: {e}")
            return None

    def collect_all(self, dias_atras=7, max_por_keyword=5):
        """Recolecta noticias de todas las fuentes disponibles"""

        todas_noticias = []

        print("\n🔍 RECOLECTANDO NOTICIAS REALES...")
        print("=" * 80)

        # 1. NewsAPI (si está configurado)
        if USE_NEWSAPI and self.newsapi_key and self.newsapi_key != "TU_API_KEY_AQUI":
            print("\n📰 Fuente: NewsAPI")
            for keyword in self.keywords_busqueda[:3]:  # Limitar para no exceder cuota
                print(f"  • Buscando: '{keyword}'")
                noticias = self.fetch_newsapi(keyword, dias_atras)
                todas_noticias.extend(noticias)
                print(f"    ✓ {len(noticias)} noticias encontradas")

        # 2. Google News (gratuito)
        print("\n📰 Fuente: Google News")
        for keyword in self.keywords_busqueda[:4]:  # Primeras 4 keywords
            print(f"  • Buscando: '{keyword}'")
            noticias = self.fetch_google_news(keyword, max_results=max_por_keyword)
            todas_noticias.extend(noticias)
            print(f"    ✓ {len(noticias)} noticias encontradas")

        # 3. RSS Feeds de medios mexicanos
        print("\n📰 Fuente: Feeds RSS")
        rss_feeds = [
            'https://www.eleconomista.com.mx',
            'https://www.elfinanciero.com.mx',
            'https://www.milenio.com/rss/negocios',
            'https://www.economia.gob.mx',
            'https://mx.investing.com',
            'https://expansion.mx/economia'
        ]

        for feed_url in rss_feeds:
            print(f"  • Leyendo: {feed_url}")
            noticias = self.fetch_rss_feed(feed_url)
            todas_noticias.extend(noticias)
            print(f"    ✓ {len(noticias)} noticias encontradas")

        # Eliminar duplicados por URL
        print("\n🧹 Limpiando duplicados...")
        urls_vistas = set()
        noticias_unicas = []

        for noticia in todas_noticias:
            url = noticia.get('url', '')
            if url and url not in urls_vistas:
                urls_vistas.add(url)
                noticias_unicas.append(noticia)

        # Filtrar por fecha
        fecha_limite = datetime.now() - timedelta(days=dias_atras)
        noticias_recientes = [n for n in noticias_unicas
                              if n.get('fecha', datetime.now()) >= fecha_limite]

        # Ordenar por fecha (más recientes primero)
        noticias_recientes.sort(key=lambda x: x.get('fecha', datetime.now()), reverse=True)

        print(f"\n✅ TOTAL: {len(noticias_recientes)} noticias únicas recolectadas")
        print("=" * 80)

        return noticias_recientes


# ============================================================================
# MÓDULO DE GENERACIÓN DE REPORTES (igual que antes)
# ============================================================================

class ReportGenerator:
    """Generador de reportes en PDF y Excel"""

    def generar_reporte_pdf(self, resultados_analisis, filename='reporte_analisis_acero.pdf'):
        """Genera reporte PDF profesional"""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

        doc = SimpleDocTemplate(filename, pagesize=letter,
                                topMargin=0.5 * inch, bottomMargin=0.5 * inch)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='CustomTitle',
                                  parent=styles['Heading1'],
                                  fontSize=22,
                                  textColor=colors.HexColor('#1a4d7c'),
                                  spaceAfter=20,
                                  alignment=TA_CENTER,
                                  fontName='Helvetica-Bold'))

        story = []

        # Portada
        story.append(Spacer(1, 1 * inch))
        title = Paragraph("Reporte de Análisis de Impacto<br/>Industria del Acero en México",
                          styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3 * inch))

        fecha = Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                          styles['Normal'])
        story.append(fecha)
        story.append(PageBreak())

        # Resumen ejecutivo
        story.append(Paragraph("1. Resumen Ejecutivo", styles['Heading1']))

        num_noticias = resultados_analisis['num_noticias']
        score_general = resultados_analisis['score_general']

        tendencia = 'POSITIVA' if score_general > 0.3 else 'NEGATIVA' if score_general < -0.3 else 'NEUTRAL'

        resumen_text = f"""
        Se analizaron {num_noticias} noticias reales de la industria del acero en México 
        recolectadas en los últimos 7 días. El score de impacto general es de {score_general:.2f}, 
        indicando una tendencia <b>{tendencia}</b> para el sector.
        """
        story.append(Paragraph(resumen_text, styles['BodyText']))
        story.append(Spacer(1, 0.2 * inch))

        # Impacto agregado
        story.append(Paragraph("2. Impacto Estimado en Indicadores Clave", styles['Heading1']))

        table_data = [['Indicador', 'Impacto Estimado (%)', 'Tendencia']]
        for indicador, valor in resultados_analisis['impacto_agregado'].items():
            signo = '+' if valor > 0 else ''
            emoji = '↗' if valor > 0 else '↘' if valor < 0 else '→'
            table_data.append([
                indicador.title(),
                f"{signo}{valor:.1f}%",
                emoji
            ])

        t = Table(table_data, colWidths=[2.5 * inch, 2 * inch, 1 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5f8d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(t)
        story.append(PageBreak())

        # Noticias más impactantes
        story.append(Paragraph("3. Noticias de Mayor Impacto", styles['Heading1']))

        # Ordenar por impacto absoluto
        noticias_ordenadas = sorted(resultados_analisis['noticias'],
                                    key=lambda x: abs(x['score_impacto']),
                                    reverse=True)

        for i, noticia in enumerate(noticias_ordenadas[:10], 1):
            story.append(Paragraph(f"<b>#{i} - {noticia['titulo'][:80]}...</b>", styles['Heading3']))

            score = noticia['score_impacto']
            sentimiento = noticia['sentimiento']['clasificacion']
            fuente = noticia.get('fuente', 'Desconocida')

            story.append(Paragraph(
                f"<b>Fuente:</b> {fuente} | <b>Score:</b> {score:.2f} | <b>Sentimiento:</b> {sentimiento}",
                styles['Normal']
            ))

            # URL si existe
            if noticia.get('url'):
                story.append(Paragraph(f"<b>URL:</b> {noticia['url'][:60]}...", styles['Normal']))

            story.append(Spacer(1, 0.1 * inch))

            # Mini tabla de impactos
            mini_table_data = [['Indicador', 'Impacto']]
            for ind, val in list(noticia['impacto_indicadores'].items())[:5]:
                signo = '+' if val > 0 else ''
                mini_table_data.append([ind.title(), f"{signo}{val:.1f}%"])

            mini_t = Table(mini_table_data, colWidths=[2 * inch, 1.5 * inch])
            mini_t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            story.append(mini_t)
            story.append(Spacer(1, 0.3 * inch))

        # Construir PDF
        doc.build(story)
        print(f"✓ Reporte PDF generado: {filename}")

    def generar_reporte_excel(self, resultados_analisis, filename='reporte_analisis_acero.xlsx'):
        """Genera reporte en Excel"""

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Hoja 1: Resumen
            resumen_data = {
                'Métrica': ['Número de Noticias', 'Score General', 'Fecha de Análisis'],
                'Valor': [
                    resultados_analisis['num_noticias'],
                    f"{resultados_analisis['score_general']:.2f}",
                    resultados_analisis['fecha_analisis']
                ]
            }
            df_resumen = pd.DataFrame(resumen_data)
            df_resumen.to_excel(writer, sheet_name='Resumen', index=False)

            # Hoja 2: Impacto
            df_impacto = pd.DataFrame([resultados_analisis['impacto_agregado']])
            df_impacto = df_impacto.T.reset_index()
            df_impacto.columns = ['Indicador', 'Impacto (%)']
            df_impacto.to_excel(writer, sheet_name='Impacto Indicadores', index=False)

            # Hoja 3: Detalle
            noticias_data = []
            for noticia in resultados_analisis['noticias']:
                noticias_data.append({
                    'Fecha': noticia['fecha'],
                    'Título': noticia['titulo'][:100],
                    'Fuente': noticia.get('fuente', 'N/A'),
                    'URL': noticia.get('url', 'N/A'),
                    'Score': noticia['score_impacto'],
                    'Sentimiento': noticia['sentimiento']['clasificacion'],
                    'Producción (%)': noticia['impacto_indicadores']['produccion'],
                    'Exportaciones (%)': noticia['impacto_indicadores']['exportaciones'],
                    'Precios (%)': noticia['impacto_indicadores']['precios'],
                    'Empleo (%)': noticia['impacto_indicadores']['empleo']
                })

            df_noticias = pd.DataFrame(noticias_data)
            df_noticias.to_excel(writer, sheet_name='Detalle Noticias', index=False)

        print(f"✓ Reporte Excel generado: {filename}")


# ============================================================================
# SCRIPT PRINCIPAL CON NOTICIAS REALES
# ============================================================================

def main():
    """Script principal - Versión con noticias reales"""

    print("\n" + "=" * 80)
    print("SISTEMA DE ANÁLISIS DE IMPACTO - NOTICIAS REALES")
    print("Industria del Acero en México")
    print("=" * 80 + "\n")

    # 1. Recolectar noticias REALES
    print("PASO 1: Recolección de Noticias Reales")
    print("-" * 80)

    collector = RealNewsCollector(newsapi_key=NEWSAPI_KEY if USE_NEWSAPI else None)
    noticias = collector.collect_all(dias_atras=30, max_por_keyword=15)

    if not noticias:
        print("\n⚠️ No se pudieron recolectar noticias reales.")
        print("💡 Verifica:")
        print("   1. Conexión a internet")
        print("   2. Librerías instaladas: pip install pygooglenews feedparser requests")
        print("   3. API key de NewsAPI (opcional)")
        return

    print(f"\n✓ {len(noticias)} noticias reales listas para analizar\n")

    # Mostrar muestra
    print("📋 MUESTRA DE NOTICIAS RECOLECTADAS:")
    for i, n in enumerate(noticias[:3], 1):
        print(f"\n{i}. {n['titulo'][:70]}...")
        print(f"   Fuente: {n.get('fuente', 'N/A')} | Fecha: {n['fecha'].strftime('%Y-%m-%d')}")
    print()

    # NUEVO: Filtrar noticias irrelevantes
    print("\nPASO 1.5: Filtrado de Relevancia")
    print("-" * 80)

    filtro = NewsRelevanceFilter(min_score=2)
    noticias_relevantes, noticias_rechazadas = filtro.filtrar_noticias(noticias, verbose=False)

    # Guardar noticias rechazadas para revisión
    if noticias_rechazadas:
        rechazadas_data = []
        for n in noticias_rechazadas:
            rechazadas_data.append({
                'titulo': n['titulo'],
                'fuente': n.get('fuente', 'N/A'),
                'score': n.get('relevancia_score', 0),
                'razones': n.get('relevancia_detalles', {}).get('razones', [])
            })

        with open(os.path.join(OUTPUT_DIR, 'noticias_rechazadas.json'), 'w', encoding='utf-8') as f:
            json.dump(rechazadas_data, f, indent=2, ensure_ascii=False)
        print(f"  ℹ️ Noticias rechazadas guardadas en: noticias_rechazadas.json")

    # Continuar solo con noticias relevantes
    noticias = noticias_relevantes

    if not noticias:
        print("\n⚠️ No hay noticias relevantes después del filtrado.")
        print("💡 Sugerencias:")
        print("   • Ajustar umbral de relevancia")
        print("   • Ampliar keywords de búsqueda")
        print("   • Revisar noticias_rechazadas.json")
        return

    print(f"\n✓ {len(noticias)} noticias relevantes para analizar\n")

    # 2. Analizar noticias
    print("\nPASO 2: Análisis de Noticias")
    print("-" * 80)

    analyzer = SteelNewsAnalyzer()
    db_dir = r'D:\Data Documents\Python Projects\news_scraper\db'
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'noticias_database.db')
    db = NewsDatabase(db_path)

    resultados = []

    for i, noticia in enumerate(noticias, 1):
        print(f"  📰 Analizando {i}/{len(noticias)}: {noticia['titulo'][:50]}...")

        try:
            analisis = analyzer.analizar_noticia(
                noticia['titulo'],
                noticia['contenido'],
                noticia.get('fecha', datetime.now())
            )

            analisis['fuente'] = noticia.get('fuente', 'Desconocida')
            analisis['url'] = noticia.get('url', '')

            # NUEVO: Determinar relevancia automática
            relevancia_auto = 'incierto'
            if noticia.get('relevancia_score', 0) >= 5:
                relevancia_auto = 'relevante'
            elif noticia.get('relevancia_score', 0) < 0:
                relevancia_auto = 'irrelevante'

            analisis['relevancia_auto'] = relevancia_auto
            analisis['relevancia_score'] = noticia.get('relevancia_score', 0)

            # NUEVO: Guardar en base de datos
            noticia_id = db.guardar_noticia({
                'titulo': noticia['titulo'],
                'contenido': noticia['contenido'],
                'url': noticia.get('url', ''),
                'fuente': noticia.get('fuente', ''),
                'fecha': noticia.get('fecha'),
                'relevancia_score': noticia.get('relevancia_score', 0),
                'relevancia_auto': relevancia_auto,
                'categorias': analisis.get('categorias', {}),
                'entidades': analisis.get('entidades', {}),
                'score_impacto': analisis.get('score_impacto', 0),
                'sentimiento': analisis.get('sentimiento', {}),
                'magnitud': analisis.get('magnitud', 'medio'),
                'impacto_indicadores': analisis.get('impacto_indicadores', {})
            })

            if noticia_id > 0:
                print(f"    ✓ Guardada en BD (ID: {noticia_id})")

            resultados.append(analisis)
        except Exception as e:
            print(f"    ⚠️ Error: {e}")
            continue

    print(f"\n✓ {len(resultados)} noticias analizadas y guardadas en base de datos\n")

    # Mostrar estadísticas de la BD
    print("\n" + "-" * 80)
    print("📊 ESTADÍSTICAS DE LA BASE DE DATOS")
    print("-" * 80)
    stats_db = db.obtener_estadisticas()
    print(f"   Total en BD: {stats_db['total']} noticias")
    print(f"   Etiquetadas manualmente: {stats_db['etiquetadas']}")
    print(f"   Pendientes de etiquetar: {stats_db['no_etiquetadas']}")
    if stats_db['etiquetadas'] > 0:
        print(f"   Precisión del filtro: {stats_db['precision_filtro']:.1f}%")
    print("-" * 80 + "\n")

    # 3. Calcular métricas
    print("PASO 3: Cálculo de Métricas Agregadas")
    print("-" * 80)

    if not resultados:
        print("❌ No hay resultados para procesar")
        return

    impacto_agregado = {
        'produccion': np.mean([r['impacto_indicadores']['produccion'] for r in resultados]),
        'exportaciones': np.mean([r['impacto_indicadores']['exportaciones'] for r in resultados]),
        'precios': np.mean([r['impacto_indicadores']['precios'] for r in resultados]),
        'empleo': np.mean([r['impacto_indicadores']['empleo'] for r in resultados]),
        'importaciones': np.mean([r['impacto_indicadores']['importaciones'] for r in resultados])
    }

    score_general = np.mean([r['score_impacto'] for r in resultados])

    print("\n📊 IMPACTO PROMEDIO EN INDICADORES:")
    for indicador, valor in impacto_agregado.items():
        emoji = "📈" if valor > 0 else "📉" if valor < 0 else "➡️"
        signo = "+" if valor > 0 else ""
        print(f"   {emoji} {indicador.title()}: {signo}{valor:.1f}%")

    print(f"\n🎯 SCORE GENERAL: {score_general:.2f}")

    if score_general > 0.3:
        print("   ✅ Tendencia: POSITIVA para la industria")
    elif score_general < -0.3:
        print("   ⚠️ Tendencia: NEGATIVA para la industria")
    else:
        print("   ➡️ Tendencia: NEUTRAL/MIXTA")

    print()

    # 4. Generar reportes
    print("PASO 4: Generación de Reportes")
    print("-" * 80)

    # Preparar datos
    resultados_json = []
    for r in resultados:
        r_copy = r.copy()
        if isinstance(r_copy['fecha'], datetime):
            r_copy['fecha'] = r_copy['fecha'].isoformat()
        resultados_json.append(r_copy)

    datos_reporte = {
        'fecha_analisis': datetime.now().isoformat(),
        'num_noticias': len(resultados),
        'score_general': float(score_general),
        'impacto_agregado': impacto_agregado,
        'noticias': resultados_json
    }

    # Guardar archivos
    output_files = {
        'json': os.path.join(OUTPUT_DIR, 'analisis_REAL.json'),
        'pdf': os.path.join(OUTPUT_DIR, 'reporte_REAL.pdf'),
        'excel': os.path.join(OUTPUT_DIR, 'reporte_REAL.xlsx')
    }

    # JSON
    with open(output_files['json'], 'w', encoding='utf-8') as f:
        json.dump(datos_reporte, f, indent=2, ensure_ascii=False)
    print(f"  ✓ {output_files['json']}")

    # PDF y Excel
    report_gen = ReportGenerator()

    try:
        report_gen.generar_reporte_pdf(datos_reporte, output_files['pdf'])
    except Exception as e:
        print(f"  ⚠️ Error generando PDF: {e}")

    try:
        report_gen.generar_reporte_excel(datos_reporte, output_files['excel'])
    except Exception as e:
        print(f"  ⚠️ Error generando Excel: {e}")

    print("\n" + "=" * 80)
    print("✅ ANÁLISIS DE NOTICIAS REALES COMPLETADO")
    print("=" * 80 + "\n")

    print("📁 Archivos generados:")
    print(f"   • {os.path.basename(output_files['json'])}")
    print(f"   • {os.path.basename(output_files['pdf'])}")
    print(f"   • {os.path.basename(output_files['excel'])}")
    print()

    print("🗄️ Base de datos:")
    print(f"   • {os.path.abspath(db.db_path)}")
    print(f"   • {stats_db['total']} noticias almacenadas")
    print()

    if stats_db['no_etiquetadas'] > 0:
        print("💡 PRÓXIMO PASO:")
        print("   Ejecuta: python etiquetador_noticias.py")
        print(f"   Para etiquetar las {stats_db['no_etiquetadas']} noticias pendientes")
        print()

    # Cerrar base de datos
    db.cerrar()


if __name__ == "__main__":
    main()