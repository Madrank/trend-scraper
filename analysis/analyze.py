import json
from pathlib import Path
from collections import Counter
from typing import Optional

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


class TrendAnalyzer:
    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or Path(__file__).resolve().parent.parent / "data" / "jobs.json"
        self.df: Optional[pd.DataFrame] = None

    def load(self) -> pd.DataFrame:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Fichier de données introuvable : {self.data_path}")
        with open(self.data_path, encoding="utf-8") as f:
            data = json.load(f)
        self.df = pd.DataFrame(data)
        if self.df.empty:
            return self.df
        self.df["skills_list"] = self.df["skills"].apply(
            lambda x: x if isinstance(x, list) else []
        )
        self.df["skill_count"] = self.df["skills_list"].apply(len)
        return self.df

    def skill_frequency(self, top_n: int = 20) -> pd.Series:
        if self.df is None or self.df.empty:
            return pd.Series(dtype=int)
        all_skills = [s.lower() for skills in self.df["skills_list"] for s in skills]
        return pd.Series(Counter(all_skills)).sort_values(ascending=False).head(top_n)

    def source_distribution(self) -> pd.Series:
        if self.df is None or self.df.empty:
            return pd.Series(dtype=int)
        return self.df["source"].value_counts()

    def trending_skills(self, min_mentions: int = 2) -> pd.DataFrame:
        if self.df is None or self.df.empty:
            return pd.DataFrame()
        tfidf = TfidfVectorizer(
            analyzer="word",
            tokenizer=lambda x: x,
            preprocessor=lambda x: x,
            max_features=100,
        )
        skill_texts = self.df["skills_list"].apply(lambda x: " ".join(x).lower() if x else "")
        non_empty = skill_texts[skill_texts.str.strip() != ""]
        if len(non_empty) < 2:
            return pd.DataFrame()

        matrix = tfidf.fit_transform(non_empty)
        feature_names = tfidf.get_feature_names_out()
        scores = np.array(matrix.sum(axis=0)).flatten()
        top_indices = scores.argsort()[::-1]
        result = []
        for idx in top_indices:
            if scores[idx] >= min_mentions:
                result.append({"skill": feature_names[idx], "relevance_score": round(scores[idx], 2)})
        return pd.DataFrame(result)

    def cluster_jobs(self, n_clusters: int = 5) -> Optional[pd.DataFrame]:
        if self.df is None or self.df.empty:
            return None
        skill_texts = self.df["skills_list"].apply(lambda x: " ".join(x).lower() if x else "")
        non_empty_idx = skill_texts[skill_texts.str.strip() != ""].index
        non_empty = skill_texts.loc[non_empty_idx]
        if len(non_empty) < n_clusters:
            return None

        tfidf = TfidfVectorizer(analyzer="word", tokenizer=lambda x: x, preprocessor=lambda x: x)
        matrix = tfidf.fit_transform(non_empty)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(matrix)

        result = self.df.loc[non_empty_idx].copy()
        result["cluster"] = labels

        pca = PCA(n_components=2, random_state=42)
        coords = pca.fit_transform(matrix.toarray())
        result["pca_x"] = coords[:, 0]
        result["pca_y"] = coords[:, 1]

        return result

    def summary_report(self) -> dict:
        if self.df is None or self.df.empty:
            return {"error": "Aucune donnée chargée"}
        return {
            "total_jobs": len(self.df),
            "unique_companies": self.df["company"].nunique(),
            "unique_skills": self.df["skills_list"].explode().nunique(),
            "avg_skills_per_job": round(self.df["skill_count"].mean(), 2),
            "top_skills": self.skill_frequency(10).to_dict(),
            "sources": self.source_distribution().to_dict(),
        }
