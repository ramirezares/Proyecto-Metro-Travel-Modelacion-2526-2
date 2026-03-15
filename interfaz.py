"""
interfaz.py - Módulo de Interfaz Gráfica para Metro Travel

Este módulo implementa la interfaz gráfica de usuario (GUI) utilizando tkinter,
siguiendo el diseño de referencia del "Sistema de Rutas - Bogotá" adaptado
a las necesidades del proyecto Metro Travel.

Colores institucionales: Naranja y Azul (UNIMET).
"""

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog, messagebox
import os
import sys
import glob


# ============================================================================
# PALETA DE COLORES INSTITUCIONALES (UNIMET - Naranja y Azul)
# Puedes modificar estos valores para ajustar los colores a tu preferencia.
# ============================================================================
COLORES = {
    "azul_oscuro":    "#1B3A5C",   # Azul oscuro principal (cabecera, acentos)
    "azul_medio":     "#2C5F8A",   # Azul medio (botones, bordes)
    "azul_claro":     "#3A7BBF",   # Azul claro (hover de botones)
    "naranja":        "#E87A1E",   # Naranja principal (botón primario, acentos)
    "naranja_hover":  "#F59A3E",   # Naranja claro (hover)
    "naranja_oscuro": "#C46A15",   # Naranja oscuro (active)
    "fondo":          "#F0F0F0",   # Fondo general de la ventana
    "fondo_panel":    "#FFFFFF",   # Fondo de paneles
    "texto_claro":    "#FFFFFF",   # Texto sobre fondos oscuros
    "texto_oscuro":   "#1A1A1A",   # Texto general
    "texto_gris":     "#555555",   # Texto secundario
    "borde":          "#CCCCCC",   # Bordes suaves
    "resultado_bg":   "#FAFAFA",   # Fondo del área de resultados
    "exito":          "#2E7D32",   # Color para mensajes de éxito
    "error":          "#C62828",   # Color para mensajes de error
}


