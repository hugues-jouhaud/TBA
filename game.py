"""Game class"""

# Import modules
from pathlib import Path
import sys

# Tkinter imports for GUI
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from PIL import Image, ImageTk 

from room import Room
from player import Player
from actions import Actions
from command import Command
from item import Item, batterie 
from character import Character
from quest import Quest
import time
import random

# --- CLASSE QTE DIALOG (POPUP) ---
class QTEDialog(tk.Toplevel):
    """Fenêtre modale pour le Quick Time Event."""
    def __init__(self, parent, target_word, time_limit):
        super().__init__(parent)
        self.title("ATTENTION !")
        self.geometry("400x250")
        self.target_word = target_word
        self.time_limit = time_limit
        self.start_time = time.time()
        self.success = False
        self.running = True  # <--- NOUVEAU : On contrôle si le timer tourne
        self.current_index = 0 

        self.transient(parent)
        self.grab_set()
        
        lbl_info = tk.Label(self, text="LE MONSTRE ATTAQUE !\nTapez le code suivant :", font=("Arial", 12, "bold"), fg="red")
        lbl_info.pack(pady=10)

        self.text_display = tk.Text(self, font=("Courier", 24, "bold"), height=1, width=len(target_word)+2, bg="#222")
        self.text_display.pack(pady=10)
        
        self.text_display.tag_config("red", foreground="red")
        self.text_display.tag_config("green", foreground="#00FF00") 

        self.text_display.insert("end", target_word)
        self.text_display.tag_add("red", "1.0", "end")
        self.text_display.configure(state="disabled") 

        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)
        self.progress["maximum"] = time_limit * 100 
        
        self.bind("<Key>", self.on_key)
        self.focus_set()
        self.update_timer()

    def update_timer(self):
        if not self.running: return  # <--- Si on a fini, on arrête le timer

        elapsed = time.time() - self.start_time
        remaining = self.time_limit - elapsed
        self.progress["value"] = remaining * 100

        if remaining <= 0:
            self.fail_qte()
        else:
            self.after(50, self.update_timer)

    def on_key(self, event):
        if self.success or not self.running: return 

        char_typed = event.char.upper()
        if not char_typed: return
        if self.current_index >= len(self.target_word): return

        expected_char = self.target_word[self.current_index]

        if char_typed == expected_char:
            self.text_display.configure(state="normal")
            start_idx = f"1.{self.current_index}"
            end_idx = f"1.{self.current_index + 1}"
            self.text_display.tag_remove("red", start_idx, end_idx)
            self.text_display.tag_add("green", start_idx, end_idx)
            self.text_display.configure(state="disabled")
            
            self.current_index += 1
            if self.current_index >= len(self.target_word):
                self.win_qte()

    def win_qte(self):
        self.running = False # <--- On arrête le timer AVANT la popup
        self.success = True
        messagebox.showinfo("SUCCÈS", "Vous avez repoussé le monstre !", parent=self)
        self.destroy()

    def fail_qte(self):
        self.running = False # <--- On arrête le timer
        self.success = False
        messagebox.showwarning("ÉCHEC", "Trop lent ! Le monstre vous frappe !", parent=self)
        self.destroy()


