import re
from civrealm.freeciv.utils.freeciv_logging import fc_logger

def analizar_situacion_juego(contenido_mensaje, acciones_disponibles):
    """
    Analiza el contenido del mensaje para extraer información sobre la situación del juego
    y proporcionar consejos estratégicos específicos.
    
    Args:
        contenido_mensaje (str): Contenido del mensaje con la información del juego
        acciones_disponibles (list): Lista de acciones disponibles
        
    Returns:
        str: Análisis estratégico basado en el contexto
    """
    # Inicializar variables para análisis
    recursos_cercanos = []
    terrenos = []
    unidades_cercanas = []
    ciudades_cercanas = 0
    casillas_inexploradas = 0
    
    # Buscar recursos en el mensaje
    recursos_buscar = ["Gold", "Iron", "Wheat", "Fish", "Buffalo", "Wine", "Silk", "Whale", "Pheasant"]
    for recurso in recursos_buscar:
        if recurso in contenido_mensaje:
            recursos_cercanos.append(recurso)
    
    # Buscar tipos de terreno
    terrenos_buscar = ["Plains", "Grassland", "Hills", "Mountains", "Forest", "Desert", "Ocean", "River", "Swamp", "Lake"]
    for terreno in terrenos_buscar:
        if terreno in contenido_mensaje:
            terrenos.append(terreno)
    
    # Buscar unidades y ciudades
    if "Settlers" in contenido_mensaje:
        unidades_cercanas.append("Settlers")
    if "Workers" in contenido_mensaje:
        unidades_cercanas.append("Workers")
    if "Explorer" in contenido_mensaje:
        unidades_cercanas.append("Explorer")
    if "Warrior" in contenido_mensaje:
        unidades_cercanas.append("Warrior")
    if "cities of myself" in contenido_mensaje:
        match = re.search(r'(\d+) cities of myself', contenido_mensaje)
        if match:
            ciudades_cercanas = int(match.group(1))
    
    # Contar casillas inexploradas
    matches = re.findall(r'(\d+) tiles unexplored', contenido_mensaje)
    for m in matches:
        casillas_inexploradas += int(m)
    
    # Generar análisis estratégico
    analisis = ""
    
    # Si hay recursos cercanos, mencionarlos
    if recursos_cercanos:
        analisis += f"Recursos cercanos: {', '.join(recursos_cercanos)}. "
        analisis += "Considera expandirte o mejorar estas casillas para aprovechar estos recursos. "
    
    # Si hay muchas casillas inexploradas, sugerir exploración
    if casillas_inexploradas > 10 and any("move" in a for a in acciones_disponibles):
        analisis += "Hay muchas áreas sin explorar. La exploración te ayudará a encontrar lugares óptimos para expandirte. "
    
    # Si hay ríos, sugerir asentamiento cerca
    if "River" in terrenos:
        analisis += "Los ríos proporcionan bonificaciones comerciales y son ideales para ciudades y agricultura. "
    
    # Si es ciudad y hay pocas ciudades, sugerir expansión
    if any("produce" in a for a in acciones_disponibles) and ciudades_cercanas < 3:
        analisis += "Estás en fase temprana, considera producir Settlers para expandir tu imperio. "
    
    # Si hay muchos bosques/montañas y hay workers
    if ("Forest" in terrenos or "Mountains" in terrenos or "Hills" in terrenos) and "Workers" in unidades_cercanas:
        analisis += "Los Workers pueden mejorar el terreno: minas en colinas/montañas y talar bosques para producción. "
    
    return analisis

