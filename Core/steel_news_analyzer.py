"""
Sistema de análisis de sentimiento y su impacto en la industria del Acero

Objetivo: Contener las funciones básicas para el funcionamiento del ejectubale principal

"""

import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
import json
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURACIÓN Y DICCIONARIOS DE CONOCIMIENTO
# ============================================================================

class SteelNewsAnalyzer:
    """Componente principal"""
    
    def __init__(self):
        self.keywords = {
            'aranceles': {
                'palabras': [
                    'arancel', 'aranceles', 'tarifa', 'tarifas', 'impuesto de importación',
                    'barrera comercial', 'gravamen', 'cuota', 'sección 232', 'tariff 232',
                    'arancel 25%', 'arancel 50%', 'dumping', 'antidumping', 'medidas compensatorias'
                ],
                'peso': 1.7,  # ↑ por la alta incidencia actual (EE.UU. 2025-2026)
                'tipo': 'negativo'
            },
            'subsidios': {
                'palabras': [
                    'subsidio', 'subsidios', 'apoyo gubernamental', 'incentivo',
                    'estímulo fiscal', 'ayuda estatal', 'subvención', 'subvencionado'
                ],
                'peso': 1.4,
                'tipo': 'negativo'  # Cambio sugerido: en contexto acero suelen ser negativos (China)
            },
            'nearshoring': {  # Categoría nueva – muy relevante para TYASA
                'palabras': [
                    'nearshoring', 'relocalización', 'near-shoring', 'friendshoring',
                    'cadena de suministro', 'reconfiguración cadenas', 'reshoring',
                    'inversión extranjera directa', 'IED', 'nueva planta', 'expansión industrial'
                ],
                'peso': 1.5,
                'tipo': 'positivo'  # Potencialmente muy positivo si se concreta
            },
            'infraestructura': {
                'palabras': [
                    'infraestructura', 'construcción', 'obra pública', 'carretera',
                    'puente', 'edificio', 'desarrollo urbano', 'tren maya', 'corredor interoceánico',
                    'refinería', 'aeropuerto', 'programa de infraestructura', 'inversión pública'
                ],
                'peso': 1.3,  # ↑ porque construcción ha estado muy débil en México
                'tipo': 'positivo'
            },
            'demanda': {
                'palabras': [
                    'demanda', 'consumo', 'ventas', 'pedidos', 'órdenes de compra',
                    'consumo aparente', 'demanda interna', 'apparent steel use', 'ASU'
                ],
                'peso': 1.4,  # ↑ importancia crítica en México 2025
                'tipo': 'neutral'
            },
            'produccion': {
                'palabras': [
                    'producción', 'fabricación', 'manufactura', 'planta', 'capacidad instalada',
                    'alto horno', 'fundición', 'laminación', 'acerería', 'colada continua'
                ],
                'peso': 1.2,
                'tipo': 'neutral'
            },
            'precios': {
                'palabras': [
                    'precio', 'precios', 'costo', 'valor', 'cotización', 'hot rolled coil',
                    'HRC', 'cold rolled', 'varilla', 'lámina', 'acero plano', 'acero largo'
                ],
                'peso': 1.2,  # ↑ volatilidad afecta márgenes de TYASA
                'tipo': 'neutral'
            },
            'importacion': {  # Muy importante diferenciar de exportación
                'palabras': [
                    'importación', 'importaciones', 'compra externa', 'importado de china',
                    'acero chino', 'inundación', 'importaciones asiáticas', 'acero asiático',
                    'vietnam', 'india', 'turquía acero'
                ],
                'peso': 1.5,  # ↑ riesgo #1 para productores mexicanos actualmente
                'tipo': 'negativo'  # Cambio sugerido
            },
            'exportacion': {
                'palabras': [
                    'exportación', 'exportaciones', 'envío al extranjero', 'venta externa',
                    'exportación a eeuu', 'export a usa'
                ],
                'peso': 1.3,
                'tipo': 'positivo'
            },
            'crisis': {
                'palabras': [
                    'crisis', 'recesión', 'caída', 'desplome', 'colapso', 'quiebra',
                    'cierre de planta', 'desaceleración', 'contracción consumo'
                ],
                'peso': 1.6,
                'tipo': 'negativo'
            },
            # ... mantener las demás categorías (inversion, empleo, regulacion)
        }
        
        # Entidades relevantes
        self.entidades = {
            'paises': [
                'méxico', 'mexicana', 'mexicano', 'estados unidos', 'eeuu', 'usa', 'unidos',
                'china', 'chino', 'canadá', 'brasil', 'alemania', 'japón', 'corea', 'vietnam',
                'india', 'turquía'  # ↑ países origen de importaciones problemáticas
            ],
            'empresas': [
                'tyasa', 'ternium', 'altos hornos de méxico', 'ahmsa', 'arcelor mittal',
                'tata steel', 'posco', 'nucor', 'gerdau', 'deacero', 'simec', 'kobe steel',
                'china baowu', 'hbis'  # ↑ competidores + grandes exportadores chinos
            ],
            'instituciones_mx': [  # Nueva sublista – muy útil para noticias locales
                'canacero', 'alacero', 'economía', 'secretaría de economía', 'sheinbaum',
                'claudia sheinbaum', 'amlo', 'siemens', 'imss', 'inegi', 'banxico'
            ],
            'productos': [
                'acero', 'acero inoxidable', 'lámina', 'varilla', 'tubería',
                'perfiles estructurales', 'alambrón', 'bobina', 'hrc', 'crc',
                'acero largo', 'acero plano', 'chatarra', 'ferroso'
            ]
        }
        
        # Modificadores de sentimiento
        self.modificadores_positivos = [
            'aumenta', 'incrementa', 'sube', 'crece', 'mejora', 'impulsa', 'fortalece',
            'récord', 'histórico', 'exitoso', 'favorable', 'beneficio', 'ganancia'
        ]
        
        self.modificadores_negativos = [
            'disminuye', 'reduce', 'baja', 'cae', 'declina', 'empeora', 'debilita',
            'mínimo', 'pérdida', 'déficit', 'problema', 'amenaza', 'riesgo'
        ]
        
        # Indicadores de magnitud
        self.magnitudes = {
            'muy_alto': ['más del 20%', 'superior al 25%', 'mayor a 30%', 'histórico', 'récord'],
            'alto': ['15%', '18%', '20%', 'significativo', 'considerable', 'importante'],
            'medio': ['10%', '12%', '8%', 'moderado'],
            'bajo': ['5%', '3%', '2%', 'leve', 'ligero', 'pequeño']
        }
    
    def extraer_numeros(self, texto):
        """Extrae números y porcentajes del texto"""
        # Buscar porcentajes
        porcentajes = re.findall(r'(\d+(?:\.\d+)?)\s*%', texto)
        
        # Buscar números con contexto monetario
        cantidades = re.findall(r'\$?\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:millones?|mil\s+millones?|billones?)?', texto)
        
        return {
            'porcentajes': [float(p) for p in porcentajes],
            'cantidades': cantidades
        }
    
    def detectar_entidades(self, texto):
        """Detecta entidades mencionadas en el texto"""
        texto_lower = texto.lower()
        entidades_encontradas = {
            'paises': [],
            'empresas': [],
            'instituciones_mx': [],
            'productos': []
        }
        
        for tipo, lista in self.entidades.items():
            for entidad in lista:
                if entidad in texto_lower:
                    entidades_encontradas[tipo].append(entidad)
        
        return entidades_encontradas
    
    def analizar_sentimiento_basico(self, texto):
        """Análisis de sentimiento basado en palabras clave"""
        texto_lower = texto.lower()
        
        puntos_positivos = sum(1 for palabra in self.modificadores_positivos 
                              if palabra in texto_lower)
        puntos_negativos = sum(1 for palabra in self.modificadores_negativos 
                              if palabra in texto_lower)
        
        # Calcular score (-1 a 1)
        total = puntos_positivos + puntos_negativos
        if total == 0:
            return {'score': 0, 'clasificacion': 'neutral'}
        
        score = (puntos_positivos - puntos_negativos) / total
        
        # Clasificar
        if score > 0.3:
            return {'score': score, 'clasificacion': 'positivo'}
        elif score < -0.3:
            return {'score': score, 'clasificacion': 'negativo'}
        else:
            return {'score': score, 'clasificacion': 'neutral'}
    
    def detectar_categorias(self, texto):
        """Detecta categorías de eventos en el texto"""
        texto_lower = texto.lower()
        categorias_detectadas = {}
        
        for categoria, info in self.keywords.items():
            matches = sum(1 for palabra in info['palabras'] if palabra in texto_lower)
            if matches > 0:
                categorias_detectadas[categoria] = {
                    'matches': matches,
                    'peso': info['peso'],
                    'tipo': info['tipo']
                }
        
        return categorias_detectadas
    
    def detectar_magnitud(self, texto):
        """Detecta la magnitud del evento"""
        texto_lower = texto.lower()
        
        for nivel, indicadores in self.magnitudes.items():
            for indicador in indicadores:
                if indicador in texto_lower:
                    return nivel
        
        # Si no se detecta, usar porcentajes extraídos
        numeros = self.extraer_numeros(texto)
        if numeros['porcentajes']:
            max_pct = max(numeros['porcentajes'])
            if max_pct >= 20:
                return 'muy_alto'
            elif max_pct >= 10:
                return 'alto'
            elif max_pct >= 5:
                return 'medio'
            else:
                return 'bajo'
        
        return 'medio'  # default
    
    def calcular_score_impacto(self, analisis):
        """Calcula el score de impacto basado en el análisis"""
        score_base = 0
        
        # Factor de sentimiento
        sentimiento = analisis['sentimiento']
        score_base += sentimiento['score']
        
        # Factor de categorías
        for categoria, info in analisis['categorias'].items():
            peso_categoria = info['peso']
            tipo = info['tipo']
            
            if tipo == 'positivo':
                score_base += 0.2 * peso_categoria
            elif tipo == 'negativo':
                score_base -= 0.2 * peso_categoria
        
        # Factor de magnitud
        magnitud = analisis['magnitud']
        multiplicador_magnitud = {
            'muy_alto': 1.5,
            'alto': 1.2,
            'medio': 1.0,
            'bajo': 0.7
        }
        
        score_final = score_base * multiplicador_magnitud.get(magnitud, 1.0)
        
        # Normalizar entre -1 y 1
        score_final = max(-1, min(1, score_final))
        
        return score_final
    
    def estimar_impacto_indicadores(self, score_impacto, categorias, magnitud):
        """Estima el impacto en indicadores específicos"""
        
        # Factores base según score
        factor = abs(score_impacto)
        direccion = 1 if score_impacto > 0 else -1
        
        # Multiplicadores según magnitud
        mult = {
            'muy_alto': 1.5,
            'alto': 1.2,
            'medio': 1.0,
            'bajo': 0.6
        }.get(magnitud, 1.0)
        
        impactos = {}
        
        # Producción
        if 'aranceles' in categorias:
            impactos['produccion'] = -10 * factor * mult  # Aranceles reducen producción
        elif 'subsidios' in categorias or 'inversion' in categorias:
            impactos['produccion'] = 8 * factor * mult
        elif 'demanda' in categorias:
            impactos['produccion'] = 6 * direccion * factor * mult
        else:
            impactos['produccion'] = 3 * direccion * factor * mult
        
        # Exportaciones
        if 'aranceles' in categorias:
            impactos['exportaciones'] = -15 * factor * mult
        elif 'exportacion' in categorias:
            impactos['exportaciones'] = 10 * direccion * factor * mult
        else:
            impactos['exportaciones'] = 4 * direccion * factor * mult
        
        # Precios
        if 'aranceles' in categorias:
            impactos['precios'] = 5 * factor * mult  # Aranceles suben precios internos
        elif 'demanda' in categorias:
            impactos['precios'] = 4 * direccion * factor * mult
        else:
            impactos['precios'] = 2 * direccion * factor * mult
        
        # Empleo
        if 'crisis' in categorias or 'aranceles' in categorias:
            impactos['empleo'] = -5 * factor * mult
        elif 'inversion' in categorias or 'infraestructura' in categorias:
            impactos['empleo'] = 4 * factor * mult
        else:
            impactos['empleo'] = 2 * direccion * factor * mult
        
        # Importaciones
        if 'aranceles' in categorias:
            impactos['importaciones'] = -12 * factor * mult
        else:
            impactos['importaciones'] = 3 * direccion * factor * mult
        
        return impactos
    
    def analizar_noticia(self, titulo, contenido, fecha=None):
        """Análisis completo de una noticia"""
        
        if fecha is None:
            fecha = datetime.now()
        
        texto_completo = f"{titulo}. {contenido}"
        
        # Realizar análisis
        analisis = {
            'fecha': fecha,
            'titulo': titulo,
            'sentimiento': self.analizar_sentimiento_basico(texto_completo),
            'categorias': self.detectar_categorias(texto_completo),
            'entidades': self.detectar_entidades(texto_completo),
            'numeros': self.extraer_numeros(texto_completo),
            'magnitud': self.detectar_magnitud(texto_completo)
        }
        
        # Calcular score de impacto
        analisis['score_impacto'] = self.calcular_score_impacto(analisis)
        
        # Estimar impacto en indicadores
        analisis['impacto_indicadores'] = self.estimar_impacto_indicadores(
            analisis['score_impacto'],
            analisis['categorias'],
            analisis['magnitud']
        )
        
        return analisis
    
    def generar_resumen(self, analisis):
        """Genera un resumen textual del análisis"""
        titulo = analisis['titulo']
        score = analisis['score_impacto']
        sentimiento = analisis['sentimiento']['clasificacion']
        magnitud = analisis['magnitud']
        
        # Clasificación de impacto
        if abs(score) > 0.7:
            nivel_impacto = "MUY ALTO"
            emoji = "🔴" if score < 0 else "🟢"
        elif abs(score) > 0.4:
            nivel_impacto = "ALTO"
            emoji = "🟠" if score < 0 else "🟢"
        elif abs(score) > 0.2:
            nivel_impacto = "MODERADO"
            emoji = "🟡"
        else:
            nivel_impacto = "BAJO"
            emoji = "⚪"
        
        direccion = "NEGATIVO" if score < 0 else "POSITIVO" if score > 0 else "NEUTRAL"
        
        resumen = f"""
{emoji} IMPACTO {nivel_impacto} - {direccion}
Noticia: {titulo}
Score: {score:.2f} | Sentimiento: {sentimiento} | Magnitud: {magnitud}

CATEGORÍAS DETECTADAS:
"""
        
        for cat, info in analisis['categorias'].items():
            resumen += f"  • {cat.title()}: {info['matches']} menciones (peso: {info['peso']})\n"
        
        resumen += "\nENTIDADES MENCIONADAS:\n"
        for tipo, entidades in analisis['entidades'].items():
            if entidades:
                resumen += f"  • {tipo.title()}: {', '.join(entidades)}\n"
        
        resumen += "\nIMPACTO ESTIMADO EN INDICADORES (%):\n"
        for indicador, valor in analisis['impacto_indicadores'].items():
            signo = "+" if valor > 0 else ""
            resumen += f"  • {indicador.title()}: {signo}{valor:.1f}%\n"
        
        return resumen


