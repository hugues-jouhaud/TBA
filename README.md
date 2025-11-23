# TBA - Mise à jour 1

Ce repo contient la première version (minimale) du jeu d’aventure TBA.

Les lieux sont au nombre de 6. Il n'y a pas encore d’objets ni de personnages autres que le joueur et très peu d’interactions. Cette première version sert de base à ce qui va suivre, et sera améliorée au fur et à mesure.

## Structuration

Il y a pour le moment 5 modules contenant chacun une classe.

- `game.py` / `Game` : description de l'environnement, interface avec le joueur ;
- `room.py` / `Room` : propriétés génériques d'un lieu  ;
- `player.py` / `Player` : le joueur ;
- `command.py` / `Command` : les consignes données par le joueur ;
- `actions.py` / `Action` : les interactions entre .

---

## 🗺️ Carte du jeu (après modifications)

Voici la carte du jeu mise à jour après les modifications fonctionnelles (Ex. 3 & 4):

* **Forest** peut aller vers : Cave (N), Castle (S).
* **Tower** peut aller vers : Cottage (N).
* **Cave** peut aller vers : Cottage (E), Forest (S).
* **Cottage** peut aller vers : Tower (S), Cave (O).
* **Swamp** peut aller vers : Tower (N), Castle (O).
* **Castle** peut aller vers : Forest (N), Swamp (E).

### Changements notables:
1.  Le chemin entre **Forest** et **Tower** est coupé dans les deux sens.
2.  Le chemin entre **Tower** et **Swamp** est coupé (déplacement de **Swamp** vers **Tower** est possible, mais **Tower** vers **Swamp** est bloqué).

---

## 📊 Diagramme des Classes

Voici le diagramme de classe représentant la structure des commandes et actions dans le jeu.
[Diagramme de classe Command/Actions](diagramme.png)