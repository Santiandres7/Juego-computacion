from entities import Entidad
from data_structures import PilaInventario


class Personaje(Entidad):
    """Héroe controlado por el jugador. Hereda de Entidad."""

    def __init__(self, nombre, clase, salud_max, ataque, defensa, velocidad, energia_max):
        """Crea un héroe de nivel 1 con inventario vacío."""
        super().__init__(nombre, salud_max, ataque, defensa, velocidad)
        self.clase = clase
        self.nivel = 1
        self.experiencia = 0
        self.exp_siguiente_nivel = 100
        self.energia_max = energia_max
        self.energia_actual = energia_max
        self.habilidades = []
        self.inventario = PilaInventario()

    def subir_nivel(self):
        """Sube el nivel, mejora las estadísticas base y restaura salud y energía."""
        self.nivel += 1
        self.salud_max += 10
        self.ataque += 5
        self.defensa += 5
        self.velocidad += 2
        self.energia_max += 10
        self.salud_actual = self.salud_max
        self.energia_actual = self.energia_max
        self.exp_siguiente_nivel = int(self.exp_siguiente_nivel * 1.5)

    def ganar_experiencia(self, puntos):
        """Suma experiencia y sube de nivel las veces que haga falta.

        Devuelve True si subió al menos un nivel.
        """
        self.experiencia += puntos
        subio = False
        while self.experiencia >= self.exp_siguiente_nivel:
            self.experiencia -= self.exp_siguiente_nivel
            self.subir_nivel()
            subio = True
        return subio

    def usar_habilidad(self, indice, objetivo):
        """Usa la habilidad en esa posición. Devuelve False si no se pudo."""
        if not 0 <= indice < len(self.habilidades):
            return False
        habilidad = self.habilidades[indice]
        if self.energia_actual < habilidad.costo_energia:
            return False
        self.energia_actual -= habilidad.costo_energia
        habilidad.aplicar(self, objetivo)
        return True

    def usar_item(self, objetivo):
        """Saca el item del tope del inventario y lo aplica.

        Devuelve False si el inventario está vacío. Si el item no es
        consumible, vuelve al inventario después de usarse.
        """
        try:
            item = self.inventario.pop()
        except IndexError:
            return False
        item.aplicar_efecto(objetivo)
        if not item.es_consumible:
            self.inventario.push(item)
        return True

    def recuperar_energia(self, cantidad):
        """Suma energía sin pasar de energia_max."""
        self.energia_actual = min(self.energia_max, self.energia_actual + cantidad)

    def atacar(self, objetivo):
        """Ataque básico. Devuelve el daño real hecho al objetivo."""
        return objetivo.recibir_danio(self.ataque)


if __name__ == "__main__":
    kael = Personaje("Kael", "Cazador", 95, 25, 10, 18, 90)
    print(kael.ganar_experiencia(250))   # True
    print(kael.nivel, kael.experiencia)  # 3 0

    dummy = Personaje("Dummy", "Prueba", 100, 10, 5, 5, 10)
    print(kael.atacar(dummy))            # 30 (35 de ataque menos 5 de defensa)
    print(dummy.salud_actual)            # 70
    print(kael.usar_item(dummy))         # False (inventario vacío)