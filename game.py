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
        cave = room("cave","")
        self.rooms.append(cave)
        rituel = room("salle de Rituel","")
        self.rooms.append(rituel)
        stock1 = room("stockage 1","")
        self.rooms.append(stock1)
        clouloir1 = room("couloir 1","")
        self.rooms.append(clouloir1)
        Prison = room("jaule","")
        self.rooms.append(Prison)
        SDB2 = room("salle de bain 2","")
        self.rooms.append(SDB2)
        ch2 = room("chambre 2","")
        self.rooms.append(ch2)
        clouloir2 = room("couloir 2","")
        self.rooms.append(clouloir2)
        stock2 = room("stockage 2","")
        self.rooms.append(stock2)
        bureau = room("bureau","")
        self.rooms.append(bureau)
        balcon = room("balcon","")
        self.rooms.append(balcon)
        safe = room("safe","")
        self.rooms.append(safe)
        cuisine = room("cuisine","")
        self.rooms.append(cuisine)
        sam = room("salle a manger","")
        self.rooms.append(sam)
        salon = room("salon","")
        self.rooms.append(salon)
        ch1 = room("chambre 1","")
        self.rooms.append(ch1)
        sdb1 = room("Salle de bain 1","")
        self.rooms.append(sdb1)
        # Create exits for rooms

        cave.exits = {"N": stock1, "E": None, "S": cuisine, "O": None}
        rituel.exits = {"N": None, "E": None, "S": clouloir1, "O": stock1}
        stock1.exits = {"N": safe, "E": rituel, "S": cave, "O": None}
        clouloir1.exits = {"N": rituel, "E": Prison, "S": None, "O": None}
        Prison.exits = {"N": None, "E": None, "S": None, "O": clouloir1}
        SDB2.exits = {"N": None, "E": None, "S": ch2, "O": None}
        ch2.exits = {"N": SDB2, "E": clouloir2, "S": None, "O": None}
        clouloir2.exits = {"N": stock2, "E": balcon, "S": None, "O": ch2}
        stock2.exits = {"N": None, "E": None, "S": clouloir2, "O": None}
        bureau.exits = {"N": clouloir1, "E": None, "S": balcon, "O": None}
        balcon.exits = {"N": bureau, "E": safe, "S": salon, "O": clouloir2}
        safe.exits = {"N": None, "E": stock1, "S": None, "O": balcon}
        cuisine.exits = {"N": cave, "E": sam, "S": None, "O": None}
        sam.exits = {"N": None, "E": salon, "S": None, "O": sam}
        salon.exits = {"N": balcon, "E": ch1, "S": None, "O": sam}
        ch1.exits = {"N": None, "E": sdb1, "S": None, "O": salon}
        sdb1.exits = {"N": None, "E": None, "S": None, "O": ch1}


        # Setup player and starting room

        self.player = Player(input("\nEntrez votre nom: "))
        self.player.current_room = salon

    # Play the game
    def play(self):
        self.setup()
        self.print_welcome()
        # Loop until the game is finished
        while not self.finished:
            # Get the command from the player
            self.process_command(input("> "))
        return None

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
