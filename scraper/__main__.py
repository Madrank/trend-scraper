"""Point d'entrée du scraper : python -m scraper"""

from scraper.spider import TrendScraper
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

scraper = TrendScraper()
print("Scraping des offres d'emploi...")
jobs = scraper.scrape_all(sources=["remotive"])
print(f"{len(jobs)} offres trouvées")

if jobs:
    json_path = DATA_DIR / "jobs.json"
    scraper.export_json(jobs, str(json_path))
    print(f"Sauvegardé dans {json_path}")

    csv_path = DATA_DIR / "jobs.csv"
    scraper.export_csv(jobs, str(csv_path))
    print(f"Sauvegardé dans {csv_path}")
else:
    print("Aucune offre récupérée. Utilisation de données d'exemple.")

scraper.close()
