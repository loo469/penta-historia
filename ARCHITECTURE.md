# Architecture cible

Penta Historia doit évoluer vers une **architecture hexagonale**, avec **ports et adapters**.

## Principe

Le cœur du jeu doit contenir :

- les règles métier
- les entités du monde
- les cas d'usage applicatifs
- la logique des agents Alpha, Beta, Gamma, Delta, Epsilon

Le cœur ne doit pas dépendre directement de :

- Pygame
- GitHub
- Sonar
- fichiers, base de données, réseau
- détails d'interface utilisateur

## Structure visée

### Domaine

Le domaine contient les concepts purs du jeu :

- monde
- civilisation
- ville
- climat
- guerre
- économie
- culture
- intrigue
- mythes
- suggestions du conseil

### Application

La couche application orchestre les cas d'usage :

- avancer un tick de simulation
- générer un monde
- produire les suggestions des cinq agents
- appliquer une décision du joueur
- charger ou sauvegarder une partie

### Ports

Les ports décrivent ce dont l'application a besoin, sans imposer la technologie.

Exemples de ports :

- `RendererPort`
- `InputPort`
- `SaveGamePort`
- `WorldGeneratorPort`
- `EventPublisherPort`

## Adapters

Les adapters implémentent les ports.

Exemples attendus :

- adapter **Pygame** pour le rendu et l'entrée clavier
- adapter fichier JSON pour sauvegarde/chargement
- adapter de génération procédurale du monde
- adapter éventuel pour outils externes, analytics ou debug

## Règle importante

Les dépendances doivent pointer vers l'intérieur :

- adapters → application/domain
- application → domain
- domain → rien d'externe

Jamais l'inverse.

## Traduction concrète pour ce projet

À terme, l'organisation visée ressemble à ceci :

```text
src/
  domain/
    world/
    economy/
    war/
    culture/
    intrigue/
    climate/
    council/
  application/
    use_cases/
    ports/
  adapters/
    pygame/
    persistence/
    generation/
  bootstrap/
    main.py
```

## Décision de projet

Toute nouvelle fonctionnalité importante doit être pensée avec cette cible en tête.

- éviter de coller la logique métier directement dans la vue Pygame
- extraire les interfaces quand un système devient stable
- isoler les dépendances techniques dans des adapters

Le prototype actuel peut rester simple, mais la direction officielle du projet est bien :

**architecture hexagonale avec ports et adapters**.
