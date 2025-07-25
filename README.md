## Avertissement (Disclaimer)

Ce dépôt est fourni **à des fins exclusivement pédagogiques** dans le cadre de mon apprentissage en data engineering.  
**Aucune donnée scrappée n’est publiée dans ce dépôt** (ni brute, ni agrégée).

- Je ne suis affilié à aucune des boutiques ou sites mentionnés.
- Les scripts ont été écrits pour démontrer des compétences techniques (requests, parsing, orchestration, stockage, etc.).
- Toute personne qui utiliserait ces scripts est **seule responsable** du respect :
  - des **Conditions Générales d’Utilisation (CGU)** et mentions légales des sites ciblés ;
  - des fichiers **robots.txt** ;
  - du **RGPD** et, plus largement, des lois applicables en matière de protection des données personnelles ;
  - du **droit sui generis des bases de données** (Code de la propriété intellectuelle, art. L341-1 s.) et de toute autre règle relative à l’extraction/réutilisation de données.
- Ces scripts **ne doivent pas être utilisés** pour contourner des mesures techniques de protection, des paywalls, ni pour réaliser une extraction substantielle ou réutilisation non autorisée de bases de données.
- Sur simple demande documentée d’un ayant droit, je m’engage à **retirer ou modifier** tout contenu problématique.

**Contact retrait / takedown** : ouvrir une *issue* sur ce dépôt ou me contacter à `<almassati.sanae@gmail.com>`.

### Politique de retrait

Si vous estimez que ce dépôt porte atteinte à vos droits (ex. violation de CGU, extraction substantielle de base de données, atteinte à la vie privée), merci de :

1. Décrire précisément le contenu en cause (fichiers, lignes, commit).
2. Indiquer la base légale ou contractuelle invoquée.
3. Proposer la mesure attendue (suppression, modification, ajout de mention).

J’examinerai la demande de bonne foi et procéderai rapidement aux ajustements nécessaires.


# Scraping GammVert

Ce projet est un scraper basé sur **Scrapy** permettant d'extraire :

* Les **catégories** du site gammvert.fr (structure hiérarchique, URL, identifiants)
* Les **produits** listés dans les pages de catégorie (nom, prix, URL...)

## Fonctionnalités principales

* Exploration récursive des catégories à partir de la page d'accueil
* Gestion des sous-catégories et détection des pages produits
* Extraction paginée des produits
* Nettoyage, validation, dédoublonnage des données
* Export au format CSV
* Import des catégories dans une base SQLite

## Structure du projet

```
gammvertscraper/
├── spiders/
│   ├── categoryspider.py           # Exploration récursive des catégories
│   ├── product_list_spider.py      # Scraping des listes de produits
│   ├── product_detail_spider.py    # (optionnel) Pour les détails produits
│   └── __init__.py
├── items.py                        # Modèles de données Scrapy (items)
├── pipelines.py                    # Nettoyage, validation, export CSV
├── middlewares.py                  # (vide ou personnalisé)
├── settings.py                     # Configuration Scrapy
import_categories.py                # Script d'import des catégories en SQLite
scrapy.cfg                          # Point d'entrée pour Scrapy
```

## Installation

1. **Cloner le dépôt**

```bash
git clone https://github.com/Sanae599/Scraping.git
cd Scraping
```

2. **Créer un environnement virtuel**

```bash
python3 -m venv .venv
source .venv/bin/activate  
```

3. **Installer les dépendances**

```bash
pip install scrapy
```

## Utilisation

### 1. Extraire les catégories

```bash
scrapy crawl categoryspider.py -O categories.csv
```

Ce spider explore récursivement toutes les catégories du site, en générant un fichier `categories.csv`.

### 2. Importer les catégories dans SQLite (optionnel)

```bash
python import_categories.py
```

Cela crée (ou recrée) une base de données `gammvert.db` avec une table `categories`.

### 3. Extraire les produits

```bash
scrapy crawl product_list_spider.py -O products.csv
```

Ce spider utilise le fichier `categories.csv` pour lancer le scraping des pages produits et enregistre les résultats dans `products.csv`.

## Format des fichiers CSV

### `categories.csv`

| name | url | category\_id | parent\_id | is\_pagelist |
| ---- | --- | ------------ | ---------- | ------------ |

### `products.csv`

| url | page\_number | name | price |
| --- | ------------ | ---- | ----- |

## Personnalisation

* Le comportement des spiders peut être ajusté via les variables `custom_settings`.
* Des pipelines Scrapy sont définis pour nettoyer les champs texte, valider les données, convertir les prix, et gérer les fichiers CSV (`pipelines.py`).

## À propos

Ce projet a été conçu pour extraire de manière structurée des données publiques disponibles sur le site gammvert.fr, à des fins d'analyse ou d'apprentissage du scraping avancé avec Scrapy.

## Crédits
Ce projet a été réalisé dans le cadre d'un travail en groupe avec les contributeurs suivants :

    @smuller59
    
    @AniceGit

    @Sanae599

Merci à chacun pour leur implication dans ce projet.
