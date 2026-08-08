# Cahier des charges — Gestion Dépenses Pro

## 1. Présentation du projet

### 1.1 Contexte

Un particulier enregistre ses dépenses mensuelles dans un fichier JSON.
Une simple liste de dépenses ne lui permet cependant pas de connaître
rapidement son total mensuel, la répartition par catégorie, le budget
restant ou la valeur de ses dépenses dans d’autres devises.

### 1.2 Problème à résoudre

L’utilisateur a besoin d’un outil local capable de contrôler ses données,
de produire un bilan financier compréhensible et de continuer à fonctionner
lorsqu’une partie des données ou un service externe est indisponible.

### 1.3 Objectif général

Développer une application en ligne de commande qui charge les dépenses
d’un mois, valide les données, calcule un bilan, récupère des taux de change,
affiche les résultats dans le terminal et exporte un rapport JSON.

### 1.4 Utilisateur cible

L’application est destinée à un particulier qui :

- sait remplir ou modifier un fichier JSON ;
- veut analyser ses dépenses mensuelles ;
- utilise l’application depuis un terminal ;
- souhaite conserver un bilan exportable.

### 1.5 Valeur apportée

L’application transforme des données brutes en informations exploitables :

- dépenses valides et invalides ;
- montant total dépensé ;
- total par catégorie ;
- budget utilisé et budget restant ;
- conversion du total en EUR et en USD ;
- rapport final enregistré dans un fichier JSON.


## 2. Périmètre

### 2.1 Fonctionnalités incluses

L’application doit permettre de :

1. charger une configuration mensuelle depuis un fichier JSON ;
2. charger une liste de dépenses depuis un fichier JSON ;
3. valider séparément chaque dépense ;
4. conserver les dépenses valides ;
5. signaler les dépenses invalides sans interrompre tout le traitement ;
6. calculer le total général ;
7. calculer les totaux par catégorie ;
8. calculer le budget restant ;
9. déterminer si le plafond mensuel est dépassé ;
10. récupérer plusieurs taux de change par HTTP ;
11. effectuer les appels indépendants de manière concurrente ;
12. convertir le total dans les devises demandées ;
13. afficher un bilan lisible dans le terminal ;
14. exporter le bilan dans un fichier JSON.

### 2.2 Fonctionnalités exclues

Cette version ne doit pas :

- proposer d’interface graphique ou web ;
- utiliser de base de données ;
- gérer plusieurs comptes utilisateurs ;
- authentifier un utilisateur ;
- modifier ou supprimer interactivement des dépenses ;
- effectuer des paiements ;
- prédire les dépenses futures ;
- remplacer une application de comptabilité officielle.

## 3. Exigences fonctionnelles

Chaque exigence possède un identifiant afin de pouvoir la relier ensuite
à une fonction et à un ou plusieurs tests.

### EF-01 — Charger la configuration

L’application doit charger la configuration depuis
`data/configuration.json`.

Si ce fichier est absent, invalide ou illisible, l’application doit afficher
une erreur claire et arrêter le traitement.

### EF-02 — Charger les dépenses

L’application doit charger les dépenses depuis `data/depenses.json`.

Si ce fichier est absent, invalide ou illisible, l’application doit afficher
une erreur claire et arrêter le traitement.

### EF-03 — Valider indépendamment les dépenses

Chaque dépense doit être validée séparément.

Une dépense invalide doit être signalée avec son index et la cause de
l’erreur, puis ignorée. Elle ne doit pas empêcher le traitement des autres
dépenses.

### EF-04 — Calculer le bilan local

À partir des dépenses valides, l’application doit calculer :

- le nombre de dépenses valides ;
- le nombre de dépenses invalides ;
- le montant total ;
- les totaux par catégorie ;
- le budget restant ;
- le pourcentage du budget utilisé ;
- l’état du budget : respecté ou dépassé.

### EF-05 — Récupérer les taux de change

L’application doit récupérer un taux pour chaque devise cible configurée.

Les requêtes correspondant à des devises différentes doivent être
exécutées de manière concurrente.

### EF-06 — Tolérer l’indisponibilité du service externe

L’échec d’une conversion ne doit pas empêcher l’affichage du bilan local.

L’application doit indiquer précisément les devises dont la conversion
est indisponible.

### EF-07 — Afficher le bilan

L’application doit afficher dans le terminal :

- la période analysée ;
- les dépenses retenues ;
- les données rejetées ;
- les totaux par catégorie ;
- la situation du budget ;
- les conversions disponibles.

### EF-08 — Exporter le bilan

L’application doit enregistrer le résultat dans `data/bilan.json`.

