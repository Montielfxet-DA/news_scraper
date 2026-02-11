#!/usr/bin/env python3
"""
Filtro de Relevancia de Noticias
Sistema para identificar y filtrar noticias relevantes vs irrelevantes
"""

import re
from typing import Dict, List, Tuple

class NewsRelevanceFilter:
    """
    Filtro inteligente que evalúa la relevancia de noticias
    para la industria del acero en México
    """
    
    def __init__(self, min_score=5):
        """
        Args:
            min_score: Score mínimo para considerar una noticia relevante (default: 5)
        """
        self.min_score = min_score
        
        # ====================================================================
        # PALABRAS CLAVE OBLIGATORIAS - Al menos UNA debe aparecer
        # ====================================================================
        self.keywords_sector = {
            # Productos y materiales
            'acero': 3,
            'acero inoxidable': 4,
            'lámina de acero': 4,
            'varilla': 3,
            'alambrón': 3,
            'riel': 3,
            'tubería': 2,
            'perfiles': 2,
            
            # Industria
            'siderúrgica': 5,
            'siderurgia': 5,
            'metalúrgica': 4,
            'fundición': 3,
            'alto horno': 4,
            'planta de acero': 4,
            'producción de acero': 5,
            
            # Empresas clave
            'ternium': 5,
            'ahmsa': 5,
            'altos hornos': 5,
            'arcelor mittal': 4,
            'deacero': 4,
            'simec': 4,
            'gerdau': 3,
            'tyasa': 3,
            
            # Asociaciones
            'canacero': 5,
            'cámara nacional del hierro': 5,
        }
        
        # ====================================================================
        # CONTEXTO MEXICANO - Debe tener al menos UNO
        # ====================================================================
        self.keywords_mexico = {
            # País
            'méxico': 3,
            'mexicano': 3,
            'mexicana': 3,
            
            # Ciudades/Estados importantes
            'monterrey': 2,
            'nuevo león': 2,
            'coahuila': 2,
            'monclova': 3,
            'ciudad de méxico': 2,
            'cdmx': 2,
            'puebla': 2,
            'veracruz': 2,
            'michoacán': 2,
            'lázaro cárdenas': 3,
            
            # Gobierno/Instituciones
            'secretaría de economía': 3,
            'gobierno federal': 2,
            'gobierno mexicano': 3,
            'tlcan': 3,
            't-mec': 3,
            'usmca': 3,
        }
        
        # ====================================================================
        # EVENTOS ECONÓMICOS/COMERCIALES - Suman puntos extra
        # ====================================================================
        self.keywords_eventos = {
            'arancel': 3,
            'aranceles': 3,
            'exportación': 2,
            'importación': 2,
            'producción': 2,
            'inversión': 2,
            'precio': 2,
            'demanda': 2,
            'oferta': 2,
            'subsidio': 3,
            'tarifa': 2,
            'dumping': 3,
            'déficit comercial': 3,
            'balanza comercial': 3,
            'cuota': 2,
        }
        
        # ====================================================================
        # INDICADORES DE CALIDAD - Noticias con datos concretos
        # ====================================================================
        self.indicadores_calidad = {
            'tiene_porcentajes': 2,      # Contiene X%
            'tiene_cantidades': 2,       # Contiene cifras como $X millones
            'tiene_fechas_futuras': 1,   # Menciona planes/proyecciones
            'es_actual': 1,              # Noticia reciente
        }
        
        # ====================================================================
        # PALABRAS DE EXCLUSIÓN - Indican que probablemente NO es relevante
        # ====================================================================
        self.keywords_exclusion = {
            # Deportes
            'futbol': -5,
            'fútbol': -5,
            'gol': -5,
            'partido': -3,
            'champions': -5,
            'mundial': -3,
            'liga mx': -5,
            'juego': -2,
            'jugador': -4,
            'entrenador': -4,
            
            # Entretenimiento
            'película': -5,
            'serie': -4,
            'actor': -5,
            'actriz': -5,
            'netflix': -5,
            'streaming': -4,
            'canción': -5,
            'música': -3,
            
            # Cocina
            'receta': -5,
            'ingrediente': -5,
            'cocina': -3,
            'platillo': -5,
            'restaurante': -3,
            
            # Otros sectores no relacionados
            'videojuego': -5,
            'smartphone': -4,
            'celular': -3,
            'aplicación móvil': -4,
            
            # Metáforas que usan "acero" pero no son del sector
            'nervios de acero': -5,
            'voluntad de acero': -5,
            'puño de acero': -5,
            'corazón de acero': -5,
        }
        
        # ====================================================================
        # PATRONES REGEX para detectar datos concretos
        # ====================================================================
        self.pattern_porcentaje = re.compile(r'\d+(?:\.\d+)?%')
        self.pattern_dinero = re.compile(r'\$\s*\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:millones?|mil\s+millones?|billones?))?')
        self.pattern_toneladas = re.compile(r'\d+(?:,\d{3})*(?:\.\d+)?\s*(?:toneladas?|mt|millones?\s+de\s+toneladas?)')
        
    def calcular_score(self, titulo: str, contenido: str) -> Tuple[int, Dict]:
        """
        Calcula el score de relevancia de una noticia
        
        Returns:
            (score, detalles): Tupla con el score total y dict con desglose
        """
        texto_completo = f"{titulo} {contenido}".lower()
        
        detalles = {
            'sector': 0,
            'mexico': 0,
            'eventos': 0,
            'calidad': 0,
            'exclusion': 0,
            'razones': []
        }
        
        # 1. PALABRAS CLAVE DEL SECTOR (OBLIGATORIO)
        for keyword, puntos in self.keywords_sector.items():
            if keyword.lower() in texto_completo:
                detalles['sector'] += puntos
                detalles['razones'].append(f"✓ Sector: '{keyword}' (+{puntos})")
        
        # 2. CONTEXTO MEXICANO (OBLIGATORIO)
        for keyword, puntos in self.keywords_mexico.items():
            if keyword.lower() in texto_completo:
                detalles['mexico'] += puntos
                detalles['razones'].append(f"✓ México: '{keyword}' (+{puntos})")
        
        # 3. EVENTOS ECONÓMICOS (BONUS)
        for keyword, puntos in self.keywords_eventos.items():
            if keyword.lower() in texto_completo:
                detalles['eventos'] += puntos
                detalles['razones'].append(f"✓ Evento: '{keyword}' (+{puntos})")
        
        # 4. INDICADORES DE CALIDAD (BONUS)
        # Tiene porcentajes
        if self.pattern_porcentaje.search(texto_completo):
            detalles['calidad'] += self.indicadores_calidad['tiene_porcentajes']
            detalles['razones'].append(f"✓ Contiene datos: porcentajes (+{self.indicadores_calidad['tiene_porcentajes']})")
        
        # Tiene cantidades monetarias
        if self.pattern_dinero.search(texto_completo):
            detalles['calidad'] += self.indicadores_calidad['tiene_cantidades']
            detalles['razones'].append(f"✓ Contiene datos: cifras monetarias (+{self.indicadores_calidad['tiene_cantidades']})")
        
        # Tiene cantidades de producción
        if self.pattern_toneladas.search(texto_completo):
            detalles['calidad'] += 1
            detalles['razones'].append(f"✓ Contiene datos: toneladas (+1)")
        
        # 5. PALABRAS DE EXCLUSIÓN (PENALIZACIÓN)
        for keyword, puntos in self.keywords_exclusion.items():
            if keyword.lower() in texto_completo:
                detalles['exclusion'] += puntos
                detalles['razones'].append(f"✗ Exclusión: '{keyword}' ({puntos})")
        
        # SCORE TOTAL
        score_total = (
            detalles['sector'] + 
            detalles['mexico'] + 
            detalles['eventos'] + 
            detalles['calidad'] + 
            detalles['exclusion']
        )
        
        return score_total, detalles
    
    def es_relevante(self, titulo: str, contenido: str, verbose=False) -> Tuple[bool, int, Dict]:
        """
        Determina si una noticia es relevante
        
        Args:
            titulo: Título de la noticia
            contenido: Contenido de la noticia
            verbose: Si True, muestra detalles del análisis
            
        Returns:
            (es_relevante, score, detalles)
        """
        score, detalles = self.calcular_score(titulo, contenido)
        
        # CRITERIOS DE ACEPTACIÓN
        es_relevante = (
            score >= self.min_score and  # Score mínimo
            detalles['sector'] > 0 and   # DEBE mencionar el sector
            detalles['mexico'] > 0       # DEBE mencionar México
        )
        
        # Agregar razón de rechazo si aplica
        if not es_relevante:
            if detalles['sector'] == 0:
                detalles['razones'].append("✗ RECHAZADO: No menciona sector del acero")
            if detalles['mexico'] == 0:
                detalles['razones'].append("✗ RECHAZADO: No menciona contexto mexicano")
            if score < self.min_score:
                detalles['razones'].append(f"✗ RECHAZADO: Score insuficiente ({score} < {self.min_score})")
        
        if verbose:
            self._print_analisis(titulo, es_relevante, score, detalles)
        
        return es_relevante, score, detalles
    
    def _print_analisis(self, titulo: str, es_relevante: bool, score: int, detalles: Dict):
        """Imprime análisis detallado de la noticia"""
        emoji = "✅" if es_relevante else "❌"
        estado = "RELEVANTE" if es_relevante else "IRRELEVANTE"
        
        print(f"\n{emoji} {estado} (Score: {score}/{self.min_score})")
        print(f"   Título: {titulo[:70]}...")
        print(f"   Desglose: Sector={detalles['sector']}, México={detalles['mexico']}, "
              f"Eventos={detalles['eventos']}, Calidad={detalles['calidad']}, "
              f"Exclusión={detalles['exclusion']}")
        
        if detalles['razones']:
            print("   Razones:")
            for razon in detalles['razones'][:5]:  # Mostrar top 5
                print(f"      {razon}")
    
    def filtrar_noticias(self, noticias: List[Dict], verbose=False) -> Tuple[List[Dict], List[Dict]]:
        """
        Filtra una lista de noticias
        
        Args:
            noticias: Lista de dicts con 'titulo' y 'contenido'
            verbose: Si True, muestra análisis de cada noticia
            
        Returns:
            (noticias_relevantes, noticias_rechazadas)
        """
        relevantes = []
        rechazadas = []
        
        print(f"\n🔍 FILTRANDO {len(noticias)} NOTICIAS...")
        print("="*80)
        
        for noticia in noticias:
            titulo = noticia.get('titulo', '')
            contenido = noticia.get('contenido', '')
            
            es_rel, score, detalles = self.es_relevante(titulo, contenido, verbose=verbose)
            
            # Agregar score y detalles a la noticia
            noticia['relevancia_score'] = score
            noticia['relevancia_detalles'] = detalles
            
            if es_rel:
                relevantes.append(noticia)
            else:
                rechazadas.append(noticia)
        
        print(f"\n✅ RESULTADO:")
        print(f"   Relevantes: {len(relevantes)}")
        print(f"   Rechazadas: {len(rechazadas)}")
        print("="*80)
        
        return relevantes, rechazadas
    
    def ajustar_umbral(self, nuevo_min_score: int):
        """Ajusta el score mínimo requerido"""
        self.min_score = nuevo_min_score
        print(f"✓ Nuevo score mínimo: {nuevo_min_score}")


