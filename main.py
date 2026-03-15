"""
main.py - Punto de entrada del Sistema de Rutas - Metro Travel

Carga los datos de aeropuertos y vuelos, construye el grafo,
inicializa la interfaz gráfica y conecta los callbacks de cálculo
y visualización.
"""

import tkinter as tk
import json
import os
import sys

# Directorio base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def cargar_json(ruta):
    """Carga y retorna el contenido de un archivo JSON."""
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    """Función principal que inicializa y ejecuta la aplicación."""
    # ------------------------------------------------------------------
    # 1. Cargar datos desde archivos externos (FRQ-0001)
    # ------------------------------------------------------------------
    ruta_aeropuertos = os.path.join(BASE_DIR, "data", "aeropuertos.json")
    ruta_vuelos = os.path.join(BASE_DIR, "data", "vuelos.json")

    # Importar módulo de grafo (siempre disponible)
    from grafo import construir_grafo, dijkstra

    datos_cargados = False
    aeropuertos = {}
    lista_vuelos = []
    grafo = None
    grafo_disponible = False

    if os.path.exists(ruta_aeropuertos) and os.path.exists(ruta_vuelos):
        try:
            lista_aeropuertos = cargar_json(ruta_aeropuertos)
            lista_vuelos = cargar_json(ruta_vuelos)

            # Convertir lista de aeropuertos a diccionario
            for ap in lista_aeropuertos:
                aeropuertos[ap["codigo"]] = {
                    "nombre": ap["nombre"],
                    "requiere_visa": ap["requiere_visa"],
                }

            # Construir el grafo
            grafo = construir_grafo(aeropuertos, lista_vuelos)
            grafo_disponible = True
            datos_cargados = True
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"AVISO: Error al cargar datos por defecto: {e}")
    else:
        print("AVISO: Archivos de datos por defecto no encontrados. "
              "La interfaz se iniciará en modo bloqueado.")

    # ------------------------------------------------------------------
    # 3. Definir callbacks
    # ------------------------------------------------------------------
    ultima_ruta = {"ruta": None, "costo": None, "criterio": None}
    data_dir = os.path.join(BASE_DIR, "data")

    def callback_calcular(origen, destino, tiene_visa, criterio):
        """Callback para el botón Calcular Ruta Óptima."""
        if not grafo_disponible:
            app.escribir_resultado(
                "\n⚠  El módulo de cálculo (grafo.py) no está disponible.\n"
            )
            return

        resultado = dijkstra(grafo, origen, destino, tiene_visa, criterio, aeropuertos)

        if resultado is None:
            app.escribir_resultado(
                "\n" + "─" * 55 +
                "\n⚠  No se encontró una ruta disponible.\n"
            )
            if not tiene_visa:
                app.escribir_resultado(
                    "   Nota: Algunos aeropuertos requieren visa y fueron\n"
                    "   excluidos del cálculo. Intente con visa habilitada.\n"
                )
            app.escribir_resultado("─" * 55 + "\n")
            return

        ruta, costo_total = resultado
        ultima_ruta["ruta"] = ruta
        ultima_ruta["costo"] = costo_total
        ultima_ruta["criterio"] = criterio

        # Formatear resultado
        ruta_str = " -> ".join(ruta)
        if criterio == "costo":
            criterio_label = "Costo"
            total_str = f"${costo_total:,.2f}"
        else:
            criterio_label = "Escalas"
            total_str = f"{int(costo_total)} escala(s)"

        app.escribir_resultado(
            "\n" + "═" * 55 +
            f"\n  ✈  RUTA ÓPTIMA ENCONTRADA" +
            "\n" + "═" * 55 +
            f"\n\n  Ruta:     {ruta_str}" +
            f"\n  Criterio: {criterio_label}" +
            f"\n  Total:    {total_str}" +
            f"\n  Escalas:  {len(ruta) - 2} escala(s)" +
            "\n\n  Detalle del recorrido:"
        )

        for i, cod in enumerate(ruta):
            nombre = aeropuertos[cod]["nombre"]
            visa_tag = " [VISA]" if aeropuertos[cod]["requiere_visa"] else ""
            if i == 0:
                app.escribir_resultado(f"    🛫 {cod} - {nombre}{visa_tag}  (Origen)")
            elif i == len(ruta) - 1:
                app.escribir_resultado(f"    🛬 {cod} - {nombre}{visa_tag}  (Destino)")
            else:
                app.escribir_resultado(f"    ✈  {cod} - {nombre}{visa_tag}  (Escala {i})")

        app.escribir_resultado("\n" + "═" * 55 + "\n")

    def callback_visualizar():
        """Callback para el botón Visualizar Mapa."""
        try:
            from visualizacion import mostrar_mapa
            ruta_a_resaltar = ultima_ruta.get("ruta")
            mostrar_mapa(aeropuertos, lista_vuelos, ruta_a_resaltar)
        except ImportError:
            app.escribir_resultado(
                "\n⚠  El módulo de visualización (visualizacion.py) no está disponible.\n"
                "   Asegúrese de tener instalados networkx y matplotlib.\n"
            )
        except Exception as e:
            app.escribir_resultado(f"\n⚠  Error al visualizar el mapa: {e}\n")

    def callback_datos_fuente(ruta_ap, ruta_vl):
        """
        Callback para recargar datos desde nuevos archivos JSON.
        Retorna True si la recarga fue exitosa, False en caso contrario.
        """
        nonlocal aeropuertos, lista_vuelos, grafo, grafo_disponible
        try:
            nueva_lista_ap = cargar_json(ruta_ap)
            nueva_lista_vl = cargar_json(ruta_vl)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            app.escribir_resultado(f"\n⚠  Error al cargar archivos: {e}\n")
            return False

        # Reconstruir diccionario de aeropuertos
        nuevos_aeropuertos = {}
        for ap_data in nueva_lista_ap:
            nuevos_aeropuertos[ap_data["codigo"]] = {
                "nombre": ap_data["nombre"],
                "requiere_visa": ap_data["requiere_visa"],
            }

        # Reconstruir grafo
        try:
            from grafo import construir_grafo as _cg
            nuevo_grafo = _cg(nuevos_aeropuertos, nueva_lista_vl)
        except Exception as e:
            app.escribir_resultado(f"\n⚠  Error al reconstruir el grafo: {e}\n")
            return False

        # Actualizar estado global
        aeropuertos = nuevos_aeropuertos
        lista_vuelos = nueva_lista_vl
        grafo = nuevo_grafo
        grafo_disponible = True
        ultima_ruta["ruta"] = None
        ultima_ruta["costo"] = None
        ultima_ruta["criterio"] = None

        # Actualizar comboboxes de la interfaz
        app.actualizar_aeropuertos(nuevos_aeropuertos)
        return True

    # ------------------------------------------------------------------
    # 4. Crear e iniciar la interfaz gráfica
    # ------------------------------------------------------------------
    from interfaz import MetroTravelApp

    root = tk.Tk()
    app = MetroTravelApp(
        root,
        aeropuertos=aeropuertos,
        callback_calcular=callback_calcular,
        callback_visualizar=callback_visualizar,
        callback_datos_fuente=callback_datos_fuente,
        data_dir=data_dir,
        datos_cargados=datos_cargados,
    )
    root.mainloop()


if __name__ == "__main__":
    main()
