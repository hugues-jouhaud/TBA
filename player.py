# player.py
from inventory import Inventory

class Player:
    """Représente le joueur."""

    def __init__(self, name):
        self.name = name
        self.inventory = Inventory()
        self.current_room = None
        self.hp = 2
        self.room_history = []
        self.prev_room = [] 
    
    def set_room(self, room):
        self.current_room = room

    def add_item(self, item, amount=1):
        if self.inventory.add_item(item, amount):
            print(f"Vous avez obtenu {amount} x {item.name}.")
            return True
        else:
            print("Votre inventaire est plein !")
            return False
            
    def remove_item(self, item_name, amount=1):
        """Tente de retirer un item de l'inventaire."""
        item_name = item_name.lower()
        for i, slot in enumerate(self.inventory.slots):
            if slot and slot.item.name.lower() == item_name:
                if slot.quantity < amount:
                    print(f"Vous n'avez pas {amount} x {slot.item.name}.")
                    return None
                item_to_drop = slot.item 
                slot.quantity -= amount
                if slot.quantity <= 0:
                    self.inventory.slots[i] = None
                return item_to_drop 
        print(f"L'objet '{item_name}' n'est pas dans l'inventaire'.")
        return None

    def get_inventory(self):
        return self.inventory.get_inventory_display()

    def move(self, direction):
        direction = direction.upper() # Correction majuscule

        if direction not in ["N","S","O","E","U","D"] :
            print("\nCette direction n'existe pas !\n")
            return False
        
        next_room = self.current_room.exits.get(direction)

        if next_room is None:
            print("\nAucune porte dans cette direction !\n")
            return False

        if self.current_room.description not in self.room_history:
            self.room_history.append(self.current_room.description)
        self.prev_room.append(self.current_room)

        self.current_room = next_room
        print(self.current_room.get_long_description())
        print(self.get_history())
        return True # Retourne True pour que le jeu sache qu'on a bougé (et active le monstre)

    def get_history(self):
        if not self.room_history:
            return ""
        history_string = "\nVous avez déja visité les pièces suivantes:"
        for description in self.room_history:
            description_cleaned = description.split(".")[0].replace("dans ", "").strip()
            history_string += f"\n        - {description_cleaned}"
        return history_string