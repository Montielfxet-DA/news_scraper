#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  AGREGAR NOTICIAS MANUALMENTE A LA BD                        ║
║                                                                              ║
║  Permite añadir noticias que amigos/colegas te compartan directamente       ║
║  a la base de datos para análisis y etiquetado posterior.                   ║
║                                                                              ║
║  MODOS DE USO:                                                               ║
║    python agregar_noticia_manual.py                    # Modo interactivo   ║
║    python agregar_noticia_manual.py --csv archivo.csv  # Importar CSV       ║
║    python agregar_noticia_manual.py --txt archivo.txt  # Importar TXT       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import csv
import argparse
from datetime import datetime

# ── Rutas del proyecto ────────────────────────────────────────────────────────
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CORE_DIR)
sys.path.append(CORE_DIR)
# ─────────────────────────────────────────────────────────────────────────────

from news_database import NewsDatabase
from steel_news_analyzer import SteelNewsAnalyzer

# Configuración
DB_PATH = os.path.join(BASE_DIR, 'db', 'noticias_database.db')


# ============================================================================
# FUNCIONES DE ENTRADA
# ============================================================================

def agregar_noticia_interactiva():
    """Modo interactivo: pregunta datos uno por uno"""
    
    print("\n" + "="*70)
    print("📝 AGREGAR NOTICIA MANUALMENTE")
    print("="*70)
    print("Ingresa los datos de la noticia (presiona Enter sin escribir para omitir campos opcionales)\n")
    
    # Datos obligatorios
    titulo = input("📌 Título (requerido): ").strip()
    if not titulo:
        print("❌ El título es obligatorio.")
        return None
    
    print("\n📄 Contenido (requerido, presiona Enter dos veces para terminar):")
    contenido_lines = []
    while True:
        linea = input()
        if linea == "" and contenido_lines and contenido_lines[-1] == "":
            break
        contenido_lines.append(linea)
    contenido = "\n".join(contenido_lines).strip()
    
    if not contenido:
        print("❌ El contenido es obligatorio.")
        return None
    
    # Datos opcionales
    url = input("\n🔗 URL (opcional): ").strip() or None
    fuente = input("📰 Fuente (opcional, ej: 'Compartido por Juan'): ").strip() or "Manual"
    
    # Fecha
    fecha_str = input("📅 Fecha publicación (YYYY-MM-DD, Enter = hoy): ").strip()
    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            print("⚠️  Fecha inválida, usando fecha de hoy")
            fecha = datetime.now()
    else:
        fecha = datetime.now()
    
    # ¿Etiquetar como relevante ahora?
    etiquetar_ahora = input("\n🏷️  ¿Marcar como relevante ahora? (s/n, Enter = no): ").strip().lower()
    etiqueta = 1 if etiquetar_ahora == 's' else None
    
    return {
        'titulo': titulo,
        'contenido': contenido,
        'url': url,
        'fuente': fuente,
        'fecha': fecha,
        'etiqueta_manual': etiqueta
    }


def agregar_desde_csv(csv_path):
    """
    Importar noticias desde CSV.
    
    Formato esperado del CSV:
    titulo,contenido,url,fuente,fecha,relevante
    
    Ejemplo:
    "Ternium invierte en MX","La empresa...",http://...,El Economista,2026-02-17,1
    """
    
    if not os.path.exists(csv_path):
        print(f"❌ Archivo no encontrado: {csv_path}")
        return []
    
    noticias = []

    # Detectar encoding automáticamente
    import chardet

    with open(csv_path, 'rb') as f_raw:
        detected = chardet.detect(f_raw.read())
        encoding = detected.get('encoding', 'utf-8') or 'utf-8'

    with open(csv_path, 'r', encoding='latin-1') as f:
        reader = csv.DictReader(f, delimiter='\t')
        
        for row in reader:
            # Validar campos obligatorios
            if not row.get('titulo') or not row.get('contenido'):
                print(f"⚠️  Fila ignorada (falta título o contenido): {row}")
                continue
            
            # Parsear fecha
            fecha_str = row.get('fecha', '').strip()
            if fecha_str:
                try:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                except ValueError:
                    fecha = datetime.now()
            else:
                fecha = datetime.now()
            
            # Parsear relevancia
            relevante_str = row.get('relevante', '').strip().lower()
            etiqueta = None
            if relevante_str in ('1', 's', 'si', 'sí', 'yes', 'true'):
                etiqueta = 1
            elif relevante_str in ('0', 'n', 'no', 'false'):
                etiqueta = 0
            
            noticia = {
                'titulo': row['titulo'].strip(),
                'contenido': row['contenido'].strip(),
                'url': row.get('url', '').strip() or None,
                'fuente': row.get('fuente', 'CSV Import').strip(),
                'fecha': fecha,
                'etiqueta_manual': etiqueta
            }
            
            noticias.append(noticia)
    
    return noticias


