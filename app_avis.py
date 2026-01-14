import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px
import json
import os
import time
from dotenv import load_dotenv

# --- 0. CHARGEMENT CONFIG ---
load_dotenv()

# --- 1. CONFIGURATION PAGE & DESIGN ---
st.set_page_config(page_title="Review Intel AI", layout="wide", page_icon="🤖")

st.markdown("""
<style>
    /* Compactage des marges pour tout faire tenir sur un écran */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; padding-left: 1rem; padding-right: 1rem; }
    .stApp { background-color: #f8f9fa; }
    
    /* Design des cartes KPI */
    .kpi-card {
        background-color: white; padding: 0.8rem; border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 4px solid #3B82F6;
        text-align: center; margin-bottom: 5px;
    }
    .kpi-title { font-size: 0.8rem; color: #6c757d; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-size: 1.8rem; font-weight: 800; color: #212529; margin: 0; }
    .kpi-delta { font-size: 0.7rem; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# --- 2. FONCTIONS CORE ---
@st.cache_data
def load_data():
    try:
        if not os.path.exists('AVIS-CLIENTS.csv'):
            st.warning("Mode Démo : Fichier CSV introuvable.")
            data = {
                'date': ['01/10/2023', '02/10/2023', '03/10/2023', '04/10/2023'],
                'source': ['Google', 'TripAdvisor', 'Google', 'Yelp'],
                'avis': ["Excellent !", "Horrible attente.", "Moyen.", "Top !"]
            }
            return pd.DataFrame(data)
        
        df = pd.read_csv('AVIS-CLIENTS.csv')
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], dayfirst=True)
        return df
    except Exception as e:
        st.error(f"Erreur chargement data: {e}")
        return pd.DataFrame()

def analyze_with_gemini_robust(text, key):
    """Fonction optimisée pour éviter les erreurs 429 et 404"""
    if not key: return "En attente", 0.0
    
    # Configuration - Utilisation de l'alias générique 'gemini-pro' pour éviter les 404
    genai.configure(api_key=key, transport='rest')
    model = genai.GenerativeModel('gemini-2.5-flash-lite')  # Utilisation d'un modèle stable
    
    prompt = f"""
    Analyse cet avis client.
    Réponds UNIQUEMENT avec ce format JSON strict, sans texte autour, sans markdown :
    {{ "sentiment": "Positif" | "Négatif" | "Neutre", "score": entier 0 à 5 }}
    
    Avis : "{text}"
    """
    
    max_retries = 3
    base_delay = 5
    
    for attempt in range(max_retries):
        try:
            time.sleep(1) # Pause de sécurité
            response = model.generate_content(prompt)
            
            # Nettoyage manuel du JSON (gemini-pro est parfois bavard)
            text_clean = response.text.replace('```json', '').replace('```', '').strip()
            # On cherche le début et la fin du JSON au cas où il y ait du texte avant/après
            if '{' in text_clean and '}' in text_clean:
                start = text_clean.find('{')
                end = text_clean.rfind('}') + 1
                text_clean = text_clean[start:end]
            
            res = json.loads(text_clean)
            return res.get('sentiment', 'Neutre'), res.get('score', 0)
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                wait_time = base_delay * (attempt + 1)
                print(f"⚠️ Quota atteint (429). Pause de {wait_time}s...")
                time.sleep(wait_time)
                continue 
            else:
                print(f"❌ Erreur sur '{text[:10]}...': {e}")
                # On ne retourne pas tout de suite, on réessaie peut-être
                time.sleep(2)
                
    return "Erreur", 0.0

# --- 3. SIDEBAR (Contrôles UNIQUEMENT) ---
with st.sidebar:
    st.title("🎛️ Contrôles")
    env_key = os.getenv("GOOGLE_API_KEY")
    api_key = env_key if env_key else st.text_input("Clé API Gemini", type="password")
    
    if api_key:
        st.success("✅ API Connectée")
    
    st.divider()
    filter_container = st.container()

# --- 4. LOGIQUE PRINCIPALE ---
df = load_data()

if df.empty:
    st.error("Aucune donnée.")
    st.stop()

with filter_container:
    all_sources = df['source'].unique().tolist() if 'source' in df.columns else []
    sources = st.multiselect("Filtrer par Source", all_sources, default=all_sources)

filtered_df = df[df['source'].isin(sources)] if 'source' in df.columns else df

# --- ANALYSE BATCH ---
if api_key and not filtered_df.empty:
    if 'analyzed_data' not in st.session_state:
        st.session_state.analyzed_data = None

    if st.session_state.analyzed_data is None:
        if st.button("🚀 Lancer l'analyse complète"):
            progress_bar = st.progress(0, text="Démarrage...")
            results_list = []
            total = len(filtered_df)
            
            for index, row in filtered_df.iterrows():
                res = analyze_with_gemini_robust(row['avis'], api_key)
                results_list.append(res)
                percent = int((index + 1) / total * 100)
                progress_bar.progress(percent, text=f"Traitement {index+1}/{total}")
            
            filtered_df['Sentiment'] = [r[0] for r in results_list]
            filtered_df['Note'] = [r[1] for r in results_list]
            st.session_state.analyzed_data = filtered_df
            progress_bar.empty()
            st.rerun() 
    else:
        filtered_df = st.session_state.analyzed_data
else:
    filtered_df['Sentiment'] = "Non analysé"
    filtered_df['Note'] = 0.0

# --- 5. UI DASHBOARD ---
st.title("ReviewBot AI 🤖")
st.divider()

if 'Sentiment' in filtered_df.columns:
    # KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_avis = len(filtered_df)
    nb_positifs = len(filtered_df[filtered_df['Sentiment'] == 'Positif'])
    valid_scores = filtered_df[filtered_df['Note'] > 0]['Note']
    score_moyen = valid_scores.mean() if not valid_scores.empty else 0
    taux_satisfaction = (nb_positifs / total_avis * 100) if total_avis > 0 else 0
    top_src = filtered_df['source'].mode()[0] if not filtered_df.empty else "N/A"

    color_score = "#10B981" if score_moyen >= 4 else "#F59E0B" if score_moyen >= 2.5 else "#EF4444"

    kpi1.markdown(f"""<div class="kpi-card"><div class="kpi-title">Avis</div><div class="kpi-value">{total_avis}</div></div>""", unsafe_allow_html=True)
    kpi2.markdown(f"""<div class="kpi-card" style="border-left-color:{color_score}"><div class="kpi-title">Note IA</div><div class="kpi-value" style="color:{color_score}">{score_moyen:.1f}/5</div></div>""", unsafe_allow_html=True)
    kpi3.markdown(f"""<div class="kpi-card"><div class="kpi-title">Satisfaction</div><div class="kpi-value">{taux_satisfaction:.0f}%</div></div>""", unsafe_allow_html=True)
    kpi4.markdown(f"""<div class="kpi-card"><div class="kpi-title">Top Source</div><div class="kpi-value" style="font-size:1.5rem; line-height:2.2rem">{top_src}</div></div>""", unsafe_allow_html=True)

    st.write("")

    c1, c2 = st.columns([3, 7])

    with c1:
        st.subheader("Répartition")
        color_map = {'Positif': '#10B981', 'Négatif': '#EF4444', 'Neutre': '#3B82F6', 'Erreur': '#9CA3AF', 'Erreur (Quota)': '#6B7280'}
        fig = px.pie(filtered_df, names='Sentiment', hole=0.6, color='Sentiment', color_discrete_map=color_map)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, showlegend=True, legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Détail des avis")
        # Correction Warning use_container_width -> width='stretch' non supporté partout, on garde par défaut
        st.dataframe(
            filtered_df, 
            use_container_width=True, 
            height=300, 
            column_config={
                "Note": st.column_config.ProgressColumn("Score", min_value=0, max_value=5, format="%d/5", width="small"),
                "avis": st.column_config.TextColumn("Verbatim", width="large"),
                "Sentiment": st.column_config.TextColumn("Humeur", width="small"),
                "source": st.column_config.TextColumn("Source", width="small"),
                "date": st.column_config.DateColumn("Date", format="DD/MM/YY", width="small")
            }
        )

    # --- 6. SECTION TEST UNITAIRE (Dépliant en bas) ---
    st.write("") 
    with st.expander("🧪 Tester un avis manuellement", expanded=False):
        col_test_in, col_test_out = st.columns([3, 1])
        test_txt = col_test_in.text_input("Phrase à analyser :", placeholder="Ex: C'était délicieux !")
        
        if col_test_out.button("Analyser") and test_txt and api_key:
            with st.spinner("..."):
                s, n = analyze_with_gemini_robust(test_txt, api_key)
            
            if s == "Positif": st.success(f"**{s}** ({n}/5)")
            elif s == "Négatif": st.error(f"**{s}** ({n}/5)")
            else: st.info(f"**{s}** ({n}/5)")

else:
    st.info("👈 Lancez l'analyse depuis le bouton ci-dessus")