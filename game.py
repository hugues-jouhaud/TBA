from room import Room
from player import Player
from actions import Actions
from command import Command
from npc import Monstre

import time
import random

class Game:
    def __init__(self):
        self.finished = False
        self.rooms = []
        self.commands = {}
        self.player = None
        self.npc = None
        self.debug = True
        self.qte_count = 0
    
    # Setup the game
    def setup(self):
        # --- COMMANDES ---
        self.commands["help"] = Command("help", " : afficher cette aide", Actions.help, 0)
        self.commands["quit"] = Command("quit", " : quitter le jeu", Actions.quit, 0)
        self.commands["go"] = Command("go", " <direction> : se déplacer dans une direction cardinale (N, E, S, O)", Actions.go, 1)
        self.commands["inv"] = Command("inv", " : Affiche l’inventaire du joueur", Actions.action_inv, 0)
        self.commands["history"] = Command("history", " : Affiche les pièces déjà visitées", Actions.action_history, 0)

        # --- SALLES ---
        self.cave = Room("Cave", "dans une cave sombre et humide")
        self.rituel = Room("Salle de Rituel", "dans une pièce étrange avec des symboles au sol")
        self.stock1 = Room("Stockage 1", "dans un débarras encombré")
        self.clouloir1 = Room("Couloir 1", "dans un long couloir sombre")
        self.prison = Room("Jaule", "enfermé dans une vieille geôle")
        self.sdb2 = Room("Salle de bain 2", "dans une salle de bain délabrée")
        self.ch2 = Room("Chambre 2", "dans une chambre d'amis poussiéreuse")
        self.clouloir2 = Room("Couloir 2", "dans le couloir de l'étage")
        self.stock2 = Room("Stockage 2", "dans une petite réserve à provisions")
        self.bureau = Room("Bureau", "dans un grand bureau rempli de livres")
        self.balcon = Room("Balcon", "sur le balcon, vous avez une vue dégagée sur le salon")
        self.safe = Room("Safe", "dans une pièce blindée et sécurisée")
        self.cuisine = Room("Cuisine", "dans une cuisine aux couteaux rouillés")
        self.sam = Room("Salle a manger", "dans une grande salle à manger")
        self.salon = Room("Salon", "dans un salon confortable avec une cheminée")
        self.ch1 = Room("Chambre 1", "dans la chambre principale")
        self.sdb1 = Room("Salle de bain 1", "dans une petite salle de bain carrelée")

        self.rooms.extend([
            self.cave, self.rituel, self.stock1, self.clouloir1, self.prison,
            self.sdb2, self.ch2, self.clouloir2, self.stock2, self.bureau,
            self.balcon, self.safe, self.cuisine, self.sam, self.salon,
            self.ch1, self.sdb1
        ])

        # --- EXITS ---
        self.cave.exits = {"N": self.stock1, "E": None, "S": None, "O": None, "U": self.cuisine, "D": None}
        self.rituel.exits = {"N": None, "E": None, "S": self.clouloir1, "O": self.stock1, "U": None, "D": None}
        self.stock1.exits = {"N": None, "E": self.rituel, "S": self.cave, "O": None, "U": self.safe, "D": None}
        self.clouloir1.exits = {"N": self.rituel, "E": self.prison, "S": None, "O": None, "U": None, "D": None}
        self.prison.exits = {"N": None, "E": None, "S": None, "O": self.clouloir1, "U": None, "D": None}
        self.sdb2.exits = {"N": None, "E": None, "S": self.ch2, "O": None, "U": None, "D": None}
        self.ch2.exits = {"N": self.sdb2, "E": self.clouloir2, "S": None, "O": None, "U": None, "D": None}
        self.clouloir2.exits = {"N": self.stock2, "E": self.balcon, "S": None, "O": self.ch2, "U": None, "D": None}
        self.stock2.exits = {"N": None, "E": None, "S": self.clouloir2, "O": None, "U": None, "D": None}
        self.bureau.exits = {"N": None, "E": None, "S": self.balcon, "O": None, "U": None, "D": self.clouloir1}
        self.balcon.exits = {"N": self.bureau, "E": self.safe, "S": None, "O": self.clouloir2, "U": None, "D": self.salon}
        self.safe.exits = {"N": None, "E": None, "S": None, "O": self.balcon, "U": None, "D": self.stock1}
        self.cuisine.exits = {"N": None, "E": self.sam, "S": None, "O": None, "U": None, "D": self.cave}
        self.sam.exits = {"N": None, "E": self.salon, "S": None, "O": self.cuisine, "U": None, "D": None}
        self.salon.exits = {"N": None, "E": self.ch1, "S": None, "O": self.sam, "U": self.balcon, "D": None}
        self.ch1.exits = {"N": None, "E": self.sdb1, "S": None, "O": self.salon, "U": None, "D": None}
        self.sdb1.exits = {"N": None, "E": None, "S": None, "O": self.ch1, "U": None, "D": None}

        # --- PLAYER ---
        self.player = Player(input("\nEntrez votre nom: "))
        self.player.current_room = self.salon

    # --- BOUCLE DE JEU ---
    def play(self):
        self.setup()
        self.print_welcome()
        while not self.finished:
            # --- DEBUG ---
            if self.debug and self.npc:
                print(f"[DEBUG] Monstre: {self.npc.current_room.name} (Stun: {self.npc.stunned_turns})")
            # --- Déplacement du joueur ---
            # Get the command from the player
            user_input = input("> ")
            if not user_input:
                continue
            words = user_input.split() 
            if not words:
                continue
            

            if self.finished:
                break

            # --- LOGIQUE DU MONSTRE ---
            # Le monstre bouge SEULEMENT si la commande est "go"
            monster_intercepted = False

            words = user_input.split()     # <-- On coupe la phrase
            command_word = words[0]        # <-- On prend le 1er mot
            
            if self.npc is not None and command_word == "go":

                # Mob stun ?
                etais_stun = self.npc.stunned_turns > 0

                # Le monstre bouge
                self.npc.move()
                
                # S'il arrive sur nous (Interception)
                if self.npc.current_room == self.player.current_room and not etais_stun:
                    monster_intercepted = True
                    self.trigger_qte()

            # --- TRAITEMENT DE LA COMMANDE ---
            # On ne bouge pas si on s'est fait intercepter
            # Sinon :
            if not monster_intercepted:
                self.process_command(user_input)

                # On vient de bouger, on vérifie si on est tombé nez à nez avec le monstre
                if self.npc is not None and self.npc.current_room == self.player.current_room:
                    # On vérifie s'il est stun (car s'il dort, pas de QTE)
                    if self.npc.stunned_turns == 0:
                        self.trigger_qte()
            
            if self.finished:
                break

            # --- GESTION DU SPAWN ---
            if self.npc is None:
                if self.player.current_room == self.rituel:
                    self.spawn_monster()
            
            # --- MESSAGES D'AMBIANCE (Distance) ---
            # On vérifie la distance APRÈS tous les mouvements
            elif self.npc is not None:
                # Si on ne s'est pas fait attaquer ce tour-ci, on donne des indices
                if self.npc.current_room != self.player.current_room:
                    distance = self.npc.distance_du_joueur(self.player.current_room)
                    if distance == 1:
                        print("\n--> Vous entendez des bruits de pas tout proches...")
                    elif distance == 2:
                        print("\n--> Un grognement résonne au loin.")

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
        if not command_string:
            return
        list_of_words = command_string.split()
        command_word = list_of_words[0]

        if command_word in self.commands:
            command = self.commands[command_word]
            command.action(self, list_of_words, command.number_of_parameters)
        else:
            print(f"\nCommande '{command_word}' non reconnue. Entrez 'help' pour voir la liste des commandes disponibles.\n")

    def print_welcome(self):
        print(f"\nBienvenue {self.player.name} dans ce jeu d'aventure !")
        print("Entrez 'help' si vous avez besoin d'aide.")
        print(self.player.current_room.get_long_description())

def main():
    Game().play()

if __name__ == "__main__":
    main()
