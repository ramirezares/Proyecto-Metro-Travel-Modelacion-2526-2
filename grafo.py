"""
grafo.py - Módulo de Lógica de Grafos para Metro Travel

Este módulo implementa la representación del grafo de aeropuertos y vuelos
del Caribe, así como el algoritmo de Dijkstra para calcular rutas óptimas.

=============================================================================
REPRESENTACIONES DE GRAFOS UTILIZADAS
=============================================================================

Este módulo utiliza DOS representaciones de grafos, cada una escogida por
su eficiencia según la operación requerida:

1. LISTA DE ADYACENCIA (estructura principal):
   - Estructura: dict[str, list[tuple[str, float]]]
     Ejemplo: {"CCS": [("AUA", 120.0), ("BOG", 180.0)], ...}
   - Se usa para: Algoritmo de Dijkstra (FRQ-0003), consulta de vecinos.
   - Justificación: La lista de adyacencia es la representación más eficiente
     para el algoritmo de Dijkstra, ya que permite recorrer los vecinos de un
     nodo en O(grado(v)) sin necesidad de iterar sobre todos los nodos del
     grafo. Además, consume O(V + E) de memoria, lo cual es óptimo para
     grafos dispersos como una red de vuelos.

2. LISTA DE ARCOS (estructura auxiliar para carga de datos):
   - Estructura: list[dict] con claves {"origen", "destino", "precio"}
     Ejemplo: [{"origen": "CCS", "destino": "AUA", "precio": 120}, ...]
   - Se usa para: Carga de datos desde JSON, construcción del grafo,
     transferencia al módulo de visualización.
   - Justificación: La lista de arcos es la representación más natural para
     almacenar datos tabulares provenientes de archivos JSON/CSV. Facilita la
     lectura, validación y transformación de datos antes de construir la
     lista de adyacencia. Además, es la forma más directa de pasar los datos
     al módulo de visualización (networkx espera listas de aristas).

Comparación de alternativas descartadas:
   - Matriz de adyacencia: Requiere O(V²) de memoria. Con 12 aeropuertos no
     es problemático, pero no ofrece ventajas sobre la lista de adyacencia
     para Dijkstra y escalaría mal si se añaden más aeropuertos.
   - Matriz de incidencia: Requiere O(V × E) de memoria, ineficiente para
     consultas de vecindad directa.
   - Representación Star (Forward Star / CSR): Eficiente en memoria y caché,
     pero requiere que el grafo sea estático tras la construcción. Como
     necesitamos filtrar nodos (por visa), tendríamos que reconstruirla cada
     vez, anulando su ventaja.
=============================================================================
"""

import json
import heapq


# ============================================================================
# FUNCIONES DE CARGA DE DATOS (Lista de Arcos)
# ============================================================================

def cargar_aeropuertos(ruta):
    """
    Carga la información de aeropuertos desde un archivo JSON.

    El archivo debe contener una lista de objetos con las claves:
        - "codigo": str (ej. "CCS")
        - "nombre": str (ej. "Caracas - Simón Bolívar")
        - "requiere_visa": bool

    Args:
        ruta (str): Ruta absoluta o relativa al archivo JSON de aeropuertos.

    Returns:
        dict: Diccionario {codigo: {"nombre": str, "requiere_visa": bool}}.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        json.JSONDecodeError: Si el archivo no es JSON válido.
        KeyError: Si faltan claves requeridas en los datos.
    """
    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)

    aeropuertos = {}
    for ap in datos:
        aeropuertos[ap["codigo"]] = {
            "nombre": ap["nombre"],
            "requiere_visa": ap["requiere_visa"],
        }
    return aeropuertos


def cargar_vuelos(ruta):
    """
    Carga la lista de vuelos (arcos) desde un archivo JSON.

    Representación utilizada: LISTA DE ARCOS.
    Cada vuelo es un diccionario con las claves:
        - "origen": str (código del aeropuerto de salida)
        - "destino": str (código del aeropuerto de llegada)
        - "precio": float (costo del pasaje en dólares)

    Args:
        ruta (str): Ruta absoluta o relativa al archivo JSON de vuelos.

    Returns:
        list[dict]: Lista de diccionarios representando los arcos del grafo.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        json.JSONDecodeError: Si el archivo no es JSON válido.
    """
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================================
# CONSTRUCCIÓN DEL GRAFO (Lista de Adyacencia)
# ============================================================================

def construir_grafo(aeropuertos, vuelos):
    """
    Construye un grafo dirigido como LISTA DE ADYACENCIA a partir de los
    datos de aeropuertos y vuelos.

    Representación: LISTA DE ADYACENCIA
        grafo[nodo] = [(vecino_1, peso_1), (vecino_2, peso_2), ...]

    Solo se incluyen arcos cuyos nodos de origen y destino existan en el
    diccionario de aeropuertos, lo que garantiza integridad referencial.

    Args:
        aeropuertos (dict): Diccionario de aeropuertos {codigo: {nombre, requiere_visa}}.
        vuelos (list[dict]): Lista de arcos con claves {origen, destino, precio}.

    Returns:
        dict[str, list[tuple[str, float]]]: Grafo como lista de adyacencia.
            Cada clave es un código de aeropuerto, cada valor es una lista de
            tuplas (destino, precio).

    Ejemplo:
        >>> grafo = construir_grafo(aeropuertos, vuelos)
        >>> grafo["CCS"]
        [("AUA", 120.0), ("BOG", 180.0), ("SDQ", 250.0), ("POS", 150.0)]
    """
    # Inicializar lista de adyacencia con todos los nodos (incluso sin arcos)
    grafo = {codigo: [] for codigo in aeropuertos}

    # Agregar arcos al grafo
    for vuelo in vuelos:
        origen = vuelo["origen"]
        destino = vuelo["destino"]
        precio = float(vuelo["precio"])

        # Solo incluir arcos entre nodos existentes
        if origen in aeropuertos and destino in aeropuertos:
            grafo[origen].append((destino, precio))

    return grafo


