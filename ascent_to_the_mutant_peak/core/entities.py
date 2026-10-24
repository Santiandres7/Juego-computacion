from abc import ABC, abstractmethod

class Entidad(ABC):
    def __init__(self, nombre, salud_max, ataque, defensa, velocidad):
        self.nombre = nombre
        self.salud_max = salud_max
        self.salud_actual = salud_max
        self.ataque = ataque
        self.defensa = defensa
        self.velocidad = velocidad
    
    def esta_vivo(self):
        
        """devuelve True si la vida es mayor que 0"""
        return self.salud_actual > 0
    
    def recibir_danio(self, cantidad):
        """Recibe danio, si la defensa es mayor al danio hace 1 de danio y no puede bajar de 0"""
        danio_real = max(0, cantidad - self.defensa)
        if danio_real <= 0:
            danio_real = 1
        else:
            self.salud_actual -= danio_real
            if self.salud_actual < 0:
                self.salud_actual = 0
        return danio_real
    
    def curar(self,cantidad):
        """Restaura salud a la  entidad sin pasar del maximo"""
        self.salud_actual += cantidad
        if self.salud_actual > self.salud_max:
            self.salud_actual = self.salud_max
    
    @abstractmethod
    def atacar(self, objetivo):
        pass