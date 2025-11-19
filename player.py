# player.py
from inventory import Inventory

class Player:
    """
    Représente le joueur.
    """

    def __init__(self, name):
        self.name = name
        self.inventory = Inventory()
        self.current_room = None

    def set_room(self, room):
        self.current_room = room

    def add_item(self, item, amount=1):
        if self.inventory.add_item(item, amount):
            print(f"Vous avez obtenu {amount} x {item.name}.")
        else:
            print("Votre inventaire est plein !")

    def move(self, direction):
        """
        Déplace le joueur dans la direction donnée si possible.
        """
        next_room = self.current_room.exits.get(direction)

        if next_room is None:
            print("\nAucune porte dans cette direction !\n")
            return False

        self.current_room = next_room
        print(self.current_room.get_long_description())
        return True
