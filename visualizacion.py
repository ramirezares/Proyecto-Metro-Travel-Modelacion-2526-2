"""
visualizacion.py - Módulo de Visualización del Grafo para Metro Travel

Utiliza las librerías networkx y matplotlib para generar una representación
visual de la red de aeropuertos y vuelos del Caribe.

Librerías externas (permitidas por NFR-0001):
    - networkx: Construcción y layout del grafo.
    - matplotlib: Renderizado gráfico.
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# Paleta de colores consistente con la interfaz
COLORES_VIS = {
    "nodo_normal":     "#2C5F8A",   # Azul medio (sin visa)
    "nodo_visa":       "#E87A1E",   # Naranja (requiere visa)
    "nodo_ruta":       "#F59A3E",   # Naranja claro (nodos en la ruta)
    "arista_normal":   "#CCCCCC",   # Gris claro
    "arista_ruta":     "#E87A1E",   # Naranja (aristas en la ruta)
    "texto_nodo":      "#FFFFFF",   # Blanco
    "texto_arista":    "#555555",   # Gris oscuro
    "fondo":           "#F8F8F8",   # Fondo claro
}


def mostrar_mapa(aeropuertos, vuelos, ruta_resaltada=None):
    """
    Genera y muestra un mapa visual de la red de vuelos del Caribe.

    Utiliza networkx para construir el grafo y matplotlib para renderizarlo.
    Los nodos se posicionan usando un layout de resorte (spring layout) para
    mejor legibilidad. La ruta calculada se resalta en color naranja.

    Args:
        aeropuertos (dict): Diccionario {codigo: {nombre, requiere_visa}}.
        vuelos (list[dict]): Lista de arcos {origen, destino, precio}.
        ruta_resaltada (list[str] | None): Lista ordenada de códigos de
            aeropuertos que forman la ruta óptima a resaltar. Si es None,
            no se resalta ninguna ruta.
    """
    # --- Crear grafo de networkx ---
    G = nx.DiGraph()

    # Agregar nodos con atributos
    for codigo, datos in aeropuertos.items():
        G.add_node(codigo, nombre=datos["nombre"],
                   requiere_visa=datos.get("requiere_visa", False))

    # Agregar aristas con peso
    for vuelo in vuelos:
        G.add_edge(vuelo["origen"], vuelo["destino"], weight=vuelo["precio"])

    # --- Layout ---
    # Posiciones geográficas aproximadas de los aeropuertos del Caribe
    # para una visualización más intuitiva
    pos_manual = {
        "CCS": (-66.99, 10.60),    # Caracas
        "AUA": (-70.01, 12.50),    # Aruba
        "CUR": (-68.96, 12.17),    # Curazao
        "SXM": (-63.11, 18.04),    # San Martín
        "SDQ": (-69.67, 18.43),    # Santo Domingo
        "SJU": (-66.00, 18.44),    # San Juan
        "MIA": (-80.29, 25.80),    # Miami
        "BOG": (-74.15, 4.70),     # Bogotá
        "PTY": (-79.38, 9.07),     # Panamá
        "KIN": (-76.79, 17.94),    # Kingston
        "POS": (-61.35, 10.60),    # Trinidad
        "BGI": (-59.49, 13.07),    # Barbados
    }

    # Usar posiciones manuales si todos los nodos las tienen; si no, spring layout
    pos = {}
    for nodo in G.nodes():
        if nodo in pos_manual:
            pos[nodo] = pos_manual[nodo]
        else:
            pos = nx.spring_layout(G, seed=42, k=2)
            break

    # --- Preparar colores de nodos ---
    colores_nodos = []
    for nodo in G.nodes():
        if ruta_resaltada and nodo in ruta_resaltada:
            colores_nodos.append(COLORES_VIS["nodo_ruta"])
        elif G.nodes[nodo].get("requiere_visa", False):
            colores_nodos.append(COLORES_VIS["nodo_visa"])
        else:
            colores_nodos.append(COLORES_VIS["nodo_normal"])

    # --- Preparar aristas de la ruta ---
    aristas_ruta = set()
    if ruta_resaltada and len(ruta_resaltada) > 1:
        for i in range(len(ruta_resaltada) - 1):
            aristas_ruta.add((ruta_resaltada[i], ruta_resaltada[i + 1]))

    colores_aristas = []
    anchos_aristas = []
    for u, v in G.edges():
        if (u, v) in aristas_ruta:
            colores_aristas.append(COLORES_VIS["arista_ruta"])
            anchos_aristas.append(3.0)
        else:
            colores_aristas.append(COLORES_VIS["arista_normal"])
            anchos_aristas.append(1.0)

    # --- Dibujar ---
    fig, ax = plt.subplots(1, 1, figsize=(14, 9))
    fig.set_facecolor(COLORES_VIS["fondo"])
    ax.set_facecolor(COLORES_VIS["fondo"])

    # Dibujar aristas
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color=colores_aristas,
        width=anchos_aristas,
        arrows=True,
        arrowsize=15,
        connectionstyle="arc3,rad=0.1",
        alpha=0.7,
    )

    # Dibujar nodos
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=colores_nodos,
        node_size=800,
        edgecolors="#333333",
        linewidths=1.5,
    )

    # Etiquetas de nodos (código del aeropuerto)
    nx.draw_networkx_labels(
        G, pos, ax=ax,
        font_size=9,
        font_weight="bold",
        font_color=COLORES_VIS["texto_nodo"],
    )

    # Etiquetas de aristas (precio)
    edge_labels = {(u, v): f"${d['weight']}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(
        G, pos, ax=ax,
        edge_labels=edge_labels,
        font_size=7,
        font_color=COLORES_VIS["texto_arista"],
        label_pos=0.3,
    )

    # --- Leyenda ---
    leyenda = [
        mpatches.Patch(color=COLORES_VIS["nodo_normal"], label="Sin visa requerida"),
        mpatches.Patch(color=COLORES_VIS["nodo_visa"], label="Requiere visa"),
    ]
    if ruta_resaltada:
        leyenda.append(
            mpatches.Patch(color=COLORES_VIS["arista_ruta"], label="Ruta óptima")
        )
    ax.legend(handles=leyenda, loc="lower left", fontsize=9,
              framealpha=0.9, facecolor="white")

    # --- Título ---
    titulo = "Red de Vuelos - Metro Travel (Mar Caribe)"
    if ruta_resaltada:
        titulo += f"\nRuta: {' → '.join(ruta_resaltada)}"
    ax.set_title(titulo, fontsize=14, fontweight="bold", color="#1B3A5C", pad=15)

    ax.axis("off")
    plt.tight_layout()
    plt.show()
