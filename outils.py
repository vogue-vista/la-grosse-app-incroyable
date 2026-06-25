import sqlite3
import streamlit as st
import requests
from groq import Groq

# ==============================================================================
# 📡 SECTION CONFIGURATION DE L'INFRASTRUCTURE RÉSEAU ET DES CLÉS API SECRÈTES
# ==============================================================================
# Récupération sécurisée des jetons d'accès depuis le fichier secrets de Streamlit Cloud
# Ces clés gèrent l'intelligence artificielle avancée et le proxy d'anonymisation du scraper.
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SCRAPE_DO_KEY = st.secrets["SCRAPE_DO_KEY"]

def obtenir_connexion():
    """
    Gère l'accès simultané à l'infrastructure de la base de données locale SQLite.
    Le paramètre timeout=30 et check_same_thread=False sont critiques ici pour 
    empêcher l'application Streamlit de crasher ou de se bloquer en cas d'accès
    simultané par plusieurs utilisateurs ou livreurs connectés sur le réseau.
    """
    return sqlite3.connect("empire_v2.db", timeout=30, check_same_thread=False)

def initialiser_base_de_donnees():
    """
    Protocole central d'initialisation de l'infrastructure SQL de stockage.
    Vérifie et forge automatiquement l'ensemble des tables requises si elles
    n'existent pas sur le serveur pour assurer une stabilité maximale à l'app.
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    
    # 🏬 TABLE DES BOUTIQUES E-COMMERCE : Enregistre le catalogue, le style visuel et le prix
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
    
    # 💎 TABLE DES ABONNEMENTS LOGICIELS MICRO-SAAS : Suit les contrats récurrents des clients Pro
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
    
    # 📊 TABLE DES STATISTIQUES CENTRALES : Permet de persister le chiffre d'affaires global
    cursor.execute("CREATE TABLE IF NOT EXISTS statistiques (cle TEXT PRIMARY KEY, valeur REAL)")
    
    # 📥 TABLE DE LA BOÎTE DE RÉCEPTION INTERNE : Stocke les paniers et les adresses réelles des clients
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boite_reception (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nom_boutique TEXT, 
            nom_client TEXT, 
            adresse TEXT, 
            commande TEXT, 
            total REAL, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 📡 TABLE DES NOTIFICATIONS DU FLUX RÉSEAU : Enregistre l'historique récent visible sur le dashboard
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            texte TEXT, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 🔒 TABLE DES CODES DE LICENCE UTILISÉS : Assure l'unicité et empêche la réutilisation frauduleuse
    cursor.execute("CREATE TABLE IF NOT EXISTS codes_utilises (code TEXT PRIMARY KEY)")
    
    # 💬 TABLE DU FORUM PRIVÉ DES ENTREPRENEURS : Gère l'historique des discussions collectives
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forum (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            auteur TEXT, 
            message TEXT, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 🚲 TABLE DU HUB LOGISTIQUE DES LIVREURS : Profils des coursiers pour les achats et les courses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS livreurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nom TEXT UNIQUE, 
            telephone TEXT, 
            zone TEXT, 
            statut TEXT DEFAULT 'Actif'
        )
    """)
    
    # Insertion de la valeur par défaut pour le compteur de chiffre d'affaires s'il n'existe pas
    cursor.execute("INSERT OR IGNORE INTO statistiques (cle, valeur) VALUES ('ca_total', 0.0)")
    
    conn.commit()
    conn.close()

