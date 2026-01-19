# room.py
from item import Item 

class Room:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.exits = {}
        self.items = {} # Stockage des items
    
    def get_exit(self, direction):
        if direction in self.exits.keys():
            return self.exits[direction]
        else:
            return None
    
    def get_exit_string(self):
        exit_string = "Sorties: " 
        for exit in self.exits.keys():
            if self.exits.get(exit) is not None:
                exit_string += exit + ", "
        exit_string = exit_string.strip(", ")
        return exit_string

    def add_item(self, item, quantity=1):
        """Ajoute un item à la salle."""
        self.items[item] = self.items.get(item, 0) + quantity

    def get_look_item_display(self):
        """Retourne la liste des objets pour la commande LOOK."""
        if not self.items:
            return "Il n'y a rien ici."
        output = "On voit:"
        for item_obj, quantity in self.items.items():
            item_str = item_obj.__str__()
            if quantity > 1:
                 item_str += f" x{quantity}"
            output += f"\n        - {item_str}"
        return output

    def take_item(self, item_name):
        """Retire un item de la salle et le retourne."""
        item_to_return = None
        item_key_to_delete = None
        
        for item_obj, quantity in self.items.items():
            if item_obj.name.lower() == item_name.lower():
                item_to_return = item_obj 
                self.items[item_obj] -= 1
                if self.items[item_obj] <= 0:
                    item_key_to_delete = item_obj
                break 
        
        if item_key_to_delete:
            del self.items[item_key_to_delete]
            
        return item_to_return

    def get_long_description(self):
        return f"\nVous êtes {self.description}\n\n{self.get_exit_string()}"
    
    def get_items_here(self):
        """Retourne la liste des items actuellement dans la pièce."""
        return self.items