def analizar_calidad_decision(accion, contexto, acciones_disponibles):
    """
    Analiza la calidad estratégica de la decisión tomada por el LLM.
    
    Args:
        accion (str): La acción elegida por el LLM
        contexto (str): El contexto del juego (mensaje del usuario)
        acciones_disponibles (list): Lista de acciones disponibles
        
    Returns:
        tuple: (puntuación de calidad (0-10), explicación de la evaluación)
    """
    fc_logger.debug(f"Analizando calidad de la decisión: {accion}")
    
    # Determinar si estamos al inicio del juego
    es_inicio_juego = "Turn: 1" in contexto or "Turn: 2" in contexto or "Turn: 3" in contexto
    
    # Verificar el tipo de acción
    es_accion_ciudad = accion.startswith("produce")
    es_accion_construccion = accion.startswith("build") or accion == "irrigation" or accion == "mine" or accion == "road"
    es_accion_movimiento = accion.startswith("move") or accion == "auto_explore"
    
    puntuacion = 5  # Puntuación neutral por defecto
    razonamiento = ""
    
    # Evaluar acciones de producción de ciudad
    if es_accion_ciudad:
        if es_inicio_juego and accion == "produce Settlers":
            puntuacion = 9
            razonamiento = "Excelente decisión producir Settlers al inicio para expandir tu imperio."
        elif es_inicio_juego and accion == "produce Warriors":
            puntuacion = 7
            razonamiento = "Producir Warriors al inicio puede ser útil para defensa, aunque expandirse suele ser prioritario."
        elif accion == "produce Barracks":
            puntuacion = 6
            razonamiento = "Las Barracks son útiles para el entrenamiento militar, pero podrían no ser prioritarias al inicio."
        elif accion == "produce Coinage":
            puntuacion = 4
            razonamiento = "Coinage proporciona oro inmediato pero no es una inversión a largo plazo."
    
    # Evaluar acciones de construcción
    elif es_accion_construccion:
        if accion == "build city":
            # Verificar si hay recursos cercanos para la ciudad
            hay_recursos_cerca = any(recurso in contexto for recurso in ["Gold", "Iron", "Wheat", "Fish"])
            hay_rio_cerca = "River" in contexto
            
            if hay_recursos_cerca and hay_rio_cerca:
                puntuacion = 10
                razonamiento = "Excelente ubicación para ciudad: recursos y río cercanos."
            elif hay_recursos_cerca:
                puntuacion = 9
                razonamiento = "Buena ubicación para ciudad cerca de recursos."
            elif hay_rio_cerca:
                puntuacion = 8
                razonamiento = "Buena ubicación para ciudad cerca de río."
            else:
                puntuacion = 6
                razonamiento = "Ubicación aceptable para ciudad."
        
        elif accion == "irrigation":
            if "Grassland" in contexto or "Plains" in contexto:
                puntuacion = 8
                razonamiento = "Buena decisión: la irrigación mejora la producción de comida."
            else:
                puntuacion = 5
                razonamiento = "La irrigación es más efectiva en praderas y llanuras."
        
        elif accion == "mine":
            if "Hills" in contexto or "Mountains" in contexto:
                puntuacion = 8
                razonamiento = "Buena decisión: las minas mejoran la producción en colinas y montañas."
            else:
                puntuacion = 4
                razonamiento = "Las minas son más efectivas en colinas y montañas."
        
        elif accion == "road":
            puntuacion = 7
            razonamiento = "Los caminos mejoran el movimiento y comercio entre ciudades."
    
    # Evaluar acciones de movimiento
    elif es_accion_movimiento:
        if accion == "auto_explore":
            puntuacion = 7
            razonamiento = "La exploración automática es útil para descubrir el mapa."
        else:  # move direcciones
            # Verificar si hay casillas sin explorar en esa dirección
            direccion = accion.split(" ")[1]
            patron_direccion = f"tile_{direccion.lower()}"
            
            if "unexplored" in contexto and patron_direccion in contexto:
                puntuacion = 8
                razonamiento = f"Buen movimiento hacia área inexplorada ({direccion})."
            elif "Minor Tribe Village" in contexto and patron_direccion in contexto:
                puntuacion = 9
                razonamiento = f"Excelente movimiento hacia aldea tribal ({direccion})."
            else:
                puntuacion = 6
                razonamiento = f"Movimiento aceptable hacia {direccion}."
    
    fc_logger.info(f"Evaluación de decisión - {accion}: {puntuacion}/10 - {razonamiento}")
    return puntuacion, razonamiento

def mejorar_prompt_estrategico(processed_dialogue, last_action_msg_idx, available_actions):
    """
    Añade consejos estratégicos específicos al diálogo según el contexto del juego.
    El agente solo usa mensajes del sistema para la orientación estratégica,
    manteniendo su total autonomía.
    
    Args:
        processed_dialogue (list): Diálogo procesado
        last_action_msg_idx (int): Índice del último mensaje con acciones
        available_actions (list): Lista de acciones disponibles
        
    Returns:
        list: Diálogo con consejos estratégicos añadidos como mensajes del sistema
    """
    if last_action_msg_idx < 0 or not available_actions:
        return processed_dialogue
        
    # Detectar el tipo de unidad o ciudad
    es_ciudad = any('produce' in action for action in available_actions)
    es_settler = any('build city' in action for action in available_actions)
    es_worker = any('irrigation' in action or 'mine' in action for action in available_actions)
    es_explorer = any('auto_explore' in action for action in available_actions)
    
    msg_content = processed_dialogue[last_action_msg_idx]['content'] if last_action_msg_idx >= 0 else ""
    
    consejo_estrategico = ""
    if es_ciudad:
        # Añadir consejos específicos para ciudades según las opciones disponibles
        if 'produce Settlers' in available_actions:
            consejo_estrategico = (
                "Prioriza la producción de Settlers al inicio del juego para expandirte. "
                "Este es el momento ideal para fundar nuevas ciudades."
            )
        elif 'produce Warriors' in available_actions or 'produce Barracks' in available_actions:
            consejo_estrategico = (
                "Construir unidades militares es importante si hay tribus bárbaras o enemigos cercanos. "
                "Las Barracks te permitirán entrenar unidades más fuertes en el futuro."
            )
        elif 'produce Coinage' in available_actions:
            consejo_estrategico = (
                "Coinage proporciona dinero inmediato, pero no es una inversión a largo plazo. "
                "Solo es recomendable si necesitas oro urgentemente."
            )
    elif es_settler:
        consejo_estrategico = (
            "Funda ciudades en llanuras (Plains) o praderas (Grassland), idealmente cerca de recursos o ríos. "
            "Mantén tus ciudades separadas por 4-5 casillas para maximizar territorio."
        )
    elif es_worker:
        consejo_estrategico = (
            "Prioriza mejorar casillas con recursos (especialmente comida y producción). "
            "Construye irrigación en praderas y llanuras, minas en colinas, y caminos para conectar ciudades."
        )
    elif es_explorer:
        consejo_estrategico = (
            "Explora para descubrir nuevos recursos y buenos lugares para ciudades. "
            "Prioriza explorar áreas desconocidas y evita mover unidades en círculos."
        )
    
    # Añadir un análisis estratégico de la situación
    analisis = analizar_situacion_juego(msg_content, available_actions)
    
    # Añadir un recordatorio como mensaje del sistema (no del usuario)
    reminder_msg = {
        'role': 'system',
        'content': (f"IMPORTANT REMINDER: You must only suggest actions from this list: {available_actions}. " 
                  f"Consejo estratégico: {consejo_estrategico} {analisis}")
    }
    
    # Insertar el recordatorio justo después del mensaje con las acciones
    processed_dialogue.insert(last_action_msg_idx + 1, reminder_msg)
    
    return processed_dialogue