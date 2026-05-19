import os
import json
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API Trend Scraper",
    description="API pour les données de tendances du marché de l'emploi tech",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_jobs() -> list[dict]:
    json_path = DATA_DIR / "jobs.json"
    if not json_path.exists():
        return []
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


@app.get("/")
def root():
    return {
        "name": "API Trend Scraper",
        "version": "1.0.0",
        "endpoints": {
            "/jobs": "Liste toutes les offres scrapées (pagination et filtres)",
            "/jobs/stats": "Statistiques agrégées (compétences, sources, etc.)",
            "/jobs/search": "Recherche d'offres par mot-clé",
            "/health": "Vérification de l'état de l'API",
        },
    }


@app.get("/health")
def health():
    return {"status": "sain", "timestamp": datetime.now().isoformat()}


@app.get("/jobs")
def list_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    source: str = Query(None),
    skill: str = Query(None),
    sort_by: str = Query("scraped_at"),
):
    jobs = load_jobs()
    if not jobs:
        return {"page": page, "limit": limit, "total": 0, "jobs": []}

    if source:
        jobs = [j for j in jobs if j.get("source") == source]
    if skill:
        jobs = [j for j in jobs if any(skill.lower() in s.lower() for s in j.get("skills", []))]

    jobs.sort(key=lambda j: j.get(sort_by, ""), reverse=True)

    total = len(jobs)
    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "jobs": jobs[start:end],
    }


@app.get("/jobs/stats")
def job_stats():
    jobs = load_jobs()
    if not jobs:
        return {"total_jobs": 0}

    skill_counts = {}
    source_counts = {}
    title_keywords = {}

    for job in jobs:
        source_counts[job.get("source", "inconnu")] = source_counts.get(job.get("source", "inconnu"), 0) + 1
        for skill in job.get("skills", []):
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        words = job.get("title", "").lower().split()
        for w in words:
            if len(w) > 3:
                title_keywords[w] = title_keywords.get(w, 0) + 1

    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    top_titles = sorted(title_keywords.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total_jobs": len(jobs),
        "sources": source_counts,
        "top_skills": [{"skill": s, "count": c} for s, c in top_skills],
        "top_title_keywords": [{"keyword": k, "count": c} for k, c in top_titles],
    }


@app.get("/jobs/search")
def search_jobs(q: str = Query(..., min_length=2)):
    jobs = load_jobs()
    if not jobs:
        return {"results": []}

    q_lower = q.lower()
    results = []
    for job in jobs:
        if (
            q_lower in job.get("title", "").lower()
            or q_lower in job.get("company", "").lower()
            or q_lower in job.get("description", "").lower()
            or any(q_lower in s.lower() for s in job.get("skills", []))
        ):
            results.append(job)
    return {"query": q, "results": results}


@app.get("/jobs/sources")
def list_sources():
    jobs = load_jobs()
    sources = set(j.get("source", "inconnu") for j in jobs)
    return {"sources": sorted(sources)}
