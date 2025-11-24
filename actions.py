# Description: The actions module.

# The actions module contains the functions that are called when a command is executed.
# Each function takes 3 parameters:
# - game: the game object
# - list_of_words: the list of words in the command
# - number_of_parameters: the number of parameters expected by the command
# The functions return True if the command was executed successfully, False otherwise.
# The functions print an error message if the number of parameters is incorrect.
# The error message is different depending on the number of parameters expected by the command.


# The error message is stored in the MSG0 and MSG1 variables and formatted with the command_word variable, the first word in the command.
# The MSG0 variable is used when the command does not take any parameter.
MSG0 = "\nLa commande '{command_word}' ne prend pas de paramètre.\n"
# The MSG1 variable is used when the command takes 1 parameter.
MSG1 = "\nLa commande '{command_word}' prend 1 seul paramètre.\n"

class Actions:

    @staticmethod
    def go(game, list_of_words, number_of_parameters):
        """Déplacer le joueur dans la direction cardinale indiquée."""
        player = game.player
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG1.format(command_word=list_of_words[0]))
            return False
        direction = list_of_words[1]
        player.move(direction)
        return True

    @staticmethod
    def quit(game, list_of_words, number_of_parameters):
        """Quitter le jeu."""
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False
        player = game.player
        print(f"\nMerci {player.name} d'avoir joué. Au revoir.\n")
        game.finished = True
        return True

    @staticmethod
    def help(game, list_of_words, number_of_parameters):
        """Afficher la liste des commandes disponibles."""
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False
        print("\nVoici les commandes disponibles:")
        for command in game.commands.values():
            print("\t- " + str(command))
        print()
        return True

    @staticmethod
    def action_inv(game, list_of_words, number_of_parameters):
        """Afficher l’inventaire du joueur."""
        print("\nInventaire du joueur :")
        # Utilise la méthode show() de Inventory
        game.player.inventory.show()
        print()
        return True
    @staticmethod
    def action_history(game, list_of_words, number_of_parameters):
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False
        
        print(game.player.get_history())
        return True
    
    @staticmethod
    def action_back(game, list_of_words, number_of_parameters):
        """Essaye de déplacer le joueur dans la direction pour aller dans la salle précédente"""
        player = game.player
        l = len(list_of_words)
        
        if l != number_of_parameters + 1:
            print(MSG1.format(command_word=list_of_words[0]))
            return False
    
        # Si pas de salle précédente (début du jeu)
        if player.prev_room is None:
            print("Impossible de reculer, vous êtes au début.")
            return True

        # On cherche quelle direction (N, E, S, O, U, D) mène à la prev_room
        direction_to_go = None
        
        if player.prev_room == [] :
            print("Vous ne pouvez pas plus revenir en arrière !")
            return True

        # On parcourt le dictionnaire exits de la salle ACTUELLE : {"N": RoomB, "S": None...}
        for direction, room in player.current_room.exits.items():
            if room == player.prev_room[-1]:
                direction_to_go = direction
                break # On a trouvé la direction, on arrête de chercher
        
        
        player.prev_room.remove(player.prev_room[-1])

        # Si on a trouvé une direction qui mène à l'ancienne salle
        if direction_to_go is not None:
            player.move(direction_to_go)
            player.prev_room.remove(player.prev_room[-1])
        else:
            # Cas où c'est un sens unique
            print("Il n'y a pas de passage pour retourner en arrière.")

        return True