def agregar_desde_txt(txt_path):
    """
    Importar noticias desde archivo TXT.
    
    Formato esperado:
    ---
    TITULO: Título de la noticia
    FUENTE: Nombre de la fuente (opcional)
    URL: http://... (opcional)
    FECHA: 2026-02-17 (opcional)
    RELEVANTE: s/n (opcional)
    
    Contenido de la noticia aquí.
    Puede tener múltiples líneas.
    ---
    
    (El separador --- indica el inicio de una nueva noticia)
    """
    
    if not os.path.exists(txt_path):
        print(f"❌ Archivo no encontrado: {txt_path}")
        return []
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        texto = f.read()
    
    noticias = []
    bloques = texto.split('---')
    
    for bloque in bloques:
        bloque = bloque.strip()
        if not bloque:
            continue
        
        lineas = bloque.split('\n')
        
        # Parsear campos
        titulo = None
        fuente = 'TXT Import'
        url = None
        fecha = datetime.now()
        etiqueta = None
        contenido_lines = []
        
        leyendo_contenido = False
        
        for linea in lineas:
            linea_stripped = linea.strip()
            
            if linea_stripped.upper().startswith('TITULO:'):
                titulo = linea_stripped[7:].strip()
            elif linea_stripped.upper().startswith('FUENTE:'):
                fuente = linea_stripped[7:].strip()
            elif linea_stripped.upper().startswith('URL:'):
                url = linea_stripped[4:].strip() or None
            elif linea_stripped.upper().startswith('FECHA:'):
                fecha_str = linea_stripped[6:].strip()
                try:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                except ValueError:
                    pass
            elif linea_stripped.upper().startswith('RELEVANTE:'):
                rel_str = linea_stripped[10:].strip().lower()
                if rel_str in ('s', 'si', 'sí', '1'):
                    etiqueta = 1
                elif rel_str in ('n', 'no', '0'):
                    etiqueta = 0
            elif linea_stripped == '':
                if titulo:  # Ya pasamos los metadatos
                    leyendo_contenido = True
            else:
                if leyendo_contenido or not any(k in linea_stripped.upper() for k in ['TITULO:', 'FUENTE:', 'URL:', 'FECHA:', 'RELEVANTE:']):
                    contenido_lines.append(linea)
        
        contenido = '\n'.join(contenido_lines).strip()
        
        if titulo and contenido:
            noticias.append({
                'titulo': titulo,
                'contenido': contenido,
                'url': url,
                'fuente': fuente,
                'fecha': fecha,
                'etiqueta_manual': etiqueta
            })
        else:
            print(f"⚠️  Bloque ignorado (falta título o contenido)")
    
    return noticias


# ============================================================================
# GUARDADO EN BASE DE DATOS
# ============================================================================

