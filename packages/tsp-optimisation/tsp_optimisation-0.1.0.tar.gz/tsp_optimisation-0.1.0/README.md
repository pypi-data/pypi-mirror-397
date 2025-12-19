# Projet_TSP

Ce dépôt contient une implémentation pour un projet sur le Problème du Voyageur de Commerce (TSP).

## Structure

- `src/` : code source principal
- `data/` : fichiers de données (ex. `data.json`)
- `tests/` : tests unitaires

## Installation

1. Créez un environnement virtuel (recommandé) :

```bash
python -m venv .venv
source .venv/bin/activate   # Sur Windows: .venv\\Scripts\\activate
```

2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

## Exécution

- Lancer le script principal :

```bash
python src/main.py
```

- Lancer les tests :

```bash
pytest -q
```

## Format des données

- Les heures doivent être exprimées en valeur décimale (par exemple `1.5` pour 1 heure 30 minutes).
- Les distances doivent être exprimées en km.

## Remarques

- Les points d'entrée, les classes et les tests se trouvent dans `src/` et `tests/`.