# ============================================================================
# ALGORITMO DE DIJKSTRA (FRQ-0003)
# ============================================================================

def dijkstra(grafo, origen, destino, tiene_visa, criterio, aeropuertos):
    """
    Implementación del Algoritmo de Dijkstra para encontrar la ruta óptima
    entre dos aeropuertos en el grafo.

    Opera sobre la LISTA DE ADYACENCIA construida por construir_grafo().
    Utiliza un min-heap (cola de prioridad) para eficiencia O((V+E) log V).

    Criterios de optimización (FRQ-0003):
        - "costo": Los pesos son los precios en dólares de cada vuelo.
        - "escalas": Todas las aristas tienen peso 1 (minimiza saltos).

    Validación de visa (FRQ-0002):
        - Si tiene_visa es False, se ignoran temporalmente los nodos que
          requieren visa durante la búsqueda.
        - Si el destino requiere visa y el pasajero no la tiene, retorna None.
        - Si el origen requiere visa y el pasajero no la tiene, retorna None.

    Args:
        grafo (dict): Grafo como lista de adyacencia {nodo: [(vecino, peso), ...]}.
        origen (str): Código del aeropuerto de origen.
        destino (str): Código del aeropuerto de destino.
        tiene_visa (bool): True si el pasajero posee visa válida.
        criterio (str): "costo" para minimizar precio, "escalas" para minimizar
                        cantidad de escalas.
        aeropuertos (dict): Diccionario de aeropuertos para consultar visa.

    Returns:
        tuple[list[str], float] | None:
            - Si se encuentra ruta: (lista_de_codigos, costo_total).
              Ejemplo: (["CCS", "AUA", "CUR"], 165.0)
            - Si no hay ruta disponible: None.
    """
    # --- Validación de visa en origen y destino (FRQ-0002) ---
    if not tiene_visa:
        if aeropuertos.get(destino, {}).get("requiere_visa", False):
            return None  # Destino requiere visa y no la tiene
        if aeropuertos.get(origen, {}).get("requiere_visa", False):
            return None  # No puede iniciar en un destino con visa si no la posee

    # --- Determinar nodos válidos (filtrado por visa) ---
    nodos_validos = set()
    for codigo, datos in aeropuertos.items():
        if tiene_visa or not datos.get("requiere_visa", False):
            nodos_validos.add(codigo)

    # Verificar que origen y destino estén en nodos válidos
    if origen not in nodos_validos or destino not in nodos_validos:
        return None

    # --- Inicialización de Dijkstra ---
    # distancias[nodo] = menor distancia conocida desde el origen
    distancias = {nodo: float("inf") for nodo in nodos_validos}
    distancias[origen] = 0

    # predecesores[nodo] = nodo anterior en la ruta óptima
    predecesores = {nodo: None for nodo in nodos_validos}

    # Cola de prioridad: (distancia_acumulada, nodo)
    cola = [(0, origen)]

    # Conjunto de nodos ya procesados
    visitados = set()

    # --- Bucle principal de Dijkstra ---
    while cola:
        dist_actual, nodo_actual = heapq.heappop(cola)

        # Si ya fue procesado, saltar
        if nodo_actual in visitados:
            continue

        # Marcar como procesado
        visitados.add(nodo_actual)

        # Si llegamos al destino, reconstruir la ruta
        if nodo_actual == destino:
            return _reconstruir_ruta(predecesores, origen, destino, dist_actual)

        # Explorar vecinos desde la lista de adyacencia
        for vecino, precio in grafo.get(nodo_actual, []):
            # Solo considerar nodos válidos (filtro de visa)
            if vecino not in nodos_validos or vecino in visitados:
                continue

            # Calcular peso según criterio
            if criterio == "escalas":
                peso = 1  # Todas las aristas pesan 1
            else:
                peso = precio  # Peso = precio del vuelo

            nueva_distancia = dist_actual + peso

            # Relajación: actualizar si encontramos una ruta mejor
            if nueva_distancia < distancias[vecino]:
                distancias[vecino] = nueva_distancia
                predecesores[vecino] = nodo_actual
                heapq.heappush(cola, (nueva_distancia, vecino))

    # Si la cola se vació sin llegar al destino, no hay ruta
    return None


def _reconstruir_ruta(predecesores, origen, destino, costo_total):
    """
    Reconstruye la ruta óptima desde el destino hacia el origen
    siguiendo los predecesores.

    Args:
        predecesores (dict): Diccionario de predecesores {nodo: predecesor}.
        origen (str): Código del aeropuerto de origen.
        destino (str): Código del aeropuerto de destino.
        costo_total (float): Costo/distancia total de la ruta.

    Returns:
        tuple[list[str], float]: (ruta_ordenada, costo_total).
    """
    ruta = []
    nodo = destino
    while nodo is not None:
        ruta.append(nodo)
        nodo = predecesores[nodo]

    ruta.reverse()
    return (ruta, costo_total)
