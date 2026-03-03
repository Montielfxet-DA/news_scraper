#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║               DESCARGADOR DE DATOS DEL INEGI - INDUSTRIA DEL ACERO           ║
║                                                                              ║
║  Descarga series de tiempo del INEGI sobre:                                 ║
║    • Producción de acero                                                    ║
║    • Exportaciones e importaciones                                          ║
║    • Índice de precios                                                      ║
║    • Empleo en manufactura de metales                                       ║
║                                                                              ║
║  REQUISITOS:                                                                 ║
║    1. Solicitar token en: https://www.inegi.org.mx/app/desarrolladores/     ║
║    2. pip install requests pandas openpyxl matplotlib                        ║
║                                                                              ║
║  USO:                                                                        ║
║    python inegi_downloader.py --token TU_TOKEN_AQUI                         ║
║    python inegi_downloader.py --token TU_TOKEN_AQUI --años 10              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import argparse
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# ── Configuración ──────────────────────────────────────────────────────────
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CORE_DIR)
OUTPUT_DIR = os.path.join(BASE_DIR, 'Output', 'INEGI_Data')

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── URLs de la API del INEGI ───────────────────────────────────────────────
# Sintaxis oficial: INDICATOR/[IdIndicador]/[Idioma]/[ÁreaGeo]/[Recientes]/[Fuente]/[Versión]/[Token]
INEGI_API_SERIES = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/{serie}/es/00/false/BISE/2.0/{token}?type=json"


# ============================================================================
# SERIES DE TIEMPO CLAVE - INDUSTRIA DEL ACERO
# ============================================================================

# IDs obtenidos del Constructor de Consultas del INEGI
# https://www.inegi.org.mx/sistemas/api/indicadores/v1/

SERIES_INEGI = {

    # ────────────────────────────────────────────────────────────────────────
    # PRODUCCIÓN
    # ────────────────────────────────────────────────────────────────────────
    'produccion_volumen_fisico': {
        'id': '796224',
        'nombre': 'Índice de volumen físico de la producción (Manufactura)',
        'unidad': 'Índice',
        'frecuencia': 'mensual'
    },

    'produccion_capacidad_planta': {
        'id': '710380',
        'nombre': 'Capacidad de planta utilizada (Manufactura)',
        'unidad': 'Porcentaje',
        'frecuencia': 'mensual'
    },

    'produccion_bruta_manufactura': {
        'id': '5300000038',
        'nombre': 'Producción bruta total — Sector 31-33 Industrias manufactureras',
        'unidad': 'Miles de pesos',
        'frecuencia': 'anual'
    },

    'produccion_valor_construccion': {
        'id': '723135',
        'nombre': 'Valor de producción total — Sector 23 Construcción',
        'unidad': 'Miles de pesos',
        'frecuencia': 'mensual'
    },

    'produccion_tendencia_manufactura': {
        'id': '701490',
        'nombre': 'Índice Agregado de Tendencia — Industrias manufactureras',
        'unidad': 'Índice',
        'frecuencia': 'mensual'
    },

    'produccion_confianza_empresarial': {
        'id': '701570',
        'nombre': 'Indicador de Confianza Empresarial — Industrias manufactureras',
        'unidad': 'Índice',
        'frecuencia': 'mensual'
    },
}

# ============================================================================
# FUNCIONES DE DESCARGA
# ============================================================================

