# Coordination du développement

Main coordonne le développement global du projet.

## Rôles

- **Main**: coordination, intégration, arbitrage technique, loop principal, architecture
- **Alpha**: guerre, carte, frontières, expansion, pression de front
- **Beta**: villes, économie, ressources, logistique
- **Gamma**: culture, recherche, histoire alternative, événements
- **Delta**: intrigue, sabotage, renseignement, déstabilisation
- **Epsilon**: climat, saisons, catastrophes, mythes
- **Zeta**: revue de code, validation PR, cohérence globale avant merge

## Sprint actuel, objectif

Transformer le prototype actuel en une base hexagonale plus claire, tout en enrichissant chaque pilier du jeu sans casser la boucle jouable.

## Tâches du sprint

### Main
- consolider la structure `domain / application / adapters`
- intégrer les contributions des autres agents
- garder le prototype jouable en continu

### Alpha
- proposer puis implémenter une première vraie notion de front
- rendre la pression de guerre plus lisible que le simple hasard local

### Beta
- enrichir le modèle ville/ressources
- introduire un début de logistique ou de flux entre villes

### Gamma
- introduire une première couche de recherche/culture plus structurée
- préparer un système simple d'événements historiques

### Delta
- rendre l'intrigue plus explicite, avec cible, effet, risque ou chaleur
- éviter que le sabotage soit seulement un malus aléatoire invisible

### Epsilon
- enrichir les saisons/anomalies climatiques
- connecter les effets climat aux récoltes, villes ou tensions

### Zeta
- relire les PR
- vérifier la cohérence avec l'architecture hexagonale
- valider seulement les PR propres, compréhensibles et testées

## Règles de coordination

- chaque agent travaille sur son domaine prioritaire
- Main garde la vue d'ensemble et tranche les conflits de conception
- Zeta ne développe pas le cœur des features, Zeta valide
- toute évolution doit respecter la cible hexagonale du projet
