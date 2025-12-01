from room import Room
from player import Player
from actions import Actions
from command import Command
from item import Item, Pile 
from npc import Monstre 
import time
import random

class Game:
    def __init__(self):
        self.finished = False
        self.rooms = []
        self.commands = {}
        self.player = None
        self.npc = None # Le monstre commence inexistant
        self.debug = True
        self.qte_count = 0
    
    def setup(self):
        # --- COMMANDES ---
        self.commands["help"] = Command("help", " : afficher cette aide", Actions.help, 0)
        self.commands["quit"] = Command("quit", " : quitter le jeu", Actions.quit, 0)
        self.commands["go"] = Command("go", " <direction> : se déplacer (N, E, S, O, U, D)", Actions.go, 1)
        self.commands["check"] = Command("check", " : Affiche l’inventaire", Actions.action_check, 0) 
        self.commands["history"] = Command("history", " : Historique des pièces", Actions.action_history, 0)
        self.commands["back"] = Command("back", " : Retour arrière", Actions.action_back, 0)
        self.commands["look"] = Command("look", " : voir les objets", Actions.action_look, 0) 
        self.commands["take"] = Command("take", " <item> : prendre un objet", Actions.action_take, 1) 
        self.commands["drop"] = Command("drop", " <item> : jeter un objet", Actions.action_drop, 1)

        # --- SALLES (VOTRE CARTE) ---
        self.cave = Room("cave", "dans une cave sombre et humide")
        self.rituel = Room("salle de Rituel", "dans une pièce étrange avec des symboles au sol")
        self.stock1 = Room("stockage 1", "dans un débarras encombré")
        self.clouloir1 = Room("Couloir 1", "dans un long couloir sombre")
        self.prison = Room("Jaule", "enfermé dans une vieille geôle")
        self.sdb2 = Room("salle de bain 2", "dans une salle de bain délabrée")
        self.ch2 = Room("Chambre 2", "dans une chambre d'amis poussiéreuse")
        self.clouloir2 = Room("Couloir 2", "dans le couloir de l'étage")
        self.stock2 = Room("Stockage 2", "dans une petite réserve à provisions")
        self.bureau = Room("Bureau", "dans un grand bureau rempli de livres")
        self.balcon = Room("balcon", "sur le balcon, vous avez une vue dégagée sur le salon")
        self.safe = Room("Safe", "dans une pièce blindée et sécurisée")
        self.cuisine = Room("Cuisine", "dans une cuisine aux couteaux rouillés")
        self.sam = Room("Salle a manger", "dans une grande salle à manger")
        self.salon = Room("salon", "dans un salon confortable avec une cheminée")
        self.ch1 = Room("Chambre 1", "dans la chambre principale")
        self.sdb1 = Room("Salle de bain 1", "dans une petite salle de bain carrelée")

        self.rooms.extend([
            self.cave, self.rituel, self.stock1, self.clouloir1, self.prison,
            self.sdb2, self.ch2, self.clouloir2, self.stock2, self.bureau,
            self.balcon, self.safe, self.cuisine, self.sam, self.salon,
            self.ch1, self.sdb1
        ])

        # --- EXITS ---
        self.cave.exits = {"N": self.stock1, "U": self.cuisine}
        self.rituel.exits = {"S": self.clouloir1, "O": self.stock1}
        self.stock1.exits = {"E": self.rituel, "S": self.cave, "U": self.safe}
        self.clouloir1.exits = {"N": self.rituel, "E": self.prison}
        self.prison.exits = {"O": self.clouloir1}
        self.sdb2.exits = {"S": self.ch2}
        self.ch2.exits = {"N": self.sdb2, "E": self.clouloir2}
        self.clouloir2.exits = {"N": self.stock2, "E": self.balcon, "O": self.ch2}
        self.stock2.exits = {"S": self.clouloir2}
        self.bureau.exits = {"S": self.balcon, "D": self.clouloir1}
        self.balcon.exits = {"N": self.bureau, "E": self.safe, "O": self.clouloir2, "D": self.salon}
        self.safe.exits = {"O": self.balcon, "D": self.stock1}
        self.cuisine.exits = {"E": self.sam, "D": self.cave}
        self.sam.exits = {"E": self.salon, "O": self.cuisine}
        self.salon.exits = {"E": self.ch1, "O": self.sam, "U": self.balcon}
        self.ch1.exits = {"E": self.sdb1, "O": self.salon}
        self.sdb1.exits = {"O": self.ch1}

        # --- ITEMS (AJOUT DU SYSTÈME D'OBJETS) ---
        sword = Item("sword", "une épée tranchante", 2.0)
        shield = Item("shield", "un bouclier", 1.5)
        potion = Item("potion", "une potion rouge", 0.5)
        pile = Pile() # Item spécial

        # Placement des items
        self.stock1.add_item(sword, 1)
        self.safe.add_item(shield, 1)
        self.cuisine.add_item(potion, 2)
        self.rituel.add_item(pile, 1)

        # --- JOUEUR ---
        self.player = Player(input("\nEntrez votre nom: "))
        self.player.set_room(self.salon)

    def play(self):
        self.setup()
        self.print_welcome()
        
        while not self.finished:
            # DEBUG
            if self.debug and self.npc:
                print(f"[DEBUG] Monstre: {self.npc.current_room.name}")

            user_input = input("> ")
            if not user_input: continue
            
            # --- LOGIQUE DU MONSTRE (Déplacement) ---
            monster_intercepted = False
            words = user_input.split()
            if words:
                command_word = words[0]
                # Le monstre bouge si le joueur bouge
                if self.npc is not None and command_word in ["go", "back"]:
                    etais_stun = self.npc.stunned_turns > 0
                    self.npc.move()
                    # Interception (Le monstre arrive sur le joueur)
                    if self.npc.current_room == self.player.current_room and not etais_stun:
                        monster_intercepted = True
                        self.trigger_qte()

            # --- TRAITEMENT COMMANDE ---
            if not monster_intercepted:
                self.process_command(user_input)
                # Rencontre (Le joueur arrive sur le monstre)
                if self.npc is not None and self.npc.current_room == self.player.current_room:
                    if self.npc.stunned_turns == 0:
                        self.trigger_qte()
            
            if self.finished: break

            # --- GESTION DU SPAWN ---
            if self.npc is None:
                # Apparition UNIQUEMENT dans la salle rituel
                if self.player.current_room == self.rituel:
                    self.spawn_monster()
            
            # --- AMBIANCE ---
            elif self.npc is not None:
                if self.npc.current_room != self.player.current_room:
                    distance = self.npc.distance_du_joueur(self.player.current_room)
                    if distance == 1:
                        print("\n--> Vous entendez des bruits de pas tout proches...")

    def spawn_monster(self):
        self.npc = Monstre()
        self.npc.current_room = self.salon
        print("\n-----------------------------------------------------")
        print("Un rugissement glacial secoue le manoir...")
        print(f"Vous avez réveillé un monstre ! Il est dans le {self.npc.current_room.name}.")
        print("-----------------------------------------------------\n")

    def trigger_qte(self):
        """Gère le Quick Time Event."""
        print("\n" + "!"*40)
        print("SURPRISE ! LE MONSTRE VOUS FONCE DESSUS !")
        print("!"*40)

        length = 3 + (self.qte_count * 2)
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        target_word = ''.join(random.choice(alphabet) for i in range(length))

        print(f"\nVous avez 5 secondes pour taper : {target_word}")
        
        start_time = time.time()
        user_input = input("CODE > ")
        end_time = time.time()
        
        duration = end_time - start_time

        if user_input == target_word and duration <= 5.0:
            print(f"\nSUCCÈS ! (Temps: {round(duration, 2)}s)")
            print("Vous repoussez le monstre ! Il est étourdi pour 3 tours.")
            self.npc.stunned_turns = 3 
            self.qte_count += 1        
            return True
            
        else:
            print(f"\nÉCHEC ! (Temps: {round(duration, 2)}s)")
            if user_input != target_word:
                print(f"Le code était incorrect (Attendu: {target_word}).")
            else:
                print("Trop lent !")
            self.player.hp -= 1
            print(f"Le monstre vous blesse ! Il vous reste {self.player.hp} PV.")
            if self.player.hp <= 0:
                self.finished = True
                print("\n=== VOUS ÊTES MORT ===")
            return False

    def process_command(self, command_string):
        if not command_string: return
        list_of_words = command_string.split()
        command_word = list_of_words[0]
        if command_word in self.commands:
            command = self.commands[command_word]
            command.action(self, list_of_words, command.number_of_parameters)
        else:
            print(f"\nCommande '{command_word}' non reconnue.")

    def print_welcome(self):
        print(f"\nBienvenue {self.player.name} !")
        print(self.player.current_room.get_long_description())

if __name__ == "__main__":
    Game().play()