Le fichier exporté ne doit contenir que des données validées et
sérialisables en JSON.



## 4. Règles métier

### RG-01 — Montant

Le montant d’une dépense doit être un nombre strictement supérieur à zéro.

### RG-02 — Catégorie

La catégorie doit contenir entre 3 et 50 caractères.

Les espaces placés au début et à la fin doivent être supprimés.
La catégorie doit être normalisée en casse titre.

Exemple :

`"  alimentation  "` devient `"Alimentation"`.

### RG-03 — Description

La description doit contenir entre 1 et 200 caractères après suppression
des espaces inutiles.

### RG-04 — Période

La date d’une dépense doit appartenir à la période définie dans la
configuration.

Une dépense située en dehors de cette période doit être rejetée.

### RG-05 — Budget

Le plafond mensuel doit être strictement supérieur à zéro.

Le budget restant est calculé ainsi :

`budget restant = plafond mensuel - total des dépenses`

Un résultat négatif signifie que le plafond est dépassé.

### RG-06 — Devises

Un code de devise doit comporter exactement trois lettres majuscules.

Exemples valides : `XAF`, `EUR`, `USD`.

Les devises cibles ne doivent pas contenir de doublon et ne doivent pas
contenir la devise source.

### RG-07 — Conversion

Un montant converti est calculé ainsi :

`montant converti = montant source × taux de change`

Le résultat doit être arrondi à deux chiffres après la virgule.## 5. Exigences non fonctionnelles

### ENF-01 — Compatibilité

Le projet doit fonctionner sous Linux avec Python 3.14 ou une version
compatible déclarée dans `pyproject.toml`.

### ENF-02 — Reproductibilité

L’environnement doit pouvoir être recréé avec :

`uv sync --frozen`

Les versions exactes des dépendances doivent être enregistrées dans
`uv.lock`.

### ENF-03 — Fiabilité

Une erreur sur une dépense isolée ou sur une conversion distante ne doit
pas faire perdre les autres résultats valides.

### ENF-04 — Performance réseau

Les appels HTTP indépendants doivent être exécutés de manière concurrente.

Chaque appel doit posséder un délai maximal afin que l’application ne reste
pas bloquée indéfiniment.

### ENF-05 — Lisibilité

Les résultats doivent être présentés clairement dans le terminal avec des
titres, tableaux, couleurs et messages compréhensibles.

### ENF-06 — Typage

Le code applicatif et les tests doivent passer `mypy` en mode strict sans
utiliser abusivement `Any` ou `type: ignore`.

### ENF-07 — Qualité du code

Le projet doit passer :

- `ruff format --check .`
- `ruff check .`

### ENF-08 — Tests

Les règles métier et les traitements d’infrastructure doivent être testés
avec pytest.

Les tests HTTP ne doivent jamais dépendre d’un véritable accès à Internet.

### ENF-09 — Couverture

La couverture du code métier doit atteindre au minimum 95 %.

### ENF-10 — Maintenabilité

Les responsabilités doivent être séparées en modules afin qu’une
modification de l’affichage ne nécessite pas de modifier les calculs métier.


## 5. Exigences non fonctionnelles

### ENF-01 — Compatibilité

Le projet doit fonctionner sous Linux avec Python 3.14 ou une version
compatible déclarée dans `pyproject.toml`.

### ENF-02 — Reproductibilité

L’environnement doit pouvoir être recréé avec :

`uv sync --frozen`

Les versions exactes des dépendances doivent être enregistrées dans
`uv.lock`.

### ENF-03 — Fiabilité

Une erreur sur une dépense isolée ou sur une conversion distante ne doit
pas faire perdre les autres résultats valides.

### ENF-04 — Performance réseau

Les appels HTTP indépendants doivent être exécutés de manière concurrente.

Chaque appel doit posséder un délai maximal afin que l’application ne reste
pas bloquée indéfiniment.

### ENF-05 — Lisibilité

Les résultats doivent être présentés clairement dans le terminal avec des
titres, tableaux, couleurs et messages compréhensibles.

### ENF-06 — Typage

Le code applicatif et les tests doivent passer `mypy` en mode strict sans
utiliser abusivement `Any` ou `type: ignore`.

### ENF-07 — Qualité du code

Le projet doit passer :

- `ruff format --check .`
- `ruff check .`

### ENF-08 — Tests

Les règles métier et les traitements d’infrastructure doivent être testés
avec pytest.

Les tests HTTP ne doivent jamais dépendre d’un véritable accès à Internet.

### ENF-09 — Couverture

La couverture du code métier doit atteindre au minimum 95 %.

### ENF-10 — Maintenabilité