def code_deja_utilise(code):
    """
    Analyse la base de données pour vérifier si une clé de licence Starter ou Pro
    a déjà été injectée et consommée par le passé afin de bloquer les doublons.
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM codes_utilises WHERE code = ?", (code,))
    res = cursor.fetchone()
    conn.close()
    return res is not None

def marquer_code_utilise(code):
    """
    Marque définitivement à usage unique un jeton ou code d'activation logicielle
    en l'insérant dans la table de sécurité des codes consommés.
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO codes_utilises (code) VALUES (?)", (code,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()
def appeler_groq(prompt, temperature=0.5):
    """
    Pilote le moteur d'intelligence artificielle avancé Llama 3.1 8B via Groq.
    Génère les fiches marketing, structures de cours digitaux ou audits concurrents.
    Incorpore une gestion d'exception robuste pour stopper proprement l'application
    Streamlit si les quotas d'API ou les serveurs sont saturés.
    """
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"⚠️ Le moteur d'intelligence artificielle est surchargé. (Erreur système : {e})")
        st.stop()

def executer_scraping_real(cible_url):
    """
    Effectue une extraction de données brute d'un site web à l'aide de l'API Scrape.do.
    Nettoie le code source HTML en supprimant les scripts et balises de style de façon
    à ne retourner que le texte brut exploitable (limité à 2500 caractères).
    """
    try:
        url_propre = cible_url if cible_url.startswith(("http://", "https://")) else f"https://{cible_url}"
        url_api = f"https://scrape.do{SCRAPE_DO_KEY}&url={url_propre}"
        response = requests.get(url_api, timeout=15)
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(separator=" ")[:2500]
        else:
            return f"Contenu indisponible actuellement (Code d'état API : {response.status_code})"
    except Exception as e:
        return f"Erreur de connexion aux serveurs de scraping réseau : {e}"

def ajouter_boutique(nom, niche, contenu, prix, couleur="#f8fafc"):
    """
    Enregistre et déploie une nouvelle infrastructure commerciale dans la base locale.
    Déclenche une notification système globale visible en temps réel sur le flux réseau.
    Retourne False en cas de doublon sur le nom (clé UNIQUE).
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO boutiques (nom, niche, contenu, couleur, prix) 
            VALUES (?, ?, ?, ?, ?)
        """, (nom, niche, contenu, couleur, prix))
        cursor.execute("INSERT INTO notifications (texte) VALUES (?)", (f"🏬 Infrastructure en ligne : '{nom}' a été déployé avec succès !",))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def enregistrer_commande_interne(nom_boutique, nom_client, adresse, commande, total):
    """
    Enregistre de manière définitive une transaction client dans la boîte de réception.
    Met automatiquement à jour le chiffre d'affaires cumulé global et génère une alerte
    sur le flux d'activité réseau pour notifier le commerçant en direct.
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO boite_reception (nom_boutique, nom_client, adresse, commande, total) 
            VALUES (?, ?, ?, ?, ?)
        """, (nom_boutique, nom_client, adresse, commande, total))
        
        # Consolidation financière instantanée du chiffre d'affaires
        cursor.execute("UPDATE statistiques SET valeur = valeur + ? WHERE cle = 'ca_total'", (total,))
        cursor.execute("INSERT INTO notifications (texte) VALUES (?)", (f"💰 Encaissé : Panier de {total}$ validé sur la vitrine {nom_boutique} !",))
        conn.commit()
    finally:
        conn.close()

def recuperer_commandes_boutique(nom_boutique):
    """
    Extrait l'ensemble de l'historique logistique des paniers validés pour une enseigne.
    Classe les résultats par ordre chronologique inverse (du plus récent au plus ancien).
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nom_client, adresse, commande, total, timestamp 
        FROM boite_reception 
        WHERE nom_boutique = ? 
        ORDER BY id DESC
    """, (nom_boutique,))
    res = cursor.fetchall()
    conn.close()
    return res

