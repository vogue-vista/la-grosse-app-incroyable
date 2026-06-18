import sqlite3
import streamlit as st
import requests
from groq import Groq

# Extraction sécurisée des clés d'API dans Streamlit Cloud
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SCRAPE_DO_KEY = st.secrets["SCRAPE_DO_KEY"]

def obtenir_connexion():
    """Gère l'accès simultané à SQLite pour éviter les plantages 'database is locked'"""
    return sqlite3.connect("empire_v2.db", timeout=10)

def initialiser_base_de_donnees():
    conn = obtenir_connexion()
    cursor = conn.cursor()
    
    # Table des boutiques (Stockage du contenu Markdown/HTML propre)
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
    
    # Table des abonnés récurrents (Pour le module Rente Réelle)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS abonnements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_plateforme TEXT,
            nom_client TEXT,
            email_client TEXT,
            tarif REAL,
            statut TEXT DEFAULT 'Actif',
            date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table des statistiques
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS statistiques (
            cle TEXT PRIMARY KEY,
            valeur REAL
        )
    """)
    
    # Table des notifications
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texte TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table des codes de sécurité anti-triche
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS codes_utilises (
            code TEXT PRIMARY KEY
        )
    """)
    
    cursor.execute("INSERT OR IGNORE INTO statistiques (cle, valeur) VALUES ('ca_total', 0.0)")
    conn.commit()
    conn.close()

def code_deja_utilise(code):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM codes_utilises WHERE code = ?", (code,))
    res = cursor.fetchone()
    conn.close()
    return res is not None

def marquer_code_utilise(code):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO codes_utilises (code) VALUES (?)", (code,))
        conn.commit()
    except:
        pass
    finally:
        conn.close()

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
        st.error(f"⚠️ Le moteur d'IA est surchargé. Réessayez dans quelques secondes. (Erreur : {e})")
        st.stop()

def executer_scraping_real(cible_url):
    try:
        url_propre = cible_url if cible_url.startswith(("http://", "https://")) else f"https://{cible_url}"
        url_api = f"https://scrape.do{SCRAPE_DO_KEY}&url={url_propre}"
        response = requests.get(url_api, timeout=12)
        if response.status_code == 200:
            # Extraction purement textuelle basique pour éviter d'envoyer trop de code HTML lourd à l'IA
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(separator=" ")[:2000]
        else:
            return "Contenu indisponible ou site protégé."
    except Exception as e:
        return f"Erreur de connexion aux serveurs de scraping : {e}"

def ajouter_boutique(nom, niche, contenu, prix, couleur="#45f3ff"):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO boutiques (nom, niche, contenu, couleur, prix) VALUES (?, ?, ?, ?, ?)", (nom, niche, contenu, couleur, prix))
        cursor.execute("INSERT INTO notifications (texte) VALUES (?)", (f"🏬 Infrastructure en ligne : '{nom}' a été déployé avec succès !",))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def enregistrer_abonnement(nom_plateforme, nom_client, email_client, tarif):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO abonnements (nom_plateforme, nom_client, email_client, tarif) VALUES (?, ?, ?, ?)", (nom_plateforme, nom_client, email_client, tarif))
        cursor.execute("INSERT INTO notifications (texte) VALUES (?)", (f"💎 Nouvel abonnement récurrent de {tarif}$ reçu sur {nom_plateforme} ! ({nom_client})",))
        conn.commit()
    finally:
        conn.close()

def recuperer_abonnements():
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT nom_plateforme, nom_client, email_client, tarif, statut, date_inscription FROM abonnements ORDER BY id DESC")
    res = cursor.fetchall()
    conn.close()
    return res

def supprimer_boutique(nom_boutique):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM boutiques WHERE nom = ?", (nom_boutique,))
        cursor.execute("INSERT INTO notifications (texte) VALUES (?)", (f"🗑️ La boutique '{nom_boutique}' a été effacée des serveurs.",))
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        conn.close()

def recuperer_boutiques():
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT nom, niche, contenu, couleur, prix FROM boutiques")
    liste = cursor.fetchall()
    conn.close()
    return list(liste)

def mettre_a_jour_boutique(nom, nouveau_contenu):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE boutiques SET contenu = ? WHERE nom = ?", (nouveau_contenu, nom))
    conn.commit()
    conn.close()

def recuperer_ca_total():
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT valeur FROM statistiques WHERE cle = 'ca_total'")
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else 0.0

def enregistrer_vente(nom_boutique, montant):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE statistiques SET valeur = valeur + ? WHERE cle = 'ca_total'", (montant,))
    cursor.execute("INSERT INTO notifications (texte) VALUES (?)", (f"💰 Encaissé : Un client a validé un panier de {montant}$ sur {nom_boutique} !",))
    conn.commit()
    conn.close()

def recuperer_notifications():
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT texte FROM notifications ORDER BY id DESC LIMIT 3")
    res = cursor.fetchall()
    conn.close()
    if not res:
        return [
            "🟢 Système centralisé en attente d'activité commerciale...",
            "📡 Proxies Scrape.do synchronisés.",
            "🤖 Modèles Groq Llama-3.1 opérationnels."
        ]
    return [r[0] for r in res]
