"""
welcome.py - Ventana de bienvenida

Este módulo implementa una interfaz gráfica de bienvenida al programa.

Colores institucionales: Naranja y Azul (UNIMET).
"""

import tkinter as tk

# Define the colors here as well to keep the file independent
COLORES_WELCOME = {
    "azul_oscuro": "#1B3A5C",
    "naranja": "#E87A1E",
    "naranja_hover": "#F59A3E",
    "texto_claro": "#FFFFFF",
    "texto_oscuro": "#1A1A1A",
}


class WelcomePage(tk.Frame):
    """Pantalla de bienvenida inicial del sistema Metro Travel."""

    def __init__(self, parent, on_start_callback):
        super().__init__(parent, bg=COLORES_WELCOME["azul_oscuro"])

        # Centering container
        self.center_frame = tk.Frame(self, bg=COLORES_WELCOME["azul_oscuro"])
        self.center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Main Icon
        tk.Label(
            self.center_frame,
            text="✈",
            font=("Segoe UI", 80),
            fg=COLORES_WELCOME["naranja"],
            bg=COLORES_WELCOME["azul_oscuro"],
        ).pack()

        # Title
        tk.Label(
            self.center_frame,
            text="Metro Travel",
            font=("Segoe UI", 42, "bold"),
            fg=COLORES_WELCOME["texto_claro"],
            bg=COLORES_WELCOME["azul_oscuro"],
        ).pack(pady=10)

        # Slogan
        tk.Label(
            self.center_frame,
            text="Sistema de Gestión de Rutas del Caribe",
            font=("Segoe UI", 14, "italic"),
            fg=COLORES_WELCOME["naranja"],
            bg=COLORES_WELCOME["azul_oscuro"],
        ).pack(pady=(0, 40))

        # Start Button
        self.btn_entrar = tk.Button(
            self.center_frame,
            text="INGRESAR AL SISTEMA",
            font=("Segoe UI", 12, "bold"),
            bg=COLORES_WELCOME["naranja"],
            fg=COLORES_WELCOME["texto_oscuro"],
            activebackground=COLORES_WELCOME["naranja_hover"],
            activeforeground=COLORES_WELCOME["texto_oscuro"],
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor="hand2",
            command=on_start_callback,
        )
        self.btn_entrar.pack()