def s_inscrire_livreur(nom_livreur, telephone, zone):
    """
    Inscrit le profil complet d'un coursier local indépendant dans la table logistique.
    Émet un message réseau pour notifier la communauté de l'arrivée d'un nouveau transporteur.
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO livreurs (nom, telephone, zone) VALUES (?, ?, ?)", (nom_livreur, telephone, zone))
        cursor.execute("INSERT INTO notifications (texte) VALUES (?)", (f"🚲 Hub Logistique : Le coursier '{nom_livreur}' a activé son statut de livraison !",))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def recuperer_commandes_sans_livreur():
    """
    Extrait toutes les fiches d'achats consignées sur l'infrastructure.
    Permet d'alimenter le tableau des missions partagées pour les coursiers réseau.
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nom_boutique, nom_client, adresse, commande, total, timestamp 
        FROM boite_reception 
        ORDER BY id DESC
    """)
    res = cursor.fetchall()
    conn.close()
    return res

def ajouter_message_forum(auteur, message):
    """
    Persiste une nouvelle note textuelle sur l'infrastructure partagée du forum privé.
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO forum (auteur, message) VALUES (?, ?)", (auteur, message))
    conn.commit()
    conn.close()

def recuperer_messages_forum():
    """
    Génère l'historique des discussions collectives des marchands (limité aux 50 derniers).
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT auteur, message, timestamp FROM forum ORDER BY id DESC LIMIT 50")
    res = cursor.fetchall()
    conn.close()
    return res

def enregistrer_abonnement(nom_plateforme, nom_client, email_client, tarif):
    """
    Valide l'activation d'un forfait d'abonnement logiciel récurent pour une plateforme SaaS.
    Génère une alerte réseau de type 'Rente récurrente perçue'.
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO abonnements (nom_plateforme, nom_client, email_client, tarif) 
            VALUES (?, ?, ?, ?)
        """, (nom_plateforme, nom_client, email_client, tarif))
        cursor.execute("INSERT INTO notifications (texte) VALUES (?)", (f"💎 Revenu Passif : Nouvel abonnement Micro-SaaS de {tarif}$ reçu sur {nom_plateforme} !",))
        conn.commit()
    finally:
        conn.close()

def recuperer_abonnements():
    """
    Extrait l'intégralité du grand livre comptable des contrats logiciels actifs sur le serveur.
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nom_plateforme, nom_client, email_client, tarif, statut, date_inscription 
        FROM abonnements 
        ORDER BY id DESC
    """)
    res = cursor.fetchall()
    conn.close()
    return res

def supprimer_boutique(nom_boutique):
    """
    Efface de manière irréversible une entité commerciale de la base de données SQLite.
    Produit une note réseau de maintenance pour officialiser la suppression.
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM boutiques WHERE nom = ?", (nom_boutique,))
        cursor.execute("INSERT INTO notifications (texte) VALUES (?)", (f"🗑️ Cluster réseau : La boutique '{nom_boutique}' a été détruite.",))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def recuperer_boutiques():
    """
    Extrait les enregistrements de toutes les vitrines e-commerce déployées.
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT nom, niche, contenu, couleur, prix FROM boutiques")
    liste = cursor.fetchall()
    conn.close()
    return list(liste)

def mettre_a_jour_boutique(nom, nouveau_contenu):
    """
    Applique des modifications structurelles sur le catalogue de vente d'une vitrine.
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE boutiques SET contenu = ? WHERE nom = ?", (nouveau_contenu, nom))
    conn.commit()
    conn.close()

def recuperer_ca_total():
    """
    Interroge la table statistiques pour extraire la valeur consolidée du Chiffre d'Affaires.
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT valeur FROM statistiques WHERE cle = 'ca_total'")
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else 0.0

def recuperer_notifications():
    """
    Fournit le flux des 3 alertes réseau les plus récentes pour l'affichage dynamique.
    Affiche des notes d'initialisation standard par défaut si la table est vide.
    """
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT texte FROM notifications ORDER BY id DESC LIMIT 3")
    res = cursor.fetchall()
    conn.close()
    if not res:
        return [
            "🟢 Central System : Infrastructure réseau opérationnelle.",
            "📡 Gateway : Routeurs Scrape.do correctement interfacés.",
            "🤖 Core Intelligence : Modèles prédictifs Groq synchronisés."
        ]
    return [r[0] for r in res]