def descargar_serie(serie_id: str, token: str, años: int = 5) -> Optional[pd.DataFrame]:
    """
    Descarga una serie de tiempo del INEGI.
    
    Args:
        serie_id: ID de la serie en el sistema del INEGI
        token: Token de autenticación
        años: Años hacia atrás (no usado, la API devuelve serie completa)
        
    Returns:
        DataFrame con la serie de tiempo o None si falla
    """
    
    # Construir URL según documentación oficial
    url = INEGI_API_SERIES.format(serie=serie_id, token=token)
    
    try:
        print(f"  Descargando serie {serie_id}...", end=' ')
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error {response.status_code}")
            return None
        
        data = response.json()
        
        # Extraer datos según estructura oficial
        if 'Series' not in data or len(data['Series']) == 0:
            print("❌ Sin datos")
            return None
        
        serie = data['Series'][0]
        
        # Extraer nombre real del indicador (si viene en la respuesta)
        nombre_real = serie.get('INDICADOR', serie_id)
        
        # Parsear observaciones
        observaciones = serie.get('OBSERVATIONS', [])
        
        if not observaciones:
            print("❌ Sin observaciones")
            return None
        
        # Convertir a DataFrame
        registros = []
        for obs in observaciones:
            fecha_str = obs.get('TIME_PERIOD', '')
            valor_str = obs.get('OBS_VALUE', '')
            
            # Parsear fecha (puede venir como YYYY, YYYY/MM, YYYY/MM/DD)
            try:
                if len(fecha_str) == 4:  # Solo año
                    fecha = datetime.strptime(fecha_str, '%Y')
                elif '/' in fecha_str:
                    partes = fecha_str.split('/')
                    if len(partes) == 2:  # YYYY/MM
                        fecha = datetime.strptime(fecha_str, '%Y/%m')
                    elif len(partes) == 3:  # YYYY/MM/DD
                        fecha = datetime.strptime(fecha_str, '%Y/%m/%d')
                    else:
                        continue
                elif '-' in fecha_str:
                    if len(fecha_str) == 7:  # YYYY-MM
                        fecha = datetime.strptime(fecha_str, '%Y-%m')
                    else:  # YYYY-MM-DD
                        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
                else:
                    continue
            except:
                continue
            
            # Parsear valor
            try:
                valor = float(valor_str)
            except:
                continue
            
            registros.append({
                'fecha': fecha,
                'valor': valor
            })
        
        if not registros:
            print("❌ No se pudieron parsear datos")
            return None
        
        df = pd.DataFrame(registros)
        df = df.sort_values('fecha')
        
        # Filtrar por años si es necesario
        fecha_limite = datetime.now() - timedelta(days=años*365)
        df = df[df['fecha'] >= fecha_limite]
        
        print(f"✅ {len(df)} observaciones")
        return df
        
    except requests.exceptions.Timeout:
        print("❌ Timeout")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
        return None


def descargar_todas_las_series(token: str, años: int = 5) -> Dict[str, pd.DataFrame]:
    """
    Descarga todas las series definidas en SERIES_INEGI.
    
    Args:
        token: Token del INEGI
        años: Años de historia
        
    Returns:
        Diccionario {nombre_serie: DataFrame}
    """
    
    print("\n" + "="*70)
    print("📥 DESCARGANDO SERIES DEL INEGI")
    print("="*70)
    print(f"Periodo: {años} años hacia atrás")
    print(f"Total series: {len(SERIES_INEGI)}\n")
    
    resultados = {}
    exitosas = 0
    fallidas = 0
    
    for nombre, info in SERIES_INEGI.items():
        serie_id = info['id']
        
        df = descargar_serie(serie_id, token, años)
        
        if df is not None:
            df['serie_nombre'] = info['nombre']
            df['unidad'] = info['unidad']
            df['frecuencia'] = info['frecuencia']
            resultados[nombre] = df
            exitosas += 1
        else:
            fallidas += 1
    
    print(f"\n✅ Descarga completada:")
    print(f"   Exitosas: {exitosas}")
    print(f"   Fallidas: {fallidas}")
    
    return resultados


# ============================================================================
# PROCESAMIENTO Y ANÁLISIS
# ============================================================================

