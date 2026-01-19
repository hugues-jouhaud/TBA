from room import Room
from player import Player
from actions import Actions
from command import Command
from item import Item, Pile 
from character import Character
from quest import Quest
import time
import random

class Game:
    def __init__(self):
        self.finished = False
        self.rooms = []
        self.commands = {}
        self.player = None
        self.character = None
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
        self.commands["talk"] = Command("talk", " : parler au personnage x qui se trouve dans la salle.", Actions.action_talk, 1)
        # commandes quêtes :
        self.commands["quests"] = Command("quests", " : afficher la liste des quêtes", Actions.quests, 0)
        self.commands["quest"] = Command("quest", " <titre> : afficher les détails d'une quête", Actions.quest, 1)
        self.commands["activate"] = Command("activate", " <titre> : activer une quête", Actions.activate, 1)
        self.commands["rewards"] = Command("rewards", " : afficher vos récompenses", Actions.rewards, 0)

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
        self.bureau.exits = {"S": self.balcon}  # Pas de "D" initialement, débloquer après les 5 livres
        self.balcon.exits = {"N": self.bureau, "E": self.safe, "O": self.clouloir2, "D": self.salon}
        self.safe.exits = {"O": self.balcon, "D": self.stock1}
        self.cuisine.exits = {"E": self.sam, "D": self.cave}
        self.sam.exits = {"E": self.salon, "O": self.cuisine}
        self.salon.exits = {"E": self.ch1, "O": self.sam, "U": self.balcon}
        self.ch1.exits = {"E": self.sdb1, "O": self.salon}
        self.sdb1.exits = {"O": self.ch1}

        # --- ITEMS (AJOUT DU SYSTÈME D'OBJETS) ---
        baterie_charge = Item("baterie", "une baterie chargée", 2.0)
        baterie_decharge = Item("baterie", "une baterie chargée", 2.0)
        livre = Item("livre", "un des 5 tomes de l'encyclopédie", 0.2)
        lampe = Item("Lampe Torche", "permet de s'éclairer dans le noir", 0.1)

        # Placement des items
        self.cave.add_item(baterie_charge, 1)

        self.rituel.add_item(baterie_charge, 1)

        self.stock1.add_item(baterie_charge, 1)

        self.clouloir1.add_item(baterie_charge, 1)

        self.prison.add_item(baterie_charge, 1)

        self.sdb2.add_item(baterie_charge, 1)

        self.ch2.add_item(baterie_charge, 1)
        self.ch2.add_item(livre, 1)

        self.clouloir2.add_item(baterie_charge, 1)

        self.stock2.add_item(baterie_charge, 1)
        self.stock2.add_item(livre, 1)

        self.bureau.add_item(baterie_charge, 1)

        self.balcon.add_item(baterie_charge, 1)

        self.safe.add_item(baterie_charge, 1)
        self.safe.add_item(livre, 1)
        self.safe.add_item(lampe, 1)

        self.cuisine.add_item(baterie_charge, 1)
        self.cuisine.add_item(livre, 1)

        self.sam.add_item(baterie_charge, 1)

        self.salon.add_item(baterie_charge, 1)

        self.ch1.add_item(baterie_charge, 1)

        self.sdb1.add_item(baterie_charge, 1)
        self.sdb1.add_item(livre, 1)

        # --- JOUEUR ---
        self.player = Player(input("\nEntrez votre nom: "))
        self.player.set_room(self.salon)

        # --- Quêtes ---
        self._setup_quests()
    
    def _setup_quests(self):
        """Initialize all quests."""
        grand_explorateur = Quest(
            title="Grand Explorateur",
            description="Explorez tous les lieux de ce mystérieux manoir.",
            objectives=["Visiter cave", "Visiter salle de Rituel", "Visiter Safe", "Visiter Cuisine"],
            reward="Pile d'énergie"
        )

        un_bruit_etonnant = Quest(
            title="Un bruit étonnant",
            description="Allez à la salle de Rituel pour découvrir la source de ce bruit étrange.",
            objectives=["Visiter salle de Rituel"],
            reward="Pile d'énergie"
        )

        une_mauvaise_surprise = Quest(
            title="Une mauvaise surprise",
            description="Survivez à la rencontre avec le monstre en réussissant le QTE.",
            objectives=["Réussir un QTE"],
            reward="Pile d'énergie"
        )

        energie_cool = Quest(
            title="L'énergie c'est cool",
            description="Ramassez votre première pile pour alimenter vos objets.",
            objectives=["Prendre baterie"],
            reward="Pile d'énergie"
        )

        survival_quest = Quest(
            title="Grand Voyageur",
            description="Déplacez-vous 10 fois dans le manoir.",
            objectives=["Se déplacer 10 fois"],
            reward="Pile d'énergie"
        )

        mysteres_manoir = Quest(
            title="Les Mystères du Manoir",
            description="Récupérez les 5 livres dispersés dans le manoir et déposez-les dans le bureau pour découvrir un secret.",
            objectives=["Déposer 5 livres dans le bureau"],
            reward="Pile d'énergie"
        )

        # Add quests to player's quest manager
        self.player.quest_manager.add_quest(un_bruit_etonnant)
        self.player.quest_manager.add_quest(une_mauvaise_surprise)
        self.player.quest_manager.add_quest(energie_cool)
        self.player.quest_manager.add_quest(grand_explorateur)
        self.player.quest_manager.add_quest(survival_quest)
        self.player.quest_manager.add_quest(mysteres_manoir)

    def play(self):
        self.setup()
        self.print_welcome()
        
        while not self.finished:
            # --- DEBUG ---
            if self.debug and self.character and self.character.current_room:
                print(f"[DEBUG] Monstre: {self.character.current_room.name} (Stun: {self.character.stunned_turns})")
            elif self.debug and self.character:
                print(f"[DEBUG] Monstre: <aucune salle> (Stun: {self.character.stunned_turns})")
            
            # --- Input du joueur ---
            user_input = input("> ")
            if not user_input: continue
            
            words = user_input.split()
            if not words: continue
            
            command_word = words[0]
            
            # --- LOGIQUE DU MONSTRE (Déplacement) ---
            monster_intercepted = False
            
            # Le monstre bouge SEULEMENT si le joueur fait une commande de mouvement ("go" ou "back")
            if self.character is not None and command_word in ["go", "back"]:
                
                etais_stun = self.character.stunned_turns > 0
                
                # --- CORRECTION ICI : On passe la salle du joueur ---
                self.character.move(self.player.current_room)
                
                # Interception (Le monstre arrive sur le joueur pendant son tour)
                if self.character.current_room == self.player.current_room and not etais_stun:
                    monster_intercepted = True
                    # Si le QTE échoue, on peut mourir ici, donc on check finished
                    if not self.trigger_qte():
                        # Si le joueur meurt pendant le QTE, on arrête la boucle
                        if self.player.hp <= 0:
                            self.finished = True
                            self.lose()
                            break

            # --- TRAITEMENT DE LA COMMANDE ---
            # On ne bouge pas si on s'est fait intercepter avant même de bouger
            if not monster_intercepted:
                self.process_command(user_input)

                # Après que le JOUEUR ait bougé, on vérifie s'il est tombé sur le monstre
                if self.character is not None and self.character.current_room == self.player.current_room:
                    # On vérifie s'il est stun (car s'il dort, pas de QTE)
                    if self.character.stunned_turns == 0:
                        if not self.trigger_qte():
                            if self.player.hp <= 0:
                                self.finished = True
                                self.lose()
                                break
            
            if self.finished: break

            # --- GESTION DU SPAWN ---
            if self.character is None:
                if self.player.current_room == self.rituel:
                    self.spawn_monster()
            
            # --- MESSAGES D'AMBIANCE (Distance) ---
            # On vérifie la distance APRÈS tous les mouvements
            elif self.character is not None:
                # Si on ne s'est pas fait attaquer ce tour-ci et qu'on n'est pas mort
                if self.character.current_room != self.player.current_room and not self.finished:
                    # --- CORRECTION ICI : On utilise aussi self.player.current_room ---
                    distance = self.character.distance_du_joueur(self.player.current_room)
                    if distance == 1:
                        print("\n--> Vous entendez des bruits de pas tout proches...")
                    elif distance == 2:
                        print("\n--> Une odeur putride flotte dans l'air...")
            
            # --- VÉRIFICATION DE LA VICTOIRE ---
            self.check_win()
    
    def spawn_monster(self):
        self.character = Character()
        self.character.current_room = self.salon
        print("\n-----------------------------------------------------")
        print("Un rugissement glacial secoue le manoir...")
        print(f"Vous avez réveillé un monstre ! Il est dans le {self.character.current_room.name}.")
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
            self.character.stunned_turns = 3 
            self.qte_count += 1
            
            # Vérifier la quête "Une mauvaise surprise"
            self.player.quest_manager.check_action_objectives("Réussir", "un QTE")
            
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

    def check_win(self):
        """Vérifie si le joueur a gagné (toutes les quêtes complétées)."""
        all_quests = self.player.quest_manager.get_all_quests()
        if all_quests and all(quest.is_completed for quest in all_quests):
            self.finished = True
            self.win()

    def win(self):
        """Affiche le message de victoire."""
        print("\n" + "="*50)
        print("🎉 FÉLICITATIONS ! VOUS AVEZ GAGNÉ ! 🎉")
        print("="*50)
        print("\nVous avez accompli toutes les quêtes du manoir.")
        print("Voici vos récompenses finales:")
        self.player.show_rewards()
        print("="*50 + "\n")

    def lose(self):
        """Affiche le message de défaite."""
        print("\n" + "="*50)
        print("💀 GAME OVER - VOUS AVEZ PERDU 💀")
        print("="*50)
        print("\nLe monstre vous a vaincu...")
        print(f"Vous avez survécu à {self.qte_count} QTE(s).")
        print("="*50 + "\n")

    def unlock_secret_path(self):
        """Déverrouille le chemin secret du bureau vers le couloir sombre."""
        self.bureau.exits["D"] = self.clouloir1
        print("\n" + "="*50)
        print("✨ Un passage secret s'ouvre dans le bureau !")
        print("Une porte vers le couloir sombre devient accessible...")
        print("="*50 + "\n")

if __name__ == "__main__":
    Game().play()