# ============================================================================
# FUNCIÓN PRINCIPAL Y EJEMPLOS
# ============================================================================

def main():
    """Demostración del sistema"""
    
    print("=" * 80)
    print("SISTEMA DE ANÁLISIS DE IMPACTO EN LA INDUSTRIA DEL ACERO - MVP")
    print("=" * 80)
    print()
    
    # Crear analizador
    analyzer = SteelNewsAnalyzer()
    
    # Noticias de ejemplo
    noticias_ejemplo = [
        {
            'titulo': 'Donald Trump anuncia aranceles del 25% a importaciones de acero de México',
            'contenido': 'El presidente de Estados Unidos anunció hoy la imposición de aranceles del 25% '
                        'a todas las importaciones de acero provenientes de México, medida que entrará en '
                        'vigor el próximo trimestre. La industria siderúrgica mexicana exporta cerca de '
                        '5 mil millones de dólares anuales a Estados Unidos.',
            'fecha': datetime.now()
        },
        {
            'titulo': 'Ternium anuncia inversión de $2,000 millones en nueva planta en México',
            'contenido': 'La empresa siderúrgica Ternium anunció una inversión histórica de 2 mil millones '
                        'de dólares para construir una nueva planta de producción de acero en Nuevo León. '
                        'El proyecto generará 3,500 empleos directos y aumentará la capacidad de producción '
                        'en un 15%. La obra iniciará en el segundo trimestre de 2026.',
            'fecha': datetime.now() - timedelta(days=2)
        },
        {
            'titulo': 'Demanda de acero en México cae 8% por desaceleración en construcción',
            'contenido': 'La demanda de acero en México registró una caída del 8% en el último trimestre '
                        'debido a la desaceleración en el sector de la construcción. Los precios se han '
                        'reducido en un 5% y las empresas reportan menores pedidos. Analistas esperan '
                        'recuperación moderada en el próximo semestre.',
            'fecha': datetime.now() - timedelta(days=5)
        },
        {
            'titulo': 'Gobierno anuncia subsidio de $500 millones para modernizar industria del acero',
            'contenido': 'La Secretaría de Economía anunció un programa de subsidios por 500 millones de '
                        'dólares para apoyar la modernización de plantas de acero en México. El programa '
                        'busca mejorar la competitividad del sector y reducir emisiones. Se espera '
                        'beneficiar a 25 empresas siderúrgicas.',
            'fecha': datetime.now() - timedelta(days=1)
        },
        {
            'titulo': 'Infraestructura: Plan Nacional de carreteras impulsará demanda de acero 12%',
            'contenido': 'El nuevo Plan Nacional de Infraestructura contempla la construcción de 5,000 '
                        'kilómetros de carreteras en los próximos 3 años, lo que se estima aumentará '
                        'la demanda de acero en un 12%. El proyecto incluye la construcción de 150 puentes '
                        'y representa una inversión de $15,000 millones de dólares.',
            'fecha': datetime.now() - timedelta(days=3)
        }
    ]
    
    # Analizar cada noticia
    resultados = []
    
    for i, noticia in enumerate(noticias_ejemplo, 1):
        print(f"\n{'='*80}")
        print(f"ANÁLISIS DE NOTICIA #{i}")
        print('='*80)
        
        analisis = analyzer.analizar_noticia(
            noticia['titulo'],
            noticia['contenido'],
            noticia['fecha']
        )
        
        resultados.append(analisis)
        
        # Mostrar resumen
        resumen = analyzer.generar_resumen(analisis)
        print(resumen)
    
    # Análisis agregado
    print("\n" + "="*80)
    print("ANÁLISIS AGREGADO - ÚLTIMOS 7 DÍAS")
    print("="*80)
    
    # Calcular impacto promedio por indicador
    impacto_agregado = {
        'produccion': 0,
        'exportaciones': 0,
        'precios': 0,
        'empleo': 0,
        'importaciones': 0
    }
    
    for resultado in resultados:
        for indicador, valor in resultado['impacto_indicadores'].items():
            impacto_agregado[indicador] += valor
    
    # Promediar
    n = len(resultados)
    for indicador in impacto_agregado:
        impacto_agregado[indicador] /= n
    
    print("\nIMPACTO PROMEDIO ESTIMADO (%):")
    for indicador, valor in impacto_agregado.items():
        signo = "+" if valor > 0 else ""
        emoji = "📈" if valor > 0 else "📉" if valor < 0 else "➡️"
        print(f"  {emoji} {indicador.title()}: {signo}{valor:.1f}%")
    
    # Score general
    score_general = sum(r['score_impacto'] for r in resultados) / n
    print(f"\nSCORE DE IMPACTO GENERAL: {score_general:.2f}")
    
    if score_general > 0.3:
        print("📊 TENDENCIA GENERAL: POSITIVA para la industria del acero")
    elif score_general < -0.3:
        print("⚠️ TENDENCIA GENERAL: NEGATIVA para la industria del acero")
    else:
        print("📊 TENDENCIA GENERAL: NEUTRAL/MIXTA")
    
    # Guardar resultados en JSON
    print("\n" + "="*80)
    print("Guardando resultados...")
    
    # Convertir a formato serializable
    resultados_json = []
    for r in resultados:
        r_copy = r.copy()
        r_copy['fecha'] = r_copy['fecha'].isoformat()
        resultados_json.append(r_copy)

    import os
    output_path = os.path.join(os.getcwd(), 'analisis_noticias.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'fecha_analisis': datetime.now().isoformat(),
            'num_noticias': len(resultados),
            'score_general': float(score_general),
            'impacto_agregado': impacto_agregado,
            'noticias': resultados_json
        }, f, indent=2, ensure_ascii=False)
    
    print("✓ Resultados guardados en: analisis_noticias.json")
    
    # Crear DataFrame para análisis
    df_impactos = pd.DataFrame([r['impacto_indicadores'] for r in resultados])
    df_impactos.index = [f"Noticia {i+1}" for i in range(len(resultados))]
    
    print("\n" + "="*80)
    print("TABLA DE IMPACTOS POR NOTICIA")
    print("="*80)
    print(df_impactos.round(1))
    
    print("\n" + "="*80)
    print("ANÁLISIS COMPLETADO")
    print("="*80)

if __name__ == "__main__":
    main()