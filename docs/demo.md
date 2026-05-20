# Démo Trend Scraper

## 1. Scraper les offres d'emploi

```bash
python -m scraper
```

Résultat attendu :
```
Scraping des offres d'emploi...
18 offres trouvées
Sauvegardé dans data\jobs.json
Sauvegardé dans data\jobs.csv
```

## 2. API REST (FastAPI)

```bash
uvicorn api.main:app --reload --port 8000
# http://localhost:8000
# Documentation interactive : http://localhost:8000/docs
```

Tester les endpoints :

```bash
# Status
curl http://localhost:8000/health
# → {"status":"sain","timestamp":"2026-05-19T..."}

# Lister les offres (page 1, 5 résultats)
curl "http://localhost:8000/jobs?page=1&limit=5"
# → {"page":1,"limit":5,"total":18,"jobs":[...]}

# Filtrer par compétence
curl "http://localhost:8000/jobs?skill=Python"

# Statistiques agrégées
curl http://localhost:8000/jobs/stats
# → {"total_jobs":18,"sources":{"remotive":18},"top_skills":[...]}

# Recherche plein texte
curl "http://localhost:8000/jobs/search?q=developer"

# Lister les sources disponibles
curl http://localhost:8000/jobs/sources
# → {"sources":["remotive"]}
```

## 3. Analyse ML

```python
from analysis.analyze import TrendAnalyzer

analyzer = TrendAnalyzer()
df = analyzer.load()

# Top compétences
print(analyzer.skill_frequency(10))

# Distribution des sources
print(analyzer.source_distribution())

# Compétences tendances (TF-IDF)
print(analyzer.trending_skills())

# Clustering K-Means (groupes d'offres similaires)
clusters = analyzer.cluster_jobs(n_clusters=5)

# Rapport synthétique
print(analyzer.summary_report())
```

## 4. Dashboard Streamlit

```bash
streamlit run dashboard/app.py
# http://localhost:8501
```

Le dashboard propose 4 onglets :

| Onglet | Contenu |
|--------|---------|
| 🎯 Compétences | Top compétences demandées (bar chart + tableau) |
| 🏢 Sources & Entreprises | Répartition par source + top entreprises |
| 📈 Tendances | Analyse TF-IDF des compétences + rapport |
| 🧠 Clustering | Visualisation 2D des clusters K-Means |

## 5. Tests

```bash
pytest tests/ -v --cov
# 8 passed
```

## End-to-end (tout en un)

```bash
# 1. Scraper
python -m scraper

# 2. API (nouveau terminal)
uvicorn api.main:app --port 8000

# 3. Dashboard (nouveau terminal)
streamlit run dashboard/app.py

# 4. Tester
curl http://localhost:8000/jobs/stats
# → Ouvrir http://localhost:8501 pour le dashboard
```
