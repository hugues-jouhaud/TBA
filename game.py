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
    
    # Setup the game
    def setup(self):
        # --- COMMANDES ---
        self.commands["help"] = Command("help", " : afficher cette aide", Actions.help, 0)
        self.commands["quit"] = Command("quit", " : quitter le jeu", Actions.quit, 0)
        self.commands["go"] = Command("go", " <direction> : se déplacer dans une direction cardinale (N, E, S, O)", Actions.go, 1)
        self.commands["inv"] = Command("inv", " : Affiche l’inventaire du joueur", Actions.action_inv, 0)

        # --- SALLES ---
        self.cave = Room("cave","")
        self.rituel = Room("salle de Rituel","")
        self.stock1 = Room("stockage 1","")
        self.clouloir1 = Room("couloir 1","")
        self.prison = Room("jaule","")
        self.sdb2 = Room("salle de bain 2","")
        self.ch2 = Room("chambre 2","")
        self.clouloir2 = Room("couloir 2","")
        self.stock2 = Room("stockage 2","")
        self.bureau = Room("bureau","")
        self.balcon = Room("balcon","")
        self.safe = Room("safe","")
        self.cuisine = Room("cuisine","")
        self.sam = Room("salle a manger","")
        self.salon = Room("salon","")
        self.ch1 = Room("chambre 1","")
        self.sdb1 = Room("Salle de bain 1","")

        self.rooms.extend([
            self.cave, self.rituel, self.stock1, self.clouloir1, self.prison,
            self.sdb2, self.ch2, self.clouloir2, self.stock2, self.bureau,
            self.balcon, self.safe, self.cuisine, self.sam, self.salon,
            self.ch1, self.sdb1
        ])

        # --- EXITS ---
        self.cave.exits = {"N": self.stock1, "E": None, "S": self.cuisine, "O": None}
        self.rituel.exits = {"N": None, "E": None, "S": self.clouloir1, "O": self.stock1}
        self.stock1.exits = {"N": self.safe, "E": self.rituel, "S": self.cave, "O": None}
        self.clouloir1.exits = {"N": self.rituel, "E": self.prison, "S": None, "O": None}
        self.prison.exits = {"N": None, "E": None, "S": None, "O": self.clouloir1}
        self.sdb2.exits = {"N": None, "E": None, "S": self.ch2, "O": None}
        self.ch2.exits = {"N": self.sdb2, "E": self.clouloir2, "S": None, "O": None}
        self.clouloir2.exits = {"N": self.stock2, "E": self.balcon, "S": None, "O": self.ch2}
        self.stock2.exits = {"N": None, "E": None, "S": self.clouloir2, "O": None}
        self.bureau.exits = {"N": self.clouloir1, "E": None, "S": self.balcon, "O": None}
        self.balcon.exits = {"N": self.bureau, "E": self.safe, "S": self.salon, "O": self.clouloir2}
        self.safe.exits = {"N": None, "E": self.stock1, "S": None, "O": self.balcon}
        self.cuisine.exits = {"N": self.cave, "E": self.sam, "S": None, "O": None}
        self.sam.exits = {"N": None, "E": self.salon, "S": None, "O": self.cuisine}
        self.salon.exits = {"N": self.balcon, "E": self.ch1, "S": None, "O": self.sam}
        self.ch1.exits = {"N": None, "E": self.sdb1, "S": None, "O": self.salon}
        self.sdb1.exits = {"N": None, "E": None, "S": None, "O": self.ch1}

        # --- PLAYER ---
        self.player = Player(input("\nEntrez votre nom: "))
        self.player.current_room = self.salon

    # --- BOUCLE DE JEU ---
    def play(self):
        self.setup()
        self.print_welcome()
        while not self.finished:
            command_input = input("> ").strip()
            self.process_command(command_input)
            # --- DEBUG ---
            if self.debug and self.npc:
                print(f"[DEBUG] Monstre: {self.npc.current_room.name} (Stun: {self.npc.stunned_turns})")
            # --- Déplacement du joueur ---
            # Get the command from the player
            user_input = input("> ")
            if not user_input:
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
            if not monster_intercepted:
                self.process_command(user_input)
            
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

    # Process the command entered by the player
    def process_command(self, command_string) -> None:

        # Split the command string into a list of words
        list_of_words = command_string.split(" ")

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