# ============================================================================
# FUNCIÓN DE PRUEBA
# ============================================================================

def test_filtro():
    """Función de prueba con noticias de ejemplo"""
    
    filtro = NewsRelevanceFilter(min_score=5)
    
    # Noticias de prueba
    noticias_test = [
        {
            'titulo': 'Ternium anuncia inversión de $500 millones en planta de Monterrey',
            'contenido': 'La empresa siderúrgica Ternium anunció una inversión de 500 millones de dólares para expandir su planta en Monterrey, México. La producción aumentará 15%.',
            'tipo': 'RELEVANTE'
        },
        {
            'titulo': 'Jugador muestra nervios de acero en la final del Mundial',
            'contenido': 'El futbolista mexicano demostró tener nervios de acero al anotar el gol decisivo en el partido de ayer.',
            'tipo': 'IRRELEVANTE - Deportes'
        },
        {
            'titulo': 'Estados Unidos impone aranceles del 25% al acero mexicano',
            'contenido': 'El gobierno de Estados Unidos anunció nuevos aranceles del 25% a las importaciones de acero provenientes de México, afectando a Ternium y AHMSA.',
            'tipo': 'RELEVANTE'
        },
        {
            'titulo': 'Receta: Cómo limpiar tu sartén de acero inoxidable',
            'contenido': 'Te enseñamos el mejor método para mantener tu sartén de acero inoxidable como nueva usando ingredientes naturales.',
            'tipo': 'IRRELEVANTE - Cocina'
        },
        {
            'titulo': 'AHMSA enfrenta crisis financiera y amenaza con despidos',
            'contenido': 'La empresa Altos Hornos de México ubicada en Monclova, Coahuila, enfrenta problemas financieros que podrían resultar en el despido de 1,500 trabajadores.',
            'tipo': 'RELEVANTE'
        },
        {
            'titulo': 'Nueva película de acción con efectos especiales de última generación',
            'contenido': 'El director mexicano presenta su nueva película con increíbles efectos especiales y un presupuesto de 50 millones de dólares.',
            'tipo': 'IRRELEVANTE - Entretenimiento'
        }
    ]
    
    print("\n" + "="*80)
    print("PRUEBA DEL FILTRO DE RELEVANCIA")
    print("="*80)
    
    relevantes, rechazadas = filtro.filtrar_noticias(noticias_test, verbose=True)
    
    # Verificar resultados
    print("\n" + "="*80)
    print("VERIFICACIÓN DE RESULTADOS")
    print("="*80)
    
    correctas = 0
    total = len(noticias_test)
    
    for noticia in noticias_test:
        esperado = 'RELEVANTE' in noticia['tipo']
        obtenido = noticia in relevantes
        
        if esperado == obtenido:
            correctas += 1
            print(f"✅ Correcto: {noticia['titulo'][:50]}...")
        else:
            print(f"❌ Error: {noticia['titulo'][:50]}...")
            print(f"   Esperado: {'RELEVANTE' if esperado else 'IRRELEVANTE'}")
            print(f"   Obtenido: {'RELEVANTE' if obtenido else 'IRRELEVANTE'}")
    
    precision = (correctas / total) * 100
    print(f"\n📊 Precisión: {correctas}/{total} ({precision:.1f}%)")


if __name__ == "__main__":
    test_filtro()
