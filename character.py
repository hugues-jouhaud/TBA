#Import modules :
import random

class Character:
    """
    Représente un monstre (NPC) qui se déplace dans le jeu.
    Il peut se déplacer et calculer sa distance au joueur.
    """
    
    # Constructeur
    def __init__(self):
        """
        Initialise le monstre.
        """
        self.current_room = None  # La salle actuelle
        self.stunned_turns = 0 # Compteur des tours stun restant
        self.name = "Monstre"
        self.description = "Un monstre hideux"
        self.msgs = "Grrrrr"
    
    def __str__(self):
        """
        Nom du monstre.
        """
        return self.name + " : " + self.description
    
    def distance_du_joueur(self, player_room, depart=None):
        """
        Calcule la distance la plus courte (en nombre de salles)
        entre le monstre et le joueur.
        
        Args:
            player_room (Room): La salle actuelle du joueur.
            depart (Room, optional): Salle de départ du calcul (par défaut self.current_room).

        Returns:
            int: La distance (0 si même salle, -1 si non trouvé/invalide).
        """
        
        # Modification ici : on permet de simuler un départ depuis une autre salle
        salle_de_depart = depart if depart else self.current_room
        salle_cible = player_room
        
        # Si le monstre ou le joueur n'a pas de position
        if not salle_de_depart or not salle_cible:
            return -1

        # S'ils sont dans la même pièce
        if salle_de_depart == salle_cible:
            return 0

        # --- Initialisation de "l'exploration" ---
        #    On stocke des tuples (salle, distance_actuelle)
        #    On commence par la salle de départ (distance 0).
        file_a_visiter = [(salle_de_depart, 0)]
        
        salles_visitees = {salle_de_depart}

        
        while file_a_visiter:
            
            # On prend la première salle de notre liste
            (salle_actuelle, distance_actuelle) = file_a_visiter.pop(0)

            for prochaine_salle in salle_actuelle.exits.values():
                
                # Si c'est une vraie sortie (pas 'None')
                # ET qu'on ne l'a pas encore visitée
                if prochaine_salle and prochaine_salle not in salles_visitees:
                    # C'est la salle du joueur ?
                    if prochaine_salle == salle_cible:
                        # OUI
                        return distance_actuelle + 1

                    # Sinon :
                    
                    # 1. On la marque comme visitée et note la nouvelle distance
                    salles_visitees.add(prochaine_salle)
                    file_a_visiter.append((prochaine_salle, distance_actuelle + 1))
        # Pas trouvé ...
        return -1

    def move(self, player_room):
        """
        Déplace le monstre.
        - Si le joueur est à 2 cases ou moins : se rapproche du joueur (pathfinding).
        - Sinon : déplacement aléatoire.
        """
        
        # 0. Le monstre a t'il spawn ?
        if not self.current_room:
            return

        # 1. Gestion de l'étourdissement ---
        if self.stunned_turns > 0:
            self.stunned_turns -= 1
            print(f"(Le monstre est étourdi, il lui reste {self.stunned_turns} tours)")
            return

        # 2. Lister les sorties qui ne sont pas "None"
        sorties_valides = [
            salle for salle in self.current_room.exits.values()
            if salle is not None and salle.name != "Safe"  # Bloque l'accès au Safe
        ]
        
        if not sorties_valides:
            return # Bloqué

        # --- LOGIQUE DE CHASSE ---
        
        # Calculer la distance actuelle par rapport au joueur
        dist_actuelle = self.distance_du_joueur(player_room)
        
        nouvelle_salle = None

        # Si le joueur est dans la Safe room, on force le mode aléatoire (le monstre ne chasse pas)
        joueur_est_safe = (player_room.name == "Safe")

        if not joueur_est_safe:
            dist_actuelle = self.distance_du_joueur(player_room)
            # Si le joueur est repéré (distance <= 2) et pas dans la même salle (> 0)
            # On vérifie aussi que le chemin existe (!= -1)
            if 0 < dist_actuelle <= 2:
                print("Le monstre a senti votre présence...")
                
                meilleure_distance = 9999 # Nombre arbitraire grand
                
                # On teste chaque sortie possible
                for sortie in sorties_valides:
                    # On calcule la distance SI le monstre prenait cette sortie
                    dist_depuis_sortie = self.distance_du_joueur(player_room, depart=sortie)
                    
                    # Si cette sortie mène au joueur et est plus courte que ce qu'on a trouvé
                    if dist_depuis_sortie != -1 and dist_depuis_sortie < meilleure_distance:
                        meilleure_distance = dist_depuis_sortie
                        nouvelle_salle = sortie
            
        # --- LOGIQUE ALEATOIRE (FALLBACK) ---
        
        # Si on n'a pas trouvé de chemin de chasse ou si le joueur est trop loin
        if nouvelle_salle is None:
            nouvelle_salle = random.choice(sorties_valides)
            
        # 3. Appliquer le déplacement
        self.current_room = nouvelle_salle