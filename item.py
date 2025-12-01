# items.py — système d’items pour le jeu

class Item:
    """Item générique stackable."""

    # ATTENTION : Ajout de 'weight' dans le constructeur et initialisation.
    def __init__(self, name, description, weight, max_stack=1):
        self.name = name
        self.description = description
        self.weight = weight # <--- AJOUTÉ
        self.max_stack = max_stack

    # ATTENTION : Ajout de la méthode __str__ pour l'affichage requis.
    def __str__(self):
        """Retourne une représentation textuelle de l'objet."""
        return f"{self.name} : {self.description} ({self.weight} kg)"

    def use(self, player):
        print(f"Vous ne pouvez pas utiliser {self.name}.")
        return False


class Pile(Item):
    """Pile d’énergie stackable."""

    def __init__(self):
        # ATTENTION : Mise à jour de l'appel super().__init__ pour inclure 'weight'
        super().__init__(
            name="pile",
            description="Pile permettant d'alimenter certains objets.",
            weight=0.1, # <--- AJOUTÉ
            max_stack=20
        )
        self.capacity = 100
        self.charge = 100

    def use(self, player):
        print(f"Cette pile a {self.charge}/{self.capacity} énergie.")
        return True

    def consume(self, amount):
        if self.charge >= amount:
            self.charge -= amount
            return True
        return False