# actions.py
from item import Item

MSG0 = "\nLa commande '{command_word}' ne prend pas de paramètre.\n"
MSG1 = "\nLa commande '{command_word}' prend 1 seul paramètre.\n"

class Actions:
    """
    The Actions class contains static methods that define the actions
    that can be performed in the game.
    """

    @staticmethod
    def go(game, list_of_words, number_of_parameters):
        player = game.player
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG1.format(command_word=list_of_words[0]))
            return False
        
        direction = list_of_words[1].upper()
        
        # GESTION DE LA CAVE SOMBRE ---
        # On regarde la future salle sans y aller tout de suite
        next_room = player.current_room.exits.get(direction)
        
        if next_room and next_room.name == "cave":
            # Si la lampe n'est pas allumée
            if not game.flashlight_on:
                print("\n🌑 Il fait noir complet ! Vous ne voyez rien.")
                print("Utilisez votre lampe torche d'abord ('use lampe').")
                return False # On bloque le déplacement
            else:
                print("\n💡 Votre lampe éclaire les murs humides de la cave...")

        return player.move(direction)

    @staticmethod
    def action_use(game, list_of_words, number_of_parameters):
        # 1. Vérification de la syntaxe
        if len(list_of_words) < 2:
            print(MSG1.format(command_word=list_of_words[0]))
            return False

        # 2. Reconstitution du nom tapé par le joueur
        item_name = " ".join(list_of_words[1:]).lower()
        player = game.player

        # --- CAS 1 : LAMPE TORCHE ---
        if "lampe" in item_name or "torche" in item_name:
            # A. Vérifier si on a la lampe (dans l'inventaire)
            has_lamp = False
            for slot in player.inventory.slots:
                # On utilise 'in' et 'lower()' pour être sûr de la trouver
                if slot and "lampe" in slot.item.name.lower():
                    has_lamp = True
                    break
            
            if not has_lamp:
                print("\nVous n'avez pas de lampe torche dans votre inventaire.")
                return False

            # B. Vérifier et consommer la batterie
            # On demande à remove_item de chercher "batterie". 
            # Assure-toi que remove_item dans player.py fait bien un .lower() !
            removed_item = player.remove_item("batterie", 1)
            
            if removed_item:
                game.flashlight_on = True
                
                # Donner une batterie vide en échange
                player.add_item(game.batterie_decharge, 1)

                print("\n💡 CLIC. Vous insérez la batterie. La lampe illumine les alentours !")
                return True
            else:
                print("\nLa lampe ne s'allume pas... Il faut une 'batterie' chargée dans l'inventaire.")
                return False

        # --- CAS 2 : BATTERIE (Pour le Radar) ---
        elif "batterie" in item_name:
            # A. Vérifier qu'on est dans la Safe Room
            if player.current_room.name != "Safe":
                print("\nVous ne pouvez pas utiliser la batterie ici (Cherchez un terminal/Safe Room).")
                print("Pour allumer la lampe, tapez 'use lampe'.")
                return False

            # B. CONSOMMER la batterie
            # remove_item cherche l'objet, le retire et le renvoie. Si None, le joueur ne l'avait pas.
            removed_item = player.remove_item("batterie", 1)
            
            if removed_item:
                # On redonne une batterie vide (déchet)
                player.add_item(game.batterie_decharge, 1)

                # Affichage du Radar
                if game.character:
                    room_name = game.character.current_room.name.upper()
                    print(f"\n[SYSTEME] 🔋 Batterie insérée. Analyse en cours...")
                    print(f"[RADAR] 🔴 ALERTE : SUJET DÉTECTÉ EN ZONE -> {room_name}")
                else:
                    print("\n[SYSTEME] 🔋 Batterie insérée.")
                    print("[RADAR] Aucun signal détecté.")
                return True
            else:
                print("\nVous n'avez pas de batterie chargée sur vous.")
                return False

        # --- CAS 3 : LEVIER ---
        elif "levier" in item_name:
            if player.current_room.name != "salon":
                print("\nIl n'y a pas de levier ici.")
                return False
            
            # Vérifier la Clé
            has_key = False
            for slot in player.inventory.slots:
                if slot and "cle" in slot.item.name.lower(): # 'cle' sans accent pour être sûr
                    has_key = True; break
            
            if not has_key:
                print("\n🔒 Le boîtier est verrouillé. Il faut la CLÉ.")
                return False

            # Vérifier les Fusibles (Dans la salle Safe)
            fuses_in_safe = 0
            if hasattr(game, "safe"):
                for item_obj, quantity in game.safe.items.items():
                    if "fusible" in item_obj.name.lower():
                        fuses_in_safe += quantity
            
            print("\n⚙️ Vous insérez la clé et tentez d'abaisser le levier...")
            
            if fuses_in_safe >= 3:
                print("\n⚡ VROUUUM ! Le courant revient ! La porte s'ouvre...")
                q = player.quest_manager.get_quest_by_title("Réparer et Fuir")
                if q: q.is_completed = True
                game.win()
                return True
            else:
                missing = 3 - fuses_in_safe
                print(f"\n❌ Rien ne se passe. Il manque {missing} fusible(s) dans la salle SAFE.")
                return False
        
        else:
            print(f"\nVous ne pouvez pas utiliser '{item_name}' directement.")
            return False

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
        
        # 1. Afficher la description de la salle et les objets
        print(game.player.current_room.get_look_item_display())
        
        # 2. Afficher le monstre s'il est là
        if game.character and game.character.current_room == game.player.current_room:
            print(f"\n {game.character.name} est là ! ({game.character.description})")
            
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
            # On utilise Actions.go pour bénéficier de la vérification de la lumière !
            # On recrée une fausse liste de mots pour appeler go
            return Actions.go(game, ["go", direction_to_go], 1)
        else:
            print("Impossible de revenir en arrière.")
        return True
    
    @staticmethod
    def action_take(game, list_of_words, number_of_parameters):
        player = game.player
        current_room = player.current_room
        
        # On vérifie qu'il y a AU MOINS 1 paramètre (donc len >= 2)
        if len(list_of_words) < 2:
            print(MSG1.format(command_word=list_of_words[0]))
            return False
        
        item_name = " ".join(list_of_words[1:]) 
        
        item_taken = current_room.take_item(item_name)
        
        if item_taken:
            if player.add_item(item_taken):
                if item_taken.name.lower() == "batterie":
                    player.quest_manager.check_action_objectives("Prendre", "batterie")
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
        
        # On accepte >= 2 mots ---
        if len(list_of_words) < 2:
            print(MSG1.format(command_word=list_of_words[0]))
            return False
        
        # On reconstitue le nom complet ---
        item_name = " ".join(list_of_words[1:]).lower() 
        
        amount = 1 
        item_to_drop = player.remove_item(item_name, amount) 
        if item_to_drop:
            current_room.add_item(item_to_drop, amount)
            print(f"Vous avez posé : {item_to_drop.name}")
            
            # --- VÉRIFICATION QUÊTE LIVRES ---
            if current_room.name == "Bureau" and "livre" in item_to_drop.name.lower():
                book_count = 0
                for item_obj, quantity in current_room.items.items():
                    if "livre" in item_obj.name.lower():
                        book_count += quantity
                
                if book_count >= 5:
                    player.quest_manager.check_action_objectives("Déposer", "5 livres")
                    game.unlock_secret_path()
            
            return True
        else:
            return False
    
    @staticmethod
    def action_talk(game, list_of_words, number_of_parameters) :
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False

        character = game.character
        player = game.player

        if character is None:
            print("Aucun personnage n'est présent pour parler.")
            return True

        nom = list_of_words[1]
        if nom != character.name:
            print("Ce personnage n'existe pas")
            return True

        if character.current_room is not None and player is not None and character.current_room == player.current_room:
            print(character.msgs)
            return True

        print("Ce personnage n'est pas dans la salle")
        return True

    # --- ACTIONS QUÊTES ---

    @staticmethod
    def quests(game, list_of_words, number_of_parameters):
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False
        game.player.quest_manager.show_quests()
        return True

    @staticmethod
    def quest(game, list_of_words, number_of_parameters):
        l = len(list_of_words)
        if l < number_of_parameters + 1:
            print(MSG1.format(command_word=list_of_words[0]))
            return False
        quest_title = " ".join(list_of_words[1:])
        current_counts = { "Se déplacer": game.player.move_count }
        game.player.quest_manager.show_quest_details(quest_title, current_counts)
        return True

    @staticmethod
    def activate(game, list_of_words, number_of_parameters):
        l = len(list_of_words)
        if l < number_of_parameters + 1:
            print(MSG1.format(command_word=list_of_words[0]))
            return False
        quest_title = " ".join(list_of_words[1:])
        if game.player.quest_manager.activate_quest(quest_title):
            return True
        print(f"\nImpossible d'activer la quête '{quest_title}'.")
        return False

    @staticmethod
    def rewards(game, list_of_words, number_of_parameters):
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False
        game.player.show_rewards()
        return True