Les responsabilités doivent être séparées en modules afin qu’une
modification de l’affichage ne nécessite pas de modifier les calculs métier.

## 6. Gestion des erreurs

| Situation | Comportement attendu |
|---|---|
| Configuration absente | Message clair et arrêt |
| Configuration JSON invalide | Message précis et arrêt |
| Configuration contraire aux règles | Détails de validation et arrêt |
| Fichier de dépenses absent | Message clair et arrêt |
| JSON des dépenses invalide | Message précis et arrêt |
| Une dépense invalide | Signalement, rejet de cette dépense et poursuite |
| Toutes les dépenses invalides | Bilan local vide avec total égal à zéro |
| Erreur HTTP pour une devise | Conversion concernée indisponible, poursuite |
| Délai HTTP dépassé | Message réseau, poursuite du bilan local |
| Réponse HTTP invalide | Conversion concernée rejetée |
| Échec de l’export | Message clair sans prétendre que le fichier a été créé |

## 7. Critères d’acceptation

Le projet est considéré comme terminé lorsque :

1. la commande `uv run gestion-depenses-pro` démarre l’application ;
2. les quatre dépenses valides produisent un total de 38 500 XAF ;
3. la dépense de montant négatif est rejetée et signalée ;
4. le total de la catégorie Alimentation est égal à 20 000 XAF ;
5. le budget restant est égal à 211 500 XAF ;
6. le budget utilisé est égal à 15,4 % ;
7. les conversions EUR et USD sont demandées concurremment ;
8. une panne réseau n’empêche pas l’affichage du bilan en XAF ;
9. un fichier `data/bilan.json` valide est produit ;
10. tous les tests passent ;
11. Ruff ne signale aucune erreur ;
12. mypy strict ne signale aucune erreur ;
13. la couverture du code métier atteint au moins 95 % ;
14. l’architecture et ses choix peuvent être expliqués.

## 8. Architecture

### 8.1 Principe général

L’application utilise une architecture modulaire dans laquelle chaque
module possède une responsabilité principale.

Le code métier ne doit pas dépendre de l’affichage, du système de fichiers
ou du réseau.

### 8.2 Structure du projet

gestion-depenses-pro/
├── data/
│   ├── configuration.json
│   ├── depenses.json
│   └── bilan.json
├── docs/
│   └── conception.md
├── src/
│   └── gestion_depenses_pro/
│       ├── __init__.py
│       ├── cli.py
│       ├── exceptions.py
│       ├── infrastructure.py
│       ├── modeles.py
│       ├── presentation.py
│       ├── services.py
│       └── py.typed
├── tests/
│   ├── conftest.py
│   ├── test_cli.py
│   ├── test_infrastructure.py
│   ├── test_modeles.py
│   └── test_services.py
├── pyproject.toml
├── README.md
└── uv.lock

### 8.3 Responsabilités

#### `modeles.py`

Ce module définit la forme et les règles de validation des données :

- configuration ;
- dépense ;
- taux de change ;
- résultat de chargement ;
- bilan mensuel ;
- conversion monétaire.

Il ne doit ni lire de fichier, ni effectuer de requête HTTP, ni afficher
dans le terminal.

#### `services.py`

Ce module contient les règles métier pures :

- calcul du total ;
- regroupement par catégorie ;
- calcul du budget restant ;
- calcul du pourcentage utilisé ;
- conversion d’un montant ;
- construction du bilan.

Ses fonctions doivent recevoir des données et retourner des résultats sans
lire de fichier, appeler Internet ou effectuer d’affichage.

#### `infrastructure.py`

Ce module communique avec l’extérieur :

- lecture de la configuration JSON ;
- lecture et validation des dépenses ;
- récupération asynchrone des taux de change ;
- écriture du bilan JSON.

#### `presentation.py`

Ce module transforme les résultats en affichage Rich :

- tableaux ;
- titres ;
- couleurs ;
- avertissements ;
- résumé final.

Il ne doit effectuer aucun calcul métier.

#### `exceptions.py`

Ce module contient les exceptions propres à l’application afin de distinguer
une erreur métier d’une erreur technique brute.

#### `cli.py`

Ce module orchestre le scénario complet :

1. charger la configuration ;
2. charger les dépenses ;
3. calculer le bilan local ;
4. récupérer les taux ;
5. calculer les conversions ;
6. afficher le résultat ;
7. exporter le bilan.

Il délègue le travail aux autres modules au lieu de le réaliser lui-même.

#### `__init__.py`

Ce module expose uniquement le point d’entrée public `main`.

#### `py.typed`

Ce fichier vide indique aux outils externes que le paquet fournit des
informations de typage.

### 8.4 Règles de dépendance