def calcular_cambios_porcentuales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula cambios porcentuales mes a mes y año a año.
    """
    df = df.copy()
    df = df.sort_values('fecha')
    
    # Cambio porcentual mensual
    df['cambio_mensual_%'] = df['valor'].pct_change() * 100
    
    # Cambio porcentual anual (12 meses atrás)
    df['cambio_anual_%'] = df['valor'].pct_change(periods=12) * 100
    
    # Promedio móvil 3 meses
    df['promedio_3m'] = df['valor'].rolling(window=3).mean()
    
    # Promedio móvil 12 meses
    df['promedio_12m'] = df['valor'].rolling(window=12).mean()
    
    return df


def generar_reporte_serie(nombre: str, df: pd.DataFrame, output_dir: str):
    """
    Genera gráficas y estadísticas para una serie.
    """
    
    # Calcular estadísticas
    df_proc = calcular_cambios_porcentuales(df)
    
    # Crear figura con 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle(f"{df['serie_nombre'].iloc[0]}", fontsize=14, fontweight='bold')
    
    # ── Gráfica 1: Serie temporal con promedios móviles ──
    ax1.plot(df_proc['fecha'], df_proc['valor'], label='Valor real', linewidth=1.5, alpha=0.7)
    ax1.plot(df_proc['fecha'], df_proc['promedio_3m'], label='Promedio 3 meses', linewidth=2)
    ax1.plot(df_proc['fecha'], df_proc['promedio_12m'], label='Promedio 12 meses', linewidth=2, linestyle='--')
    
    ax1.set_ylabel(f"{df['unidad'].iloc[0]}")
    ax1.set_title("Serie Temporal")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # ── Gráfica 2: Cambios porcentuales ──
    ax2.bar(df_proc['fecha'], df_proc['cambio_mensual_%'], alpha=0.6, label='Cambio mensual %')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.set_ylabel("Cambio %")
    ax2.set_xlabel("Fecha")
    ax2.set_title("Variación Porcentual Mensual")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Guardar
    filename = f"{nombre}_grafica.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  ✅ Gráfica: {filename}")


def consolidar_en_un_archivo(series: Dict[str, pd.DataFrame], output_dir: str):
    """
    Consolida todas las series en un solo archivo Excel con múltiples hojas.
    """
    
    excel_path = os.path.join(output_dir, 'series_inegi_consolidadas.xlsx')
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        
        # Hoja resumen
        resumen_data = []
        for nombre, df in series.items():
            resumen_data.append({
                'Serie': nombre,
                'Nombre completo': df['serie_nombre'].iloc[0],
                'Unidad': df['unidad'].iloc[0],
                'Frecuencia': df['frecuencia'].iloc[0],
                'Observaciones': len(df),
                'Fecha inicio': df['fecha'].min().strftime('%Y-%m-%d'),
                'Fecha fin': df['fecha'].max().strftime('%Y-%m-%d'),
                'Último valor': df['valor'].iloc[-1]
            })
        
        df_resumen = pd.DataFrame(resumen_data)
        df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
        
        # Una hoja por serie (con cambios porcentuales)
        for nombre, df in series.items():
            df_proc = calcular_cambios_porcentuales(df)
            
            # Seleccionar columnas relevantes
            df_export = df_proc[['fecha', 'valor', 'cambio_mensual_%', 'cambio_anual_%', 
                                 'promedio_3m', 'promedio_12m']].copy()
            
            # Renombrar para claridad
            df_export.columns = ['Fecha', 'Valor', 'Cambio mensual (%)', 
                                'Cambio anual (%)', 'Promedio 3M', 'Promedio 12M']
            
            # Escribir (limitar nombre de hoja a 31 caracteres)
            sheet_name = nombre[:31]
            df_export.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"\n✅ Archivo consolidado: series_inegi_consolidadas.xlsx")
    print(f"   Ubicación: {excel_path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Descargador de datos del INEGI - Industria del Acero'
    )
    parser.add_argument('--token', required=True, help='Token de autenticación del INEGI')
    parser.add_argument('--años', type=int, default=5, help='Años de historia (default: 5)')
    parser.add_argument('--sin-graficas', action='store_true', help='No generar gráficas')
    
    args = parser.parse_args()
    
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + "  📊 DESCARGADOR DE DATOS DEL INEGI  ".center(68) + "║")
    print("╚" + "═"*68 + "╝")
    
    # Validar token
    if args.token == 'TU_TOKEN_AQUI' or len(args.token) < 20:
        print("\n❌ Token inválido.")
        print("\n📝 Para obtener un token:")
        print("   1. Ve a: https://www.inegi.org.mx/app/desarrolladores/")
        print("   2. Regístrate con tu email")
        print("   3. Recibirás el token por correo (tarda ~2 horas)")
        print("\n   Luego ejecuta:")
        print("   python inegi_downloader.py --token TU_TOKEN_REAL")
        return
    
    # Descargar series
    series = descargar_todas_las_series(args.token, args.años)
    
    if not series:
        print("\n❌ No se pudo descargar ninguna serie.")
        print("   Verifica que el token sea válido.")
        return
    
    # Generar gráficas
    if not args.sin_graficas:
        print("\n" + "="*70)
        print("📈 GENERANDO GRÁFICAS")
        print("="*70)
        
        for nombre, df in series.items():
            generar_reporte_serie(nombre, df, OUTPUT_DIR)
    
    # Consolidar en Excel
    consolidar_en_un_archivo(series, OUTPUT_DIR)
    
    # Estadísticas finales
    print("\n" + "="*70)
    print("📊 ESTADÍSTICAS GENERALES")
    print("="*70)
    
    for nombre, df in series.items():
        df_proc = calcular_cambios_porcentuales(df)
        
        print(f"\n{nombre}:")
        print(f"  Último valor: {df_proc['valor'].iloc[-1]:.2f}")
        print(f"  Cambio mensual: {df_proc['cambio_mensual_%'].iloc[-1]:.2f}%")
        print(f"  Cambio anual: {df_proc['cambio_anual_%'].iloc[-1]:.2f}%")
    
    print("\n" + "="*70)
    print("✅ PROCESO COMPLETADO")
    print("="*70)
    print(f"\n📁 Archivos generados en: {OUTPUT_DIR}/")
    print(f"   • series_inegi_consolidadas.xlsx")
    if not args.sin_graficas:
        print(f"   • {len(series)} gráficas PNG")


if __name__ == '__main__':
    main()
