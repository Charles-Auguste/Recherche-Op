# Recherche-Op

 Mise à jour du Git

Il est maintenant organisé en 3 fichiers principaux
- PL.py est le problème linéaire équivalent et peut-être appelé par tous les autres fichiers
- cout.py calcule les coûts d'une solution (dans le nouveau format)
- json-reader.py que j'ai légèrement modifié pour accepter le nouveau format de solution

Par ailleurs, après discussion avec Thomas, on s'est dit que se serait bien si chaque personne qui développe une heuristique pouvait le faire dans un fichier séparé (ce que j'ai fait avec mon heuristique super client encore en cours de développement)

Enfin, par clarté, essayez de ranger les solutions dans des fichiers au nom explicite du style:
"KIRO-large_heuristique_A_date-et-heure"
Rangé dans solution, comme ca on garde une trace de tout ce que l'on a fait et ce sera pratique pour la fin
Si vous ne savez pas comment faire, regarder ce que j'ai fait dans mon heuristique avec le module os.
