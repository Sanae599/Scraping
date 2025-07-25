Avertissement (Disclaimer)
Ce dépôt est fourni à des fins exclusivement pédagogiques dans le cadre de mon apprentissage en data engineering.
Aucune donnée scrappée n’est publiée dans ce dépôt (ni brute, ni agrégée).

Je ne suis affilié à aucune des boutiques ou sites mentionnés.
Les scripts ont été écrits pour démontrer des compétences techniques (requests, parsing, orchestration, stockage, etc.).
Toute personne qui utiliserait ces scripts est seule responsable du respect :
des Conditions Générales d’Utilisation (CGU) et mentions légales des sites ciblés ;
des fichiers robots.txt ;
du RGPD et, plus largement, des lois applicables en matière de protection des données personnelles ;
du droit sui generis des bases de données (Code de la propriété intellectuelle, art. L341-1 s.) et de toute autre règle relative à l’extraction/réutilisation de données.
Ces scripts ne doivent pas être utilisés pour contourner des mesures techniques de protection, des paywalls, ni pour réaliser une extraction substantielle ou réutilisation non autorisée de bases de données.
Sur simple demande documentée d’un ayant droit, je m’engage à retirer ou modifier tout contenu problématique.

Contact retrait / takedown : ouvrir une issue sur ce dépôt ou me contacter à <ton.email@exemple.com>.
Politique de retrait
Si vous estimez que ce dépôt porte atteinte à vos droits (ex. violation de CGU, extraction substantielle de base de données, atteinte à la vie privée), merci de :

Décrire précisément le contenu en cause (fichiers, lignes, commit).
Indiquer la base légale ou contractuelle invoquée.
Proposer la mesure attendue (suppression, modification, ajout de mention).

J’examinerai la demande de bonne foi et procéderai rapidement aux ajustements nécessaires.

# 🪴 GammvertScraper

Un projet Scrapy complet pour crawler les **catégories** et **produits** du site [gammvert.fr](https://www.gammvert.fr), avec stockage CSV et base SQLite.

## 📦 Fonctionnalités

- 🔁 **Exploration récursive** des catégories du site via `RecursiveCategoriesSpider`
- 🛍️ **Extraction de listes de produits** paginées avec `ProductListSpider`
- 🧹 Nettoyage, validation, déduplication via des **pipelines personnalisés**
- 📄 Export des données vers **CSV**
- 🗃️ Chargement des catégories dans une **base SQLite**

---

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/ton-utilisateur/gammvertscraper.git
cd gammvertscraper
2. Créer un environnement virtuel
bash
Copier
Modifier
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
3. Installer les dépendances
bash
Copier
Modifier
pip install -r requirements.txt
Exemple de requirements.txt :

txt
Copier
Modifier
Scrapy>=2.10.0
🕷️ Spiders disponibles
1. recursive_categories
Explore toutes les catégories du site (hors /c/destockage) et génère un fichier categories.csv.

bash
Copier
Modifier
scrapy crawl recursive_categories
📥 Résultat : un fichier CSV categories.csv contenant :

name	url	category_id	parent_id	is_pagelist
jardinage	/c/jardinage	jardinage_...	NULL	1

2. ProductListSpider
Charge les catégories depuis categories.csv, identifie les pages paginées, et extrait les produits listés.

bash
Copier
Modifier
scrapy crawl ProductListSpider
📥 Résultat : un fichier CSV products.csv contenant :

url	page_number	name	price
/produit1	1	engrais bio	12.90

🛠️ Pipelines
Les pipelines Scrapy intégrés :

CleanCategoriesPipeline : Nettoyage des noms, suppression de caractères spéciaux

ValidateCategoriesPipeline : Vérifie les champs requis

DedupeCategoriesPipeline : Supprime les doublons

CsvCategoriesPipeline : Sauvegarde dans categories.csv

Et côté produits :

CleanProductsPipeline

ConvertPricePipeline : Convertit les prix (str) en Decimal

CsvProductsPipeline : Sauvegarde dans products.csv

💡 Les pipelines sont activés dans settings.py.

🧱 Chargement en base SQLite
Utilise le script suivant pour importer les catégories dans une base SQLite :

bash
Copier
Modifier
python scripts/load_categories_sqlite.py
📁 Cela crée un fichier gammvert.db avec une table categories.

📁 Structure du projet
markdown
Copier
Modifier
gammvertscraper/
│
├── spiders/
│   ├── recursive_categories.py
│   └── product_list.py
│
├── pipelines.py
├── items.py
├── settings.py
│
├── categories.csv
├── products.csv
├── gammvert.db
└── scripts/
    └── load_categories_sqlite.py
🧪 Exemple de flux
bash
Copier
Modifier
# 1. Crawler les catégories
scrapy crawl recursive_categories

# 2. Charger les catégories en base
python scripts/load_categories_sqlite.py

# 3. Crawler les produits
scrapy crawl ProductListSpider
📋 À faire
 Crawler les pages produit détaillées

 Extraire les images et les descriptions complètes

 Améliorer la détection des prix réduits

 Intégrer PostgreSQL ou MongoDB pour stockage avancé

🛡️ Avertissement
Ce projet est à usage éducatif. Respecte toujours les conditions d'utilisation du site cible. N'effectue pas de scraping agressif.

🧑‍💻 Auteur
Projet développé par Anice Sanae Stéphane