from core.data_structures import ColaTurnos


class Combate:
    def __init__(self, heroes, enemigos, entrada=input):
        self.heroes = heroes
        self.enemigos = enemigos
        self.cola_turnos = ColaTurnos()
        self.ronda = 0
        self.entrada = entrada       # se puede reemplazar para hacer pruebas
        self.defensa_extra = {}      # entidad -> bonus de defensa por usar "Defender"

    
    def iniciar_combate(self):
        """Devuelve True si ganan los héroes y False si pierden."""
        print("\n==============================")
        print("     ¡COMIENZA EL COMBATE!")
        print("==============================")

        resultado = "continua"
        while resultado == "continua":
            self.ejecutar_ronda()
            resultado = self.verificar_fin_combate()

        self._quitar_defensas()
        if resultado == "victoria":
            self._dar_recompensas()
            return True
        print("\nEl escuadrón ha caído... La niebla desciende sobre los valles.")
        return False

    def ejecutar_ronda(self):
        """Una ronda: cada entidad viva actúa una vez, de más rápida a más lenta."""
        self.ronda += 1
        print(f"\n########## RONDA {self.ronda} ##########")
        self._mostrar_estado()

        vivos = [e for e in self.heroes + self.enemigos if e.esta_vivo()]
        self.cola_turnos.ordenar_por_velocidad(vivos)

        while not self.cola_turnos.esta_vacia():
            if self.verificar_fin_combate() != "continua":
                break

            entidad = self.cola_turnos.desencolar()
            if not entidad.esta_vivo():
                continue

            if entidad in self.heroes:
                self.procesar_turno_jugador(entidad)
            else:
                self.procesar_turno_enemigo(entidad)

    def verificar_fin_combate(self):
        """Devuelve "victoria", "derrota" o "continua"."""
        if not self._vivos(self.enemigos):
            return "victoria"
        if not self._vivos(self.heroes):
            return "derrota"
        return "continua"

    
    def procesar_turno_jugador(self, heroe):
        self._quitar_defensa(heroe)
        while True:
            print(f"\n--- Turno de {heroe.nombre} (HP {heroe.salud_actual}/{heroe.salud_max}) ---")
            print("1. Atacar   2. Habilidad   3. Usar ítem   4. Defender")
            opcion = self._pedir_numero("Elegí una acción: ", 1, 4)

            if opcion == 1:
                objetivo = self._elegir_objetivo(self._vivos(self.enemigos))
                danio = heroe.atacar(objetivo)
                print(f"{heroe.nombre} ataca a {objetivo.nombre} y causa {danio} de daño.")
                self._avisar_si_cae(objetivo)
                return

            if opcion == 2 and self._turno_habilidad(heroe):
                return

            if opcion == 3 and self._turno_item(heroe):
                return

            if opcion == 4:
                bonus = max(1, heroe.defensa // 2)
                heroe.defensa += bonus
                self.defensa_extra[heroe] = bonus
                print(f"{heroe.nombre} se pone en guardia: +{bonus} de defensa hasta su próximo turno.")
                return

    def procesar_turno_enemigo(self, enemigo):
        """El enemigo ataca al héroe que provoca; si no hay, al de menor vida."""
        self._quitar_defensa(enemigo)
        vivos = self._vivos(self.heroes)
        provocadores = [h for h in vivos if getattr(h, "provocando", False)]
        if provocadores:
            objetivo = provocadores[0]
        else:
            objetivo = min(vivos, key=lambda h: h.salud_actual)

        danio = enemigo.atacar(objetivo)
        print(f"\n{enemigo.nombre} ataca a {objetivo.nombre} y causa {danio} de daño.")
        self._avisar_si_cae(objetivo)

    
    def _turno_habilidad(self, heroe):
        habilidades = getattr(heroe, "habilidades", [])
        if not habilidades:
            print("Todavía no tenés habilidades.")
            return False

        print("Habilidades (0 para volver):")
        for i, h in enumerate(habilidades, start=1):
            print(f"{i}. {h.nombre} (energía: {h.costo_energia})")
        eleccion = self._pedir_numero("Elegí una habilidad: ", 0, len(habilidades))
        if eleccion == 0:
            return False

        objetivo = self._elegir_objetivo(self._vivos(self.enemigos) + self._vivos(self.heroes),
                                         marcar_aliados=True)
        if heroe.usar_habilidad(eleccion - 1, objetivo):
            self._avisar_si_cae(objetivo)
            return True
        print("No pudiste usar la habilidad (¿te falta energía?).")
        return False

    def _turno_item(self, heroe):
        inventario = getattr(heroe, "inventario", None)
        if inventario is None or inventario.esta_vacia():
            print("No tenés ítems.")
            return False

        print("Inventario (el primero es el tope de la pila):")
        inventario.mostrar_inventario()
        cantidad = len(inventario.elementos)
        eleccion = self._pedir_numero("Número de ítem (0 para volver): ", 0, cantidad)
        if eleccion == 0:
            return False

        objetivo = self._elegir_objetivo(self._vivos(self.heroes), texto="¿Sobre quién lo usás?")
        if heroe.usar_item(eleccion - 1, objetivo):
            return True
        print("No pudiste usar ese ítem.")
        return False

  
    def _dar_recompensas(self):
        print("\n*** ¡VICTORIA! ***")
        sobrevivientes = self._vivos(self.heroes)

        exp_total = sum(getattr(e, "exp_otorgada", 0) for e in self.enemigos)
        print(f"Cada superviviente gana {exp_total} de experiencia.")
        for heroe in sobrevivientes:
            if hasattr(heroe, "ganar_experiencia"):
                heroe.ganar_experiencia(exp_total)

        for i, enemigo in enumerate(self.enemigos):
            if hasattr(enemigo, "soltar_loot"):
                item = enemigo.soltar_loot()
                if item is not None:
                    receptor = sobrevivientes[i % len(sobrevivientes)]
                    receptor.inventario.push(item)
                    print(f"{receptor.nombre} recoge: {item}.")

    
    @staticmethod
    def _vivos(entidades):
        return [e for e in entidades if e.esta_vivo()]

    def _avisar_si_cae(self, objetivo):
        if not objetivo.esta_vivo():
            print(f"  >> {objetivo.nombre} ha caído.")

    def _quitar_defensa(self, entidad):
        entidad.defensa -= self.defensa_extra.pop(entidad, 0)

    def _quitar_defensas(self):
        for entidad in list(self.defensa_extra):
            self._quitar_defensa(entidad)

    def _mostrar_estado(self):
        print("\nHÉROES")
        for h in self.heroes:
            print(f"  {self._linea(h)}")
        print("ENEMIGOS")
        for e in self.enemigos:
            print(f"  {self._linea(e)}")

    @staticmethod
    def _linea(entidad):
        llenos = int(10 * entidad.salud_actual / entidad.salud_max)
        barra = "█" * llenos + "░" * (10 - llenos)
        return f"{entidad.nombre:<28} {barra} {entidad.salud_actual}/{entidad.salud_max}"

    def _pedir_numero(self, texto, minimo, maximo):
        while True:
            respuesta = self.entrada(texto).strip()
            if respuesta.isdigit() and minimo <= int(respuesta) <= maximo:
                return int(respuesta)
            print(f"Ingresá un número entre {minimo} y {maximo}.")

    def _elegir_objetivo(self, lista, texto="Elegí el objetivo:", marcar_aliados=False):
        if len(lista) == 1:
            return lista[0]
        print(texto)
        for i, entidad in enumerate(lista, start=1):
            marca = " (aliado)" if marcar_aliados and entidad in self.heroes else ""
            print(f"{i}. {entidad.nombre} ({entidad.salud_actual}/{entidad.salud_max}){marca}")
        return lista[self._pedir_numero("> ", 1, len(lista)) - 1]