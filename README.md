# Trend Scraper — Analyse du Marché de l'Emploi Tech

Pipeline de données complet : scraper → API → analyser → visualiser. Scrape les offres d'emploi tech et extrait les tendances du marché grâce au Machine Learning.

## Architecture

```
┌────────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐
│  Scraper   │───▶│  FastAPI  │───▶│  Analyse  │───▶│Dashboard │
│ (httpx +   │    │  REST API │    │ pandas +  │    │ Streamlit│
│  BS4)      │    │  :8000    │    │ sklearn   │    │ :8501    │
└────────────┘    └──────────┘    └───────────┘    └──────────┘
       │                                                │
       └────────────────── Données ─────────────────────┘
                            (JSON)
```

## Stack

| Couche | Technologie |
|--------|-------------|
| Scraping | Python / httpx / BeautifulSoup |
| API | FastAPI |
| Analyse | Pandas / NumPy / scikit-learn (TF-IDF, K-Means, PCA) |
| Dashboard | Streamlit / Plotly |
| Tests | pytest |

## Démarrage rapide

```bash
# Installation
pip install -r requirements.txt

# Lancer le scraper
python -m scraper

# Démarrer l'API
uvicorn api.main:app --reload --port 8000

# Démarrer le dashboard
streamlit run dashboard/app.py

# Lancer les tests
pytest tests/ -v --cov
```

## Fonctionnalités

### Scraper
- Scraping multi-sources (Remotive, Indeed)
- Extraction automatique des compétences depuis les descriptions
- Export CSV et JSON
- Gestion des erreurs et limitation de débit

### API (`/api/docs`)
- `GET /jobs` — liste paginée avec filtres par compétence et source
- `GET /jobs/stats` — métriques agrégées (top compétences, sources, mots-clés)
- `GET /jobs/search` — recherche plein texte (titre, entreprise, compétences)
- `GET /jobs/sources` — liste des sources de données disponibles

### Analyse
- **Fréquence des compétences** — les compétences les plus demandées
- **Tendances TF-IDF** — classement pondéré par pertinence
- **Clustering K-Means** — catégories d'emplois visualisées via PCA
- **Rapport synthétique** — statistiques globales du marché

### Dashboard
- Cartes de métriques clés (offres totales, compétences uniques, etc.)
- Graphiques à barres interactifs des compétences les plus demandées
- Diagramme circulaire de répartition des sources
- Analyse des tendances TF-IDF
- Visualisation 2D du clustering des offres
- Explorateur de données brutes

## Structure du projet

```
.
├── scraper/           # Module de scraping web
│   ├── spider.py     # Classe TrendScraper
│   └── __init__.py
├── api/               # API REST FastAPI
│   ├── main.py       # Endpoints
│   └── __init__.py
├── analysis/          # Analyse de données & ML
│   ├── analyze.py    # Classe TrendAnalyzer
│   └── __init__.py
├── dashboard/         # Dashboard Streamlit
│   └── app.py
├── data/              # Données scrapées (JSON/CSV)
│   └── .gitkeep
├── notebooks/         # Exploration Jupyter
├── tests/             # Tests unitaires
├── requirements.txt   # Dépendances
└── README.md
```
