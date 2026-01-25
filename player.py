# player.py
from inventory import Inventory
from quest import QuestManager  # <-- Ajout de l'import

class Player:
    """Représente le joueur."""

    def __init__(self, name):
        """
        Initialize a new player.
        
        Args:
            name (str): The name of the player.
            
        Examples:
        
        >>> player = Player("Alice")
        >>> player.name
        'Alice'
        """
        self.name = name
        self.inventory = Inventory()
        self.current_room = None
        self.hp = 2
        self.room_history = []
        self.prev_room = []
        self.max_weight = 10.0
        
        # --- AJOUT QUÊTES ---
        self.move_count = 0
        self.quest_manager = QuestManager(self)
        self.rewards = []  # List to store earned rewards
        # --------------------
    
    def set_room(self, room):
        self.current_room = room

    def add_item(self, item, amount=1):
        # 1. Calcul du poids actuel
        current_weight = 0
        for slot in self.inventory.slots:
            if slot:
                current_weight += slot.item.weight * slot.quantity
        
        # 2. Vérification si on dépasse le max avec le nouvel objet
        if current_weight + (item.weight * amount) > self.max_weight:
            print(f"\n Trop lourd ! ({item.name} pèse {item.weight}kg)")
            print(f"Poids actuel : {current_weight}/{self.max_weight}kg")
            return False

        # 3. Ajout normal si le poids est OK
        if self.inventory.add_item(item, amount):
            print(f"Vous avez obtenu {amount} x {item.name}.")
            return True
        else:
            print("Votre inventaire est plein (slots) !")
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

        # --- AJOUT QUÊTES ---
        # Vérification des objectifs de visite (Check room visit objectives)
        self.quest_manager.check_room_objectives(self.current_room.name)

        # Incrément du compteur de mouvement et vérification (Check movement objectives)
        self.move_count += 1
        self.quest_manager.check_counter_objectives("Se déplacer", self.move_count)
        # --------------------

        return True # Retourne True pour que le jeu sache qu'on a bougé (et active le monstre)

    def get_history(self):
        if not self.room_history:
            return ""
        history_string = "\nVous avez déja visité les pièces suivantes:"
        for description in self.room_history:
            description_cleaned = description.split(".")[0].replace("dans ", "").strip()
            history_string += f"\n        - {description_cleaned}"
        return history_string

    # --- AJOUT MÉTHODES QUÊTES ---

    def add_reward(self, reward):
        """
        Add a reward to the player's rewards list and inventory.
        """
        if reward and reward not in self.rewards:
            self.rewards.append(reward)
            # Ajouter la batterie d'énergie à l'inventaire
            if "batterie" in reward:
                from item import batterie
                batterie = batterie()
                self.inventory.add_item(batterie, 1)
            print(f"\n🎁 Vous avez obtenu: {reward}\n")

    def show_rewards(self):
        """
        Display all rewards earned by the player.
        """
        if not self.rewards:
            print("\n🎁 Aucune récompense obtenue pour le moment.\n")
        else:
            print("\n🎁 Vos récompenses:")
            for reward in self.rewards:
                print(f"  • {reward}")
            print()