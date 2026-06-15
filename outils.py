import sqlite3
import streamlit as st
import requests
from groq import Groq

# Extraction sécurisée des clés d'API dans Streamlit Cloud
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SCRAPE_DO_KEY = st.secrets["SCRAPE_DO_KEY"]

def initialiser_base_de_donnees():
    # SÉCURITÉ ABSOLUE : On change le nom du fichier pour 'empire_v2.db' 
    # pour forcer Streamlit Cloud à recréer une base propre avec la colonne 'prix'
    conn = sqlite3.connect("empire_v2.db")
    cursor = conn.cursor()
    
    # Création de la table boutiques avec TOUTES les colonnes nécessaires dès le départ
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boutiques (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE,
            niche TEXT,
            contenu TEXT,
            couleur TEXT,
            prix REAL DEFAULT 0.0
        )
    """)
    
    # Création des tables de statistiques et notifications
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS statistiques (
            cle TEXT PRIMARY KEY,
            valeur REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texte TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Initialisation du chiffre d'affaires à 0.0
    cursor.execute("INSERT OR IGNORE INTO statistiques (cle, valeur) VALUES ('ca_total', 0.0)")
    conn.commit()
    conn.close()

def appeler_groq(prompt, temperature=0.7):
   def appeler_groq(prompt, temperature=0.7):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur avec l'IA Groq : {e}"

def executer_scraping_real(cible_url):
    try:
        url_api = f"http://scrape.do{SCRAPE_DO_KEY}&url={cible_url}"
        response = requests.get(url_api)
        if response.status_code == 200:

        else:
            return f"❌ Échec du scraping via Scrape.do. Code erreur : {response.status_code}"
    except Exception as e:
        return f"Erreur technique de connexion à Scrape.do : {e}"

def ajouter_boutique(nom, niche, contenu, prix, couleur="#45f3ff"):
    conn = sqlite3.connect("empire_v2.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO boutiques (nom, niche, contenu, couleur, prix) VALUES (?, ?, ?, ?, ?)", (nom, niche, contenu, couleur, prix))
        cursor.execute("INSERT INTO notifications (texte) VALUES (?)", (f"🏬 Nouvelle boutique '{nom}' déployée dans la niche {niche} !",))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def recuperer_boutiques():
    conn = sqlite3.connect("empire_v2.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nom, niche, contenu, couleur, prix FROM boutiques")
    liste = cursor.fetchall()
    conn.close()
    return list(liste)

def mettre_a_jour_boutique(nom, nouveau_contenu):
    conn = sqlite3.connect("empire_v2.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE boutiques SET contenu = ? WHERE nom = ?", (nouveau_contenu, nom))
    conn.commit()
    conn.close()

def recuperer_ca_total():
    conn = sqlite3.connect("empire_v2.db")
    cursor = conn.cursor()
    cursor.execute("SELECT valeur FROM statistiques WHERE cle = 'ca_total'")
    res = cursor.fetchone()
    conn.close()
    return res if res else 0.0

def enregistrer_vente(nom_boutique, montant):
    conn = sqlite3.connect("empire_v2.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE statistiques SET valeur = valeur + ? WHERE cle = 'ca_total'", (montant,))
    cursor.execute("INSERT INTO notifications (texte) VALUES (?)", (f"💰 Vente ! Un client vient de dépenser {montant}$ sur la boutique '{nom_boutique}' !",))
    conn.commit()
    conn.close()

def recuperer_notifications():
    conn = sqlite3.connect("empire_v2.db")
    cursor = conn.cursor()
    cursor.execute("SELECT texte FROM notifications ORDER BY id DESC LIMIT 3")
    res = cursor.fetchall()
    conn.close()
    if not res:
        return [
            "🟢 Système en attente d'activité commerciale...",
            "📡 Connexion établie avec le réseau de proxies rotatifs de Scrape.do.",
            "🤖 IA Groq synchronisée et prête à propulser vos ventes."
        ]
    return [r for r in res]
