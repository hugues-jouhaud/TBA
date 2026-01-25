# item.py — système d’items pour le jeu

class Item:
    """Item générique stackable."""

    def __init__(self, name, description, weight, max_stack=1):
        self.name = name
        self.description = description
        self.weight = weight 
        self.max_stack = max_stack

    def __str__(self):
        """Retourne une représentation textuelle de l'objet."""
        return f"{self.name} : {self.description} ({self.weight} kg)"

    def use(self, player):
        print(f"Vous ne pouvez pas utiliser {self.name}.")
        return False


class batterie(Item):
    """batterie d’énergie stackable."""

    def __init__(self):
        super().__init__(
            name="batterie",
            description="batterie permettant d'alimenter certains objets.",
            weight=0.1, 
            max_stack=20
        )
        self.capacity = 100
        self.charge = 100

    def use(self, player):
        print(f"Cette batterie a {self.charge}/{self.capacity} énergie.")
        return True

    def consume(self, amount):
        if self.charge >= amount:
            self.charge -= amount
            return True
        return False