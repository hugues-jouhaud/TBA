# actions.py
MSG0 = "\nLa commande '{command_word}' ne prend pas de paramètre.\n"
MSG1 = "\nLa commande '{command_word}' prend 1 seul paramètre.\n"

class Actions:

    @staticmethod
    def go(game, list_of_words, number_of_parameters):
        player = game.player
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG1.format(command_word=list_of_words[0]))
            return False
        direction = list_of_words[1]
        return player.move(direction) # Retourne le succès du mouvement

    @staticmethod
    def quit(game, list_of_words, number_of_parameters):
        game.finished = True
        print("\nMerci d'avoir joué. Au revoir.\n")
        return True

    @staticmethod
    def help(game, list_of_words, number_of_parameters):
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False
        print("\nCommandes disponibles :")
        for command in game.commands.values():
            print(f"- {command}")
        print()
        return True
    
    @staticmethod
    def action_check(game, list_of_words, number_of_parameters):
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False
        print(game.player.get_inventory())
        print()
        return True
    
    @staticmethod
    def action_look(game, list_of_words, number_of_parameters):
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False
        result = game.player.current_room.get_look_item_display()

        resultCharacter = game.character.curre
        print(result, )
        if result == "Il n'y a rien ici.":
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
        player = game.player
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG1.format(command_word=list_of_words[0]))
            return False
        if not player.prev_room :
            print("Vous ne pouvez pas plus revenir en arrière !")
            return True
        direction_to_go = None
        for direction, room in player.current_room.exits.items():
            if room == player.prev_room[-1]:
                direction_to_go = direction
                break 
        player.prev_room.pop()
        if direction_to_go is not None:
            player.move(direction_to_go) 
            if player.prev_room: 
                player.prev_room.pop()
        else:
            print("Impossible de revenir en arrière.")
        return True
    
    @staticmethod
    def action_take(game, list_of_words, number_of_parameters):
        player = game.player
        current_room = player.current_room
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG1.format(command_word=list_of_words[0]))
            return False
        item_name = list_of_words[1] 
        item_taken = current_room.take_item(item_name)
        if item_taken:
            if player.add_item(item_taken):
                return True
            else:
                current_room.add_item(item_taken)
                return False
        else:
            print(f"L'objet '{item_name}' n'est pas dans la pièce.")
            return False

    @staticmethod
    def action_drop(game, list_of_words, number_of_parameters):
        player = game.player
        current_room = player.current_room
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG1.format(command_word=list_of_words[0]))
            return False
        item_name = list_of_words[1].lower() 
        amount = 1 
        item_to_drop = player.remove_item(item_name, amount) 
        if item_to_drop:
            current_room.add_item(item_to_drop, amount)
            return True
        else:
            return False
    
    @staticmethod
    def action_talk(game, list_of_words, number_of_parameters) :
        """ Parler au npc x """
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False

        character = game.character
        player = game.player

        # Pas de personnage disponible
        if character is None:
            print("Aucun personnage n'est présent pour parler.")
            return True

        nom = list_of_words[1]
        # Comparaison basique du nom (sensible à la casse pour l'instant)
        if nom != character.name:
            print("Ce personnage n'existe pas")
            return True

        # Vérifier qu'on a bien des salles avant d'y accéder
        if character.current_room is not None and player is not None and character.current_room == player.current_room:
            print(character.msgs)
            return True

        print("Ce personnage n'est pas dans la salle")
        return True

        