# Collaboration des agents

Ce prototype est développé avec les cinq agents comme responsables de systèmes.

## Contributions intégrées

- **Alpha** a poussé une structure orientée `Territory`, `Front`, ravitaillement et stabilisation de l'arrière.
- **Beta** a poussé une économie orientée `Resource`, `Stock`, `Route`, `Convoy`, `Market`.
- **Gamma** a poussé une progression orientée `CultureProfile`, `ResearchTree`, bifurcations et événements.
- **Delta** a poussé un système orienté `SpyAgent`, `NetworkCell`, `Operation`, `Rumor`.
- **Epsilon** a poussé une dynamique orientée `ClimateSystem`, `SeasonCycle`, `CatastropheEngine`, `MythSystem`.

## Règle de développement

Le cœur jouable reste simple au début, mais chaque nouveau système doit pouvoir se brancher proprement sur :

- `WorldState`
- la boucle de simulation dans `src/game.py`
- le conseil dans `src/ui/council.py`

## Prochaine étape

Faire passer le prototype d'un modèle abstrait à des systèmes plus riches, un domaine à la fois, sans casser la boucle jouable.
