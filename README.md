🤖 Review Intel AI : Analyseur de Sentiment Intelligent

Transformer le chaos des avis clients en décisions stratégiques.

Review Intel AI est un dashboard interactif qui ingère des données brutes, utilise un LLM (Google Gemini) pour scorer la satisfaction client en temps réel, et automatise le reporting via une interface visuelle.

🎯 Le Problème (Business Case)

Dans le secteur du service, le volume d'avis (Google, TripAdvisor) est massif et non structuré. L'analyse manuelle est impossible à l'échelle, entraînant une perte d'information critique sur la satisfaction client (ex: détection tardive de problèmes récurrents comme "Service lent" ou "Plats froids").

💡 La Solution

Une pipeline Data & IA capable de traiter ces données textuelles instantanément :

Ingestion de fichiers de données brutes (CSV).

Traitement NLP via l'API Google Gemini 2.0 Flash (Analyse de sentiment + Scoring /5).

Restitution via un Dashboard Streamlit interactif pour les managers.

✨ Compétences Clés & Challenges Techniques

Ce projet démontre l'intégration de l'IA dans un flux de production robuste :

🧠 Prompt Engineering Avancé : Configuration stricte du LLM pour obtenir une sortie JSON structurée exploitable par le code (pas de texte libre), garantissant la stabilité du pipeline ETL.

⚡ Optimisation API (Caching) : Utilisation de @st.cache_data pour stocker les résultats d'analyse, réduisant drastiquement la latence et les coûts d'appels API.

🔒 Sécurité : Gestion des secrets via variables d'environnement (.env) pour sécuriser les clés API.

📊 Data Visualization : Création de KPIs dynamiques et graphiques interactifs avec Plotly Express.

🛠️ Stack Technique

Langage : Python

App Framework : Streamlit

Moteur IA : Google Generative AI (Gemini 2.0 Flash)

Data Manipulation : Pandas

Visualisation : Plotly Express

🚀 Installation et Lancement

Cloner le repo

git clone [https://github.com/TON-PSEUDO/review-intel-ai.git](https://github.com/TON-PSEUDO/review-intel-ai.git)
cd review-intel-ai


Installer les dépendances

pip install -r requirements.txt


Configuration (API Key)

Renommez .env.example en .env

Ajoutez votre clé : GOOGLE_API_KEY=votre_clé_ici

Note : Une interface de secours permet de saisir la clé directement dans l'app pour les tests.

Lancer l'application

streamlit run app_avis.py


👤 Shayaan SHAKHUN

Projet réalisé dans le cadre de mon Portfolio Data Analyst / Data Engineer.
Lien vers mon LinkedIn
