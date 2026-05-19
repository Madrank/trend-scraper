import json
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from analysis.analyze import TrendAnalyzer

st.set_page_config(
    page_title="Trend Scraper - Analyse du Marché",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Analyse du Marché de l'Emploi Tech")
st.markdown("Tendances, compétences et clustering des offres d'emploi tech")


@st.cache_data
def load_data():
    analyzer = TrendAnalyzer()
    try:
        df = analyzer.load()
        return analyzer, df
    except FileNotFoundError:
        st.error("Aucune donnée trouvée. Lance d'abord le scraper : `python -m scraper`")
        return None, None


analyzer, df = load_data()

if df is not None and not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Offres totales", len(df))
    with col2:
        st.metric("Entreprises uniques", df["company"].nunique())
    with col3:
        all_skills = df["skills_list"].explode()
        st.metric("Compétences uniques", all_skills.nunique())
    with col4:
        st.metric("Moy. compétences/offre", round(df["skill_count"].mean(), 1))

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🎯 Compétences", "🏢 Sources & Entreprises", "📈 Tendances", "🧠 Clustering"]
    )

    with tab1:
        st.subheader("Top Compétences Demandées")
        top_col, data_col = st.columns([1, 2])

        top_n = top_col.slider("Nombre de compétences", 5, 30, 15)
        skill_freq = analyzer.skill_frequency(top_n)

        fig = px.bar(
            x=skill_freq.values[::-1],
            y=skill_freq.index[::-1],
            orientation="h",
            labels={"x": "Nombre de mentions", "y": ""},
            color=skill_freq.values[::-1],
            color_continuous_scale="viridis",
        )
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        with data_col:
            st.dataframe(
                skill_freq.reset_index().rename(
                    columns={"index": "Compétence", 0: "Mentions"}
                ),
                use_container_width=True,
            )

    with tab2:
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("Offres par Source")
            source_dist = analyzer.source_distribution()
            fig = px.pie(
                values=source_dist.values,
                names=source_dist.index,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.subheader("Top Entreprises")
            company_counts = df["company"].value_counts().head(15)
            fig = px.bar(
                x=company_counts.values,
                y=company_counts.index,
                orientation="h",
                labels={"x": "Offres publiées", "y": ""},
                color=company_counts.values,
                color_continuous_scale="blues",
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Compétences Tendance (Analyse TF-IDF)")
        trending = analyzer.trending_skills(min_mentions=2)
        if not trending.empty:
            fig = px.bar(
                trending.head(20),
                x="relevance_score",
                y="skill",
                orientation="h",
                labels={"relevance_score": "Score de pertinence", "skill": ""},
                color="relevance_score",
                color_continuous_scale="magma",
            )
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas assez de données pour l'analyse des tendances")

        st.subheader("Rapport Synthétique")
        report = analyzer.summary_report()
        st.json(report)

    with tab4:
        st.subheader("Clustering des Offres (K-Means + PCA)")
        clustered = analyzer.cluster_jobs(n_clusters=5)
        if clustered is not None:
            fig = px.scatter(
                clustered,
                x="pca_x",
                y="pca_y",
                color=clustered["cluster"].astype(str),
                hover_data=["title", "company", "skills"],
                labels={"pca_x": "PCA 1", "pca_y": "PCA 2", "color": "Cluster"},
                color_discrete_sequence=px.colors.qualifier.Set1,
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)

            cluster_counts = clustered["cluster"].value_counts().sort_index()
            st.dataframe(
                cluster_counts.reset_index().rename(
                    columns={"index": "Cluster", "cluster": "Nombre d'offres"}
                ),
                use_container_width=True,
            )
        else:
            st.info("Pas assez de données pour le clustering (minimum 5 offres avec compétences)")

    st.divider()
    st.subheader("Données Brutes")
    show_raw = st.checkbox("Afficher les données brutes")
    if show_raw:
        cols_to_show = ["title", "company", "location", "skills", "source"]
        st.dataframe(df[cols_to_show], use_container_width=True)

else:
    st.info("Aucune donnée à afficher. Lance le scraper d'abord.")
