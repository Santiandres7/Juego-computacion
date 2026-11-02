"""
Data Structures Module.
Implements:
1. InventoryStack (LIFO): For fast-access hero inventory.
2. TurnQueue (FIFO): For speed-based round combat turns.
3. StageNode & StageLinkedList: Singly linked list for stage progression.
"""
from collections import deque
import json
import os


class InventoryStack:
    """Pila LIFO para gestionar el inventario del héroe (el último objeto añadido es el primero disponible)."""
    def __init__(self):
        self._items = []

    def push(self, item):
        """Inserta un elemento en la parte superior de la pila."""
        self._items.append(item)

    def pop(self):
        """Saca y devuelve el elemento superior de la pila."""
        if self.is_empty():
            return None
        return self._items.pop()

    def peek(self):
        """Examina el elemento superior sin retirarlo."""
        if self.is_empty():
            return None
        return self._items[-1]

    def is_empty(self) -> bool:
        """Devuelve True si la pila no tiene elementos."""
        return len(self._items) == 0

    def show_inventory(self):
        """Imprime los elementos desde la parte superior hasta la inferior."""
        if self.is_empty():
            print("El inventario está vacío.")
            return
        for item in reversed(self._items):
            print(f"- {item.name}")

    def get_all(self) -> list:
        """Devuelve todos los elementos en orden de visualización."""
        return list(reversed(self._items))


class TurnQueue:
    """Cola FIFO para organizar el orden de turno en las rondas de combate"""
    def __init__(self):
        self._queue = deque()

    def enqueue(self, entity):
        """Añade una entidad al final de la cola."""
        self._queue.append(entity)

    def dequeue(self):
        """Elimina y devuelve la entidad al frente de la cola."""
        if self.is_empty():
            return None
        return self._queue.popleft()

    def peek(self):
        """Examina la próxima entidad sin eliminarla."""
        if self.is_empty():
            return None
        return self._queue[0]

    def is_empty(self) -> bool:
        """Devuelve True si no quedan entidades en la ronda actual."""
        return len(self._queue) == 0

    def sort_by_speed(self, entities: list):
        """
        Filtra las entidades vivas, las ordena por velocidad en orden descendente,
        y las carga en la cola FIFO.
        """
        self._queue.clear()
        alive_entities = [e for e in entities if e.is_alive()]
        alive_entities.sort(key=lambda x: x.speed, reverse=True)
        for entity in alive_entities:
            self.enqueue(entity)


class StageNode:
    """Elemento de nodo para la lista enlazada que representa una etapa individual."""
    def __init__(self, data):
        self.data = data
        self.next = None


class StageLinkedList:
    """Lista enlazada simple que conecta las etapas de la ascensión de la montaña en orden."""
    def __init__(self):
        self.head = None
        self.current = None

    def append(self, stage_data):
        """Añade un nuevo nodo de etapa al final de la lista."""
        new_node = StageNode(stage_data)
        if self.is_empty():
            self.head = new_node
            self.current = new_node
        else:
            runner = self.head
            while runner.next is not None:
                runner = runner.next
            runner.next = new_node

    def is_empty(self) -> bool:
        """Comprueba si la lista de etapas está vacía."""
        return self.head is None

    def get_current_stage(self):
        """Devuelve los datos de la etapa actual activa."""
        if self.is_empty() or self.current is None:
            return None
        return self.current.data

    def advance(self) -> bool:
        """Avanza al siguiente nodo de etapa. Devuelve False si ya se encuentra en la cima."""
        if self.current is None or self.current.next is None:
            return False
        self.current = self.current.next
        return True

    def display_stages(self):
        """Recorre e imprime todas las etapas, desde la base hasta la cima."""
        if self.is_empty():
            print("No hay etapas registradas.")
            return
        runner = self.head
        while runner is not None:
            print(runner.data)
            runner = runner.next


# ---------------------------------------------------------
# Persistencia: Guardado y Carga de Partida
# ---------------------------------------------------------

SAVE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "saved_game.json")


def save_game_state(mountain: StageLinkedList, squad: list) -> bool:
    """Guarda el progreso de la montaña y del escuadrón en data/saved_game.json."""
    try:
        current_stage = mountain.get_current_stage()
        stage_num = current_stage.number if current_stage and hasattr(current_stage, "number") else 1

        data = {
            "current_stage_number": stage_num,
            "squad": []
        }

        for hero in squad:
            # Extraemos los nombres de los ítems usando get_all() de InventoryStack
            items_data = [item.name for item in hero.backpack.get_all()] if hasattr(hero, "backpack") else []
            
            hero_info = {
                "name": hero.name,
                "role": getattr(hero, "role", ""),
                "current_hp": hero.current_hp,
                "max_hp": hero.max_hp,
                "attack": getattr(hero, "attack", 10),
                "defense": getattr(hero, "defense", 5),
                "speed": getattr(hero, "speed", 5),
                "inventory": items_data
            }
            data["squad"].append(hero_info)

        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"Error al guardar la partida: {e}")
        return False


def load_game_state() -> dict | None:
    """Lee el archivo data/saved_game.json si existe."""
    if not os.path.exists(SAVE_PATH):
        return None
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al cargar la partida: {e}")
        return None

