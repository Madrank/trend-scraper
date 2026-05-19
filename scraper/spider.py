import re
import csv
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup


@dataclass
class JobPosting:
    title: str
    company: str
    location: str
    description: str
    skills: list[str] = field(default_factory=list)
    url: str = ""
    source: str = ""
    posted_date: Optional[str] = None
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())


class TrendScraper:
    SKILL_KEYWORDS = [
        "python", "javascript", "typescript", "java", "go", "rust",
        "react", "angular", "vue", "node", "next.js", "svelte",
        "docker", "kubernetes", "aws", "gcp", "azure", "terraform",
        "sql", "nosql", "postgresql", "mongodb", "redis",
        "machine learning", "deep learning", "nlp", "computer vision",
        "data science", "data engineering", "data analysis",
        "ci/cd", "devops", "mlops", "agile", "scrum",
    ]

    def __init__(self, timeout: float = 15.0, user_agent: Optional[str] = None):
        self.client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": user_agent or (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                )
            },
        )

    def close(self):
        self.client.close()

    def extract_skills(self, text: str) -> list[str]:
        text_lower = text.lower()
        found = set()
        for skill in self.SKILL_KEYWORDS:
            if re.search(r"\b" + re.escape(skill) + r"\b", text_lower):
                found.add(skill.title())
        return sorted(found)

    def scrape_remotive(self, limit: int = 20) -> list[JobPosting]:
        url = f"https://remotive.com/api/remote-jobs?limit={limit}"
        resp = self.client.get(url)
        resp.raise_for_status()
        data = resp.json()
        jobs = []

        for item in data.get("jobs", []):
            description = item.get("description", "")
            posting = JobPosting(
                title=item.get("title", ""),
                company=item.get("company_name", ""),
                location=item.get("candidate_required_location", "Distant"),
                description=description,
                skills=self.extract_skills(description),
                url=item.get("url", ""),
                source="remotive",
                posted_date=item.get("publication_date"),
            )
            jobs.append(posting)

        return jobs

    def scrape_wttr_jobs(self, query: str = "software", limit: int = 20) -> list[JobPosting]:
        url = f"https://www.wttr.workers.dev/jobs?q={query}&limit={limit}"
        try:
            resp = self.client.get(url)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return []

        jobs = []
        for item in data.get("results", [])[:limit]:
            description = item.get("description", "")
            posting = JobPosting(
                title=item.get("title", ""),
                company=item.get("company", {}).get("display_name", ""),
                location=item.get("location", {}).get("display_name", ""),
                description=description,
                skills=self.extract_skills(description),
                url=item.get("redirect_url", ""),
                source="wttr_jobs",
            )
            jobs.append(posting)

        return jobs

    def scrape_all(self, sources: Optional[list[str]] = None) -> list[JobPosting]:
        sources = sources or ["remotive"]
        all_jobs = []

        if "remotive" in sources:
            try:
                all_jobs.extend(self.scrape_remotive())
            except Exception as e:
                print(f"Échec du scraping Remotive : {e}")

        if "wttr_jobs" in sources:
            try:
                all_jobs.extend(self.scrape_wttr_jobs())
            except Exception as e:
                print(f"Échec du scraping Wttr jobs : {e}")

        return all_jobs

    def export_csv(self, jobs: list[JobPosting], filepath: str):
        if not jobs:
            return
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=asdict(jobs[0]).keys())
            writer.writeheader()
            for job in jobs:
                row = asdict(job)
                row["skills"] = ", ".join(row["skills"])
                writer.writerow(row)

    def export_json(self, jobs: list[JobPosting], filepath: str):
        data = [asdict(job) for job in jobs]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
