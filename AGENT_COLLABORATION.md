# Collaboration des agents

Ce prototype est développé avec les cinq agents comme responsables de systèmes.

Main coordonne le développement global.
Zeta joue un rôle transversal de validation et de revue de code.

## Contributions intégrées

- **Alpha** a poussé une structure orientée `Territory`, `Front`, ravitaillement et stabilisation de l'arrière.
- **Beta** a poussé une économie orientée `Resource`, `Stock`, `Route`, `Convoy`, `Market`.
- **Gamma** a poussé une progression orientée `CultureProfile`, `ResearchTree`, bifurcations et événements.
- **Delta** a poussé un système orienté `SpyAgent`, `NetworkCell`, `Operation`, `Rumor`.
- **Epsilon** a poussé une dynamique orientée `ClimateSystem`, `SeasonCycle`, `CatastropheEngine`, `MythSystem`.
- **Zeta** valide les pull requests, relit la cohérence globale et sert de garde-fou qualité avant merge.

## Règle de développement

Le cœur jouable reste simple au début, mais chaque nouveau système doit pouvoir se brancher proprement sur :

- `WorldState`
- la boucle de simulation dans `src/game.py`
- le conseil dans `src/ui/council.py`

Chaque agent développe prioritairement son domaine, puis fait valider sa PR par Zeta.
Sur GitHub, chaque texte écrit par un agent doit commencer par son nom suivi de `:`, par exemple `Alpha:` ou `Zeta:`.

## Prochaine étape

Faire passer le prototype d'un modèle abstrait à des systèmes plus riches, un domaine à la fois, sans casser la boucle jouable.
