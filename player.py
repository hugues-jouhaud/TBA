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
        self.hp = 2 # Le joueur début avec deux PV.
        self.room_history = []
        self.prev_room = []
    
    # Define the move method.

    def set_room(self, room):
        self.current_room = room

    def add_item(self, item, amount=1):
        if self.inventory.add_item(item, amount):
            print(f"Vous avez obtenu {amount} x {item.name}.")
        else:
            print("Votre inventaire est plein !")
            
    # ATTENTION : Ajout de la méthode get_inventory()
    def get_inventory(self):
        """
        Retourne la représentation textuelle de l'inventaire.
        Délègue l'affichage à la classe Inventory.
        """
        # Appelle la méthode d'affichage dans Inventory
        return self.inventory.get_inventory_display()

    def move(self, direction):
        """
        Déplace le joueur dans la direction donnée si possible.
        """

        if direction not in ["N","S","O","E","U","D"] :
            print("\nCette direction n'existe pas !\n")
            return False
        
        next_room = self.current_room.exits.get(direction)

        if next_room is None:
            print("\nAucune porte dans cette direction !\n")
            return False

        # Ajout de la description de la pièce actuelle à l'historique AVANT de bouger
        if self.current_room.description not in self.room_history:
            self.room_history.append(self.current_room.description)
        self.prev_room.append(self.current_room)


        self.current_room = next_room
        print(self.current_room.get_long_description())
        print(self.get_history())
        return True

    def get_history(self):
        if not self.room_history:
            return ""
            
        history_string = "\nVous avez déja visité les pièces suivantes:"
        for description in self.room_history:

            description_cleaned = description.replace("dans ", "")
            history_string += f"\n\t- {description_cleaned}"
            
        return history_string