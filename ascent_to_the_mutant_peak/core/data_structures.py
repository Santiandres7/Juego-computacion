from collections import deque

class PilaInventario:
    def __init__(self):
        self.elementos = []
    
    """agregar un elemento a la pila"""
    def push(self, item):
        self.elementos.append(item)
    
    """elimina el elemento superior de la pila"""
    def pop(self):
        if self.esta_vacia():
            raise IndexError("La pila está vacía")
        return self.elementos.pop()
    
    """devuelve el elemento superior de la pila"""
    def peek(self):
        if self.esta_vacia():
            raise IndexError("La pila está vacía")
        return self.elementos[-1]

    """verifica si la pila esta vacia"""
    def esta_vacia(self):
        return len(self.elementos) == 0
    
    """devuelve los elementos de la pila"""
    def mostrar_inventario(self):
        if self.esta_vacia():
            print("La pila está vacía")
            return
        for item in reversed(self.elementos):
            print(item) 

class ColaTurnos:
    """Cola (FIFO) para el orden de turnos en combate."""

    def __init__(self):
        self.cola = deque()

    def encolar(self, entidad):
        """Agrega una entidad al FINAL de la cola."""
        self.cola.append(entidad)

    def desencolar(self):
        """Quita y devuelve la entidad del FRENTE de la cola."""
        if self.esta_vacia():
            raise IndexError("La cola está vacía")
        return self.cola.popleft()

    def siguiente(self):
        """Devuelve la entidad del frente SIN quitarla."""
        if self.esta_vacia():
            raise IndexError("La cola está vacía")
        return self.cola[0]


    def esta_vacia(self):
        """Devuelve True si no hay entidades en la cola."""
        return len(self.cola) == 0

    def ordenar_por_velocidad(self, entidades):
        """Recibe una lista de entidades y las encola de mayor a menor velocidad."""
        self.cola.clear()
        entidades = sorted(entidades, key=lambda x: x.velocidad, reverse=True)
        for entidad in entidades:
            self.encolar(entidad)


class Nodo:
    """Un eslabón de la lista: guarda un dato y apunta al siguiente."""

    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class ListaTramos:
    """Lista enlazada que une los tramos del ascenso en orden."""

    def __init__(self):
        self.cabeza = None
        self.actual = None

    def agregar(self, tramo):
        """Agrega un tramo al FINAL de la lista."""
        actual_nodo = self.cabeza
        new_node = Nodo(tramo)
        if self.esta_vacia():
            self.cabeza = new_node
            self.actual = new_node
        else:
            while actual_nodo.siguiente is not None:
                actual_nodo = actual_nodo.siguiente
            actual_nodo.siguiente = new_node

    def esta_vacia(self):
        """Devuelve True si no hay tramos."""
        return self.cabeza is None

    def tramo_actual(self):
        """Devuelve el tramo en el que está el equipo."""
        if self.esta_vacia():
            raise IndexError("La lista de tramos está vacía")
        return self.actual.dato

    def avanzar(self):
        """Pasa al siguiente tramo. Devuelve False si ya era el último."""
        if self.actual.siguiente is None:
            return False
        else:
            self.actual = self.actual.siguiente
            return True

    def recorrer(self):
        """Imprime los tramos desde la cabeza hasta el final."""
        if self.esta_vacia():
            raise IndexError("La lista de tramos está vacía")
        actual_nodo = self.cabeza
        while actual_nodo is not None:
            print(actual_nodo.dato)
            actual_nodo = actual_nodo.siguiente