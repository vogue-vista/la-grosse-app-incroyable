import sqlite3
import streamlit as st
import requests
from groq import Groq

# Extraction sécurisée des clés d'API dans Streamlit Cloud
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SCRAPE_DO_KEY = st.secrets["SCRAPE_DO_KEY"]

def initialiser_base_de_donnees():
    conn = sqlite3.connect("empire.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boutiques (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE,
            niche TEXT,
            contenu TEXT,
            couleur TEXT
        )
    """)
    conn.commit()
    conn.close()

def appeler_groq(prompt, temperature=0.7):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama3-8b-8098",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return completion.choices.message.content
    except Exception as e:
        return f"Erreur avec l'IA Groq : {e}"

def executer_scraping_real(cible_url):
    """
    Exécute un appel réel à l'API Scrape.do en lui passant une URL cible.
    Scrape.do s'occupe de contourner les anti-bots et renvoie le HTML brut.
    """
    try:
        # URL officielle de l'API Scrape.do pour exécuter la requête via proxy rotatif
        url_api = f"http://scrape.do{SCRAPE_DO_KEY}&url={cible_url}"
        response = requests.get(url_api)
        
        if response.status_code == 200:
            # Pour la démonstration client, on extrait un extrait du HTML reçu
            html_brut = response.text[:500] 
            return f"✅ Données extraites avec succès via Scrape.do !\n\nExtrait du code source de la page ciblée :\n{html_brut}..."
        else:
            return f"❌ Échec du scraping via Scrape.do. Code erreur : {response.status_code}"
    except Exception as e:
        return f"Erreur technique de connexion à Scrape.do : {e}"

def ajouter_boutique(nom, niche, contenu, couleur="#45f3ff"):
    conn = sqlite3.connect("empire.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO boutiques (nom, niche, contenu, couleur) VALUES (?, ?, ?, ?)", (nom, niche, contenu, couleur))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def recuperer_boutiques():
    conn = sqlite3.connect("empire.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nom, niche, contenu, couleur FROM boutiques")
    liste = cursor.fetchall()
    conn.close()
    return liste

def mettre_a_jour_boutique(nom, nouveau_contenu):
    conn = sqlite3.connect("empire.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE boutiques SET contenu = ? WHERE nom = ?", (nouveau_contenu, nom))
    conn.commit()
    conn.close()