def guardar_noticias(noticias, analizar=True):
    """
    Guarda noticias en la base de datos.
    
    Args:
        noticias: Lista de diccionarios con datos de noticias
        analizar: Si True, analiza cada noticia con SteelNewsAnalyzer
    """
    
    if not noticias:
        print("\n⚠️  No hay noticias para guardar.")
        return
    
    db = NewsDatabase(DB_PATH)
    analyzer = SteelNewsAnalyzer() if analizar else None
    
    print(f"\n💾 Guardando {len(noticias)} noticia(s) en la base de datos...")
    
    guardadas = 0
    duplicadas = 0
    
    for noticia in noticias:
        # Analizar con SteelNewsAnalyzer si está habilitado
        if analyzer:
            analisis = analyzer.analizar_noticia(
                titulo=noticia['titulo'],
                contenido=noticia['contenido'],
                fecha=noticia['fecha']
            )
            
            # Combinar datos originales con análisis
            noticia_completa = {
                'titulo': noticia['titulo'],
                'contenido': noticia['contenido'],
                'url': noticia.get('url'),
                'fuente': noticia.get('fuente', 'Manual'),
                'fecha': noticia['fecha'],
                'categorias': analisis.get('categorias', {}),
                'entidades': analisis.get('entidades', {}),
                'score_impacto': analisis.get('score_impacto', 0),
                'sentimiento': analisis.get('sentimiento', {}),
                'magnitud': analisis.get('magnitud', 'medio'),
                'impacto_indicadores': analisis.get('impacto_indicadores', {}),
                'relevancia_score': 50,  # Valor neutral por defecto para manuales
                'relevancia_auto': 'incierto'
            }
        else:
            noticia_completa = {
                'titulo': noticia['titulo'],
                'contenido': noticia['contenido'],
                'url': noticia.get('url'),
                'fuente': noticia.get('fuente', 'Manual'),
                'fecha': noticia['fecha'],
                'relevancia_score': 50,
                'relevancia_auto': 'incierto'
            }
        
        # Guardar en BD
        noticia_id = db.guardar_noticia(noticia_completa)
        
        if noticia_id == -1:
            duplicadas += 1
        else:
            guardadas += 1
            
            # Si venía pre-etiquetada, guardar etiqueta
            if noticia.get('etiqueta_manual') is not None:
                db.etiquetar_noticia(
                    noticia_id=noticia_id,
                    es_relevante=(noticia['etiqueta_manual'] == 1),
                    usuario='manual_import'
                )
    
    db.cerrar()
    
    print(f"\n✅ Proceso completado:")
    print(f"   • Guardadas: {guardadas}")
    print(f"   • Duplicadas (ignoradas): {duplicadas}")
    
    if guardadas > 0:
        print(f"\n💡 Próximo paso:")
        print(f"   python Core/etiquetador_noticias.py")
        print(f"   (para etiquetar las noticias recién agregadas)")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Agregar noticias manualmente a la base de datos'
    )
    parser.add_argument('--csv', help='Importar desde archivo CSV')
    parser.add_argument('--txt', help='Importar desde archivo TXT')
    parser.add_argument('--no-analizar', action='store_true',
                       help='No analizar con SteelNewsAnalyzer (más rápido)')
    
    args = parser.parse_args()
    
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + "  📰 AGREGAR NOTICIAS MANUALMENTE  ".center(68) + "║")
    print("╚" + "═"*68 + "╝")
    
    # Determinar modo
    if args.csv:
        print(f"\n📂 Modo: Importar desde CSV ({args.csv})")
        noticias = agregar_desde_csv(args.csv)
    elif args.txt:
        print(f"\n📂 Modo: Importar desde TXT ({args.txt})")
        noticias = agregar_desde_txt(args.txt)
    else:
        print("\n📝 Modo: Interactivo")
        noticias = []
        
        while True:
            noticia = agregar_noticia_interactiva()
            
            if noticia:
                noticias.append(noticia)
                print(f"\n✅ Noticia agregada a la cola")
            
            continuar = input("\n¿Agregar otra noticia? (s/n): ").strip().lower()
            if continuar != 's':
                break
    
    # Guardar
    if noticias:
        analizar = not args.no_analizar
        guardar_noticias(noticias, analizar=analizar)
    else:
        print("\n⚠️  No se agregó ninguna noticia.")


# ============================================================================
# SCRIPT DE EJEMPLO
# ============================================================================

def generar_ejemplo_csv():
    """Genera un archivo CSV de ejemplo"""
    ejemplo = """titulo,contenido,url,fuente,fecha,relevante
"Ternium anuncia inversión en Monterrey","La empresa siderúrgica Ternium anunció una inversión de 500 millones de dólares para expandir su planta en Monterrey.",https://ejemplo.com,Compartido por Juan,2026-02-17,1
"Aranceles del 25% al acero","Estados Unidos impone aranceles del 25% a las importaciones de acero mexicano.",https://ejemplo2.com,Compartido por María,2026-02-15,1
"""
    
    with open('ejemplo_noticias.csv', 'w', encoding='utf-8') as f:
        f.write(ejemplo)
    
    print("✅ Archivo de ejemplo creado: ejemplo_noticias.csv")


def generar_ejemplo_txt():
    """Genera un archivo TXT de ejemplo"""
    ejemplo = """---
TITULO: Ternium anuncia inversión en Monterrey
FUENTE: Compartido por Juan
URL: https://ejemplo.com
FECHA: 2026-02-17
RELEVANTE: s

La empresa siderúrgica Ternium anunció una inversión de 500 millones
de dólares para expandir su planta en Monterrey, México.
---
TITULO: Aranceles del 25% al acero
FUENTE: Compartido por María
FECHA: 2026-02-15
RELEVANTE: s

Estados Unidos impone aranceles del 25% a las importaciones
de acero mexicano.
---
"""
    
    with open('ejemplo_noticias.txt', 'w', encoding='utf-8') as f:
        f.write(ejemplo)
    
    print("✅ Archivo de ejemplo creado: ejemplo_noticias.txt")


if __name__ == '__main__':
    # Descomentar para generar archivos de ejemplo
    # generar_ejemplo_csv()
    # generar_ejemplo_txt()
    
    main()
