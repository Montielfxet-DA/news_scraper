#!/usr/bin/env python3
"""
Sistema de Base de Datos para Noticias
Almacena todas las noticias analizadas para futuro entrenamiento de ML
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os

class NewsDatabase:
    """
    Base de datos SQLite para almacenar noticias y preparar datos de ML
    """
    
    def __init__(self, db_path='noticias_database.db'):
        """
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Conectar a la base de datos"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Permite acceder por nombre de columna
        self.cursor = self.conn.cursor()
    
    def _create_tables(self):
        """Crear tablas si no existen"""
        
        # Tabla principal de noticias
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS noticias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Información de la noticia
                titulo TEXT NOT NULL,
                contenido TEXT NOT NULL,
                url TEXT,
                fuente TEXT,
                fecha_publicacion DATETIME,
                fecha_analisis DATETIME NOT NULL,
                
                -- Análisis automático (del filtro de reglas)
                relevancia_score INTEGER,
                relevancia_auto TEXT,  -- 'relevante', 'irrelevante', 'incierto'
                
                -- Categorías detectadas (JSON)
                categorias_detectadas TEXT,
                entidades_detectadas TEXT,
                
                -- Score de impacto (del analizador)
                score_impacto REAL,
                sentimiento TEXT,
                magnitud TEXT,
                
                -- Impacto estimado en indicadores (JSON)
                impacto_indicadores TEXT,
                
                -- ETIQUETA MANUAL (para ML)
                etiqueta_manual INTEGER,  -- NULL, 0 (no relevante), 1 (relevante)
                etiqueta_fecha DATETIME,
                etiqueta_usuario TEXT,
                etiqueta_notas TEXT,
                
                -- Metadata
                version_sistema TEXT,
                
                UNIQUE(url, fecha_publicacion)  -- Evitar duplicados
            )
        ''')
        
        # Índices para búsquedas rápidas
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_fecha_analisis 
            ON noticias(fecha_analisis)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_etiqueta_manual 
            ON noticias(etiqueta_manual)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_relevancia_auto 
            ON noticias(relevancia_auto)
        ''')
        
        # Tabla de estadísticas (opcional)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS estadisticas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                total_analizadas INTEGER,
                relevantes_auto INTEGER,
                irrelevantes_auto INTEGER,
                etiquetadas_manual INTEGER,
                precision_estimada REAL,
                UNIQUE(fecha)
            )
        ''')
        
        self.conn.commit()
    
    def guardar_noticia(self, noticia_data: Dict) -> int:
        """
        Guarda una noticia analizada en la base de datos
        
        Args:
            noticia_data: Dict con toda la información de la noticia
            
        Returns:
            ID de la noticia insertada
        """
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO noticias (
                    titulo, contenido, url, fuente, fecha_publicacion,
                    fecha_analisis, relevancia_score, relevancia_auto,
                    categorias_detectadas, entidades_detectadas,
                    score_impacto, sentimiento, magnitud,
                    impacto_indicadores, version_sistema
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                noticia_data.get('titulo', ''),
                noticia_data.get('contenido', ''),
                noticia_data.get('url', ''),
                noticia_data.get('fuente', ''),
                noticia_data.get('fecha', datetime.now()),
                datetime.now(),
                noticia_data.get('relevancia_score', 0),
                noticia_data.get('relevancia_auto', 'incierto'),
                json.dumps(noticia_data.get('categorias', {})),
                json.dumps(noticia_data.get('entidades', {})),
                noticia_data.get('score_impacto', 0),
                noticia_data.get('sentimiento', {}).get('clasificacion', 'neutral'),
                noticia_data.get('magnitud', 'medio'),
                json.dumps(noticia_data.get('impacto_indicadores', {})),
                '1.0'
            ))
            
            self.conn.commit()
            return self.cursor.lastrowid
            
        except sqlite3.IntegrityError:
            # Noticia duplicada
            return -1
        except Exception as e:
            print(f"Error guardando noticia: {e}")
            return -1
    
    def etiquetar_noticia(self, noticia_id: int, es_relevante: bool, 
                         usuario='sistema', notas=''):
        """
        Agrega etiqueta manual a una noticia
        
        Args:
            noticia_id: ID de la noticia
            es_relevante: True si es relevante, False si no
            usuario: Nombre del usuario que etiqueta
            notas: Notas adicionales
        """
        self.cursor.execute('''
            UPDATE noticias 
            SET etiqueta_manual = ?,
                etiqueta_fecha = ?,
                etiqueta_usuario = ?,
                etiqueta_notas = ?
            WHERE id = ?
        ''', (
            1 if es_relevante else 0,
            datetime.now(),
            usuario,
            notas,
            noticia_id
        ))
        
        self.conn.commit()
    
    def obtener_no_etiquetadas(self, limit=50) -> List[Dict]:
        """
        Obtiene noticias que aún no han sido etiquetadas manualmente
        
        Args:
            limit: Número máximo de noticias a retornar
            
        Returns:
            Lista de noticias sin etiquetar
        """
        self.cursor.execute('''
            SELECT * FROM noticias
            WHERE etiqueta_manual IS NULL
            ORDER BY fecha_analisis DESC
            LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def obtener_etiquetadas(self) -> List[Dict]:
        """
        Obtiene todas las noticias etiquetadas manualmente
        Para entrenamiento de ML
        """
        self.cursor.execute('''
            SELECT * FROM noticias
            WHERE etiqueta_manual IS NOT NULL
            ORDER BY fecha_analisis DESC
        ''')
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas de la base de datos"""
        
        stats = {}
        
        # Total de noticias
        self.cursor.execute('SELECT COUNT(*) as total FROM noticias')
        stats['total'] = self.cursor.fetchone()['total']
        
        # Etiquetadas
        self.cursor.execute('''
            SELECT COUNT(*) as total FROM noticias 
            WHERE etiqueta_manual IS NOT NULL
        ''')
        stats['etiquetadas'] = self.cursor.fetchone()['total']
        
        # No etiquetadas
        stats['no_etiquetadas'] = stats['total'] - stats['etiquetadas']
        
        # Distribución de etiquetas
        self.cursor.execute('''
            SELECT 
                SUM(CASE WHEN etiqueta_manual = 1 THEN 1 ELSE 0 END) as relevantes,
                SUM(CASE WHEN etiqueta_manual = 0 THEN 1 ELSE 0 END) as no_relevantes
            FROM noticias
            WHERE etiqueta_manual IS NOT NULL
        ''')
        row = self.cursor.fetchone()
        stats['relevantes_manual'] = row['relevantes'] or 0
        stats['no_relevantes_manual'] = row['no_relevantes'] or 0
        
        # Distribución automática
        self.cursor.execute('''
            SELECT 
                SUM(CASE WHEN relevancia_auto = 'relevante' THEN 1 ELSE 0 END) as relevantes,
                SUM(CASE WHEN relevancia_auto = 'irrelevante' THEN 1 ELSE 0 END) as no_relevantes,
                SUM(CASE WHEN relevancia_auto = 'incierto' THEN 1 ELSE 0 END) as inciertos
            FROM noticias
        ''')
        row = self.cursor.fetchone()
        stats['relevantes_auto'] = row['relevantes'] or 0
        stats['no_relevantes_auto'] = row['no_relevantes'] or 0
        stats['inciertos_auto'] = row['inciertos'] or 0
        
        # Precisión del filtro automático (comparando con etiquetas manuales)
        if stats['etiquetadas'] > 0:
            self.cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE 
                        WHEN (relevancia_auto = 'relevante' AND etiqueta_manual = 1) OR
                             (relevancia_auto = 'irrelevante' AND etiqueta_manual = 0)
                        THEN 1 ELSE 0 
                    END) as correctas
                FROM noticias
                WHERE etiqueta_manual IS NOT NULL
                  AND relevancia_auto IN ('relevante', 'irrelevante')
            ''')
            row = self.cursor.fetchone()
            if row['total'] > 0:
                stats['precision_filtro'] = (row['correctas'] / row['total']) * 100
            else:
                stats['precision_filtro'] = 0
        else:
            stats['precision_filtro'] = 0
        
        return stats
    
    def exportar_para_ml(self, output_file='dataset_ml.csv'):
        """
        Exporta noticias etiquetadas a CSV para entrenamiento de ML
        """
        import pandas as pd
        
        etiquetadas = self.obtener_etiquetadas()
        
        if not etiquetadas:
            print("⚠️ No hay noticias etiquetadas para exportar")
            return
        
        # Convertir a DataFrame
        df = pd.DataFrame(etiquetadas)
        
        # Seleccionar columnas relevantes
        columnas = ['id', 'titulo', 'contenido', 'fecha_publicacion', 
                   'relevancia_score', 'score_impacto', 'sentimiento',
                   'etiqueta_manual']
        
        df_export = df[columnas].copy()
        df_export.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"✅ Dataset exportado a {output_file}")
        print(f"   Total: {len(df_export)} noticias")
        print(f"   Relevantes: {df_export['etiqueta_manual'].sum()}")
        print(f"   No relevantes: {len(df_export) - df_export['etiqueta_manual'].sum()}")
    
    def cerrar(self):
        """Cerrar conexión a la base de datos"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cerrar()


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def mostrar_estadisticas(db_path='noticias_database.db'):
    """Muestra estadísticas de la base de datos"""
    
    with NewsDatabase(db_path) as db:
        stats = db.obtener_estadisticas()
        
        print("\n" + "="*80)
        print("📊 ESTADÍSTICAS DE LA BASE DE DATOS")
        print("="*80)
        
        print(f"\n📰 NOTICIAS TOTALES: {stats['total']}")
        print(f"   • Etiquetadas manualmente: {stats['etiquetadas']}")
        print(f"   • Pendientes de etiquetar: {stats['no_etiquetadas']}")
        
        if stats['etiquetadas'] > 0:
            print(f"\n✅ ETIQUETAS MANUALES:")
            print(f"   • Relevantes: {stats['relevantes_manual']}")
            print(f"   • No relevantes: {stats['no_relevantes_manual']}")
            
            pct_relevantes = (stats['relevantes_manual'] / stats['etiquetadas']) * 100
            print(f"   • Balance: {pct_relevantes:.1f}% relevantes")
        
        print(f"\n🤖 CLASIFICACIÓN AUTOMÁTICA:")
        print(f"   • Relevantes: {stats['relevantes_auto']}")
        print(f"   • No relevantes: {stats['no_relevantes_auto']}")
        print(f"   • Inciertos: {stats['inciertos_auto']}")
        
        if stats['precision_filtro'] > 0:
            print(f"\n📈 PRECISIÓN DEL FILTRO: {stats['precision_filtro']:.1f}%")
            
            if stats['etiquetadas'] >= 50:
                print(f"\n💡 RECOMENDACIÓN: Tienes {stats['etiquetadas']} noticias etiquetadas.")
                print("   ¡Ya puedes entrenar un modelo de ML!")
            elif stats['etiquetadas'] >= 20:
                print(f"\n💡 PROGRESO: {stats['etiquetadas']}/100 noticias etiquetadas.")
                print("   Necesitas al menos 100 para entrenar ML.")
            else:
                print(f"\n💡 INICIO: {stats['etiquetadas']} noticias etiquetadas.")
                print("   Sigue etiquetando para alcanzar 100.")
        
        print("="*80 + "\n")


# ============================================================================
# SCRIPT DE PRUEBA
# ============================================================================

if __name__ == "__main__":
    
    # Crear/conectar a base de datos
    db = NewsDatabase('noticias_database.db')
    
    print("✅ Base de datos creada/conectada exitosamente")
    print(f"   Ubicación: {os.path.abspath(db.db_path)}")
    
    # Mostrar estadísticas
    mostrar_estadisticas('noticias_database.db')
    
    # Ejemplo de uso
    print("\n📝 EJEMPLO DE USO:\n")
    print("# Guardar una noticia")
    print("db.guardar_noticia({")
    print("    'titulo': 'Ternium invierte en México',")
    print("    'contenido': '...',")
    print("    'relevancia_score': 15,")
    print("    'relevancia_auto': 'relevante'")
    print("})")
    print()
    print("# Etiquetar manualmente")
    print("db.etiquetar_noticia(noticia_id=1, es_relevante=True)")
    print()
    print("# Exportar para ML")
    print("db.exportar_para_ml('dataset_ml.csv')")
    
    db.cerrar()
