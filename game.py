# Description: Game class

# Import modules

from room import Room
from player import Player
from command import Command
from actions import Actions
from npc import Monstre


class Game:

    # Constructor
    def __init__(self):
        self.finished = False
        self.rooms = []
        self.commands = {}
        self.player = None
        self.npc = None
    
    # Setup the game
    def setup(self):

        # Setup commands

        help = Command("help", " : afficher cette aide", Actions.help, 0)
        self.commands["help"] = help
        quit = Command("quit", " : quitter le jeu", Actions.quit, 0)
        self.commands["quit"] = quit
        go = Command("go", " <direction> : se déplacer dans une direction cardinale (N, E, S, O)", Actions.go, 1)
        self.commands["go"] = go
        
        # Setup rooms
        self.cave = Room("cave","")
        self.rooms.append(self.cave)
        self.rituel = Room("salle de Rituel","")
        self.rooms.append(self.rituel)
        self.stock1 = Room("stockage 1","")
        self.rooms.append(self.stock1)
        self.clouloir1 = Room("couloir 1","")
        self.rooms.append(self.clouloir1)
        self.prison = Room("jaule","")
        self.rooms.append(self.prison)
        self.sdb2 = Room("salle de bain 2","")
        self.rooms.append(self.sdb2)
        self.ch2 = Room("chambre 2","")
        self.rooms.append(self.ch2)
        self.clouloir2 = Room("couloir 2","")
        self.rooms.append(self.clouloir2)
        self.stock2 = Room("stockage 2","")
        self.rooms.append(self.stock2)
        self.bureau = Room("bureau","")
        self.rooms.append(self.bureau)
        self.balcon = Room("balcon","")
        self.rooms.append(self.balcon)
        self.safe = Room("safe","")
        self.rooms.append(self.safe)
        self.cuisine = Room("cuisine","")
        self.rooms.append(self.cuisine)
        self.sam = Room("salle a manger","")
        self.rooms.append(self.sam)
        self.salon = Room("salon","")
        self.rooms.append(self.salon)
        self.ch1 = Room("chambre 1","")
        self.rooms.append(self.ch1)
        self.sdb1 = Room("Salle de bain 1","")
        self.rooms.append(self.sdb1)
        # Create exits for rooms

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


        # Setup player and starting room

        self.player = Player(input("\nEntrez votre nom: "))
        self.player.current_room = self.salon

    # Play the game
    def play(self):
        self.setup()
        self.print_welcome()
        # Loop until the game is finished
        while not self.finished:
            # --- Déplacement du joueur ---
            # Get the command from the player
            self.process_command(input("> "))

            if self.finished:
                break
            
            # --- LOGIQUE DU MONSTRE ---
            if self.npc is None:
                if self.player.current_room == self.rituel:
                    self.spawn_monster()
            else:
                # OUI. Le monstre existe, on le fait jouer.
                self.npc.move() 
                distance = self.npc.distance_du_joueur(self.player.current_room)

                if distance == 0:
                    print("\n!!!! ATTENTION !!!!")
                    
                    # Message générique
                    print("Le monstre est dans la même pièce que vous !")
                
                elif distance == 1:
                    print("Vous entendez des bruits de pas tout proches...")
                
                elif distance == 2:
                    print("Un grognement résonne au loin.")

        return None

    def spawn_monster(self):
        """Crée le monstre et le place dans sa salle de spawn."""

        self.npc = Monstre()
        self.npc.current_room = self.salon
        
        # Message générique
        print("\n-----------------------------------------------------")
        print("Un rugissement glacial secoue le manoir...")
        print(f"Vous avez réveillé un monstre ! Il est dans le {self.npc.current_room.name}.")
        print("-----------------------------------------------------\n")

    # Process the command entered by the player
    def process_command(self, command_string) -> None:

        # Split the command string into a list of words
        list_of_words = command_string.split(" ")

        command_word = list_of_words[0]

        # If the command is not recognized, print an error message
        if command_word not in self.commands.keys():
            print(f"\nCommande '{command_word}' non reconnue. Entrez 'help' pour voir la liste des commandes disponibles.\n")
        # If the command is recognized, execute it
        else:
            command = self.commands[command_word]
            command.action(self, list_of_words, command.number_of_parameters)

    # Print the welcome message
    def print_welcome(self):
        print(f"\nBienvenue {self.player.name} dans ce jeu d'aventure !")
        print("Entrez 'help' si vous avez besoin d'aide.")
        #
        print(self.player.current_room.get_long_description())
    

def main():
    # Create a game object and play the game
    Game().play()
    

if __name__ == "__main__":
    main()