class MetroTravelApp:
    """
    Clase principal de la interfaz gráfica del Sistema de Rutas - Metro Travel.
    
    Estructura de la interfaz (basada en la imagen de referencia):
        - Cabecera: Título y subtítulo
        - Panel de configuración: Origen, Destino, Visa, Criterio
        - Barra de acción: Botones de acción
        - Área de resultados: ScrolledText con scroll
    """

    def __init__(self, root, aeropuertos=None, callback_calcular=None,
                 callback_visualizar=None, callback_datos_fuente=None,
                 data_dir=None, datos_cargados=True,
                 nombre_archivo_ap=None, nombre_archivo_vl=None):
        """
        Inicializa la interfaz gráfica.

        Args:
            root: Ventana principal de tkinter.
            aeropuertos: Dict con datos de aeropuertos {codigo: {nombre, requiere_visa}}.
            callback_calcular: Función a ejecutar al presionar "Calcular Ruta Óptima".
            callback_visualizar: Función a ejecutar al presionar "Visualizar Mapa".
            callback_datos_fuente: Función a ejecutar al cambiar fuente de datos.
                Recibe (ruta_aeropuertos, ruta_vuelos) y retorna True si cargó OK.
            data_dir: Directorio donde se encuentran los archivos JSON de datos.
        """
        self.root = root
        self.aeropuertos = aeropuertos or {}
        self.callback_calcular = callback_calcular
        self.callback_visualizar = callback_visualizar
        self.callback_datos_fuente = callback_datos_fuente
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "data")
        self.datos_cargados = datos_cargados
        self.nombre_archivo_ap = nombre_archivo_ap or "aeropuertos.json"
        self.nombre_archivo_vl = nombre_archivo_vl or "vuelos.json"

        # Variables de tkinter
        self.var_origen = tk.StringVar()
        self.var_destino = tk.StringVar()
        self.var_visa = tk.BooleanVar(value=True)
        self.var_criterio = tk.StringVar(value="costo")

        self._configurar_ventana()
        self._crear_interfaz()

        if self.datos_cargados:
            self._mostrar_bienvenida()
        else:
            self._mostrar_sin_datos()
            self.bloquear_interfaz()

    # ========================================================================
    # CONFIGURACIÓN DE LA VENTANA
    # ========================================================================

    def _configurar_ventana(self):
        """Configura las propiedades generales de la ventana principal."""
        self.root.title("Sistema de Rutas - Metro Travel")
        self.root.configure(bg=COLORES["fondo"])
        self.root.minsize(900, 720)

        # Centrar la ventana en la pantalla
        ancho = 950
        alto = 720
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

        # Icono (opcional, no falla si no existe)
        try:
            ico_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
            if os.path.exists(ico_path):
                self.root.iconbitmap(ico_path)
        except Exception:
            pass

    # ========================================================================
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ========================================================================

    def _crear_interfaz(self):
        """Construye todos los widgets de la interfaz en orden vertical."""
        self._crear_cabecera()
        self._crear_panel_configuracion()
        self._crear_barra_accion()
        self._crear_area_resultados()

    # --- Cabecera -----------------------------------------------------------

    def _crear_cabecera(self):
        """Crea la sección de cabecera con título y subtítulo."""
        frame_cabecera = tk.Frame(self.root, bg=COLORES["azul_oscuro"], pady=16)
        frame_cabecera.pack(fill=tk.X)

        # Título principal
        tk.Label(
            frame_cabecera,
            text="✈  Sistema de Rutas - Metro Travel",
            font=("Segoe UI", 20, "bold"),
            fg=COLORES["texto_claro"],
            bg=COLORES["azul_oscuro"],
        ).pack()

        # Subtítulo
        tk.Label(
            frame_cabecera,
            text="Calcula las rutas óptimas por el Mar Caribe",
            font=("Segoe UI", 12),
            fg=COLORES["naranja"],
            bg=COLORES["azul_oscuro"],
        ).pack(pady=(4, 0))

    # --- Panel de configuración ---------------------------------------------

    def _crear_panel_configuracion(self):
        """Crea el panel con los controles de configuración de viaje."""
        # Marco contenedor con borde
        frame_config = tk.LabelFrame(
            self.root,
            text="  ✈ Configuración de Viaje  ",
            font=("Segoe UI", 11, "bold"),
            fg=COLORES["azul_oscuro"],
            bg=COLORES["fondo_panel"],
            padx=20,
            pady=15,
            bd=2,
            relief=tk.GROOVE,
        )
        frame_config.pack(fill=tk.X, padx=20, pady=(15, 5))

        # Lista de códigos para los combobox
        codigos = self._obtener_lista_aeropuertos()

        # --- Fila 1: Origen y Destino ---
        fila_od = tk.Frame(frame_config, bg=COLORES["fondo_panel"])
        fila_od.pack(fill=tk.X, pady=(0, 10))

        # Origen
        tk.Label(
            fila_od, text="Origen:", font=("Segoe UI", 10, "bold"),
            fg=COLORES["texto_oscuro"], bg=COLORES["fondo_panel"],
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.combo_origen = ttk.Combobox(
            fila_od, textvariable=self.var_origen, values=codigos,
            state="readonly", width=32, font=("Segoe UI", 10),
        )
        self.combo_origen.pack(side=tk.LEFT, padx=(0, 30))

        # Destino
        tk.Label(
            fila_od, text="Destino:", font=("Segoe UI", 10, "bold"),
            fg=COLORES["texto_oscuro"], bg=COLORES["fondo_panel"],
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.combo_destino = ttk.Combobox(
            fila_od, textvariable=self.var_destino, values=codigos,
            state="readonly", width=32, font=("Segoe UI", 10),
        )
        self.combo_destino.pack(side=tk.LEFT)

        # --- Fila 2: Visa y Criterio ---
        fila_vc = tk.Frame(frame_config, bg=COLORES["fondo_panel"])
        fila_vc.pack(fill=tk.X)

        # Checkbutton de Visa
        self.check_visa = tk.Checkbutton(
            fila_vc,
            text="  El pasajero posee visa válida",
            variable=self.var_visa,
            font=("Segoe UI", 10),
            fg=COLORES["texto_oscuro"],
            bg=COLORES["fondo_panel"],
            activebackground=COLORES["fondo_panel"],
            selectcolor=COLORES["fondo_panel"],
        )
        self.check_visa.pack(side=tk.LEFT, padx=(0, 40))

        # Separador visual
        tk.Label(
            fila_vc, text="|", font=("Segoe UI", 12),
            fg=COLORES["borde"], bg=COLORES["fondo_panel"],
        ).pack(side=tk.LEFT, padx=(0, 15))

        # Label Criterio
        tk.Label(
            fila_vc, text="Criterio:", font=("Segoe UI", 10, "bold"),
            fg=COLORES["texto_oscuro"], bg=COLORES["fondo_panel"],
        ).pack(side=tk.LEFT, padx=(0, 8))

        # Radiobuttons
        tk.Radiobutton(
            fila_vc, text="Minimizar Costo ($)", variable=self.var_criterio,
            value="costo", font=("Segoe UI", 10),
            fg=COLORES["texto_oscuro"], bg=COLORES["fondo_panel"],
            activebackground=COLORES["fondo_panel"],
            selectcolor=COLORES["fondo_panel"],
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Radiobutton(
            fila_vc, text="Minimizar Escalas", variable=self.var_criterio,
            value="escalas", font=("Segoe UI", 10),
            fg=COLORES["texto_oscuro"], bg=COLORES["fondo_panel"],
            activebackground=COLORES["fondo_panel"],
            selectcolor=COLORES["fondo_panel"],
        ).pack(side=tk.LEFT)

    # --- Barra de acción ----------------------------------------------------

    def _crear_barra_accion(self):
        """Crea la barra de botones de acción."""
        frame_botones = tk.Frame(self.root, bg=COLORES["fondo"], pady=8)
        frame_botones.pack(fill=tk.X, padx=20)

        # Botón: Instrucciones (azul)
        self.btn_instrucciones = tk.Button(
            frame_botones,
            text="📖  Instrucciones",
            font=("Segoe UI", 10),
            fg=COLORES["texto_claro"],
            bg=COLORES["azul_medio"],
            activebackground=COLORES["azul_oscuro"],
            activeforeground=COLORES["texto_claro"],
            relief=tk.RAISED,
            bd=1,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._on_instrucciones,
        )
        self.btn_instrucciones.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_instrucciones.bind("<Enter>", lambda e: self.btn_instrucciones.config(bg=COLORES["azul_claro"]))
        self.btn_instrucciones.bind("<Leave>", lambda e: self.btn_instrucciones.config(bg=COLORES["azul_medio"]))

        # Botón primario: Calcular Ruta Óptima (naranja)
        self.btn_calcular = tk.Button(
            frame_botones,
            text="✈  Calcular Ruta Óptima",
            font=("Segoe UI", 10, "bold"),
            fg=COLORES["texto_claro"],
            bg=COLORES["naranja"],
            activebackground=COLORES["naranja_oscuro"],
            activeforeground=COLORES["texto_claro"],
            relief=tk.RAISED,
            bd=1,
            padx=18,
            pady=6,
            cursor="hand2",
            command=self._on_calcular,
        )
        self.btn_calcular.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_calcular.bind("<Enter>", lambda e: self.btn_calcular.config(bg=COLORES["naranja_hover"]))
        self.btn_calcular.bind("<Leave>", lambda e: self.btn_calcular.config(bg=COLORES["naranja"]))

        # Botón: Visualizar Mapa (azul)
        self.btn_mapa = tk.Button(
            frame_botones,
            text="🗺  Visualizar Mapa",
            font=("Segoe UI", 10),
            fg=COLORES["texto_claro"],
            bg=COLORES["azul_medio"],
            activebackground=COLORES["azul_oscuro"],
            activeforeground=COLORES["texto_claro"],
            relief=tk.RAISED,
            bd=1,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._on_visualizar,
        )
        self.btn_mapa.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_mapa.bind("<Enter>", lambda e: self.btn_mapa.config(bg=COLORES["azul_claro"]))
        self.btn_mapa.bind("<Leave>", lambda e: self.btn_mapa.config(bg=COLORES["azul_medio"]))

        # Botón: Limpiar
        self.btn_limpiar = tk.Button(
            frame_botones,
            text="🔄  Limpiar",
            font=("Segoe UI", 10),
            fg=COLORES["texto_oscuro"],
            bg="#E0E0E0",
            activebackground="#BDBDBD",
            relief=tk.RAISED,
            bd=1,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._on_limpiar,
        )
        self.btn_limpiar.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_limpiar.bind("<Enter>", lambda e: self.btn_limpiar.config(bg="#D0D0D0"))
        self.btn_limpiar.bind("<Leave>", lambda e: self.btn_limpiar.config(bg="#E0E0E0"))

        # Botón: Seleccionar fuente de datos
        self.btn_datos = tk.Button(
            frame_botones,
            text="📂  Fuente de Datos (JSON)",
            font=("Segoe UI", 10),
            fg=COLORES["texto_oscuro"],
            bg="#E0E0E0",
            activebackground="#BDBDBD",
            relief=tk.RAISED,
            bd=1,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._on_datos_fuente,
        )
        self.btn_datos.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_datos.bind("<Enter>", lambda e: self.btn_datos.config(bg="#D0D0D0"))
        self.btn_datos.bind("<Leave>", lambda e: self.btn_datos.config(bg="#E0E0E0"))

        # Botón: Salir (derecha)
        self.btn_salir = tk.Button(
            frame_botones,
            text="✖  Salir",
            font=("Segoe UI", 10),
            fg=COLORES["error"],
            bg="#E0E0E0",
            activebackground="#FFCDD2",
            relief=tk.RAISED,
            bd=1,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._on_salir,
        )
        self.btn_salir.pack(side=tk.RIGHT)
        self.btn_salir.bind("<Enter>", lambda e: self.btn_salir.config(bg="#FFCDD2"))
        self.btn_salir.bind("<Leave>", lambda e: self.btn_salir.config(bg="#E0E0E0"))

    # --- Área de resultados -------------------------------------------------

    def _crear_area_resultados(self):
        """Crea el área de resultados con ScrolledText."""
        # Etiqueta de sección
        frame_label = tk.Frame(self.root, bg=COLORES["fondo"])
        frame_label.pack(fill=tk.X, padx=20, pady=(5, 2))

        tk.Label(
            frame_label,
            text="📋 Resultados",
            font=("Segoe UI", 11, "bold"),
            fg=COLORES["azul_oscuro"],
            bg=COLORES["fondo"],
        ).pack(anchor=tk.W)

        # Cuadro de texto desplazable
        self.txt_resultados = ScrolledText(
            self.root,
            font=("Consolas", 10),
            bg=COLORES["resultado_bg"],
            fg=COLORES["texto_oscuro"],
            relief=tk.SUNKEN,
            bd=2,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=14,
        )
        self.txt_resultados.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

    # ========================================================================
    # UTILIDADES
    # ========================================================================

    def _obtener_lista_aeropuertos(self):
        """
        Genera la lista formateada de aeropuertos para los combobox.
        
        Returns:
            Lista de strings con formato "CCS - Caracas - Simón Bolívar".
        """
        items = []
        for codigo, datos in sorted(self.aeropuertos.items()):
            nombre = datos.get("nombre", codigo)
            visa_tag = " [VISA]" if datos.get("requiere_visa", False) else ""
            items.append(f"{codigo} - {nombre}{visa_tag}")
        return items

    def _mostrar_bienvenida(self):
        """Muestra el mensaje de bienvenida en el área de resultados."""
        self.limpiar_resultados()
        linea = "═" * 58
        msg = (
            f"{linea}\n"
            "  ✈  BIENVENIDO AL SISTEMA DE RUTAS - METRO TRAVEL  ✈\n"
            f"{linea}\n\n"
            "  Base de datos de vuelos cargada exitosamente.\n\n"
            f"  Fuentes cargadas por defecto:\n"
            f"    • Aeropuertos: {self.nombre_archivo_ap}\n"
            f"    • Vuelos:      {self.nombre_archivo_vl}\n"
        )
        self.escribir_resultado(msg)
        self._mostrar_instrucciones()

    def _mostrar_instrucciones(self):
        """Muestra las instrucciones de uso en el área de resultados."""
        linea = "─" * 58
        msg = (
            f"\n{linea}\n"
            "  📖  INSTRUCCIONES DE USO\n"
            f"{linea}\n\n"
            "  1. Seleccione un aeropuerto de Origen\n"
            "  2. Seleccione un aeropuerto de Destino\n"
            "  3. Indique si el pasajero posee visa válida\n"
            "  4. Elija el criterio: Minimizar Costo o Escalas\n"
            "  5. Haga clic en 'Calcular Ruta Óptima'\n"
            "  6. Visualice el mapa si lo desea\n\n"
            "  ¡Comience seleccionando un origen y calculando la ruta!\n"
            f"{linea}"
        )
        self.escribir_resultado(msg)

    def _mostrar_sin_datos(self):
        """Muestra mensaje de advertencia cuando no hay datos cargados."""
        self.limpiar_resultados()
        linea = "═" * 58
        msg = (
            f"{linea}\n"
            "  ⚠  SISTEMA DE RUTAS - METRO TRAVEL  ⚠\n"
            f"{linea}\n\n"
            "  No se encontraron los archivos de datos por defecto\n"
            "  (aeropuertos.json y vuelos.json) en la carpeta 'data'.\n\n"
            "  Para utilizar el sistema debe cargar las fuentes de\n"
            "  datos primero utilizando el botón:\n\n"
            "     📂 Fuente de Datos (JSON)\n\n"
            "  La interfaz permanecerá bloqueada hasta que se\n"
            "  carguen ambos archivos correctamente.\n"
            f"{linea}"
        )
        self.escribir_resultado(msg)

    def escribir_resultado(self, texto):
        """
        Escribe texto en el área de resultados.

        Args:
            texto: String a mostrar en el área de resultados.
        """
        self.txt_resultados.config(state=tk.NORMAL)
        self.txt_resultados.insert(tk.END, texto + "\n")
        self.txt_resultados.see(tk.END)
        self.txt_resultados.config(state=tk.DISABLED)

    def limpiar_resultados(self):
        """Limpia el contenido del área de resultados."""
        self.txt_resultados.config(state=tk.NORMAL)
        self.txt_resultados.delete("1.0", tk.END)
        self.txt_resultados.config(state=tk.DISABLED)

    def obtener_codigo_seleccionado(self, texto_combo):
        """
        Extrae el código del aeropuerto del texto del combobox.

        Args:
            texto_combo: Texto seleccionado en formato "CCS - Nombre".

        Returns:
            String con el código del aeropuerto, o None si no hay selección.
        """
        if not texto_combo:
            return None
        return texto_combo.split(" - ")[0].strip()

    # ========================================================================
    # CALLBACKS DE BOTONES
    # ========================================================================

    def _on_calcular(self):
        """Maneja el evento del botón 'Calcular Ruta Óptima'."""
        origen_txt = self.var_origen.get()
        destino_txt = self.var_destino.get()
        origen = self.obtener_codigo_seleccionado(origen_txt)
        destino = self.obtener_codigo_seleccionado(destino_txt)

        # Validaciones básicas
        if not origen or not destino:
            self.escribir_resultado(
                "\n⚠  ERROR: Debe seleccionar un aeropuerto de origen y destino.\n"
            )
            return
        if origen == destino:
            self.escribir_resultado(
                "\n⚠  ERROR: El origen y el destino no pueden ser el mismo.\n"
            )
            return

        tiene_visa = self.var_visa.get()
        criterio = self.var_criterio.get()

        if self.callback_calcular:
            self.callback_calcular(origen, destino, tiene_visa, criterio)
        else:
            self.escribir_resultado(
                "\n⚠  La función de cálculo no está conectada aún.\n"
            )

    def _on_visualizar(self):
        """Maneja el evento del botón 'Visualizar Mapa'."""
        if self.callback_visualizar:
            self.callback_visualizar()
        else:
            self.escribir_resultado(
                "\n⚠  La función de visualización no está conectada aún.\n"
            )

    def _on_instrucciones(self):
        """Muestra las instrucciones en el área de resultados."""
        self._mostrar_instrucciones()

    def _on_limpiar(self):
        """Maneja el evento del botón 'Limpiar'. Restablece todos los campos."""
        self.var_origen.set("")
        self.var_destino.set("")
        self.var_visa.set(True)
        self.var_criterio.set("costo")
        self.limpiar_resultados()
        self._mostrar_bienvenida()

    def _on_datos_fuente(self):
        """Abre el diálogo de selección de fuente de datos JSON."""
        dialogo = DialogoFuenteDatos(self.root, self.data_dir)
        self.root.wait_window(dialogo.ventana)

        # Si el usuario confirmó ambas selecciones
        if dialogo.confirmado and dialogo.ruta_aeropuertos and dialogo.ruta_vuelos:
            if self.callback_datos_fuente:
                exito = self.callback_datos_fuente(
                    dialogo.ruta_aeropuertos, dialogo.ruta_vuelos
                )
                if exito:
                    # Actualizar nombres de archivos
                    self.nombre_archivo_ap = os.path.basename(dialogo.ruta_aeropuertos)
                    self.nombre_archivo_vl = os.path.basename(dialogo.ruta_vuelos)

                    # Si estaba bloqueada, desbloquear
                    if not self.datos_cargados:
                        self.datos_cargados = True
                        self.desbloquear_interfaz()

                    self.escribir_resultado(
                        "\n" + "═" * 55 +
                        "\n  📂  FUENTE DE DATOS ACTUALIZADA" +
                        "\n" + "═" * 55 +
                        f"\n\n  Aeropuertos: {self.nombre_archivo_ap}" +
                        f"\n  Vuelos:      {self.nombre_archivo_vl}" +
                        "\n\n  Datos recargados exitosamente." +
                        "\n" + "═" * 55
                    )
                    # Mostrar instrucciones después de cargar datos
                    self._mostrar_instrucciones()
            else:
                self.escribir_resultado(
                    "\n⚠  La función de recarga de datos no está conectada.\n"
                )

    def _on_salir(self):
        """Maneja el evento del botón 'Salir'. Cierra la aplicación."""
        self.root.quit()
        self.root.destroy()

    # ========================================================================
    # BLOQUEO / DESBLOQUEO DE INTERFAZ
    # ========================================================================

    def bloquear_interfaz(self):
        """
        Bloquea todos los controles de la interfaz excepto el botón Salir
        y el botón Fuente de Datos. Se usa cuando no hay datos cargados.
        """
        self.combo_origen.config(state=tk.DISABLED)
        self.combo_destino.config(state=tk.DISABLED)
        self.check_visa.config(state=tk.DISABLED)
        self.btn_instrucciones.config(state=tk.DISABLED)
        self.btn_calcular.config(state=tk.DISABLED)
        self.btn_mapa.config(state=tk.DISABLED)
        self.btn_limpiar.config(state=tk.DISABLED)
        # btn_datos y btn_salir permanecen habilitados

    def desbloquear_interfaz(self):
        """
        Desbloquea todos los controles de la interfaz.
        Se activa cuando se cargan datos correctamente.
        """
        self.combo_origen.config(state="readonly")
        self.combo_destino.config(state="readonly")
        self.check_visa.config(state=tk.NORMAL)
        self.btn_instrucciones.config(state=tk.NORMAL)
        self.btn_calcular.config(state=tk.NORMAL)
        self.btn_mapa.config(state=tk.NORMAL)
        self.btn_limpiar.config(state=tk.NORMAL)

    # ========================================================================
    # ACTUALIZACIÓN DE DATOS
    # ========================================================================

    def actualizar_aeropuertos(self, nuevos_aeropuertos):
        """
        Actualiza los datos de aeropuertos y refresca los combobox.

        Args:
            nuevos_aeropuertos: Nuevo dict de aeropuertos {codigo: {nombre, requiere_visa}}.
        """
        self.aeropuertos = nuevos_aeropuertos
        codigos = self._obtener_lista_aeropuertos()
        self.combo_origen["values"] = codigos
        self.combo_destino["values"] = codigos
        self.var_origen.set("")
        self.var_destino.set("")


# ============================================================================
# DIÁLOGO DE SELECCIÓN DE FUENTE DE DATOS
# ============================================================================

class DialogoFuenteDatos:
    """
    Ventana modal para seleccionar los archivos JSON de aeropuertos y vuelos.

    Muestra los archivos .json disponibles en la carpeta 'data' y permite
    seleccionar uno para aeropuertos y otro para vuelos. También permite
    buscar archivos en otras ubicaciones.

    Reglas:
        - Ambos archivos deben estar seleccionados para poder confirmar.
        - Si se cierra sin confirmar, no se guardan los cambios.
    """

    def __init__(self, parent, data_dir):
        self.parent = parent
        self.data_dir = data_dir
        self.ruta_aeropuertos = None
        self.ruta_vuelos = None
        self.confirmado = False

        self._crear_ventana()

    def _crear_ventana(self):
        """Crea la ventana modal del diálogo."""
        self.ventana = tk.Toplevel(self.parent)
        self.ventana.title("Seleccionar Fuente de Datos (JSON)")
        self.ventana.configure(bg=COLORES["fondo"])
        self.ventana.resizable(False, False)
        self.ventana.grab_set()  # Modal
        self.ventana.transient(self.parent)

        # Centrar respecto al padre
        ancho, alto = 560, 340
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() // 2) - (ancho // 2)
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() // 2) - (alto // 2)
        self.ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

        # Interceptar cierre con X
        self.ventana.protocol("WM_DELETE_WINDOW", self._on_cancelar)

        # --- Cabecera del diálogo ---
        frame_header = tk.Frame(self.ventana, bg=COLORES["azul_oscuro"], pady=10)
        frame_header.pack(fill=tk.X)
        tk.Label(
            frame_header, text="📂  Seleccionar Fuente de Datos",
            font=("Segoe UI", 14, "bold"),
            fg=COLORES["texto_claro"], bg=COLORES["azul_oscuro"],
        ).pack()
        tk.Label(
            frame_header,
            text="Seleccione un archivo JSON para aeropuertos y otro para vuelos",
            font=("Segoe UI", 9),
            fg=COLORES["naranja"], bg=COLORES["azul_oscuro"],
        ).pack()

        # --- Cuerpo ---
        frame_body = tk.Frame(self.ventana, bg=COLORES["fondo"], padx=25, pady=15)
        frame_body.pack(fill=tk.BOTH, expand=True)

        # Buscar JSONs disponibles en la carpeta data
        self.archivos_json = self._listar_json()

        # -- Sección Aeropuertos --
        tk.Label(
            frame_body, text="✈  Archivo de Aeropuertos:",
            font=("Segoe UI", 10, "bold"),
            fg=COLORES["azul_oscuro"], bg=COLORES["fondo"],
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 4))

        self.var_archivo_ap = tk.StringVar()
        self.combo_ap = ttk.Combobox(
            frame_body, textvariable=self.var_archivo_ap,
            values=self.archivos_json, state="readonly",
            width=35, font=("Segoe UI", 10),
        )
        self.combo_ap.grid(row=1, column=0, sticky=tk.W, padx=(0, 8))

        btn_buscar_ap = tk.Button(
            frame_body, text="📁 Buscar...",
            font=("Segoe UI", 9), fg=COLORES["texto_oscuro"],
            bg="#E0E0E0", cursor="hand2", padx=8, pady=2,
            command=lambda: self._buscar_archivo("aeropuertos"),
        )
        btn_buscar_ap.grid(row=1, column=1, sticky=tk.W)

        self.lbl_estado_ap = tk.Label(
            frame_body, text="❌ No seleccionado",
            font=("Segoe UI", 9), fg=COLORES["error"], bg=COLORES["fondo"],
        )
        self.lbl_estado_ap.grid(row=2, column=0, sticky=tk.W, pady=(2, 12))

        # -- Sección Vuelos --
        tk.Label(
            frame_body, text="🛫  Archivo de Vuelos:",
            font=("Segoe UI", 10, "bold"),
            fg=COLORES["azul_oscuro"], bg=COLORES["fondo"],
        ).grid(row=3, column=0, sticky=tk.W, pady=(0, 4))

        self.var_archivo_vl = tk.StringVar()
        self.combo_vl = ttk.Combobox(
            frame_body, textvariable=self.var_archivo_vl,
            values=self.archivos_json, state="readonly",
            width=35, font=("Segoe UI", 10),
        )
        self.combo_vl.grid(row=4, column=0, sticky=tk.W, padx=(0, 8))

        btn_buscar_vl = tk.Button(
            frame_body, text="📁 Buscar...",
            font=("Segoe UI", 9), fg=COLORES["texto_oscuro"],
            bg="#E0E0E0", cursor="hand2", padx=8, pady=2,
            command=lambda: self._buscar_archivo("vuelos"),
        )
        btn_buscar_vl.grid(row=4, column=1, sticky=tk.W)

        self.lbl_estado_vl = tk.Label(
            frame_body, text="❌ No seleccionado",
            font=("Segoe UI", 9), fg=COLORES["error"], bg=COLORES["fondo"],
        )
        self.lbl_estado_vl.grid(row=5, column=0, sticky=tk.W, pady=(2, 0))

        # Bind combobox changes
        self.combo_ap.bind("<<ComboboxSelected>>", lambda e: self._on_combo_change("aeropuertos"))
        self.combo_vl.bind("<<ComboboxSelected>>", lambda e: self._on_combo_change("vuelos"))

        # --- Barra de botones ---
        frame_btns = tk.Frame(self.ventana, bg=COLORES["fondo"], pady=10)
        frame_btns.pack(fill=tk.X, padx=25)

        self.btn_confirmar = tk.Button(
            frame_btns, text="✔  Confirmar",
            font=("Segoe UI", 10, "bold"),
            fg=COLORES["texto_claro"], bg=COLORES["naranja"],
            activebackground=COLORES["naranja_oscuro"],
            activeforeground=COLORES["texto_claro"],
            padx=16, pady=5, cursor="hand2",
            command=self._on_confirmar, state=tk.DISABLED,
        )
        self.btn_confirmar.pack(side=tk.LEFT, padx=(0, 10))

        btn_cancelar = tk.Button(
            frame_btns, text="✖  Cancelar",
            font=("Segoe UI", 10),
            fg=COLORES["error"], bg="#E0E0E0",
            padx=16, pady=5, cursor="hand2",
            command=self._on_cancelar,
        )
        btn_cancelar.pack(side=tk.LEFT)

    # --- Helpers del diálogo ---

    def _listar_json(self):
        """Lista los archivos .json disponibles en la carpeta data."""
        if not os.path.isdir(self.data_dir):
            return []
        archivos = []
        for f in sorted(os.listdir(self.data_dir)):
            if f.lower().endswith(".json"):
                archivos.append(f)
        return archivos

    def _buscar_archivo(self, tipo):
        """
        Abre un diálogo de sistema para buscar un archivo JSON.

        Args:
            tipo: "aeropuertos" o "vuelos".
        """
        ruta = filedialog.askopenfilename(
            parent=self.ventana,
            title=f"Seleccionar archivo de {tipo}",
            initialdir=self.data_dir,
            filetypes=[("Archivos JSON", "*.json"), ("Todos", "*.*")],
        )
        if ruta:
            nombre = os.path.basename(ruta)
            if tipo == "aeropuertos":
                self.ruta_aeropuertos = ruta
                self.var_archivo_ap.set(nombre)
                self.lbl_estado_ap.config(text=f"✔ {nombre}", fg=COLORES["exito"])
            else:
                self.ruta_vuelos = ruta
                self.var_archivo_vl.set(nombre)
                self.lbl_estado_vl.config(text=f"✔ {nombre}", fg=COLORES["exito"])
            self._verificar_seleccion()

    def _on_combo_change(self, tipo):
        """
        Maneja la selección de un archivo desde el combobox.

        Args:
            tipo: "aeropuertos" o "vuelos".
        """
        if tipo == "aeropuertos":
            nombre = self.var_archivo_ap.get()
            if nombre:
                self.ruta_aeropuertos = os.path.join(self.data_dir, nombre)
                self.lbl_estado_ap.config(text=f"✔ {nombre}", fg=COLORES["exito"])
        else:
            nombre = self.var_archivo_vl.get()
            if nombre:
                self.ruta_vuelos = os.path.join(self.data_dir, nombre)
                self.lbl_estado_vl.config(text=f"✔ {nombre}", fg=COLORES["exito"])
        self._verificar_seleccion()

    def _verificar_seleccion(self):
        """Habilita el botón Confirmar solo si ambos archivos están seleccionados."""
        if self.ruta_aeropuertos and self.ruta_vuelos:
            self.btn_confirmar.config(state=tk.NORMAL)
        else:
            self.btn_confirmar.config(state=tk.DISABLED)

    def _on_confirmar(self):
        """Confirma la selección y cierra el diálogo."""
        if not self.ruta_aeropuertos or not self.ruta_vuelos:
            messagebox.showwarning(
                "Selección incompleta",
                "Debe seleccionar un archivo de aeropuertos y uno de vuelos.",
                parent=self.ventana,
            )
            return
        self.confirmado = True
        self.ventana.destroy()

    def _on_cancelar(self):
        """Cancela sin guardar cambios y cierra el diálogo."""
        self.confirmado = False
        self.ruta_aeropuertos = None
        self.ruta_vuelos = None
        self.ventana.destroy()
