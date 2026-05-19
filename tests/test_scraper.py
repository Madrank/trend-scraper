import pytest
from scraper.spider import TrendScraper, JobPosting


class TestJobPosting:
    def test_default_scraped_at(self):
        job = JobPosting(title="Dev", company="Co", location="Remote", description="")
        assert job.scraped_at is not None
        assert job.skills == []
        assert job.source == ""

    def test_asdict_includes_all_fields(self):
        job = JobPosting(
            title="Engineer",
            company="ACME",
            location="Paris",
            description="Python developer",
            skills=["Python"],
            url="https://example.com",
            source="test",
        )
        d = job.__dict__
        assert d["title"] == "Engineer"
        assert d["company"] == "ACME"
        assert d["skills"] == ["Python"]


class TestTrendScraper:
    def setup_method(self):
        self.scraper = TrendScraper()

    def teardown_method(self):
        self.scraper.close()

    def test_extract_skills_finds_matching(self):
        text = "We need a Python developer with Docker and AWS experience"
        skills = self.scraper.extract_skills(text)
        assert "Python" in skills
        assert "Docker" in skills
        assert "Aws" in skills

    def test_extract_skills_empty(self):
        assert self.scraper.extract_skills("") == []

    def test_extract_skills_no_match(self):
        assert self.scraper.extract_skills("We are hiring a barista") == []

    def test_extract_skills_case_insensitive(self):
        text = "We use PYTHON and docker and Aws"
        skills = self.scraper.extract_skills(text)
        assert "Python" in skills
        assert "Docker" in skills
        assert "Aws" in skills

    def test_extract_skills_multi_word(self):
        text = "Looking for machine learning and data science experts"
        skills = self.scraper.extract_skills(text)
        assert "Machine Learning" in skills
        assert "Data Science" in skills

    def test_extract_skills_no_partial_match(self):
        text = "We need a rust developer"
        skills = self.scraper.extract_skills(text)
        assert "Rust" in skills
        assert "Crust" not in [s.lower() for s in skills]
