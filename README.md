# Penta Historia

Prototype Python/Pygame d'un jeu qui mélange OpenFront, Pax Historia et WorldBox,
structuré autour d'un conseil de cinq agents : Alpha, Beta, Gamma, Delta et Epsilon.

## Boucle actuelle

- génération d'un petit monde 2D
- plusieurs civilisations avec villes et statistiques simples
- simulation légère de guerre, économie, culture et climat
- cinq suggestions d'agents à chaque tour
- choix joueur via les touches `1` à `5`

## Installation

```bash
cd penta_historia
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.game
```

## Contrôles

- `1` à `5` : appliquer une suggestion du conseil
- `R` : régénérer un monde
- `ESC` ou fermer la fenêtre : quitter

## Répartition collaborative

- **Alpha** : carte, territoires, fronts, expansion
- **Beta** : villes, ressources, logistique
- **Gamma** : culture, recherche, histoire alternative
- **Delta** : intrigue, sabotage, déstabilisation
- **Epsilon** : climat, saisons, catastrophes, mythes
- **Main** : coordination du développement, intégration, loop de jeu, UI, arbitrage des systèmes
- **Zeta** : validation des PR, revue de code, cohérence transversale

## État

Ce dépôt contient un squelette jouable, pensé pour être enrichi progressivement par les agents.

## Architecture

Le projet doit évoluer vers une **architecture hexagonale**.

- le **domaine** et les règles du jeu restent au centre
- les **ports** définissent les interfaces attendues par le cœur applicatif
- les **adapters** branchent le rendu Pygame, les entrées joueur, le stockage, la CI ou d'autres intégrations
- la logique métier ne doit pas dépendre directement de Pygame ou d'un détail technique externe

Voir `ARCHITECTURE.md` pour la cible de structure.

## Collaboration

Le projet avance via **pull requests**.

- pas de merge direct de features sur `main`
- chaque agent développe sa partie du jeu dans sa branche ou sa PR
- les revues de code et validations de PR doivent être faites par **Zeta**
- comme il n'y a qu'un seul compte GitHub, on ne bloque pas le merge sur un nombre d'approvals
- les checks **CI** doivent être verts avant merge
- **Sonar n'est pas bloquant pour l'instant**, le temps que l'intégration PR soit fiable
- voir `CONTRIBUTING.md` pour la règle de contribution
