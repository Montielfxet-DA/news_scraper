#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          ENTRENADOR DE MODELOS ML - INDUSTRIA DEL ACERO EN MÉXICO           ║
║                                                                              ║
║  Entrena DOS modelos que REEMPLAZAN el filtro de reglas:                    ║
║    1. Clasificador Binario  → relevante (1) o no relevante (0)              ║
║    2. Predictor de Score    → score numérico 0-100                          ║
║                                                                              ║
║  USO:                                                                        ║
║    python train_ml_classifier.py                  # Entrenar                ║
║    python train_ml_classifier.py --eval           # Solo evaluar            ║
║    python train_ml_classifier.py --predict        # Probar con texto        ║
╚══════════════════════════════════════════════════════════════════════════════╝

DEPENDENCIAS:
    pip install scikit-learn pandas numpy joblib
"""

import os
import sys
import json
import sqlite3
import argparse
import warnings
warnings.filterwarnings('ignore')

# ── Rutas del proyecto ────────────────────────────────────────────────────────
# El script vive en Core/, así que la raíz del proyecto es un nivel arriba
CORE_DIR = os.path.dirname(os.path.abspath(__file__))   # .../news_scraper/Core
BASE_DIR = os.path.dirname(CORE_DIR)                    # .../news_scraper/

# Agregar carpeta Core al path para poder importar news_database, etc.
sys.path.append(CORE_DIR)
# ─────────────────────────────────────────────────────────────────────────────

import numpy as np
import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.svm import LinearSVC
from sklearn.model_selection import cross_val_score, StratifiedKFold, train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix,
    mean_absolute_error, r2_score,
    roc_auc_score
)
from sklearn.preprocessing import MinMaxScaler


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

DB_PATH         = os.path.join(BASE_DIR, 'db', 'noticias_database.db')  # Base de datos SQLite
MODELS_DIR      = os.path.join(BASE_DIR, 'ml_models')                   # Carpeta donde se guardan modelos
CLASSIFIER_FILE = 'clasificador_binario.pkl'                             # Clasificador relevante/no relevante
REGRESSOR_FILE  = 'predictor_score.pkl'                                  # Predictor de score numérico
MIN_NOTICIAS    = 50                                                      # Mínimo para entrenar


# ============================================================================
# CARGA DE DATOS
# ============================================================================

def cargar_datos_desde_bd(db_path: str) -> pd.DataFrame:
    """
    Lee las noticias etiquetadas manualmente desde la base de datos SQLite.
    Solo usa registros donde etiqueta_manual no es NULL.
    """
    if not os.path.exists(db_path):
        print(f"❌ No se encontró la base de datos: {db_path}")
        print("   Asegúrate de ejecutar este script desde la carpeta del proyecto.")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    query = """
        SELECT
            id,
            titulo,
            contenido,
            relevancia_score   AS score_reglas,
            etiqueta_manual    AS label
        FROM noticias
        WHERE etiqueta_manual IS NOT NULL
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"✅ Datos cargados: {len(df)} noticias etiquetadas")
    print(f"   • Relevantes    : {df['label'].sum()}")
    print(f"   • No relevantes : {(df['label'] == 0).sum()}")
    print(f"   • Balance       : {df['label'].mean()*100:.1f}% relevantes")

    return df


def preparar_texto(df: pd.DataFrame) -> pd.Series:
    """
    Combina título + contenido con más peso al título
    (se repite 3 veces para darle mayor peso en TF-IDF).
    """
    texto = (
        df['titulo'].fillna('').str.strip() + ' ' +
        df['titulo'].fillna('').str.strip() + ' ' +
        df['titulo'].fillna('').str.strip() + ' ' +
        df['contenido'].fillna('').str.strip()
    )
    return texto


