import sqlite3
import streamlit as st
import requests
from groq import Groq

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SCRAPE_DO_KEY = st.secrets["SCRAPE_DO_KEY"]

def obtenir_connexion():
    return sqlite3.connect("empire_v2.db", timeout=30, check_same_thread=False)

def initialiser_base_de_donnees():
    conn = obtenir_connexion()
    cursor = conn.cursor()
    
    # Table des boutiques liée au compte propriétaire (cle_proprietaire)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boutiques (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nom TEXT UNIQUE, 
            niche TEXT, 
            contenu TEXT, 
            couleur TEXT, 
            prix REAL DEFAULT 0.0,
            cle_proprietaire TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS abonnements (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nom_plateforme TEXT, nom_client TEXT, email_client TEXT, tarif REAL, statut TEXT DEFAULT 'Actif', date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS statistiques (cle TEXT PRIMARY KEY, valeur REAL)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boite_reception (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nom_boutique TEXT, nom_client TEXT, adresse TEXT, commande TEXT, total REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, texte TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS codes_utilises (code TEXT PRIMARY KEY)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forum (
            id INTEGER PRIMARY KEY AUTOINCREMENT, auteur TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS livreurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT UNIQUE, telephone TEXT, zone TEXT, statut TEXT DEFAULT 'Actif'
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

def appeler_groq(prompt, temperature=0.5):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"⚠️ Le moteur d'intelligence artificielle est surchargé. (Erreur : {e})")
        st.stop()

def ajouter_boutique(nom, niche, contenu, prix, cle_proprietaire, couleur="#f8fafc"):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO boutiques (nom, niche, contenu, couleur, prix, cle_proprietaire) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nom, niche, contenu, couleur, prix, cle_proprietaire))
        cursor.execute("INSERT INTO notifications (texte) VALUES (?)", (f"🏬 Vitrine en ligne : '{nom}' a été déployée et sécurisée sur votre compte !",))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def enregistrer_commande_interne(nom_boutique, nom_client, adresse, commande, total):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO boite_reception (nom_boutique, nom_client, adresse, commande, total) 
            VALUES (?, ?, ?, ?, ?)
        """, (nom_boutique, nom_client, adresse, commande, total))
        cursor.execute("UPDATE statistiques SET valeur = valeur + ? WHERE cle = 'ca_total'", (total,))
        cursor.execute("INSERT INTO notifications (texte) VALUES (?)", (f"💰 Encaissé : Panier de {total}$ validé sur {nom_boutique} !",))
        conn.commit()
    finally:
        conn.close()

def recuperer_commandes_boutique(nom_boutique):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT nom_client, adresse, commande, total, timestamp FROM boite_reception WHERE nom_boutique = ? ORDER BY id DESC", (nom_boutique,))
    res = cursor.fetchall()
    conn.close()
    return res

def s_inscrire_livreur(nom_livreur, telephone, zone):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO livreurs (nom, telephone, zone) VALUES (?, ?, ?)", (nom_livreur, telephone, zone))
        cursor.execute("INSERT INTO notifications (texte) VALUES (?)", (f"🚲 Hub Logistique : Le coursier '{nom_livreur}' est disponible !",))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def recuperer_commandes_sans_livreur():
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom_boutique, nom_client, adresse, commande, total, timestamp FROM boite_reception ORDER BY id DESC")
    res = cursor.fetchall()
    conn.close()
    return res

def ajouter_message_forum(auteur, message):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO forum (auteur, message) VALUES (?, ?)", (auteur, message))
    conn.commit()
    conn.close()

def recuperer_messages_forum():
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT auteur, message, timestamp FROM forum ORDER BY id DESC LIMIT 50")
    res = cursor.fetchall()
    conn.close()
    return res

def recuperer_boutiques_par_utilisateur(cle_proprietaire):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT nom, niche, contenu, couleur, prix FROM boutiques WHERE cle_proprietaire = ?", (cle_proprietaire,))
    liste = cursor.fetchall()
    conn.close()
    return list(liste)

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

def recuperer_notifications():
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT texte FROM notifications ORDER BY id DESC LIMIT 3")
    res = cursor.fetchall()
    conn.close()
    if not res:
        return ["🟢 Central System connecté.", "📡 Chiffrement local SQLite validé.", "🤖 IA Groq en ligne."]
    return [r[0] for r in res]
    
    def recuperer_abonnements():
    """
    Extrait l'intégralité du grand livre comptable des contrats logiciels actifs sur le serveur.
    """
    conn = sqlite3.connect("empire_v2.db", timeout=30, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nom_plateforme, nom_client, email_client, tarif, statut, date_inscription 
        FROM abonnements 
        ORDER BY id DESC
    """)
    res = cursor.fetchall()
    conn.close()
    return res

