import sqlite3
import streamlit as st
import requests
from groq import Groq

# Recouvrement automatique des clés sécurisées dans Streamlit Cloud
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SCRAP_IO_KEY = st.secrets["SCRAP_IO_KEY"]

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

def executer_scraping_reel(metier, ville):
    # Exemple de structure d'appel réel vers l'API scrap.io
    # url = f"https://scrap.io{SCRAP_IO_KEY}&category={metier}&city={ville}"
    # response = requests.get(url).json()
    
    # Simulation du format renvoyé par l'API pour votre démonstration
    return [
        {"nom": f"{metier} Dynamique {ville}", "site": "Aucun site internet répertorié"},
        {"nom": f"Groupe Experts {metier}", "site": f"www.expert-{metier}.ca"}
    ]

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
