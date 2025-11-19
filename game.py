from room import Room
from player import Player
from actions import Actions
from command import Command
from npc import Monstre

class Game:
    def __init__(self):
        self.finished = False
        self.rooms = []
        self.commands = {}
        self.player = None
        self.npc = None
    
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
            if self.finished:
                break

            # --- LOGIQUE DU MONSTRE ---
            if self.npc is None and self.player.current_room == self.rituel:
                self.spawn_monster()
            elif self.npc is not None:
                self.npc.move()
                distance = self.npc.distance_du_joueur(self.player.current_room)
                if distance == 0:
                    print("\n!!!! ATTENTION !!!!\nLe monstre est dans la même pièce que vous !")
                elif distance == 1:
                    print("Vous entendez des bruits de pas tout proches...")
                elif distance == 2:
                    print("Un grognement résonne au loin.")

    def spawn_monster(self):
        self.npc = Monstre()
        self.npc.current_room = self.salon
        print("\n-----------------------------------------------------")
        print("Un rugissement glacial secoue le manoir...")
        print(f"Vous avez réveillé un monstre ! Il est dans le {self.npc.current_room.name}.")
        print("-----------------------------------------------------\n")

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
