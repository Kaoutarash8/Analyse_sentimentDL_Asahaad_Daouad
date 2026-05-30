import streamlit as st
from model import model
import time

# Configuration de la page
st.set_page_config(
    page_title="Analyse de Sentiment - Darija",
    page_icon="",
    layout="centered"
)

# Style CSS
st.markdown("""
    <style>
        .stApp {
            background-color: white;
        }
        
        .auth-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
            border: 1px solid #e2e8f0;
            overflow: hidden;
            margin-bottom: 20px;
        }
        
        .card-header {
            background: #001f3f;
            padding: 28px 32px;
            text-align: center;
        }
        
        .card-header h1 {
            color: white;
            font-size: 28px;
            font-weight: 600;
            margin: 0;
        }
        
        .card-header p {
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
            margin-top: 8px;
        }
        
        .card-body {
            padding: 32px;
        }
        
        .card-footer {
            background: #f8fafc;
            padding: 16px 32px;
            text-align: center;
            border-top: 1px solid #e2e8f0;
        }
        
        .card-footer p {
            font-size: 12px;
            color: #64748b;
            margin: 0;
        }
        
        .stTextArea textarea {
            border: 2px solid #e2e8f0 !important;
            border-radius: 12px !important;
            font-size: 14px !important;
            font-family: monospace !important;
        }
        
        .stTextArea textarea:focus {
            border-color: #001f3f !important;
            box-shadow: 0 0 0 3px rgba(0, 31, 63, 0.1) !important;
        }
        
        .stButton button {
            width: 100%;
            background-color: #001f3f !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px 24px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease;
        }
        
        .stButton button:hover {
            background-color: #002a5c !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 31, 63, 0.2);
        }
        
        .result-container {
            margin-top: 28px;
        }
        
        .result-box {
            background: #f8fafc;
            padding: 20px 24px;
            border-radius: 16px;
            text-align: center;
            border-left: 4px solid;
            transition: all 0.3s ease;
        }
        
        .result-label {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            color: #64748b;
            margin-bottom: 8px;
        }
        
        .result-value {
            font-size: 28px;
            font-weight: 700;
            margin: 5px 0;
        }
        
        .confidence {
            font-size: 13px;
            color: #64748b;
            margin-top: 8px;
        }
        
        .confidence-bar {
            width: 100%;
            height: 6px;
            background: #e2e8f0;
            border-radius: 3px;
            margin-top: 12px;
            overflow: hidden;
        }
        
        .confidence-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.3s ease;
        }
        
        .stats-badge {
            background: #f1f5f9;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 11px;
            color: #475569;
            text-align: center;
            margin-top: 16px;
        }
        
        .warning-message {
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 12px 16px;
            border-radius: 8px;
            margin-top: 16px;
            font-size: 13px;
            color: #92400e;
        }
        
        @media (max-width: 600px) {
            .card-header {
                padding: 20px 24px;
            }
            .card-header h1 {
                font-size: 24px;
            }
            .card-body {
                padding: 24px;
            }
            .result-value {
                font-size: 22px;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Interface principale
st.markdown("""
    <div class="auth-card">
        <div class="card-header">
            <h1>Analyse de Sentiment</h1>
            <p>Détection automatique en darija (Modele BERT)</p>
        </div>
        <div class="card-body">
""", unsafe_allow_html=True)

# Champ de saisie
user_input = st.text_area(
    "Votre phrase",
    height=120,
    placeholder="entrer "
)

# Bouton d'analyse
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button("Analyser le sentiment", use_container_width=True)

if analyze_button:
    if not user_input.strip():
        st.markdown("""
            <div class="warning-message">
                ⚠️ Veuillez entrer une phrase à analyser.
            </div>
        """, unsafe_allow_html=True)
    else:
        with st.spinner("Analyse en cours..."):
            try:
                # Prédiction avec le modèle BERT
                sentiment, confidence = model.predict(user_input)
                
                # Configuration des couleurs
                colors = {
                    'positif': '#10b981',
                    'negatif': '#ef4444',
                    'neutre': '#64748b'
                }
                
                # Affichage du résultat
                st.markdown(f"""
                    <div class="result-container">
                        <div class="result-box" style="border-left-color: {colors[sentiment]}">
                            <div class="result-label">RESULTAT DE L ANALYSE</div>
                            <div class="result-value" style="color: {colors[sentiment]}">
                                {sentiment.upper()}
                            </div>
                        
                            
                        
                    
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.markdown(f"""
                    <div class="warning-message">
                        Erreur: {str(e)}
                    </div>
                """, unsafe_allow_html=True)

# Badge d'information
st.markdown("""
    
""", unsafe_allow_html=True)

st.markdown("""
        </div>
        <div class="card-footer">
            <p>Analyse de sentiment - Darija BERT</p>
        </div>
    </div>
""", unsafe_allow_html=True)