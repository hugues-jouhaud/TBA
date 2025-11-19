# inventory.py — Inventaire du joueur

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

    def show(self):
        print("=== INVENTAIRE ===")
        for i, slot in enumerate(self.slots):
            if slot:
                print(f"[{i}] {slot.item.name} x{slot.quantity}")
            else:
                print(f"[{i}] (vide)")
