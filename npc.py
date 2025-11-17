#Import modules :
import random

class Monstre:
    """
    Représente un monstre (NPC) qui se déplace dans le jeu.
    Il peut se dépalcer et calculer sa distance au joueur.
    """
    
    # Constructeur
    def __init__(self):
        """
        Initialise le monstre.
        """
        self.current_room = None  # La salle actuelle
    
    def distance_du_joueur(self, player_room):
        """
        Calcule la distance la plus courte (en nombre de salles)
        entre le monstre et le joueur
        
        Args:
            player_room (Room): La salle actuelle du joueur.

        Returns:
            int: La distance (0 si même salle, -1 si non trouvé/invalide).
        """
        
        salle_de_depart = self.current_room
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

    def move(self):
        """
        Déplace le monstre d'une salle au hasard SI il a spawn.
        Choisit une sortie valide et met à jour self.current_room.
        """
        
        # 0. Le monstre a t'il spawn ?
        if not self.current_room:
            return

        # 1. Lister les sorties qui ne sont pas "None"
        sorties_valides = [
            salle for salle in self.current_room.exits.values()
            if salle is not None
        ]

        # 2. Choisir une salle aléatoire et déplacé le monstre dedans.
        nouvelle_salle = random.choice(sorties_valides)
        self.current_room = nouvelle_salle