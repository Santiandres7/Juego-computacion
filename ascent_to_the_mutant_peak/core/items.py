class Item:
    def __init__(self, nombre, tipo, atributo_afectado, valor, es_consumible):
        self.nombre = nombre
        self.tipo = tipo
        self.atributo_afectado = atributo_afectado
        self.valor = valor
        self.es_consumible = es_consumible

    def aplicar_efecto(self, objetivo):
        if self.atributo_afectado == "salud":
            objetivo.curar(self.valor)
        elif self.atributo_afectado == "energia":
            objetivo.recuperar_energia(self.valor)
        else:
            actual = getattr(objetivo, self.atributo_afectado)
            setattr(objetivo, self.atributo_afectado, actual + self.valor)


def crear_suero_primis():
    return Item("Suero de Primis Purificado", "curacion", "salud", 40, True)


def crear_racion_termica():
    return Item("Ración Térmica", "energia", "energia", 30, True)


def crear_piolet_reforzado():
    return Item("Piolet Reforzado", "equipamiento", "ataque", 5, False)


def crear_inyector_quimico():
    return Item("Inyector Químico", "equipamiento", "ataque", 4, False)

        
          