- `modeles.py` ne dépend d’aucun autre module du projet.
- `services.py` peut dépendre de `modeles.py`.
- `infrastructure.py` peut dépendre de `modeles.py` et `exceptions.py`.
- `presentation.py` peut dépendre de `modeles.py`.
- `cli.py` peut utiliser tous les modules nécessaires à l’orchestration.
- aucun autre module ne doit importer `cli.py`.
- `services.py` ne doit jamais importer HTTPX, Rich, JSON ou Path.

### 8.5 Scénario principal

1. L’utilisateur lance `uv run gestion-depenses-pro`.
2. La CLI demande à l’infrastructure de charger la configuration.
3. L’infrastructure charge et valide les dépenses.
4. Les dépenses incorrectes sont séparées des dépenses valides.
5. Les services calculent le bilan en XAF.
6. L’infrastructure récupère concurremment les taux demandés.
7. Les services calculent les conversions disponibles.
8. La présentation affiche le bilan avec Rich.
9. L’infrastructure exporte le bilan dans `data/bilan.json`.
10. La CLI retourne un code de sortie indiquant le succès ou l’échec.

## 9. Modèle des données

### 9.1 Configuration

| Champ | Type conceptuel | Obligatoire | Contraintes |
|---|---|---:|---|
| `periode` | texte | oui | format `AAAA-MM` |
| `plafond_xaf` | nombre décimal | oui | strictement supérieur à zéro |
| `devise_source` | texte | oui | exactement 3 lettres majuscules |
| `devises_cibles` | liste de textes | oui | au moins une devise, sans doublon |

La devise source ne doit pas apparaître dans les devises cibles.

### 9.2 Dépense

| Champ | Type conceptuel | Obligatoire | Contraintes |
|---|---|---:|---|
| `date` | date | oui | doit appartenir à la période analysée |
| `montant` | nombre décimal | oui | strictement supérieur à zéro |
| `categorie` | texte | oui | entre 3 et 50 caractères |
| `description` | texte ou absence | non | entre 1 et 200 caractères si présente |

La catégorie est normalisée après suppression des espaces placés au début
et à la fin.

La description est facultative parce qu’une dépense peut être exploitable
avec sa date, son montant et sa catégorie uniquement.

### RG-03 — Description

La description est facultative.

Lorsqu’elle est fournie, ses espaces extérieurs doivent être supprimés et
elle doit contenir entre 1 et 200 caractères.

### 9.3 Dépense rejetée

| Champ | Type conceptuel | Description |
|---|---|---|
| `index` | entier | position de la dépense dans le tableau JSON |
| `erreurs` | liste de textes | raisons expliquant le rejet |

Exemple conceptuel :

{
  "index": 4,
  "erreurs": [
    "montant : la valeur doit être supérieure à zéro"
  ]
}

### 9.4 Taux de change

| Champ | Type conceptuel | Contraintes |
|---|---|---|
| `date` | date | date fournie par le service |
| `base` | code de devise | trois lettres majuscules |
| `quote` | code de devise | trois lettres majuscules |
| `rate` | nombre décimal | strictement supérieur à zéro |

### 9.5 Conversion réussie

| Champ | Type conceptuel | Description |
|---|---|---|
| `devise` | code de devise | devise cible |
| `taux` | nombre décimal | taux appliqué |
| `montant_converti` | nombre décimal | total converti et arrondi |

### 9.6 Conversion indisponible

| Champ | Type conceptuel | Description |
|---|---|---|
| `devise` | code de devise | conversion demandée |
| `raison` | texte | cause compréhensible de l’échec |


### 9.7 Bilan mensuel

| Champ | Type conceptuel |
|---|---|
| `periode` | texte |
| `devise_source` | code de devise |
| `plafond` | nombre décimal |
| `depenses` | liste des dépenses valides |
| `depenses_rejetees` | liste des rejets |
| `nombre_depenses_valides` | entier |
| `nombre_depenses_rejetees` | entier |
| `total` | nombre décimal |
| `totaux_par_categorie` | dictionnaire catégorie → montant |
| `budget_restant` | nombre décimal |
| `pourcentage_utilise` | nombre décimal |
| `plafond_depasse` | booléen |
| `conversions` | liste des conversions réussies |
| `conversions_indisponibles` | liste des échecs |

### 9.8 Cycle de transformation

Les données suivent les états suivants :

1. texte JSON lu depuis le disque ;
2. données Python brutes ;
3. objets validés ;
4. résultats métier calculés ;
5. bilan présenté dans le terminal ;
6. bilan sérialisé dans un nouveau fichier JSON.

Une donnée brute ne doit jamais être utilisée directement dans un calcul
métier avant validation.