class Game:
    def __init__(self):
        self.finished = False
        self.rooms = []
        self.commands = {}
        self.player = None
        self.character = None
        self.debug = True
        self.qte_count = 0
        self.gui_root = None # Référence vers la fenêtre principale
        self.final_quest_added = False
        self.flashlight_on = False
    
    def setup(self,player_name=None):
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
        self.commands["use"] = Command("use", " <item> : utiliser un objet (lampe, batterie...)", Actions.action_use, 1)
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
        
        # --- ASSOCIATION DES IMAGES ---
        self.cave.image = "cave.png"
        self.rituel.image = "rituel.png"
        self.stock1.image = "stockage1.png"
        self.clouloir1.image = "couloir1.png"
        self.prison.image = "prison.png"
        self.sdb2.image = "salledebain2.png"
        self.ch2.image = "chambre2.png"
        self.clouloir2.image = "couloir2.png"
        self.stock2.image = "stockage2.png"
        self.bureau.image = "bureau.png"
        self.balcon.image = "balcon.png"
        self.safe.image = "safe.png"
        self.cuisine.image = "cuisine.png"
        self.sam.image = "salleamanger.png"
        self.salon.image = "salon.png"
        self.ch1.image = "chambre1.png"
        self.sdb1.image = "salledebain1.png"

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
        self.batterie_charge = Item("batterie", "une batterie chargée", 2.0)
        self.batterie_decharge = Item("batterie déchargée", "une batterie déchargée", 2.0)
        livre = Item("livre", "un des 5 tomes de l'encyclopédie", 3)
        lampe = Item("Lampe Torche", "permet de s'éclairer dans le noir", 0.3)
        cle = Item("cle", "Une vieille clé rouillée pour sortir d'ici.", 0.1)
        fusible = Item("fusible", "Un gros fusible industriel très lourd.", 5.5)
        levier = Item("levier", "Un levier de secours fixé au mur à côté de la porte, il y a un trou pour une clé", 999.0)


        # Placement des items
        self.salon.add_item(levier, 1)
        self.bureau.add_item(cle, 1)
        # Les 3 Fusibles (Objectif Principal)
        self.prison.add_item(fusible, 1)  # Fusible 1 (Remplace la clé)
        self.cave.add_item(fusible, 1)    # Fusible 2 (Dans le noir)
        self.sdb1.add_item(fusible, 1)    # Fusible 3 (Salle de bain 1)
        # batteries et Livres
        self.cave.add_item(self.batterie_charge, 1)
        self.rituel.add_item(self.batterie_charge, 1)
        self.stock1.add_item(self.batterie_charge, 1)
        self.prison.add_item(self.batterie_charge, 1)
        self.ch2.add_item(self.batterie_charge, 1)
        self.ch2.add_item(livre, 1) 
        self.clouloir2.add_item(self.batterie_charge, 1)
        self.stock2.add_item(self.batterie_charge, 1)
        self.stock2.add_item(livre, 1)
        self.bureau.add_item(self.batterie_charge, 1)
        self.safe.add_item(self.batterie_charge, 1)
        self.safe.add_item(livre, 1)
        self.safe.add_item(lampe, 1)
        self.cuisine.add_item(self.batterie_charge, 1)
        self.cuisine.add_item(livre, 1)
        self.sam.add_item(self.batterie_charge, 1)
        self.sdb1.add_item(livre, 1)

        # --- JOUEUR ---
        if player_name is None:
            player_name = input("\nEntrez votre nom: ")
        self.player = Player(player_name)
        self.player.current_room = self.salon

        # --- Quêtes ---
        self._setup_quests()
    
    def _setup_quests(self):
        """Initialize all quests."""
        grand_explorateur = Quest(
            title="Grand Explorateur",
            description="Explorez tous les lieux de ce mystérieux manoir.",
            objectives=["Visiter cave", "Visiter salle de Rituel", "Visiter Safe", "Visiter Cuisine"],
            reward="batterie"
        )

        un_bruit_etonnant = Quest(
            title="Un bruit étonnant",
            description="Allez à la salle de Rituel pour découvrir la source de ce bruit étrange.",
            objectives=["Visiter salle de Rituel"],
            reward="batterie"
        )

        une_mauvaise_surprise = Quest(
            title="Une mauvaise surprise",
            description="Survivez à la rencontre avec le monstre en réussissant le QTE.",
            objectives=["Réussir un QTE"],
            reward="batterie"
        )

        energie_cool = Quest(
            title="L'énergie c'est cool",
            description="Ramassez votre première batterie pour alimenter vos objets.",
            objectives=["Prendre batterie"],
            reward="batterie"
        )

        survival_quest = Quest(
            title="Grand Voyageur",
            description="Déplacez-vous 10 fois dans le manoir.",
            objectives=["Se déplacer 10 fois"],
            reward="batterie"
        )

        mysteres_manoir = Quest(
            title="Les Mystères du Manoir",
            description="Récupérez les 5 livres dispersés dans le manoir et déposez-les dans le bureau pour découvrir un secret.",
            objectives=["Déposer 5 livres dans le bureau"],
            reward="batterie"
        )

        # Add quests to player's quest manager
        self.player.quest_manager.add_quest(un_bruit_etonnant)
        self.player.quest_manager.add_quest(une_mauvaise_surprise)
        self.player.quest_manager.add_quest(energie_cool)
        self.player.quest_manager.add_quest(grand_explorateur)
        self.player.quest_manager.add_quest(survival_quest)
        self.player.quest_manager.add_quest(mysteres_manoir)

    def play(self):
        # Cette fonction sert surtout pour le mode Console (CLI)
        # Mais on va s'assurer que check_events() est appelé
        self.setup()
        self.print_welcome()
        while not self.finished:
            user_input = input("> ")
            if not user_input: continue
            self.process_command(user_input)
            
    def spawn_monster(self):
        # Vérification pour ne pas créer plusieurs monstres
        if self.character is None:
            self.character = Character()
            self.character.current_room = self.salon
            print("\n-----------------------------------------------------")
            print("Un rugissement glacial secoue le manoir...")
            print(f"Vous avez réveillé un monstre ! Il est dans le {self.character.current_room.name}.")
            print("-----------------------------------------------------\n")

    def trigger_qte(self):
        length = 3 + (self.qte_count * 2)
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        target_word = ''.join(random.choice(alphabet) for i in range(length))
        
        success = False

        if self.gui_root:
            qte_window = QTEDialog(self.gui_root, target_word, 5.0)
            self.gui_root.wait_window(qte_window) 
            success = qte_window.success
        else:
            print("\n" + "!"*40)
            print(f"SURPRISE ! TAPEZ : {target_word}")
            print("!"*40)
            start = time.time()
            inp = input("CODE > ").upper()
            dur = time.time() - start
            success = (inp == target_word and dur <= 5.0)

        if success:
            print("\nSUCCÈS ! Vous repoussez le monstre !")
            if self.character:
                self.character.stunned_turns = 3 
            self.qte_count += 1
            self.player.quest_manager.check_action_objectives("Réussir", "un QTE")
            return True
        else:
            print("\nÉCHEC ! Le monstre vous blesse.")
            self.player.hp -= 1
            print(f"PV restants : {self.player.hp}")
            if self.player.hp <= 0:
                self.finished = True
                self.lose()
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
        
        self.check_game_events(command_word)

    def check_game_events(self, last_command):
        """
        Simule un tour de boucle de jeu après une action du joueur.
        Ordre : Spawn -> Gestion Stun -> Collision (entrée) -> Mouvement Monstre -> Collision (sortie) -> Ambiance -> Victoire
        """
        if self.finished: return

        # ---------------------------------------------------------
        # 1. SCÉNARIO & SPAWN (Comme avant)
        # ---------------------------------------------------------
        if self.player.current_room == self.rituel:
            # Spawn du monstre
            if self.character is None:
                self.spawn_monster()
            
            # Ajout de la quête finale (Levier + Fusibles)
            if not self.final_quest_added:
                print("\n Un monstre est apparu dans le manoir ! Il faut rétablir le courant et fuir !")
                # On définit la quête finale
                fuir_quest = Quest(
                    title="Réparer et Fuir", 
                    description="1. Posez 3 FUSIBLES dans la salle SAFE.\n2. Prenez la CLÉ.\n3. Actionnez le LEVIER dans le SALON !", 
                    objectives=["Poser 3 fusibles dans Safe", "Utiliser Levier au Salon"], 
                    reward="La LIBERTÉ"
                )
                self.player.quest_manager.add_quest(fuir_quest)
                self.player.quest_manager.activate_quest("Réparer et Fuir")
                
                if self.gui_root:
                    messagebox.showwarning("ALERTE", "Un monstre est apparu dans le manoir ! Il faut rétablir le courant et fuir !")
                
                self.final_quest_added = True

        # ---------------------------------------------------------
        # 2. LOGIQUE DU MONSTRE
        # ---------------------------------------------------------
        if self.character is not None:
            
            # A. GESTION DU STUN
            # Si le monstre est stun, il perd 1 tour et ne fait RIEN d'autre.
            if self.character.stunned_turns > 0:
                self.character.stunned_turns -= 1
                if self.character.current_room == self.player.current_room:
                    print(f"\n💤 Le monstre est étourdi au sol... (Reste {self.character.stunned_turns} tour(s))")
                # ON S'ARRÊTE ICI POUR LE MONSTRE : RETURN
                # On continue juste pour check_win en bas, mais pas de mouvement/attaque
            
            else:
                # B. COLLISION IMMÉDIATE
                # (Le joueur vient d'entrer dans la salle du monstre)
                if self.character.current_room == self.player.current_room:
                    print("\n😱 Vous tombez nez à nez avec le monstre !")
                    self.trigger_qte()
                    return

                # C. DÉPLACEMENT DU MONSTRE
                # Le monstre ne bouge que si le joueur a bougé (go/back)
                # Et seulement si le jeu n'est pas fini
                if last_command in ["go", "back"] and not self.finished:
                    self.character.move(self.player.current_room)
                    
                    # D. COLLISION APRÈS DÉPLACEMENT
                    # (Le monstre vient d'entrer dans la salle du joueur)
                    if self.character.current_room == self.player.current_room:
                        print("\n😱 Le monstre vous rattrape !")
                        self.trigger_qte()
                        return

                # E. AMBIANCE (Seulement s'il n'est pas dans la même pièce)
                if self.character.current_room != self.player.current_room and not self.finished:
                    dist = self.character.distance_du_joueur(self.player.current_room)
                    if dist == 1:
                        print("\n--> Vous entendez des bruits de pas tout proches...")
                    elif dist == 2:
                        print("\n--> Une odeur putride flotte dans l'air...")

        # ---------------------------------------------------------
        # 3. VÉRIFICATION DE LA VICTOIRE
        # ---------------------------------------------------------
        if not self.finished:
            self.check_win()
        
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
        print("\n" + "="*50)
        print("🎉 VOUS AVEZ GAGNÉ ! VOUS AVEZ RÉUSSI À FUIR ! 🎉")
        print("="*50)
        self.player.show_rewards()
        
        if self.gui_root:
            messagebox.showinfo("VICTOIRE", "BRAVO !\nVous avez réussi à fuir le manoir !\n\nCliquez pour quitter.", parent=self.gui_root)
            self.gui_root.destroy()
        else:
            sys.exit()

    def lose(self):
        print("\n" + "="*50)
        print("💀 GAME OVER - VOUS AVEZ PERDU 💀")
        print("="*50)
        
        if self.gui_root:
            messagebox.showerror("DÉFAITE", "Le monstre vous a vaincu...\nGAME OVER", parent=self.gui_root)
            self.gui_root.destroy()
        else:
            sys.exit()

    def unlock_secret_path(self):
        """Déverrouille le chemin secret du bureau vers le couloir sombre."""
        self.bureau.exits["D"] = self.clouloir1
        print("\n" + "="*50)
        print("✨ Un passage secret s'ouvre dans le bureau !")
        print("Une porte vers le couloir sombre devient accessible...")
        print("="*50 + "\n")

##############################
# Tkinter GUI Implementation #
##############################

class _StdoutRedirector:
    """Redirect sys.stdout writes into a Tkinter Text widget."""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, msg):
        # On ajoute un try/except pour ignorer les erreurs si la fenêtre est détruite
        try:
            if msg:
                self.text_widget.configure(state="normal")
                self.text_widget.insert("end", msg)
                self.text_widget.see("end")
                self.text_widget.configure(state="disabled")
        except tk.TclError:
            pass # La fenêtre est fermée, on ignore le message

    def flush(self):
        pass

class SelectionWindow(tk.Toplevel):
    """Une fenêtre popup générique pour choisir un item ou une quête."""
    def __init__(self, parent, title, items_dict, callback_action=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("350x450")
        
        lbl = ttk.Label(self, text=title, font=("Helvetica", 12, "bold"))
        lbl.pack(pady=10)

        # Zone scrollable pour les items si la liste est longue
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=5)
        scrollbar.pack(side="right", fill="y")

        if not items_dict:
            ttk.Label(scrollable_frame, text="Rien à afficher !").pack(pady=20)
        else:
            for obj, info in items_dict.items():
                # Gestion de l'affichage du nom selon le type d'objet (Item ou Quest)
                if hasattr(obj, 'name'):
                    name_str = obj.name
                elif hasattr(obj, 'title'):
                    name_str = obj.title
                else:
                    name_str = str(obj)

                # Construction du texte du bouton
                txt = f"{name_str}"
                # Si 'info' est un nombre (quantité), on l'ajoute
                if isinstance(info, int) and info > 1:
                    txt += f" (x{info})"
                # Si 'info' est une string (statut quête), on l'ajoute
                elif isinstance(info, str):
                    txt += f" {info}"
                
                # Création du bouton
                btn = ttk.Button(
                    scrollable_frame, 
                    text=txt, 
                    command=lambda o=obj: self._on_click(callback_action, o)
                )
                btn.pack(fill="x", pady=2, padx=10)
        
        # Bouton fermer
        ttk.Button(self, text="Fermer", command=self.destroy).pack(pady=10, side="bottom")

    def _on_click(self, callback, obj):
        # 1. On ferme d'abord la petite fenêtre (pour éviter le conflit)
        try:
            if self.winfo_exists():
                self.destroy()
        except Exception:
            pass # Si elle est déjà détruite, on s'en fiche

        # 2. Ensuite on exécute l'action (qui peut fermer le jeu complet)
        if callback:
            callback(obj)

