import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px
import json
import os
from dotenv import load_dotenv

# --- 0. CHARGEMENT CONFIG ---
load_dotenv()

# --- 1. CONFIGURATION PAGE & DESIGN ---
st.set_page_config(page_title="Review Intel AI", layout="wide", page_icon="🤖")

# CSS PERSONNALISÉ POUR LE LOOK "DASHBOARD PRO"
st.markdown("""
<style>
    /* Réduire les marges folles de Streamlit */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Fond global légèrement gris */
    .stApp {
        background-color: #f8f9fa;
    }

    /* Style des KPI Cards (Petites cartes du haut) */
    .kpi-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #3B82F6;
        text-align: center;
        margin-bottom: 10px;
    }
    .kpi-title { font-size: 0.9rem; color: #6c757d; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { font-size: 2rem; font-weight: 800; color: #212529; margin: 0.2rem 0; }
    .kpi-delta { font-size: 0.8rem; font-weight: 500; }
    
</style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR (CONFIG & FILTRES) ---
with st.sidebar:
    st.title("🎛️ Contrôles")
    
    # Gestion API Key
    env_key = os.getenv("GOOGLE_API_KEY")
    if env_key:
        api_key = env_key
        st.success("✅ API Key chargée")
    else:
        api_key = st.text_input("Clé API Gemini", type="password")
        if not api_key:
            st.warning("Clé requise")
    
    st.divider()
    
    # Placeholder pour les filtres (rempli après chargement des data)
    filter_container = st.container()

# --- 3. FONCTIONS CORE (DATA & IA) ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('AVIS-CLIENTS.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def analyze_with_gemini(text, key):
    if not key: return "En attente", 0.0
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""
        Analyse l'avis restaurant suivant. Réponds en JSON strict :
        {{ "sentiment": "Positif" | "Négatif" | "Neutre", "score": entier 0 à 5 }}
        Avis : "{text}"
        """
        response = model.generate_content(prompt)
        clean = response.text.replace('```json', '').replace('```', '').strip()
        res = json.loads(clean)
        return res['sentiment'], res['score']
    except: return "Erreur", 0.0

# --- 4. LOGIQUE PRINCIPALE ---
df = load_data()

if df.empty:
    st.error("Fichier de données manquant.")
    st.stop()

# Remplissage des filtres dans la sidebar
with filter_container:
    sources = st.multiselect("Filtrer par Source", df['source'].unique(), default=df['source'].unique())

# Filtrage
filtered_df = df[df['source'].isin(sources)]

# Analyse IA (Batch)
if api_key and not filtered_df.empty:
    # On ne re-calcule que si nécessaire grâce au cache
    results = df['avis'].apply(lambda x: analyze_with_gemini(x, api_key))
    df['Sentiment'] = results.apply(lambda x: x[0])
    df['Note'] = results.apply(lambda x: x[1])
    # On met à jour le dataframe filtré avec les résultats
    filtered_df = df[df['source'].isin(sources)]
else:
    filtered_df['Sentiment'] = "Non analysé"
    filtered_df['Note'] = 0.0


# --- 5. UI DASHBOARD (LA PARTIE VISUELLE) ---

# En-tête Simple
st.title(" ReviewBot AI")
st.caption("Analyse sémantique et scoring automatique des avis clients via Gemini Flash 2.0")

st.write("") # Petit espacement

# Section KPI (Custom HTML Cards)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_avis = len(filtered_df)
nb_positifs = len(filtered_df[filtered_df['Sentiment'] == 'Positif'])
score_moyen = filtered_df['Note'].mean() if api_key else 0
taux_satisfaction = (nb_positifs / total_avis * 100) if total_avis > 0 else 0

# Couleurs dynamiques pour le score
color_score = "#10B981" if score_moyen >= 4 else "#F59E0B" if score_moyen >= 2.5 else "#EF4444"

with kpi1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Volume Avis</div>
        <div class="kpi-value">{total_avis}</div>
        <div class="kpi-delta" style="color: gray">Sur la période</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: {color_score};">
        <div class="kpi-title">Note IA</div>
        <div class="kpi-value" style="color: {color_score}">{score_moyen:.1f}<span style="font-size:1rem">/5</span></div>
        <div class="kpi-delta" style="color: {color_score}">Qualité perçue</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #10B981;">
        <div class="kpi-title">Satisfaction</div>
        <div class="kpi-value">{taux_satisfaction:.0f}%</div>
        <div class="kpi-delta" style="color: #10B981">{nb_positifs} avis positifs</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    top_source = filtered_df['source'].mode()[0] if not filtered_df.empty else "N/A"
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #8B5CF6;">
        <div class="kpi-title">Top Canal</div>
        <div class="kpi-value" style="font-size: 1.5rem; line-height: 2.5rem;">{top_source}</div>
        <div class="kpi-delta" style="color: #8B5CF6">Source principale</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Section Principale : Graphique + Tableau (Split 1/3 - 2/3)
col_charts, col_table = st.columns([1, 2])

with col_charts:
    st.subheader("📊 Répartition")
    if not filtered_df.empty:
        color_map = {'Positif': '#10B981', 'Négatif': '#EF4444', 'Neutre': '#3B82F6', 'Non analysé': '#E5E7EB'}
        fig = px.pie(filtered_df, names='Sentiment', hole=0.6, color='Sentiment', color_discrete_map=color_map)
        fig.update_layout(
            showlegend=True, 
            margin=dict(t=0, b=0, l=0, r=0), 
            height=250,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Pas de données")

with col_table:
    st.subheader("📝 Analyse Détaillée")
    st.dataframe(
        filtered_df[['date', 'source', 'avis', 'Sentiment', 'Note']].sort_values(by='date', ascending=False),
        use_container_width=True,
        height=400, # Hauteur fixe pour éviter un tableau infini qui casse le design
        hide_index=True,
        column_config={
            "date": st.column_config.DateColumn("Date", format="DD/MM", width="small"),
            "source": st.column_config.TextColumn("Canal", width="small"),
            "avis": st.column_config.TextColumn("Verbatim Client", width="large"),
            "Sentiment": st.column_config.TextColumn("IA", width="small"),
            "Note": st.column_config.ProgressColumn(
                "Note / 5",
                format="%d",
                min_value=0,
                max_value=5,
                width="small"
            ),
        }
    )

# Section Sandbox (Test en direct) - Optionnel, en bas
with st.expander("🧪 Tester l'IA avec une phrase personnalisée (Sandbox)", expanded=False):
    c_in, c_out = st.columns([3, 1])
    txt = c_in.text_input("Entrez un avis fictif :", placeholder="Le service était lent mais le plat délicieux...")
    if txt and api_key:
        s, n = analyze_with_gemini(txt, api_key)
        if s == "Positif": c_out.success(f"**{s}** ({n}/5)")
        elif s == "Négatif": c_out.error(f"**{s}** ({n}/5)")
        else: c_out.info(f"**{s}** ({n}/5)")