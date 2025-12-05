🤖 Review Intel AI : Analyseur de Sentiment Intelligent

Transformer le chaos des avis clients en décisions stratégiques.
Un dashboard interactif qui ingère des données brutes, utilise un LLM pour scorer la satisfaction client en temps réel, et automatise le reporting.

🎯 Le Problème (Business Case)

Dans le secteur du service, le volume d'avis (Google, TripAdvisor) est massif et non structuré. L'analyse manuelle est impossible à l'échelle, entraînant une perte d'information critique sur la satisfaction client ("Service lent", "Plats froids").

💡 La Solution

J'ai développé une pipeline Data & IA capable de traiter ces données textuelles instantanément :

Ingestion de fichiers de données brutes (CSV/Excel).

Traitement NLP via l'API Google Gemini 2.0 Flash (Analyse de sentiment + Scoring /5).

Restitution via un Dashboard Streamlit interactif pour les managers.

✨ Compétences Clés "Data Engineer"

Ce projet démontre ma capacité à intégrer l'IA dans un flux de production :

🧠 Prompt Engineering Avancé : Configuration stricte du LLM pour obtenir une sortie JSON structurée exploitable par le code (pas de texte libre), garantissant la stabilité du pipeline.

⚡ Optimisation API (Caching) : Utilisation de @st.cache_data pour stocker les résultats d'analyse et réduire la latence et les coûts d'appels API.

🔒 Gestion de la Sécurité : Implémentation des variables d'environnement (.env) pour sécuriser les clés API, avec un fallback UI pour la démonstration.

📊 Data Visualization : Création de KPIs dynamiques et de graphiques interactifs avec Plotly Express.

🛠️ Stack Technique

Langage : Python

Framework Data App : Streamlit

Moteur IA : Google Generative AI (Gemini 2.0 Flash)

Manipulation de Données : Pandas

Visualisation : Plotly

🚀 Comment lancer le projet ?

# 1. Cloner le repo
git clone [https://github.com/TON-PSEUDO/review-intel-ai.git](https://github.com/TON-PSEUDO/review-intel-ai.git)
cd review-intel-ai

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer l'API (Optionnel - Sinon via l'interface)
# Renommez .env.example en .env et ajoutez votre GOOGLE_API_KEY

# 4. Lancer l'application
streamlit run app_avis.py


Projet réalisé dans le cadre de mon Portfolio Data Analyst / Engineer.