class GameGUI(tk.Tk):
    IMAGE_WIDTH = 600
    IMAGE_HEIGHT = 400

    def __init__(self):
        super().__init__()
        self.title("TBA - L'Aventure du Manoir")
        self.geometry("1000x800")
        self.minsize(900, 700)

        self.game = Game()
        self.game.gui_root = self
        
        # Ask player name
        name = simpledialog.askstring("Nom", "Entrez votre nom:", parent=self)
        if not name: name = "Joueur"
        self.game.setup(player_name=name)

        self._build_layout()

        self.original_stdout = sys.stdout
        sys.stdout = _StdoutRedirector(self.text_output)

        self.game.print_welcome()
        self._update_room_image()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # --- Top Frame (Image + Boutons) ---
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=(6,3))
        top_frame.grid_columnconfigure(0, weight=0)
        top_frame.grid_columnconfigure(1, weight=1)

        # Image
        image_frame = ttk.Frame(top_frame, width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT)
        image_frame.grid(row=0, column=0, sticky="nw", padx=(0,6))
        image_frame.grid_propagate(False)
        self.canvas = tk.Canvas(image_frame, width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT, bg="#222")
        self.canvas.pack(fill="both", expand=True)
        self._image_ref = None

        # --- Zone des Boutons (Droite) ---
        buttons_frame = ttk.Frame(top_frame)
        buttons_frame.grid(row=0, column=1, sticky="nsew")
        buttons_frame.grid_columnconfigure(0, weight=1)

        # Chargement des icones
        self.icons = {}
        assets_dir = Path(__file__).parent / 'assets'
        
        icon_files = {
            "help": "help-50.png", "quit": "quit-50.png",
            "up": "up-arrow-50.png", "down": "down-arrow-50.png",
            "left": "left-arrow-50.png", "right": "right-arrow-50.png",
            "look": "look.png", "talk": "talk.png",
            "take": "take.png", "drop": "drop.png", 
            "use": "use.png",
            "inventory": "inventory.png", "quests": "quests.png",
            "history": "history.png", "back": "back.png"
        }

        for key, filename in icon_files.items():
            path = assets_dir / filename
            if path.exists():
                try:
                    pil_icon = Image.open(str(path))
                    pil_icon = pil_icon.resize((50, 50), Image.Resampling.LANCZOS)
                    self.icons[key] = ImageTk.PhotoImage(pil_icon)
                except Exception as e:
                    print(f"Erreur chargement icone {filename}: {e}")
                    self.icons[key] = None
            else:
                self.icons[key] = None

        # 1. Groupe Déplacements
        move_frame = ttk.LabelFrame(buttons_frame, text="Déplacements")
        move_frame.pack(fill="x", pady=5)
        
        self._create_btn(move_frame, "up", "go N", 0, 1)
        self._create_btn(move_frame, "left", "go O", 1, 0)
        self._create_btn(move_frame, "right", "go E", 1, 2)
        self._create_btn(move_frame, "down", "go S", 2, 1)
        self._create_btn(move_frame, "up", "go U", 0, 3) 
        self._create_btn(move_frame, "down", "go D", 2, 3) 
        
        if self.icons.get("back"):
            tk.Button(move_frame, image=self.icons["back"], command=lambda: self._send_command("back"), bd=0).grid(row=1, column=3)

        # 2. Groupe Actions
        act_frame = ttk.LabelFrame(buttons_frame, text="Actions")
        act_frame.pack(fill="x", pady=5)
        
        self._create_btn(act_frame, "look", "look", 0, 0)
        
        # Talk ouvre une fenêtre désormais
        tk.Button(act_frame, image=self.icons.get("talk"), command=self._open_talk_window, bd=0).grid(row=0, column=1, padx=2, pady=2)
        
        # Boutons avec Popup
        tk.Button(act_frame, image=self.icons.get("take"), command=self._open_take_window, bd=0).grid(row=1, column=0, padx=2, pady=2)
        tk.Button(act_frame, image=self.icons.get("drop"), command=self._open_drop_window, bd=0).grid(row=1, column=1, padx=2, pady=2)
        tk.Button(act_frame, image=self.icons.get("use"), command=self._open_use_window, bd=0).grid(row=2, column=0, columnspan=2, padx=2, pady=2)

        # 3. Groupe Menu
        menu_frame = ttk.LabelFrame(buttons_frame, text="Menu")
        menu_frame.pack(fill="x", pady=5)

        tk.Button(menu_frame, image=self.icons.get("inventory"), command=self._open_inventory_window, bd=0).grid(row=0, column=0, padx=5, pady=2)
        tk.Button(menu_frame, image=self.icons.get("quests"), command=self._open_quests_window, bd=0).grid(row=0, column=1, padx=5, pady=2)
        
        tk.Button(menu_frame, image=self.icons.get("history"), command=lambda: self._send_command("history"), bd=0).grid(row=0, column=2, padx=5, pady=2)
        tk.Button(menu_frame, image=self.icons.get("help"), command=lambda: self._send_command("help"), bd=0).grid(row=1, column=0, padx=5, pady=2)
        tk.Button(menu_frame, image=self.icons.get("quit"), command=lambda: self._send_command("quit"), bd=0).grid(row=1, column=2, padx=5, pady=2)


        # --- Middle (Terminal) ---
        output_frame = ttk.Frame(self)
        output_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=3)
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical")
        self.text_output = tk.Text(output_frame, wrap="word", yscrollcommand=scrollbar.set, state="disabled", bg="#111", fg="#eee", font=("Consolas", 10))
        scrollbar.config(command=self.text_output.yview)
        self.text_output.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # --- Bottom (Entry) ---
        entry_frame = ttk.Frame(self)
        entry_frame.grid(row=2, column=0, sticky="ew", padx=6, pady=(3,6))
        entry_frame.grid_columnconfigure(0, weight=1)
        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(entry_frame, textvariable=self.entry_var)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()

    def _create_btn(self, parent, icon_key, command_str, r, c):
        img = self.icons.get(icon_key)
        if img:
            tk.Button(parent, image=img, command=lambda: self._send_command(command_str), bd=0).grid(row=r, column=c, padx=2, pady=2)
        else:
            tk.Button(parent, text=command_str, command=lambda: self._send_command(command_str)).grid(row=r, column=c, padx=2, pady=2)

    # --- UTILITAIRE DE SÉCURITÉ INVENTAIRE ---
    def _get_inventory_dict(self):
        """Récupère le dictionnaire d'objets depuis l'inventaire du joueur, en gérant la structure 'slots'."""
        inv_obj = self.game.player.inventory
        
        # --- CORRECTION ICI : On lit 'slots' ---
        if hasattr(inv_obj, "slots"):
            items_dict = {}
            for slot in inv_obj.slots:
                if slot is not None:
                    # On associe l'objet Item à sa quantité
                    items_dict[slot.item] = slot.quantity
            return items_dict
        
        # Fallback si jamais l'inventaire change de structure
        if isinstance(inv_obj, dict): return inv_obj
        return {}

    # --- Logique des Popups ---

    def _open_talk_window(self):
        """Demande à qui parler avant d'envoyer la commande."""
        target = simpledialog.askstring("Parler", "À qui voulez-vous parler ?", parent=self)
        if target:
            self._send_command(f"talk {target}")

    def _open_take_window(self):
        """Ouvre la fenêtre pour PRENDRE des objets."""
        room = self.game.player.current_room
        items = room.items 
        
        def do_take(item_obj):
            self._send_command(f"take {item_obj.name}")
            
        SelectionWindow(self, "Prendre un objet", items, do_take)

    def _open_drop_window(self):
        """Ouvre la fenêtre pour JETER des objets."""
        # --- UTILISATION DE LA CORRECTION ---
        items = self._get_inventory_dict()
        
        def do_drop(item_obj):
            self._send_command(f"drop {item_obj.name}")

        SelectionWindow(self, "Jeter un objet", items, do_drop)
    
    def _open_use_window(self):
        """Ouvre l'inventaire ET les objets de la salle pour choisir quoi UTILISER."""
        # 1. On récupère les items de l'inventaire
        items = self._get_inventory_dict().copy() 
        
        # 2. On récupère les items présents dans la salle actuelle
        room_items = self.game.player.current_room.items
        
        # 3. On fusionne les deux (ajoute les objets de la salle à la liste)
        items.update(room_items)
        
        # 4. On ouvre la fenêtre
        SelectionWindow(self, "Utiliser un objet", items, lambda i: self._send_command(f"use {i.name}"))

    def _open_inventory_window(self):
        """Ouvre l'inventaire en lecture seule."""
        # --- UTILISATION DE LA CORRECTION ---
        items = self._get_inventory_dict()
        
        # On passe None en callback pour ne pas avoir de boutons
        SelectionWindow(self, "Mon Inventaire", items, callback_action=None)
    
    def _open_quests_window(self):
        """Ouvre la fenêtre des quêtes."""
        # Récupération de toutes les quêtes
        all_quests = self.game.player.quest_manager.get_all_quests()
        quests_dict = {}
        
        for q in all_quests:
            status = "(Terminée)" if q.is_completed else "(En cours)" if q.is_active else "(Non commencée)"
            quests_dict[q] = status

        def on_quest_click(quest_obj):
            # Construction du message de description
            msg = f"Titre : {quest_obj.title}\n\n"
            msg += f"Description : {quest_obj.description}\n"
            msg += f"Objectifs : {', '.join(quest_obj.objectives)}\n"
            msg += f"Récompense : {quest_obj.reward}\n\n"
            
            if quest_obj.is_completed:
                msg += "Statut : TERMINÉE ✅"
                messagebox.showinfo("Détails de la quête", msg)
            elif quest_obj.is_active:
                msg += "Statut : EN COURS 🏃"
                messagebox.showinfo("Détails de la quête", msg)
            else:
                msg += "Statut : NON COMMENCÉE ❌"
                msg += "\nVoulez-vous activer cette quête maintenant ?"
                if messagebox.askyesno("Activer la quête ?", msg):
                    self._send_command(f"activate {quest_obj.title}")

        SelectionWindow(self, "Journal de Quêtes", quests_dict, on_quest_click)

    # --- Méthodes existantes ---
    def _update_room_image(self):
        try:
            if not self.winfo_exists() or self.game.finished:
                return
        except tk.TclError:
            return

        if not self.game.player or not self.game.player.current_room: return
        room = self.game.player.current_room
        assets_dir = Path(__file__).parent / 'assets'
        
        image_path = assets_dir / (Path(room.image).name if room.image else 'scene.png')

        try:
            pil_image = Image.open(str(image_path))
            pil_image = pil_image.resize((self.IMAGE_WIDTH, self.IMAGE_HEIGHT), Image.Resampling.LANCZOS)
            self._image_ref = ImageTk.PhotoImage(pil_image)
            self.canvas.delete("all")
            self.canvas.create_image(self.IMAGE_WIDTH/2, self.IMAGE_HEIGHT/2, image=self._image_ref)
        except Exception as e:
            # On utilise un print sécurisé (grâce à la modif 1)
            print(f"[GUI] Erreur image: {e}")
            self.canvas.delete("all")
            self.canvas.create_text(self.IMAGE_WIDTH/2, self.IMAGE_HEIGHT/2, text=f"Image manquante:\n{room.name}", fill="white", font=("Arial", 14), justify="center")

    def _on_enter(self, _event=None):
        value = self.entry_var.get().strip()
        if value: self._send_command(value)
        self.entry_var.set("")

    def _send_command(self, command):
        if self.game.finished: return
        print(f"> {command}\n")
        self.game.process_command(command)
        if self.game.finished:
            return

        self._update_room_image()

    def _on_close(self):
        sys.stdout = self.original_stdout
        self.destroy()


def main():
    """Entry point."""
    args = sys.argv[1:]
    if '--cli' in args:
        Game().play()
        return
    try:
        app = GameGUI()
        app.mainloop()
    except tk.TclError as e:
        print(f"GUI indisponible ({e}). Passage en mode console.")
        Game().play()


if __name__ == "__main__":
    main()