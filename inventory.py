# inventory.py — Inventaire du joueur
from item import Item # Ajout de l'import pour la clarté et l'accès à Item.name/max_stack

class InventorySlot:
    """Case d’inventaire contenant un objet + quantité."""

    def __init__(self, item, quantity=1):
        self.item = item
        self.quantity = quantity


class Inventory:
    def __init__(self, size=20):
        self.size = size
        self.slots = [None] * size

    def add_item(self, item, amount=1):
        """Ajoute un item en gérant les stacks."""

        # Empiler si stack déjà existant
        for slot in self.slots:
            if slot and slot.item.name == item.name and slot.quantity < item.max_stack:
                space = item.max_stack - slot.quantity
                to_add = min(space, amount)
                slot.quantity += to_add
                amount -= to_add
                if amount <= 0:
                    return True

        # Mettre dans un espace vide
        for i in range(self.size):
            if self.slots[i] is None:
                to_add = min(item.max_stack, amount)
                self.slots[i] = InventorySlot(item, to_add)
                amount -= to_add
                if amount <= 0:
                    return True

        return False  # Inventaire plein

    # ATTENTION : Méthode modifiée pour correspondre au format d'affichage requis.
    def get_inventory_display(self):
        """
        Produit la chaîne de caractères représentant l'inventaire du joueur.
        Format : 'Votre inventaire est vide.' ou 'Vous disposez des items suivants : ...'
        """
        item_list_strings = []
        
        # Consolidation des items uniques (si plusieurs stacks du même item)
        # Mais pour la consigne, il faut afficher chaque slot utilisé
        
        for slot in self.slots:
            if slot:
                # Utilise la méthode __str__ de l'Item
                item_str = f"{slot.item.__str__()} x{slot.quantity}"
                item_list_strings.append(item_str)
        
        if not item_list_strings:
            return "Votre inventaire est vide."
        
        output = "Vous disposez des items suivants :"
        for item_str in item_list_strings:
            output += f"\n    - {item_str}"
            
        return output