def generar_score_supervisado(df: pd.DataFrame) -> pd.Series:
    """
    Convierte la etiqueta binaria + el score de reglas en un
    score supervisado 0-100 para entrenar el regresor.

    Lógica:
      - Relevante (1):     score en rango [55, 100]
      - No relevante (0):  score en rango [0,  45]
    El score_reglas original se usa para distribuir dentro del rango,
    de modo que el modelo aprenda matices (muy relevante vs algo relevante).
    """
    # Normalizar score_reglas al rango [-1, 1] usando percentiles
    sr = df['score_reglas'].fillna(0).astype(float)
    sr_norm = (sr - sr.min()) / (sr.max() - sr.min() + 1e-9)  # 0..1

    score_supervisado = np.where(
        df['label'] == 1,
        55 + sr_norm * 45,   # relevantes: 55..100
        0  + sr_norm * 45    # no relevantes: 0..45
    )

    return pd.Series(score_supervisado.round(1), index=df.index)


# ============================================================================
# ENTRENAMIENTO
# ============================================================================

def entrenar_clasificador(X_texto: pd.Series, y: pd.Series) -> Pipeline:
    """
    Entrena y compara 3 clasificadores binarios.
    Devuelve el mejor según AUC-ROC en validación cruzada.
    """
    print("\n" + "="*70)
    print("🤖 ENTRENANDO CLASIFICADOR BINARIO (relevante / no relevante)")
    print("="*70)

    candidatos = {
        'Regresión Logística': Pipeline([
            ('tfidf', TfidfVectorizer(
                analyzer='word',
                ngram_range=(1, 2),
                max_features=20_000,
                sublinear_tf=True,
                min_df=2
            )),
            ('clf', LogisticRegression(
                C=1.0,
                class_weight='balanced',
                max_iter=1000,
                random_state=42
            ))
        ]),
        'Random Forest': Pipeline([
            ('tfidf', TfidfVectorizer(
                analyzer='word',
                ngram_range=(1, 2),
                max_features=10_000,
                sublinear_tf=True,
                min_df=2
            )),
            ('clf', RandomForestClassifier(
                n_estimators=200,
                class_weight='balanced',
                random_state=42,
                n_jobs=-1
            ))
        ]),
        'SVM Lineal': Pipeline([
            ('tfidf', TfidfVectorizer(
                analyzer='word',
                ngram_range=(1, 2),
                max_features=15_000,
                sublinear_tf=True,
                min_df=2
            )),
            ('clf', LinearSVC(
                C=0.5,
                class_weight='balanced',
                max_iter=2000,
                random_state=42
            ))
        ]),
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    mejor_nombre  = None
    mejor_score   = -1
    mejor_modelo  = None

    for nombre, pipeline in candidatos.items():
        try:
            scores = cross_val_score(
                pipeline, X_texto, y,
                cv=cv, scoring='f1', n_jobs=-1
            )
            media = scores.mean()
            print(f"   {nombre:<25} F1-CV = {media:.3f}  (±{scores.std():.3f})")
            if media > mejor_score:
                mejor_score  = media
                mejor_nombre = nombre
                mejor_modelo = pipeline
        except Exception as e:
            print(f"   {nombre:<25} ⚠️  Error: {e}")

    print(f"\n   🏆 Mejor modelo: {mejor_nombre}  (F1 = {mejor_score:.3f})")

    # Entrenar con TODOS los datos
    mejor_modelo.fit(X_texto, y)

    # Reporte final en split 80/20
    X_tr, X_te, y_tr, y_te = train_test_split(
        X_texto, y, test_size=0.2, stratify=y, random_state=42
    )
    mejor_modelo_eval = type(mejor_modelo)
    mejor_modelo.fit(X_tr, y_tr)
    y_pred = mejor_modelo.predict(X_te)

    print("\n📊 REPORTE EN DATOS DE PRUEBA (20%):")
    print(classification_report(y_te, y_pred, target_names=['No relevante', 'Relevante']))

    # Reentrenar con el 100% de datos antes de guardar
    mejor_modelo.fit(X_texto, y)

    return mejor_modelo


def entrenar_regresor(X_texto: pd.Series, y_score: pd.Series) -> Pipeline:
    """
    Entrena y compara 2 regresores para predecir score 0-100.
    Devuelve el mejor según MAE en validación cruzada.
    """
    print("\n" + "="*70)
    print("📈 ENTRENANDO PREDICTOR DE SCORE (0-100)")
    print("="*70)

    candidatos = {
        'Ridge Regression': Pipeline([
            ('tfidf', TfidfVectorizer(
                analyzer='word',
                ngram_range=(1, 2),
                max_features=20_000,
                sublinear_tf=True,
                min_df=2
            )),
            ('reg', Ridge(alpha=1.0))
        ]),
        'Gradient Boosting': Pipeline([
            ('tfidf', TfidfVectorizer(
                analyzer='word',
                ngram_range=(1, 2),
                max_features=10_000,
                sublinear_tf=True,
                min_df=2
            )),
            ('reg', GradientBoostingRegressor(
                n_estimators=200,
                max_depth=4,
                learning_rate=0.05,
                random_state=42
            ))
        ]),
    }

    mejor_nombre  = None
    mejor_mae     = 999
    mejor_modelo  = None

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for nombre, pipeline in candidatos.items():
        try:
            scores = cross_val_score(
                pipeline, X_texto, y_score,
                cv=5, scoring='neg_mean_absolute_error', n_jobs=-1
            )
            mae = -scores.mean()
            print(f"   {nombre:<25} MAE-CV = {mae:.2f}  (±{scores.std():.2f})")
            if mae < mejor_mae:
                mejor_mae    = mae
                mejor_nombre = nombre
                mejor_modelo = pipeline
        except Exception as e:
            print(f"   {nombre:<25} ⚠️  Error: {e}")

    print(f"\n   🏆 Mejor modelo: {mejor_nombre}  (MAE = {mejor_mae:.2f} puntos)")

    # Evaluación en split 80/20
    X_tr, X_te, y_tr, y_te = train_test_split(
        X_texto, y_score, test_size=0.2, random_state=42
    )
    mejor_modelo.fit(X_tr, y_tr)
    y_pred = mejor_modelo.predict(X_te).clip(0, 100)

    mae_final = mean_absolute_error(y_te, y_pred)
    r2_final  = r2_score(y_te, y_pred)

    print(f"\n📊 RESULTADO EN DATOS DE PRUEBA (20%):")
    print(f"   MAE = {mae_final:.2f} puntos  (error promedio)")
    print(f"   R²  = {r2_final:.3f}         (varianza explicada)")

    # Reentrenar con 100% antes de guardar
    mejor_modelo.fit(X_texto, y_score)

    return mejor_modelo


# ============================================================================
# GUARDADO DE MODELOS
# ============================================================================

def guardar_modelos(clasificador, regresor, df: pd.DataFrame):
    """Guarda ambos modelos en disco junto con metadata."""

    os.makedirs(MODELS_DIR, exist_ok=True)

    clf_path = os.path.join(MODELS_DIR, CLASSIFIER_FILE)
    reg_path = os.path.join(MODELS_DIR, REGRESSOR_FILE)
    meta_path = os.path.join(MODELS_DIR, 'metadata.json')

    joblib.dump(clasificador, clf_path)
    joblib.dump(regresor,     reg_path)

    metadata = {
        'noticias_entrenamiento': len(df),
        'relevantes':   int(df['label'].sum()),
        'no_relevantes': int((df['label'] == 0).sum()),
        'modelos': {
            'clasificador': CLASSIFIER_FILE,
            'regresor':     REGRESSOR_FILE
        },
        'version': '1.0'
    }

    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n✅ MODELOS GUARDADOS EN: {os.path.abspath(MODELS_DIR)}/")
    print(f"   • {CLASSIFIER_FILE}")
    print(f"   • {REGRESSOR_FILE}")
    print(f"   • metadata.json")


# ============================================================================
# ACTUALIZAR BASE DE DATOS CON PREDICCIONES ML
# ============================================================================

def actualizar_bd_con_ml(clasificador, regresor, db_path: str):
    """
    Recorre TODAS las noticias de la BD (no solo etiquetadas)
    y actualiza relevancia_score y relevancia_auto con las predicciones ML.
    """
    print("\n" + "="*70)
    print("🔄 ACTUALIZANDO BASE DE DATOS CON PREDICCIONES ML")
    print("="*70)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Leer todas las noticias
    df_all = pd.read_sql_query(
        "SELECT id, titulo, contenido FROM noticias",
        conn
    )

    if df_all.empty:
        print("⚠️  No hay noticias en la base de datos.")
        conn.close()
        return

    print(f"   Procesando {len(df_all)} noticias...")

    # Preparar texto
    texto = (
        df_all['titulo'].fillna('').str.strip() + ' ' +
        df_all['titulo'].fillna('').str.strip() + ' ' +
        df_all['titulo'].fillna('').str.strip() + ' ' +
        df_all['contenido'].fillna('').str.strip()
    )

    # Predecir
    labels_pred  = clasificador.predict(texto)
    scores_pred  = regresor.predict(texto).clip(0, 100).round(1)

    # Mapear label → texto
    auto_map = {1: 'relevante', 0: 'irrelevante'}

    # Actualizar en BD
    cursor = conn.cursor()
    actualizados = 0

    for idx, row in df_all.iterrows():
        nid    = row['id']
        label  = int(labels_pred[idx])
        score  = float(scores_pred[idx])
        auto   = auto_map[label]

        cursor.execute("""
            UPDATE noticias
            SET relevancia_score = ?,
                relevancia_auto  = ?
            WHERE id = ?
        """, (score, auto, nid))
        actualizados += 1

    conn.commit()
    conn.close()

    print(f"   ✅ {actualizados} noticias actualizadas")
    print(f"   • relevancia_score → predicción ML (0-100)")
    print(f"   • relevancia_auto  → predicción ML (relevante/irrelevante)")

    n_rel = int(labels_pred.sum())
    n_irr = len(labels_pred) - n_rel
    print(f"\n   📊 Distribución:")
    print(f"      Relevantes   : {n_rel}")
    print(f"      Irrelevantes : {n_irr}")


# ============================================================================
# CLASE PÚBLICA: MLRelevanceFilter
# (Reemplaza a NewsRelevanceFilter en el sistema principal)
# ============================================================================

class MLRelevanceFilter:
    """
    Drop-in replacement de NewsRelevanceFilter.
    Usa los modelos ML entrenados para clasificar noticias.

    USO en steel_impact_system_REAL.py:
        from train_ml_classifier import MLRelevanceFilter
        filtro = MLRelevanceFilter()
        noticias_relevantes, rechazadas = filtro.filtrar_noticias(noticias)
    """

    def __init__(self, models_dir: str = MODELS_DIR, umbral: float = 0.5):
        """
        Args:
            models_dir: Carpeta donde están los modelos guardados.
            umbral: Probabilidad mínima para considerar relevante (0.0-1.0).
        """
        self.models_dir = models_dir
        self.umbral     = umbral
        self._clf       = None
        self._reg       = None
        self._cargar_modelos()

    def _cargar_modelos(self):
        clf_path = os.path.join(self.models_dir, CLASSIFIER_FILE)
        reg_path = os.path.join(self.models_dir, REGRESSOR_FILE)

        if not os.path.exists(clf_path) or not os.path.exists(reg_path):
            raise FileNotFoundError(
                f"❌ Modelos no encontrados en '{self.models_dir}'.\n"
                f"   Ejecuta primero: python train_ml_classifier.py"
            )

        self._clf = joblib.load(clf_path)
        self._reg = joblib.load(reg_path)

    def _texto(self, titulo: str, contenido: str) -> str:
        t = (titulo or '').strip()
        c = (contenido or '').strip()
        return f"{t} {t} {t} {c}"

    def es_relevante(self, titulo: str, contenido: str, verbose: bool = False):
        """
        Devuelve (es_relevante: bool, score: float, detalles: dict)
        Compatible con la interfaz de NewsRelevanceFilter.
        """
        texto   = self._texto(titulo, contenido)
        label   = int(self._clf.predict([texto])[0])
        score   = float(self._reg.predict([texto])[0])
        score   = round(min(max(score, 0), 100), 1)

        # Intentar obtener probabilidad si el clasificador lo soporta
        try:
            proba = float(self._clf.predict_proba([texto])[0][1])
        except AttributeError:
            # LinearSVC no tiene predict_proba por defecto
            proba = 1.0 if label == 1 else 0.0

        es_rel = proba >= self.umbral

        detalles = {
            'ml_label':      label,
            'ml_score':      score,
            'ml_proba':      round(proba, 3),
            'decision':      'relevante' if es_rel else 'irrelevante',
            'razones':       [
                f"🤖 ML score: {score:.1f}/100",
                f"🤖 ML probabilidad: {proba:.1%}",
            ]
        }

        if verbose:
            print(f"\n📊 ML ANÁLISIS: '{titulo[:60]}...'")
            print(f"   Score   : {score:.1f}/100")
            print(f"   Proba   : {proba:.1%}")
            print(f"   Decisión: {'✅ RELEVANTE' if es_rel else '❌ IRRELEVANTE'}")

        return es_rel, score, detalles

    def filtrar_noticias(self, noticias: list, verbose: bool = False):
        """
        Filtra lista de noticias.
        Devuelve (relevantes, rechazadas) igual que NewsRelevanceFilter.
        """
        relevantes = []
        rechazadas = []

        for noticia in noticias:
            titulo   = noticia.get('titulo', '')
            contenido = noticia.get('contenido', '')

            es_rel, score, detalles = self.es_relevante(titulo, contenido, verbose)

            noticia['relevancia_score']   = score
            noticia['relevancia_auto']    = detalles['decision']
            noticia['relevancia_detalles'] = detalles

            if es_rel:
                relevantes.append(noticia)
            else:
                rechazadas.append(noticia)

        print(f"\n✅ FILTRO ML:")
        print(f"   Relevantes  : {len(relevantes)}")
        print(f"   Rechazadas  : {len(rechazadas)}")

        return relevantes, rechazadas


# ============================================================================
# MODO INTERACTIVO: probar predicción con texto libre
# ============================================================================

def modo_prediccion_interactiva():
    """Permite probar el modelo con noticias de prueba."""
    print("\n" + "="*70)
    print("🔬 MODO PRUEBA INTERACTIVA")
    print("="*70)
    print("Escribe 'salir' para terminar.\n")

    try:
        filtro = MLRelevanceFilter()
    except FileNotFoundError as e:
        print(e)
        return

    while True:
        titulo = input("\n📌 Título   : ").strip()
        if titulo.lower() == 'salir':
            break

        contenido = input("📄 Contenido (opcional): ").strip()

        es_rel, score, detalles = filtro.es_relevante(titulo, contenido, verbose=True)
        print(f"\n   → {'✅ RELEVANTE' if es_rel else '❌ NO RELEVANTE'}  |  Score ML: {score:.1f}/100")


# ============================================================================
# EVALUACIÓN DE MODELOS YA ENTRENADOS
# ============================================================================

def evaluar_modelos():
    """Carga modelos existentes y muestra métricas en los datos etiquetados."""
    print("\n" + "="*70)
    print("📊 EVALUACIÓN DE MODELOS EXISTENTES")
    print("="*70)

    try:
        filtro = MLRelevanceFilter()
    except FileNotFoundError as e:
        print(e)
        return

    df = cargar_datos_desde_bd(DB_PATH)
    if len(df) < MIN_NOTICIAS:
        print(f"⚠️  Solo hay {len(df)} noticias etiquetadas.")
        return

    texto = preparar_texto(df)

    # Clasificador
    y_pred = filtro._clf.predict(texto)
    print("\n🤖 CLASIFICADOR BINARIO:")
    print(classification_report(df['label'], y_pred, target_names=['No relevante', 'Relevante']))

    # Regresor
    y_score_sup = generar_score_supervisado(df)
    s_pred = filtro._reg.predict(texto).clip(0, 100)
    mae = mean_absolute_error(y_score_sup, s_pred)
    r2  = r2_score(y_score_sup, s_pred)

    print(f"\n📈 PREDICTOR DE SCORE:")
    print(f"   MAE = {mae:.2f} puntos  |  R² = {r2:.3f}")

    # Metadata
    meta_path = os.path.join(MODELS_DIR, 'metadata.json')
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        print(f"\n📁 MODELOS ENTRENADOS CON: {meta['noticias_entrenamiento']} noticias")


# ============================================================================
# FLUJO PRINCIPAL
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Entrena modelos ML para clasificación de noticias de acero'
    )
    parser.add_argument('--eval',    action='store_true', help='Solo evaluar modelos existentes')
    parser.add_argument('--predict', action='store_true', help='Modo prueba interactiva')
    parser.add_argument('--update-db', action='store_true',
                        help='Actualizar BD con predicciones ML (sin re-entrenar)')
    args = parser.parse_args()

    # ── Modo evaluación ──────────────────────────────────────────────────────
    if args.eval:
        evaluar_modelos()
        return

    # ── Modo predicción interactiva ───────────────────────────────────────────
    if args.predict:
        modo_prediccion_interactiva()
        return

    # ── Modo actualizar BD ────────────────────────────────────────────────────
    if args.update_db:
        try:
            clf = joblib.load(os.path.join(MODELS_DIR, CLASSIFIER_FILE))
            reg = joblib.load(os.path.join(MODELS_DIR, REGRESSOR_FILE))
            actualizar_bd_con_ml(clf, reg, DB_PATH)
        except FileNotFoundError:
            print("❌ No se encontraron modelos. Entrena primero sin --update-db")
        return

    # ── Entrenamiento completo ────────────────────────────────────────────────
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + "  🤖 ENTRENADOR ML - SISTEMA DE NOTICIAS DE ACERO  ".center(68) + "║")
    print("╚" + "═"*68 + "╝")

    # 1. Cargar datos
    df = cargar_datos_desde_bd(DB_PATH)

    if len(df) < MIN_NOTICIAS:
        print(f"\n⚠️  Solo tienes {len(df)} noticias etiquetadas.")
        print(f"   Se necesitan al menos {MIN_NOTICIAS}. Sigue etiquetando.")
        sys.exit(1)

    # 2. Preparar features
    X_texto   = preparar_texto(df)
    y_label   = df['label']
    y_score   = generar_score_supervisado(df)

    # 3. Entrenar modelos
    clasificador = entrenar_clasificador(X_texto, y_label)
    regresor     = entrenar_regresor(X_texto, y_score)

    # 4. Guardar modelos
    guardar_modelos(clasificador, regresor, df)

    # 5. Actualizar BD con predicciones ML
    actualizar_bd_con_ml(clasificador, regresor, DB_PATH)

    # 6. Instrucciones de uso
    print("\n" + "="*70)
    print("🚀 INTEGRACIÓN EN TU SISTEMA PRINCIPAL")
    print("="*70)
    print("""
Para usar el filtro ML en steel_impact_system_REAL.py,
REEMPLAZA la línea:

  from Core.news_relevance_filter import NewsRelevanceFilter
  filtro = NewsRelevanceFilter(min_score=2)

POR:

  from train_ml_classifier import MLRelevanceFilter
  filtro = MLRelevanceFilter()

¡El resto del código no cambia!  El MLRelevanceFilter tiene
la misma interfaz (filtrar_noticias, es_relevante).
""")

    print("="*70)
    print("📅 PRÓXIMOS PASOS")
    print("="*70)
    print("""
  1. Integra MLRelevanceFilter en steel_impact_system_REAL.py (ver arriba)
  2. Ejecuta el sistema normalmente y observa los nuevos scores ML
  3. Cuando tengas 100 noticias más etiquetadas, re-entrena:
       python train_ml_classifier.py
  4. Para actualizar la BD sin re-entrenar:
       python train_ml_classifier.py --update-db
  5. Para evaluar el modelo actual:
       python train_ml_classifier.py --eval
  6. Para probar con una noticia de texto libre:
       python train_ml_classifier.py --predict
""")


if __name__ == '__main__':
    main()
