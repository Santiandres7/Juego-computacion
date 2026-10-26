"""
Data Structures Module.
Implements:
1. InventoryStack (LIFO): For fast-access hero inventory.
2. TurnQueue (FIFO): For speed-based round combat turns.
3. StageNode & StageLinkedList: Singly linked list for stage progression.
"""
from collections import deque


class InventoryStack:
    """LIFO Stack to manage hero inventory (last item in is the first available)."""
    def __init__(self):
        self._items = []

    def push(self, item):
        """Pushes an item onto the top of the stack."""
        self._items.append(item)

    def pop(self):
        """Pops and returns the top item from the stack."""
        if self.is_empty():
            return None
        return self._items.pop()

    def peek(self):
        """Inspects the top item without removing it."""
        if self.is_empty():
            return None
        return self._items[-1]

    def is_empty(self) -> bool:
        """Returns True if the stack has no items."""
        return len(self._items) == 0

    def show_inventory(self):
        """Prints items from top to bottom."""
        if self.is_empty():
            print("The inventory is empty.")
            return
        for item in reversed(self._items):
            print(f"- {item.name}")

    def get_all(self) -> list:
        """Returns all items in display order."""
        return list(reversed(self._items))


class TurnQueue:
    """FIFO Queue to organize the turn order in combat rounds."""
    def __init__(self):
        self._queue = deque()

    def enqueue(self, entity):
        """Appends an entity to the back of the queue."""
        self._queue.append(entity)

    def dequeue(self):
        """Removes and returns the entity at the front of the queue."""
        if self.is_empty():
            return None
        return self._queue.popleft()

    def peek(self):
        """Inspects the next entity without dequeuing it."""
        if self.is_empty():
            return None
        return self._queue[0]

    def is_empty(self) -> bool:
        """Returns True if no entities remain in the current round."""
        return len(self._queue) == 0

    def sort_by_speed(self, entities: list):
        """
        Filters alive entities, sorts them by speed descending,
        and loads them into the FIFO queue.
        """
        self._queue.clear()
        alive_entities = [e for e in entities if e.is_alive()]
        alive_entities.sort(key=lambda x: x.speed, reverse=True)
        for entity in alive_entities:
            self.enqueue(entity)


class StageNode:
    """Node element for the linked list representing a single stage."""
    def __init__(self, data):
        self.data = data
        self.next = None


class StageLinkedList:
    """Singly Linked List connecting mountain ascent stages in order."""
    def __init__(self):
        self.head = None
        self.current = None

    def append(self, stage_data):
        """Appends a new stage node at the end of the list."""
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
        """Checks if the stage list is empty."""
        return self.head is None

    def get_current_stage(self):
        """Returns the data of the current active stage."""
        if self.is_empty() or self.current is None:
            return None
        return self.current.data

    def advance(self) -> bool:
        """Moves to the next stage node. Returns False if already at the summit."""
        if self.current is None or self.current.next is None:
            return False
        self.current = self.current.next
        return True

    def display_stages(self):
        """Traverses and prints all stages from base to summit."""
        if self.is_empty():
            print("No stages registered.")
            return
        runner = self.head
        while runner is not None:
            print(runner.data)
            runner = runner.next

