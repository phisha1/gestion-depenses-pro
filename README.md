# Gestion Dépenses Pro

Application Python permettant de valider, analyser,
convertir et exporter des dépenses mensuelles.

## Fonctionnalités

- chargement de fichiers JSON ;
- validation des données avec Pydantic ;
- rejet individuel des dépenses incorrectes ;
- calcul du total et des totaux par catégorie ;
- suivi du plafond mensuel ;
- récupération asynchrone des taux de change ;
- conversions concurrentes en plusieurs devises ;
- affichage avec Rich ;
- export d’un bilan JSON ;
- tests, couverture, lint et typage strict.

## Prérequis

- Linux, macOS ou Windows ;
- Python 3.14 ;
- uv.

## Installation

Cloner le projet, entrer dans son dossier puis recréer
l’environnement :

```bash
uv sync --frozen
```

## Configuration

Le fichier `data/configuration.json` définit la période,
le plafond et les devises :

```json
{
  "periode": "2026-08",
  "plafond_xaf": 250000,
  "devise_source": "XAF",
  "devises_cibles": ["EUR", "USD"]
}
```

## Dépenses

Les dépenses sont placées dans `data/depenses.json` :

```json
[
  {
    "date": "2026-08-01",
    "montant": 8000,
    "categorie": "Alimentation",
    "description": "Courses du week-end"
  }
]
```

Une dépense incorrecte est signalée et ignorée sans empêcher
le traitement des autres données.

## Exécution

Depuis la racine du projet :

```bash
uv run gestion-depenses-pro
```

Le bilan est affiché dans le terminal puis enregistré dans :

```text
data/bilan.json
```

Le bilan local reste disponible si le service de change est
temporairement inaccessible.

## Architecture

```text
src/gestion_depenses_pro/
├── __init__.py
├── cli.py
├── exceptions.py
├── infrastructure.py
├── modeles.py
├── presentation.py
├── py.typed
└── services.py
```

- `modeles.py` : contrats et validation des données ;
- `services.py` : règles métier et calculs purs ;
- `infrastructure.py` : fichiers JSON et appels HTTP ;
- `presentation.py` : affichage Rich ;
- `cli.py` : orchestration de l’application ;
- `exceptions.py` : erreurs contrôlées.

Le document détaillé de conception se trouve dans
`docs/conception.md`.

## Qualité

Exécuter la porte de qualité complète :

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
```

Le projet exige une couverture de branches minimale de 95 %.

## Reproductibilité

`pyproject.toml` définit les plages de versions compatibles.

`uv.lock` conserve les versions exactes utilisées par le projet.

La commande suivante vérifie que l’environnement peut être recréé
sans modifier le fichier de verrouillage :

```bash
uv sync --frozen
```

## Limites

Cette version :

- utilise des fichiers JSON plutôt qu’une base de données ;
- fonctionne en ligne de commande ;
- ne gère qu’un utilisateur local ;
- n’effectue aucun paiement ;
- dépend d’un service externe uniquement pour les conversions.

## Contrôles qualité

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest