#!/usr/bin/env python3
"""
Etiquetador de Noticias - Interfaz Gráfica
Versión con GUI usando Tkinter para etiquetar noticias de forma visual
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import sys

# Agregar carpeta Core al path
sys.path.append(r'D:\Data Documents\Python Projects\news_scraper\Core')

from news_database import NewsDatabase, mostrar_estadisticas

# CONFIGURACIÓN
DB_PATH = r'D:\Data Documents\Python Projects\news_scraper\db\noticias_database.db'


class NewsLabelerGUI:
    """Interfaz gráfica para etiquetar noticias"""

    def __init__(self, root):
        self.root = root
        self.root.title("Etiquetador de Noticias - Industria del Acero")

        # Maximizar ventana o tamaño grande
        # Opción 1: Maximizar
        # self.root.state('zoomed')  # Windows
        # Si estás en Mac/Linux, usa: self.root.attributes('-zoomed', True)

        # Opción 2: Tamaño fijo más grande
        self.root.geometry("1400x900")

        # Hacer la ventana redimensionable
        self.root.resizable(True, True)

        # Base de datos
        self.db = NewsDatabase(DB_PATH)

        # Noticias pendientes
        self.noticias = []
        self.current_index = 0
        self.etiquetadas_sesion = 0

        # Colores
        self.color_relevante = "#2ecc71"  # Verde
        self.color_no_relevante = "#e74c3c"  # Rojo
        self.color_incierto = "#f39c12"  # Naranja

        self.setup_ui()
        self.cargar_noticias()
        self.mostrar_noticia_actual()

    def setup_ui(self):
        """Configurar la interfaz de usuario - VERSIÓN COMPACTA"""

        # HEADER
        header_frame = tk.Frame(self.root, bg="#34495e")
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        title_label = tk.Label(
            header_frame,
            text="📰 ETIQUETADOR DE NOTICIAS",
            font=("Arial", 13, "bold"),
            bg="#34495e",
            fg="white"
        )
        title_label.pack(pady=6)

        self.stats_label = tk.Label(
            header_frame,
            text="Cargando estadísticas...",
            font=("Arial", 8),
            bg="#34495e",
            fg="white"
        )
        self.stats_label.pack(pady=3)

        # PROGRESS BAR
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=10, pady=3)

        self.progress_label = tk.Label(
            progress_frame,
            text="Noticia 0 de 0",
            font=("Arial", 9, "bold")
        )
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(pady=3)

        # CONTENIDO
        content_frame = tk.Frame(self.root, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=3)

        # Metadata
        meta_frame = tk.Frame(content_frame, bg="#ecf0f1")
        meta_frame.pack(fill=tk.X, padx=5, pady=3)

        self.id_label = tk.Label(meta_frame, text="ID: -", font=("Arial", 8), bg="#ecf0f1", anchor="w")
        self.id_label.pack(side=tk.LEFT, padx=5)

        self.fecha_label = tk.Label(meta_frame, text="Fecha: -", font=("Arial", 8), bg="#ecf0f1", anchor="w")
        self.fecha_label.pack(side=tk.LEFT, padx=5)

        self.fuente_label = tk.Label(meta_frame, text="Fuente: -", font=("Arial", 8), bg="#ecf0f1", anchor="w")
        self.fuente_label.pack(side=tk.LEFT, padx=5)

        self.score_frame = tk.Frame(meta_frame, bg="#ecf0f1")
        self.score_frame.pack(side=tk.RIGHT, padx=5)

        tk.Label(self.score_frame, text="🤖 Auto:", font=("Arial", 8, "bold"), bg="#ecf0f1").pack(side=tk.LEFT)
        self.score_label = tk.Label(self.score_frame, text="Score: -", font=("Arial", 8), bg="#ecf0f1")
        self.score_label.pack(side=tk.LEFT, padx=3)

        # Título
        titulo_frame = tk.Frame(content_frame, bg="white")
        titulo_frame.pack(fill=tk.X, padx=5, pady=3)

        tk.Label(titulo_frame, text="📌 TÍTULO:", font=("Arial", 9, "bold"), bg="white", anchor="w").pack(anchor="w")

        self.titulo_text = tk.Text(titulo_frame, height=2, wrap=tk.WORD, font=("Arial", 10), bg="#f8f9fa",
                                   relief=tk.FLAT)
        self.titulo_text.pack(fill=tk.X, pady=2)
        self.titulo_text.config(state=tk.DISABLED)

        # Contenido
        contenido_frame = tk.Frame(content_frame, bg="white")
        contenido_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)

        tk.Label(contenido_frame, text="📄 CONTENIDO:", font=("Arial", 9, "bold"), bg="white", anchor="w").pack(
            anchor="w")

        self.contenido_text = scrolledtext.ScrolledText(
            contenido_frame, wrap=tk.WORD, font=("Arial", 9), bg="#f8f9fa", relief=tk.FLAT, height=12
        )
        self.contenido_text.pack(fill=tk.BOTH, expand=True, pady=2)
        self.contenido_text.config(state=tk.DISABLED)

        # BOTONES DE ACCIÓN
        action_frame = tk.Frame(self.root, bg="white")
        action_frame.pack(fill=tk.X, padx=10, pady=8)

        question_label = tk.Label(
            action_frame,
            text="¿Esta noticia es RELEVANTE?",
            font=("Arial", 11, "bold"),
            bg="white"
        )
        question_label.pack(pady=5)

        buttons_frame = tk.Frame(action_frame, bg="white")
        buttons_frame.pack(pady=5)

        self.btn_relevante = tk.Button(
            buttons_frame, text="✅ RELEVANTE", font=("Arial", 11, "bold"),
            bg=self.color_relevante, fg="white", width=16, height=2,
            command=lambda: self.etiquetar(1), cursor="hand2", relief=tk.RAISED, bd=3
        )
        self.btn_relevante.pack(side=tk.LEFT, padx=8)

        self.btn_no_relevante = tk.Button(
            buttons_frame, text="❌ NO RELEVANTE", font=("Arial", 11, "bold"),
            bg=self.color_no_relevante, fg="white", width=16, height=2,
            command=lambda: self.etiquetar(0), cursor="hand2", relief=tk.RAISED, bd=3
        )
        self.btn_no_relevante.pack(side=tk.LEFT, padx=8)

        self.btn_saltar = tk.Button(
            buttons_frame, text="⏭ SALTAR", font=("Arial", 10, "bold"),
            bg="#95a5a6", fg="white", width=14, height=2,
            command=self.saltar, cursor="hand2", relief=tk.RAISED, bd=3
        )
        self.btn_saltar.pack(side=tk.LEFT, padx=8)

        # Botón VER COMPLETO
        self.btn_ver_completo = tk.Button(
            buttons_frame,
            text="🔍 VER COMPLETO",
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white",
            width=14,
            height=2,
            command=self.ver_completo,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3
        )
        self.btn_ver_completo.pack(side=tk.LEFT, padx=8)

        # Botón ABRIR EN WEB
        self.btn_navegador = tk.Button(
            buttons_frame,
            text="🌐 ABRIR WEB",
            font=("Arial", 10, "bold"),
            bg="#16a085",
            fg="white",
            width=14,
            height=2,
            command=self.ver_en_navegador,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3
        )
        self.btn_navegador.pack(side=tk.LEFT, padx=8)

        # FOOTER
        footer_frame = tk.Frame(self.root, bg="#ecf0f1", height=25)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)

        help_text = "💡 [1] Relevante | [0] No Relevante | [S] Saltar | [Q] Salir"
        help_label = tk.Label(footer_frame, text=help_text, font=("Arial", 8), bg="#ecf0f1", fg="#7f8c8d")
        help_label.pack(pady=4)

        # Menú y atajos (sin cambios)
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Estadísticas", command=self.mostrar_estadisticas)
        file_menu.add_command(label="Exportar Dataset", command=self.exportar_dataset)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.salir)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Guía de Etiquetado", command=self.mostrar_ayuda)
        help_menu.add_command(label="Acerca de", command=self.acerca_de)

        self.root.bind('1', lambda e: self.etiquetar(1))
        self.root.bind('0', lambda e: self.etiquetar(0))
        self.root.bind('s', lambda e: self.saltar())
        self.root.bind('S', lambda e: self.saltar())
        self.root.bind('h', lambda e: self.mostrar_ayuda())
        self.root.bind('H', lambda e: self.mostrar_ayuda())
        self.root.bind('q', lambda e: self.salir())
        self.root.bind('Q', lambda e: self.salir())

        self.root.protocol("WM_DELETE_WINDOW", self.salir)

    def ver_en_navegador(self):
        """Abrir noticia en navegador"""
        if not self.noticias or self.current_index >= len(self.noticias):
            return

        noticia = self.noticias[self.current_index]
        url = noticia.get('url', '')

        if not url:
            messagebox.showwarning("Sin URL", "Esta noticia no tiene URL disponible")
            return

        import webbrowser
        webbrowser.open(url)

    def ver_completo(self):
        """Scraping del artículo completo"""
        if not self.noticias or self.current_index >= len(self.noticias):
            return

        noticia = self.noticias[self.current_index]
        url = noticia.get('url', '')

        if not url:
            messagebox.showwarning("Sin URL", "Esta noticia no tiene URL disponible")
            return

        loading = tk.Toplevel(self.root)
        loading.title("Cargando...")
        loading.geometry("300x100")
        tk.Label(loading, text="🔄 Descargando artículo completo...",
                 font=("Arial", 11)).pack(pady=30)
        loading.update()

        try:
            from newspaper import Article

            article = Article(url)
            article.download()
            article.parse()

            contenido_completo = article.text

            if not contenido_completo:
                raise Exception("No se pudo extraer contenido")

            loading.destroy()
            self.mostrar_ventana_contenido(contenido_completo, noticia['titulo'])

        except ImportError:
            loading.destroy()
            messagebox.showerror(
                "Librería Faltante",
                "Instala newspaper3k:\n\npip install newspaper3k"
            )
        except Exception as e:
            loading.destroy()
            messagebox.showerror(
                "Error",
                f"No se pudo obtener el contenido:\n{str(e)}"
            )

    def mostrar_ventana_contenido(self, contenido, titulo):
        """Muestra ventana con contenido completo"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Artículo Completo")
        ventana.geometry("800x600")

        titulo_label = tk.Label(
            ventana,
            text=titulo,
            font=("Arial", 12, "bold"),
            wraplength=750,
            justify=tk.LEFT,
            bg="#ecf0f1",
            padx=10,
            pady=10
        )
        titulo_label.pack(fill=tk.X)

        frame = tk.Frame(ventana)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="white"
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, contenido)
        text_widget.config(state=tk.DISABLED)

        btn_cerrar = tk.Button(
            ventana,
            text="Cerrar",
            command=ventana.destroy,
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            width=15
        )
        btn_cerrar.pack(pady=10)

    def cargar_noticias(self):
        """Cargar noticias pendientes de etiquetar"""
        self.noticias = self.db.obtener_no_etiquetadas(limit=100)
        self.current_index = 0
        self.actualizar_stats()

    def actualizar_stats(self):
        """Actualizar estadísticas en el header"""
        stats = self.db.obtener_estadisticas()

        stats_text = (
            f"Total: {stats['total']} | "
            f"Etiquetadas: {stats['etiquetadas']} | "
            f"Pendientes: {stats['no_etiquetadas']} | "
            f"En esta sesión: {self.etiquetadas_sesion}"
        )

        self.stats_label.config(text=stats_text)

        # Actualizar progress bar
        if self.noticias:
            progress = (self.current_index / len(self.noticias)) * 100
            self.progress_bar['value'] = progress
            self.progress_label.config(
                text=f"Noticia {self.current_index + 1} de {len(self.noticias)}"
            )

    def mostrar_noticia_actual(self):
        """Mostrar la noticia actual"""
        if not self.noticias:
            self.mostrar_fin()
            return

        if self.current_index >= len(self.noticias):
            self.mostrar_fin()
            return

        noticia = self.noticias[self.current_index]

        # Metadata
        self.id_label.config(text=f"ID: {noticia['id']}")
        self.fecha_label.config(text=f"📅 {noticia.get('fecha_publicacion', 'N/A')}")
        self.fuente_label.config(text=f"📍 {noticia.get('fuente', 'N/A')}")

        # Score automático
        score = noticia.get('relevancia_score', 0)
        relevancia_auto = noticia.get('relevancia_auto', 'incierto')

        color = self.color_incierto
        if relevancia_auto == 'relevante':
            color = self.color_relevante
        elif relevancia_auto == 'irrelevante':
            color = self.color_no_relevante

        self.score_label.config(
            text=f"Score: {score} ({relevancia_auto.upper()})",
            fg=color
        )

        # Título
        self.titulo_text.config(state=tk.NORMAL)
        self.titulo_text.delete(1.0, tk.END)
        self.titulo_text.insert(1.0, noticia.get('titulo', ''))
        self.titulo_text.config(state=tk.DISABLED)

        # Contenido
        contenido = noticia.get('contenido', '')
        if len(contenido) > 1000:
            contenido = contenido[:1000] + "\n\n... (contenido truncado)"

        self.contenido_text.config(state=tk.NORMAL)
        self.contenido_text.delete(1.0, tk.END)
        self.contenido_text.insert(1.0, contenido)
        self.contenido_text.config(state=tk.DISABLED)

        # Actualizar stats
        self.actualizar_stats()

    def etiquetar(self, etiqueta):
        """Etiquetar la noticia actual"""
        if not self.noticias or self.current_index >= len(self.noticias):
            return

        noticia = self.noticias[self.current_index]

        # Guardar etiqueta
        self.db.etiquetar_noticia(
            noticia_id=noticia['id'],
            es_relevante=bool(etiqueta),
            usuario=os.getenv('USERNAME', 'usuario')
        )

        self.etiquetadas_sesion += 1

        # Feedback visual
        if etiqueta == 1:
            self.flash_button(self.btn_relevante)
        else:
            self.flash_button(self.btn_no_relevante)

        # Siguiente noticia
        self.current_index += 1
        self.root.after(200, self.mostrar_noticia_actual)

    def flash_button(self, button):
        """Efecto visual al presionar botón"""
        original_color = button.cget('bg')
        button.config(relief=tk.SUNKEN)
        self.root.after(100, lambda: button.config(relief=tk.RAISED))

    def saltar(self):
        """Saltar noticia actual"""
        if not self.noticias or self.current_index >= len(self.noticias):
            return

        self.current_index += 1
        self.mostrar_noticia_actual()

    def mostrar_fin(self):
        """Mostrar mensaje de fin"""
        stats = self.db.obtener_estadisticas()

        mensaje = f"""
¡Sesión de Etiquetado Completada! 🎉

Estadísticas:
• Etiquetadas en esta sesión: {self.etiquetadas_sesion}
• Total etiquetadas: {stats['etiquetadas']}
• Pendientes: {stats['no_etiquetadas']}

Balance:
• Relevantes: {stats['relevantes_manual']}
• No relevantes: {stats['no_relevantes_manual']}
        """

        if stats['etiquetadas'] >= 100:
            mensaje += "\n\n✅ ¡Ya puedes entrenar un modelo de ML!"
        elif stats['etiquetadas'] >= 50:
            mensaje += f"\n\n💪 Buen progreso! {stats['etiquetadas']}/100"
        else:
            faltantes = 100 - stats['etiquetadas']
            mensaje += f"\n\n📝 Faltan ~{faltantes} para ML"

        respuesta = messagebox.askquestion(
            "Sesión Completada",
            mensaje + "\n\n¿Deseas cargar más noticias?",
            icon='info'
        )

        if respuesta == 'yes':
            self.cargar_noticias()
            self.mostrar_noticia_actual()
        else:
            self.root.quit()

    def mostrar_estadisticas(self):
        """Mostrar ventana de estadísticas detalladas"""
        stats = self.db.obtener_estadisticas()

        mensaje = f"""
📊 ESTADÍSTICAS COMPLETAS

NOTICIAS:
• Total en BD: {stats['total']}
• Etiquetadas manualmente: {stats['etiquetadas']}
• Pendientes: {stats['no_etiquetadas']}

ETIQUETAS MANUALES:
• Relevantes: {stats['relevantes_manual']}
• No relevantes: {stats['no_relevantes_manual']}
        """

        if stats['etiquetadas'] > 0:
            pct = (stats['relevantes_manual'] / stats['etiquetadas']) * 100
            mensaje += f"• Balance: {pct:.1f}% relevantes\n"

        mensaje += f"""
CLASIFICACIÓN AUTOMÁTICA:
• Relevantes: {stats['relevantes_auto']}
• No relevantes: {stats['no_relevantes_auto']}
• Inciertos: {stats['inciertos_auto']}
        """

        if stats['precision_filtro'] > 0:
            mensaje += f"\n📈 Precisión del filtro: {stats['precision_filtro']:.1f}%"

        messagebox.showinfo("Estadísticas", mensaje)

    def exportar_dataset(self):
        """Exportar dataset para ML"""
        try:
            self.db.exportar_para_ml('dataset_ml.csv')
            messagebox.showinfo(
                "Exportación Exitosa",
                "Dataset exportado a: dataset_ml.csv\n\n"
                "Ya puedes entrenar un modelo de ML!"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {e}")

    def mostrar_ayuda(self):
        """Mostrar guía de etiquetado"""
        ayuda = """
📖 GUÍA DE ETIQUETADO

✅ MARCA COMO RELEVANTE (1) SI:
• Habla de producción, venta o demanda de acero
• Menciona empresas del sector (Ternium, AHMSA, etc.)
• Trata sobre políticas/regulaciones que afectan la industria
• Incluye datos económicos del sector siderúrgico
• Impacta directamente a México o empresas mexicanas
• Menciona precios, aranceles, exportaciones del acero

❌ MARCA COMO NO RELEVANTE (0) SI:
• Usa 'acero' como metáfora (nervios de acero, etc.)
• Es de otro sector (deportes, entretenimiento, cocina)
• Habla de productos de consumo (sartenes, utensilios)
• No menciona México ni el contexto mexicano
• Es sobre construcción residencial sin mencionar acero

❓ EN CASO DE DUDA:
• Si PODRÍA afectar la industria → Marca RELEVANTE
• Si claramente no tiene relación → Marca NO RELEVANTE
• Puedes SALTAR si estás muy inseguro

⌨️ ATAJOS DE TECLADO:
• 1 = Relevante
• 0 = No Relevante
• S = Saltar
• H = Ayuda
• Q = Salir
        """

        messagebox.showinfo("Guía de Etiquetado", ayuda)

    def acerca_de(self):
        """Información sobre la aplicación"""
        about = """
📰 ETIQUETADOR DE NOTICIAS
Versión 2.0 - GUI

Sistema de etiquetado manual de noticias
para preparar datasets de Machine Learning.

Industria del Acero en México

Desarrollado con Tkinter
        """
        messagebox.showinfo("Acerca de", about)

    def salir(self):
        """Salir de la aplicación"""
        if self.etiquetadas_sesion > 0:
            respuesta = messagebox.askquestion(
                "Confirmar Salida",
                f"Has etiquetado {self.etiquetadas_sesion} noticias.\n\n"
                "¿Seguro que deseas salir?",
                icon='warning'
            )

            if respuesta == 'no':
                return

        self.db.cerrar()
        self.root.quit()


def main():
    """Función principal"""
    root = tk.Tk()
    app = NewsLabelerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()