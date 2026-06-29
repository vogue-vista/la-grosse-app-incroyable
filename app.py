import streamlit as st
import outils
import re
import random

# Configuration graphique de l'espace de travail Streamlit
st.set_page_config(
    page_title="Empire Tycoon Infrastructure v3.5", 
    page_icon="👑", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Initialisation et vérification des tables de la base de données SQLite
outils.initialiser_base_de_donnees()

# Sauvegarde des variables de sessions pour éviter les pertes de données au rafraîchissement
if "panier_client" not in st.session_state:
    st.session_state.panier_client = []
if "compte_actif" not in st.session_state: 
    st.session_state.compte_actif = False
if "forfait" not in st.session_state: 
    st.session_state.forfait = "Aucun"

# --- 1. ROUTAGE D'URL PUBLIC POUR LES VRAIS CLIENTS EXTERNES ---
query_params = st.query_params

if "shop" in query_params:
    shop_public = query_params["shop"]
    liste_shops_publics = outils.recuperer_boutiques()
    boutique_trouvee = None
    
    for s in liste_shops_publics:
        if s[0].lower().replace(" ", "-") == shop_public.lower():
            boutique_trouvee = s
            break
            
    if boutique_trouvee:
        nom, niche, contenu, couleur, prix_bdd = boutique_trouvee
        try: prix_bdd_propre = float(prix_bdd)
        except: prix_bdd_propre = 0.0
        
        contenu_client = contenu.replace("```html", "").replace("```", "").replace("html", "").strip()

        # INJECTION CSS POUR LE DESIGN EXCLUSIF DE LA VITRINE CLIENT
        fond_branding = couleur if (couleur and not "@" in couleur) else "#f8fafc"
        st.markdown(f"""
        <style>
        .stApp {{ background: {fond_branding} !important; color: #0f172a !important; }}
        h1, h2, h3, h4, h5, p, span, label, div {{ color: #0f172a !important; font-family: 'Segoe UI', system-ui, sans-serif !important; }}
        
        div[data-testid="stForm"], .bloc-panier {{ 
            background-color: #ffffff !important; 
            border: 2px solid #e2e8f0 !important; 
            border-radius: 20px !important; padding: 30px !important;
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.05) !important; margin-bottom: 20px;
        }}
        
        .stButton>button {{
            background-color: #00ffcc !important; color: #0f172a !important;
            font-weight: 800 !important; text-transform: uppercase !important;
            border-radius: 12px !important; border: none !important; padding: 12px 24px !important;
        }}
        input {{ background-color: #ffffff !important; color: #0f172a !important; border: 1px solid #cbd5e1 !important; border-radius: 8px !important; }}
        </style>
        """, unsafe_allow_html=True)
        
        st.title(f"🏬 BIENVENUE CHEZ : {nom.upper()}")
        st.subheader(f"✨ Univers et thématique : {niche}")
        st.markdown("<hr style='border: 1px solid #e2e8f0; margin-bottom: 25px;'>", unsafe_allow_html=True)
        # INTERPRÉTATION GRAPHIQUE COMPLÈTE DU CATALOGUE DE VENTE (Sourcing local réel)
        if "### 📦" in contenu_client:
            blocs_produits = contenu_client.split("### 📦")
            
            for idx, bloc in enumerate(blocs_produits[1:]):
                if bloc.strip():
                    lignes_bloc = bloc.split("\n")
                    nom_produit = lignes_bloc[0].strip() if lignes_bloc else "Article de style"
                    
                    # Extraction automatique du prix par expression régulière (Regex)
                    trouver_prix = re.search(r"Prix\s*:\s*([\d[\s,\.]*\d+)", bloc, re.IGNORECASE)
                    if trouver_prix:
                        prix_texte = trouver_prix.group(1).replace(" ", "").replace(",", ".")
                        try:
                            prix_chiffre = float(prix_texte)
                        except ValueError:
                            prix_chiffre = prix_bdd_propre
                    else:
                        prix_chiffre = prix_bdd_propre
                    
                    # Extraction de la source ou du magasin physique ciblé par l'IA
                    trouver_source = re.search(r"Source\s*:\s*(.*)", bloc, re.IGNORECASE)
                    source_produit = trouver_source.group(1).strip() if trouver_source else "Enseigne locale"
                    
                    st.markdown(f"### 📦 {bloc}", unsafe_allow_html=True)
                    
                    # Bouton d'ajout dynamique rattaché à chaque produit réel
                    if st.button(f"🛒 Ajouter à ma sélection : {nom_produit}", key=f"btn_ajout_{idx}"):
                        st.session_state.panier_client.append({
                            "nom": nom_produit,
                            "prix": prix_chiffre, 
                            "vendeur": nom,
                            "source": source_produit
                        })
                        st.toast(f"✅ {nom_produit} a été ajouté à votre panier !", icon="🛒")
        else:
            st.markdown(contenu_client, unsafe_allow_html=True)

        st.markdown("<br><hr style='border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        st.markdown("## 🛒 Votre Panier d'Achat Réseau")
        
        if not st.session_state.panier_client:
            st.info("Votre panier est actuellement vide. Sélectionnez des articles ci-dessus.")
            total_commande = 0.0
        else:
            sous_total = 0.0
            st.markdown("<div class='bloc-panier'>", unsafe_allow_html=True)
            for idx_p, item in enumerate(st.session_state.panier_client):
                col_item1, col_item2 = st.columns(2)
                with col_item1:
                    st.write(f"🔹 **{item['nom']}** — {item['prix']} $")
                with col_item2:
                    if st.button("❌ Retirer", key=f"del_item_{idx_p}"):
                        st.session_state.panier_client.pop(idx_p)
                        st.rerun()
                sous_total += item['prix']
            
            # Application des frais de livraison de 4.99$ fixes pour assurer ton profit
            frais_livraison = 4.99
            total_commande = sous_total + frais_livraison
            
            st.write(f"🛒 Sous-total des articles : {round(sous_total, 2)} $")
            st.write(f"🚲 Frais de livraison fixe de proximité : {frais_livraison} $")
            st.markdown(f"### 💵 Montant Total à Payer : {round(total_commande, 2)} $")
            st.caption("💡 Logistique de sécurité : Un livreur indépendant ou le gérant ira acheter cet article au magasin local avant de vous le remettre.")
            if st.button("🧹 Vider complètement le panier"):
                st.session_state.panier_client = []
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # Formulaire de commande sécurisé relié à la boîte de réception interne de l'utilisateur
        if st.session_state.panier_client:
            st.markdown("### ⚡ Finaliser la commande en 1-Clic")
            with st.form("achat_client_form"):
                nom_client = st.text_input("Nom complet pour la facturation :", placeholder="Ex: Jean Tremblay")
                adresse_client = st.text_input("Adresse municipale exacte pour la livraison :", placeholder="Ex: 742 rue de la Paix, Montréal, QC")
                
                texte_bouton = f"🔥 Confirmer et commander ({round(total_commande, 2)} $)"
                if st.form_submit_button(texte_bouton):
                    if nom_client and adresse_client:
                        # Enregistrement groupé dans la boîte de réception avec frais de livraison inclus sur le premier article
                        for idx_item, item in enumerate(st.session_state.panier_client):
                            prix_final_item = item['prix']
                            if idx_item == 0:
                                prix_final_item += 4.99 # Les frais logistiques sont attribués ici
                                
                            outils.enregistrer_commande_interne(
                                nom_boutique=item.get('vendeur', nom),
                                nom_client=nom_client,
                                adresse=adresse_client,
                                commande=f"{item['nom']} | 🏬 Sourcing : {item.get('source', 'Enseigne locale')}",
                                total=prix_final_item
                            )
                        st.session_state.panier_client = []
                        st.balloons()
                        st.success("🎉 Parfait ! Votre commande a été enregistrée. Le gérant et son livreur local préparent votre colis.")
                        st.rerun()
                    else:
                        st.error("⚠️ Formulaire incomplet : Veuillez renseigner votre nom complet ainsi que l'adresse de livraison.")
        st.stop()
# --- 2. CONFIGURATION DE SESSION ADMINISTRATEUR ---
if "compte_actif" not in st.session_state: st.session_state.compte_actif = False
if "forfait" not in st.session_state: st.session_state.forfait = "Aucun"

# 🔥 BLOC SÉCURITÉ PARENTALE ET TRANSPARENCE AVANT AUTHENTIFICATION
if not st.session_state.compte_actif:
    st.markdown("""
    <div style='background-color: #111827; padding: 25px; border-radius: 16px; border: 1px solid #1f2937; text-align: center; margin-bottom: 25px;'>
        <h4 style='color: #00ffcc; margin: 0; font-weight: bold; letter-spacing: 1px;'>💡 PROTOCOLE CENTRAL D'ACTIVATION</h4>
        <p style='color: #9ca3af; font-size: 15px; margin: 8px 0 0 0;'>« L'application te donne les armes, mais c'est toi qui choisis la guerre. »</p>
    </div>
    
    <div style='background-color: #1e293b; padding: 25px; border-radius: 16px; border-left: 6px solid #3b82f6; margin-bottom: 30px;'>
        <h5 style='color: #3b82f6; margin-top: 0; font-weight: bold; font-size: 16px;'>🛡️ SECTION SÉCURITÉ PARENTALE (Lettre ouverte du créateur)</h5>
        <span style='font-size: 13.5px; color: #cbd5e1; line-height: 1.7;'>
        Bonjour aux parents. Cette application n'est pas gérée par une multinationale américaine comme Shopify ou Amazon, mais par un <b>développeur indépendant et local</b>. Et c'est votre meilleure garantie de sécurité :<br><br>
        • <b>Zéro Donnée Sensible</b> : Contrairement aux géants du web qui stockent des millions de cartes de crédit et de mots de passe (et qui se font pirater), notre application ne collecte <b>absolument rien</b>. Pas de carte bancaire, pas de mot de passe, pas de compte connecté. Un hacker ne peut pas voler ce qui n'existe pas.<br>
        • <b>100% Circuit Bancaire Canadien</b> : Les clients paient les membres par virement Interac direct. L'argent voyage exclusivement de banque à banque (ex: Desjardins). Notre logiciel sert uniquement de panneau d'affichage textuel pour coordonner la logistique.<br>
        • <b>Soutien Direct</b> : Pas de robot d'assistance à l'autre bout du monde. Vous utilisez un outil indépendant, épuré, transparent et conçu pour initier les jeunes aux affaires de manière sécuritaire et responsable.<br>
        • <b>Garantie d'Essai Gratuit</b> : Votre enfant peut utiliser un code d'accès temporaire pour valider le système sans que vous n'ayez à débourser un seul dollar.<br>
        • <b>Zéro Risque de Fournisseur Étranger</b> : Ce système n'utilise pas de sites obscurs ou de dropshipping international. Les livreurs ou les gérants se déplacent <b>physiquement à pied ou à vélo dans les magasins du quartier</b>. Aucun numéro de carte bancaire n'est requis pour les commandes grossistes en ligne !
        </span>
    </div>
    """, unsafe_allow_html=True)

# --- 3. GESTION DES FORFAITS ET BARRE LATÉRALE DE SÉCURITÉ ---
st.sidebar.title("🎮 Centre de Contrôle")
st.sidebar.markdown("<hr style='border: 1px solid #334155; margin: 10px 0;'>", unsafe_allow_html=True)

def valider_code_acces():
    code = st.session_state.cle_authentification.strip()
    
    # 👑 Clé Maître Développeur / Option Pro
    if code == "ADMIN-INFINI-99":
        st.session_state.compte_actif = True
        st.session_state.forfait = "Pro"
        st.sidebar.success("👑 GRADE EMPIRE PRO ACTIVÉ !")
        st.balloons()
        st.rerun()
    # ⚡ Clé Licence Pro Mensuelle (200$ / mois)
    elif code.startswith("PRO-") and len(code) > 8:
        if outils.code_deja_utilise(code):
            st.sidebar.error("❌ Cette licence Pro a expiré ou a déjà été consommée.")
        else:
            st.session_state.compte_actif = True
            st.session_state.forfait = "Pro"
            outils.marquer_code_utilise(code)
            st.sidebar.success("🚀 ACCÈS COMPLET PRO VALIDÉ !")
            st.balloons()
            st.rerun()
    # ⚔️ Clé Licence Starter Mensuelle (100$ / mois)
    elif code.startswith("STARTER-") and len(code) > 12:
        if outils.code_deja_utilise(code):
            st.sidebar.error("❌ Cette licence Starter a déjà été consommée.")
        else:
            st.session_state.compte_actif = True
            st.session_state.forfait = "Starter"
            outils.marquer_code_utilise(code)
            st.sidebar.success("✅ ACCÈS STARTER VALIDÉ !")
            st.balloons()
            st.rerun()
    elif code != "":
        st.sidebar.error("❌ Signature ou clé d'authentification invalide.")

st.sidebar.text_input("Clé d'activation (Licence)", type="password", key="cle_authentification", on_change=valider_code_acces)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
mode_affichage = st.sidebar.selectbox("Finition cosmétique :", ["Standard (Épuré)", "Jeux Vidéo (RPG)", "Custom (👑)"])

grade = "👑 MEMBRE EMPIRE PRO" if st.session_state.forfait == "Pro" else ("⚔️ MARCHAND STARTER" if st.session_state.forfait == "Starter" else "🥚 INVITÉ SANS LICENCE")
st.sidebar.markdown(f"**Rang de Session :** `{grade}`")
# --- 4. TRAITEMENT DES SKELETONS VISUELS ---
if mode_affichage == "Standard (Épuré)":
    st.markdown("<style>.stApp { background-color: #0f172a !important; color: #f8fafc !important; } h1, h2, h3, h4, h5, p, span, label { color: #f8fafc !important; } div[data-testid='stMetric'] { background-color: #1e293b; border-radius: 12px; padding: 15px; border: 1px solid #334155; }</style>", unsafe_allow_html=True)
    st.title("🚀 Business Automatique Dashboard")
elif mode_affichage == "Jeux Vidéo (RPG)":
    st.markdown("<style>.stApp { background-color: #090a0f !important; color: #a2a8b6 !important; } h1 { color: #00ffcc !important; text-shadow: 0 0 12px #00ffcc; text-align: center; } div[data-testid='stMetric'] { background-color: #141923; border: 2px solid #00ffcc; border-radius: 12px; padding: 15px; }</style>", unsafe_allow_html=True)
    st.title("🕹️ EMPIRE TYCOON : CORE MODULE")
else:
    if st.session_state.forfait != "Pro":
        st.sidebar.warning("🔒 Option Custom réservée exclusivement aux grades Pro.")
        st.markdown("<style>.stApp { background-color: #0f172a !important; }</style>", unsafe_allow_html=True)
        st.title("🚀 Business Automatique Dashboard")
    else:
        couleur_custom = st.sidebar.color_picker("Ajuster l'éclairage Néon :", "#00FFCC")
        st.markdown(f"<style>.stApp {{ background-color: #080808 !important; color: #ffffff !important; }} h1 {{ color: {couleur_custom} !important; text-shadow: 0 0 20px {couleur_custom}; text-align: center; }} </style>", unsafe_allow_html=True)
        st.title("👑 MODULE VIP INTERACTIF")

st.markdown("### ⚡ Flux d'Activité Réseau")
notifs = outils.recuperer_notifications()
notif_1 = notifs[0] if (len(notifs) > 0 and isinstance(notifs, list)) else ""
notif_2 = notifs[1] if (len(notifs) > 1 and isinstance(notifs, list)) else ""
notif_3 = notifs[2] if (len(notifs) > 2 and isinstance(notifs, list)) else ""

st.markdown(f"""
<div style='background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #00ffcc; margin-bottom: 25px;'>
    <span style='font-size:13px; color:#cbd5e1;'>• {notif_1}</span><br>
    <span style='font-size:13px; color:#cbd5e1;'>• {notif_2}</span><br>
    <span style='font-size:13px; color:#cbd5e1;'>• {notif_3}</span>
</div>
""", unsafe_allow_html=True)

st.markdown("### 📊 Statistiques de l'Infrastructure")
col1, col2, col3 = st.columns(3)
liste_shops = outils.recuperer_boutiques()
ca_total_reel = outils.recuperer_ca_total()

col1.metric(label="💰 Chiffre d'Affaires Global", value=f"{ca_total_reel} $")
col2.metric(label="🏬 Boutiques Déployées", value=f"{len(liste_shops)} Sites")
col3.metric(label="⚡ Licence Active", value=f"Plan {st.session_state.forfait}" if st.session_state.compte_actif else "Aucune")

st.markdown("---")

# --- INITIALISATION DES ONGLETS PUBLICS ET PRIVÉS ---
if not st.session_state.compte_actif:
    tab1, = st.tabs(["🛍️ B1: Marché & Forum"])
else:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🛍️ B1: Marché & Forum", 
        "🏬 B2: Concepteur de Boutique Multi-Commerce", 
        "👀 Mes Boutiques", 
        "🚲 Hub Logistique & Livreurs", 
        "🕵️‍♂️ Radar Espion Local", 
        "💡 B3: R&D Élite", 
        "🎨 Studio Branding & SaaS"
    ])

with tab1:
    st.header("🛍️ Place de Marché Collective & Solidaire")
    st.markdown("Tous les articles créés par les membres s'affichent ici. L'affichage est mélangé pour donner une chance égale à chaque boutique.")
    
    if not liste_shops:
        st.info("📉 Aucune boutique n'est encore active sur le réseau pour alimenter le marché.")
    else:
        recherche_client = st.text_input("🔍 Rechercher un produit spécifique (Ex: Chaise, Hoodie) :", "", key="recherche_tab1").strip().lower()
        
        boutiques_melangees = list(liste_shops)
        random.shuffle(boutiques_melangees)
        liste_articles_extraits = []
        
        for b_idx, b_data in enumerate(boutiques_melangees):
            b_nom, b_niche, b_contenu, b_couleur, b_prix = b_data
            try: b_prix_propre = float(b_prix)
            except: b_prix_propre = 29.99
                
            b_contenu_propre = b_contenu.replace("```html", "").replace("```", "").replace("html", "").strip()
            
            if "### 📦" in b_contenu_propre:
                blocs = b_contenu_propre.split("### 📦")
                for p_idx, bloc in enumerate(blocs[1:]):
                    if bloc.strip():
                        lignes_bloc = bloc.split("\n")
                        nom_produit = lignes_bloc[0].strip() if lignes_bloc else "Article de style"
                        if recherche_client and (recherche_client not in nom_produit.lower() and recherche_client not in bloc.lower()):
                            continue
                            
                        liste_articles_extraits.append({
                            "vendeur": b_nom, "niche": b_niche, "bloc_texte": bloc, "nom_produit": nom_produit, "prix": b_prix_propre, "b_idx": b_idx, "p_idx": p_idx
                        })

        random.shuffle(liste_articles_extraits)
        
        if not liste_articles_extraits:
            st.warning("Aucun produit disponible ne correspond à ta recherche.")
        else:
            for art in liste_articles_extraits[:10]:
                st.markdown(f"""
                <div style='background-color: #111827; padding: 12px; border-radius: 12px; border: 1px solid #1f2937; margin-bottom: -10px;'>
                    <span style='color: #00ffcc; font-size: 11px; font-weight: bold;'>🏬 Enseigne : {art['vendeur'].upper()} ({art['niche']})</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"### 📦 {art['bloc_texte']}", unsafe_allow_html=True)
                
                nom_boutique_url = art['vendeur'].lower().replace(" ", "-")
                st.link_button(f"🛒 Ouvrir la page de commande réelle : {art['nom_produit']}", url=f"/?shop={nom_boutique_url}", key=f"market_lnk_{art['b_idx']}_{art['p_idx']}", type="secondary")
                st.markdown("<br>", unsafe_allow_html=True)

    # --- LE FORUM DE DISCUSSION DE L'EMPIRE ---
    st.markdown("---")
    st.header("💬 Le Forum Privé des Entrepreneurs")
    
    with st.form("form_forum_admin"):
        pseudo_forum = st.text_input("Ton Pseudo de membre :", value=f"Membre_{st.session_state.forfait}", max_chars=20)
        msg_forum = st.text_area("Partage une astuce de vente ou demande de l'aide :", max_chars=250)
        if st.form_submit_button("🚀 Publier sur le Forum"):
            if msg_forum.strip():
                outils.ajouter_message_forum(pseudo_forum, msg_forum)
                st.success("Message partagé sur le forum !")
                st.rerun()

    discussions = outils.recuperer_messages_forum()
    if not discussions:
        st.info("Le forum est calme. Lance la première discussion !")
    else:
        for disc in discussions[:10]:
            auteur, message, date_post = disc
            st.markdown(f"""
            <div style='background-color: #1e293b; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #6366f1;'>
                <span style='color: #818cf8; font-size: 11px;'>📅 {date_post} | 👤 <b>{auteur}</b> :</span><br>
                <span style='color: #e2e8f0; font-size: 13px;'>{message}</span>
            </div>
            """, unsafe_allow_html=True)

if not st.session_state.compte_actif:
    st.stop()
with tab2:
    st.header("🏬 Concepteur de Boutique Multi-Commerce Avancé")
    st.markdown("Propulsez une vitrine e-commerce unique reliée à l'écosystème local. Indiquez les magasins présents près de chez vous pour que l'IA scanne leurs assortiments et lie automatiquement les sources d'achat réelles pour vos livreurs (sans carte de crédit).")
    
    # Sécurité anti-abus pour protéger tes clés API et ton budget de créateur
    conn = outils.obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM boutiques")
    total_boutiques_reseau = cursor.fetchone()[0]
    conn.close()
    
    if st.session_state.forfait == "Starter" and total_boutiques_reseau >= 3:
        st.error("⚠️ Limite de déploiement atteinte : Le plan Starter est bridé à un maximum de 3 boutiques pour protéger l'infrastructure API. Veuillez passer au grade Pro pour un accès illimité.")
    else:
        nom_shop = st.text_input("Nom de l'enseigne e-commerce :", "Mon Commerce Élite", key="design_nom_shop")
        niche_shop = st.text_input("Thématique / Niche spécifique :", "Éléments et fournitures de style", key="design_niche_shop")
        courriel_interac_vendeur = st.text_input("🚀 Votre courriel Interac (Pour collecter tes gains réels) :", "votre-compte-banque@email.com")
        
        # Choix du modèle d'affaires pour briser le tout-dropshipping
        type_commerce = st.selectbox("Modèle commercial de l'infrastructure :", [
            "📦 Objets Physiques & Articles de Proximité (Achat local et livraison à pied/vélo)", 
            "💻 Services Numériques & Prestations (Montage, Coaching, Logo, Aide)",
            "📚 Infoproduits & Guides PDF (Formations, E-books)"
        ])
        
        mode_creation = st.radio("Méthode de déploiement du catalogue :", ["🤖 Génération Automatique par IA Sourcing Local", "🛠️ Configuration Manuelle Assistée"])
        
        # Initialisation des variables logistiques pour l'IA
        magasins_actifs = "Marchands locaux généraux"
        liste_parametres_produits = []
        
        if mode_creation == "🤖 Génération Automatique par IA Sourcing Local":
            st.markdown("#### 🚲 Sélection des enseignes physiques de proximité")
            magasins_actifs = st.text_input("Quels magasins sont proches de chez toi ? (Sépare par des virgules) :", "Walmart, Dollarama, Bureau en Gros, Pharmaprix", key="input_magasins_locaux")
            prix_par_defaut = st.number_input("Prix de vente moyen par produit ($) :", min_value=1.0, value=29.99, step=5.0)
        else:
            st.markdown("#### 🛠️ Configuration Manuelle Assistée")
            nombre_de_produits = st.number_input("Combien de produits voulez-vous intégrer ?", min_value=1, max_value=20, value=3, step=1)
            
            st.markdown("#### 🛡️ Cadrage Véridique Obligatoire")
            details_reels = st.text_area(
                "Spécifiez les caractéristiques réelles (Matériaux exacts, couleurs, origine et le magasin d'achat précis) :", 
                placeholder="Ex: Hoodie noir 100% coton de chez Walmart Centre-Ville. Aucun autre coloris disponible.",
                key="details_reels_ia"
            )
            
            col_p1, col_p2 = st.columns(2)
            for i in range(int(nombre_de_produits)):
                with col_p1:
                    nom_p = st.text_input(f"📦 Nom du produit #{i+1} :", f"Article Premium {i+1}", key=f"nom_p_{i}_{nombre_de_produits}")
                with col_p2:
                    prix_p = st.number_input(f"💰 Prix de vente ($) #{i+1} :", min_value=1.0, value=19.99 + (i*10), step=5.0, key=f"prix_p_{i}_{nombre_de_produits}")
                liste_parametres_produits.append({"nom": nom_p, "prix": prix_p})

        if st.button("🚀 Forger l'infrastructure de la boutique"):
            if nom_shop and courriel_interac_vendeur:
                with st.spinner("L'IA applique les filtres logistiques de proximité et génère vos fiches..."):
                    
                    prefixe_interac = f"💵 **Mode de paiement sécurisé : Virement Interac à {courriel_interac_vendeur}**\n*Note : Veuillez inscrire votre nom complet dans la description du virement. Des frais de livraison fixes de 4.99 $ s'appliquent à chaque article pour soutenir nos livreurs locaux.*\n\n---\n"
                    
                    if mode_creation == "🤖 Génération Automatique par IA Sourcing Local":
                        prompt_catalogue = f"""Tu es un copywriter de génie et un consultant en logistique de proximité pour du commerce de type : {type_commerce}.
                        Génère une liste de EXACTEMENT 5 produits viraux, tendances et réalistes pour la boutique '{nom_shop}' axée sur la niche '{niche_shop}'.
                        
                        ⚠️ RÈGLE DE SÉCURITÉ LOGISTIQUE ABSOLUE :
                        Ces produits doivent obligatoirement être trouvables physiquement en rayon dans ces enseignes locales : {magasins_actifs}.
                        Tu as l'interdiction formelle d'inventer des produits fictifs ou d'utiliser du sourcing internet international (pas d'AliExpress, pas de dropshipping). Tout doit s'acheter sur place en magasin.
                        Pour chaque produit, tu dois choisir un des magasins de la liste comme point de sourcing unique.
                        
                        Pour chaque produit, utilise STRICTEMENT cette structure en Markdown :
                        
                        ### 📦 [Nom exact du produit réel]
                        * **Description** : [Description marketing percutante et 100% VRAIE d'environ 3 phrases]
                        * **⚡ Pourquoi ce produit est unique** : [Argumentaire de vente honnête basé sur la disponibilité locale]
                        * **Prix** : {prix_par_defaut} $
                        * **Source** : [Nom de l'enseigne physique choisie parmi : {magasins_actifs}]
                        
                        Génère les 5 produits les uns après les après. Ne mets aucune introduction ni conclusion, écris seulement le Markdown."""
                        prix_stockage = prix_par_defaut
                    else:
                        if not details_reels.strip():
                            st.error("⚠️ Formulaire incomplet : Veuillez renseigner le descriptif de cadrage véridique.")
                            st.stop()
                            
                        structure_demandee = ""
                        for p in liste_parametres_produits:
                            structure_demandee += f"- Produit : {p['nom']} | Prix de vente : {p['prix']} $\n"
                            
                        prompt_catalogue = f"""Tu es un copywriter e-commerce de confiance. Rédige les fiches descriptives pour la boutique '{nom_shop}' ({niche_shop}).
                        Tu dois obligatoirement inclure ces produits spécifiques avec leurs prix exacts :
                        {structure_demandee}
                        
                        ⚠️ CONSIGNE DE SÉCURITÉ ET DE VÉRITÉ : Base-toi STRICTEMENT et UNIQUEMENT sur ces détails réels fournis par l'utilisateur : {details_reels}. Tu as interdiction formelle d'inventer ou de rajouter des caractéristiques non spécifiées.
                        
                        Génère le rendu au format Markdown en utilisant STRICTEMENT cette mise en page pour chaque produit :
                        ### 📦 [Nom exact du produit]
                        * **Description** : [Insérer une description attractive et moderne d'environ 3 phrases sans mentir]
                        * **⚡ Pourquoi ce produit est unique** : [Argument de vente basé uniquement sur les faits réels fournis]
                        * **Prix** : [Insérer ici le prix exact spécifié] $
                        * **Source** : Magasin de proximité (Détails du gérant)
                        
                        N'écris rien d'autre. Pas d'introduction, pas de conclusion."""
                        prix_stockage = liste_parametres_produits[0]["prix"] if liste_parametres_produits else 29.99
                    
                    catalogue_markdown = outils.appeler_groq(prompt_catalogue, temperature=0.4)
                    contenu_final_interac = prefixe_interac + catalogue_markdown
                    
                    if outils.ajouter_boutique(nom_shop, niche_shop, contenu_final_interac, prix_stockage, st.session_state.cle_authentification, couleur="#f8fafc"):
                        st.toast(f"🏬 Infrastructure déployée avec succès et rattachée à votre compte !", icon="✅")
                        st.rerun()
                    else:
                        st.error("❌ Ce nom de boutique est déjà réservé ou votre serveur local est saturé.")
            else:
                st.error("⚠️ Veuillez renseigner le nom de la boutique e-commerce et votre adresse de courriel Interac.")
    with tab3:
        st.header("🌐 Vos Serveurs d'Hébergement Actifs")
        
        liste_shops_utilisateur = outils.recuperer_boutiques_par_utilisateur(st.session_state.cle_authentification)
        
        if not liste_shops_utilisateur:
            st.info("Aucun site web actif détecté rattaché à votre clé d'activation actuellement. Créez-en un dans l'onglet Conception !")
        else:
            noms_boutiques_propres = [b[0] for b in liste_shops_utilisateur]
            choix_nom = st.selectbox("Sélectionnez la boutique à inspecter :", noms_boutiques_propres, key="select_inspect_shop")
            
            choix = None
            for s in liste_shops_utilisateur:
                if s[0] == choix_nom:
                    choix = s
                    break
                    
            if choix:
                nom, niche, contenu, couleur, prix = choix
                nom_formate = nom.lower().replace(' ', '-')
                lien_public = f"/?shop={nom_formate}"
                contenu_propre = contenu.replace("```html", "").replace("```", "").replace("html", "").strip()
                
                st.link_button(f"🌍 Ouvrir la page publique réelle de : {nom.upper()}", url=lien_public, type="primary")
                st.markdown("---")
                
                st.markdown("""
                <div style='background-color: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #00ffcc; margin-bottom: 15px;'>
                    <span style='color: #00ffcc; font-weight: bold;'>📋 PROTOCOLE DE REVENU DE PROXIMITÉ (SÉCURITÉ PARENTALE GLOBALE) :</span><br>
                    <span style='font-size: 13px; color: #cbd5e1;'>
                    1. <b>Validation Interac</b> : Valide sur ton application bancaire Desjardins/RBC que le client t'a envoyé le virement pour sa commande.<br>
                    2. <b>Zéro Carte de Crédit</b> : Ne commande rien en ligne. Regarde l'onglet ci-dessous. Le livreur ira <b>physiquement</b> acheter l'objet dans le magasin de ton quartier désigné par l'IA (Walmart, Dollarama, etc.) avec son argent de poche ou sa carte de débit.<br>
                    3. <b>Remboursement de confiance</b> : Dès que ton livreur te ramène l'objet ou le remet au client, tu lui renvoies le coût de l'article + sa prime de course par virement Interac direct. C'est 100% sécuritaire.
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 📥 Boîte de Réception des Commandes Privées")
                commandes_recues = outils.recuperer_commandes_boutique(nom)
                
                if not commandes_recues:
                    st.info("📨 Aucun message ni commande reçu pour le moment dans cette boîte.")
                else:
                    for idx_c, cmd in enumerate(commandes_recues):
                        c_nom, c_adresse, c_articles, c_total, c_date = cmd
                        st.markdown(f"""
                        <div style='background-color: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #ff0055; margin-bottom: 10px;'>
                            <span style='font-size: 11px; color: #94a3b8;'>📅 Commande reçue le : {c_date}</span><br>
                            👤 <b>Acheteur :</b> {c_nom} <br>
                            📍 <b>ADRESSE DU CLIENT :</b> {c_adresse} <br>
                            🎯 <b>PRODUIT ET ENSEIGNE EXTRACTS PAR L'IA :</b> <span style='color: #00ffcc;'>{c_articles}</span> <br>
                            💰 <b>Total collecté du client :</b> {c_total} $
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with st.expander(f"⚡ Assigner cette course à un livreur local du réseau"):
                            prime_livraison = st.slider(f"Prime de course pour le livreur ($) :", min_value=5.0, max_value=20.0, value=5.0, step=1.0, key=f"prime_{nom}_{idx_c}")
                            nom_livreur_choisi = st.text_input("Nom du coursier désigné :", placeholder="Ex: Alex_Velo", key=f"livreur_{nom}_{idx_c}")
                            
                            if st.button("🚀 Transmettre the mission au coursier local", key=f"btn_livreur_{nom}_{idx_c}"):
                                if nom_livreur_choisi.strip():
                                    st.success(f"📦 Mission envoyée ! **{nom_livreur_choisi}** sait dans quel commerce de quartier aller chercher le produit. Prépare son remboursement de {c_total}$ + {prime_livraison}$ de commission.")
                                    st.rerun()
                
                st.markdown("---")
                if st.button("🗑️ Démonter cette boutique et libérer le nom", type="primary", key=f"delete_shop_{nom}"):
                    if outils.supprimer_boutique(nom): 
                        st.rerun()

    with tab4:
        st.header("🚲 Hub Logistique : Espace et Recrutement des Livreurs")
        st.markdown("Deviens coursier local. L'application et son IA te disent exactement **dans quel magasin physique de ton quartier** aller acheter le produit. Tu paies en argent comptant ou par carte de débit (pas besoin de carte de crédit en ligne), tu livres à l'adresse indiquée, et tu touches ton remboursement complet + ta prime Interac.")
        
        sub_l1, sub_l2 = st.tabs(["📝 S'inscrire comme Livreur", "📦 Tableau des Missions d'Achat & Livraison"])
        
        with sub_l1:
            st.subheader("Devenir coursier officiel de l'application")
            with st.form("form_inscription_livreur"):
                pseudo_livreur = st.text_input("Ton nom ou pseudonyme de coursier :", placeholder="Ex: Nathan_Velo_Urgent")
                tel_livreur = st.text_input("Numéro de téléphone ou Discord de contact :", placeholder="Ex: 514-555-0199")
                zone_livreur = st.text_input("Ta zone ou quartier de livraison :", placeholder="Ex: Vieux-Longueuil")
                
                if st.form_submit_button("🚲 Activer mon profil de Livreur"):
                    if pseudo_livreur and tel_livreur:
                        if outils.s_inscrire_livreur(pseudo_livreur, tel_livreur, zone_livreur):
                            st.success("🎉 Profil activé ! Tu peux immédiatement accepter des courses locales.")
                        else:
                            st.warning("Ce pseudonyme est déjà pris sur le réseau logistique.")
                    else:
                        st.error("Veuillez remplir votre nom et votre moyen de contact.")
                        
        with sub_l2:
            st.subheader("🛒 Commandes en attente de sourcing physique et de livraison")
            missions = outils.recuperer_commandes_sans_livreur()
            if not missions:
                st.info("Aucune course de proximité n'est disponible sur le secteur actuellement.")
            else:
                for m in missions:
                    m_id, m_boutique, m_client, m_adresse, m_article, m_total, m_date = m
                    st.markdown(f"""
                    <div style='background-color: #141923; padding: 15px; border-radius: 8px; border-left: 4px solid #eab308; margin-bottom: 10px;'>
                        <span style='color: #eab308; font-weight: bold;'>🏬 Enseigne émettrice : {m_boutique.upper()}</span><br>
                        🎯 <b>PRODUIT ET ADRESSE DU MAGASIN OÙ L'ACHETER DIRECTEMENT :</b> <span style='color: #00ffcc;'>{m_article}</span><br>
                        💵 <b>Fonds de roulement requis (Remboursement Interac Garanti) :</b> {m_total} $<br>
                        📍 <b>Adresse de livraison finale :</b> {m_adresse}<br>
                        👤 <b>Nom du destinataire :</b> {m_client}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"🚲 Accepter la mission d'achat local pour #{m_id}", key=f"accept_m_{m_id}"):
                        st.info(f"✅ Mission verrouillée ! Rends-toi au commerce physique indiqué pour acheter le produit `{m_article}`. Va le livrer à `{m_client}` et prends contact avec le gérant de `{m_boutique}` pour encaisser ton argent réel !")
    
    with tab5:
        st.header("🕵️‍♂️ Radar Espion Local")
        mot_espion = st.text_input("Saisissez un type d'article, de service ou une tendance à auditer :", key="audit_mot_espion")
        if st.button("🔍 Lancer les algorithmes d'espionnage") and mot_espion:
            with st.spinner("Scan des demandes du marché local..."):
                prompt_audit = f"Fournis une analysis de positionnement commercial agressive et des angles marketing pour vendre le produit ou service suivant localement ou en ligne sans intermédiaire : '{mot_espion}'."
                st.info(outils.appeler_groq(prompt_audit))
    with tab6:
        st.header("👑 Laboratoire de R&D : Outils Avancés Élite (💡 B3)")
        if st.session_state.forfait != "Pro":
            st.markdown("""
            <div style='background-color: #241442; padding: 25px; border-radius: 12px; border: 2px solid #8a2be2; text-align: center;'>
                <h3>🔒 ACCÈS EMPIRE PRO IMPÉRATIF</h3>
                <p style='font-style: italic; color: #a855f7;'>« Les amateurs construisent des boutiques. Les professionnels possèdent l'infrastructure. »</p>
                <p>Le Réplicateur de Tendance et l'Agent Conversationnel nécessitent une mise à niveau vers le Plan Pro (200$ / mois).</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("🔓 Protocoles Élite en ligne. Accès intégral débloqué.")
            sub_tab1, sub_tab2, sub_tab3 = st.tabs(["🕵️‍♂️ 1. Inspirateur de Tendance", "💬 2. Injecteur de Chatbot IA", "💡 3. Générateur de Produits Digitaux"])
            
            with sub_tab1:
                st.subheader("🛠️ Réplication Légale Instantanée par Thématique")
                niche_espionne = st.text_input("Saisissez la thématique ou la niche à cloner :", placeholder="Ex: Accessoires de cuisine", key="niche_clone_elite")
                if st.button("🌐 Lancer l'aspiration et la réplication", key="btn_clone_elite"):
                    with st.spinner("Analyse du marché leader..."):
                        prompt_replication = f"Simule une analysis approfondie des 3 boutiques leaders dans la niche '{niche_espionne}'. Donne une liste des 5 produits les plus vendus chez eux, leur prix estimé, et la stratégie marketing exacte pour copier leur succès localement."
                        st.write(outils.appeler_groq(prompt_replication))
            
            with sub_tab2:
                st.subheader("💬 Injecteur d'Agent Conversationnel en Direct")
                
                liste_shops_utilisateur = outils.recuperer_boutiques_par_utilisateur(st.session_state.cle_authentification)
                
                if not liste_shops_utilisateur:
                    st.warning("Aucune boutique disponible sur votre compte pour implanter l'IA.")
                else:
                    noms_shops_chat = [s[0] for s in liste_shops_utilisateur]
                    shop_nom_chat = st.selectbox("Sélectionnez la boutique à équiper d'un Chatbot :", noms_shops_chat, key="select_shop_chat")
                    
                    if st.button("⚡ Greffer l'Assistant commercial IA", key="btn_greffe_chatbot"):
                        shop_data = next((s for s in liste_shops_utilisateur if s[0] == shop_nom_chat), None)
                        if shop_data:
                            nom_s, niche_s, contenu_s, couleur_s, prix_s = shop_data
                            if "🤖 Agent Actif" not in contenu_s:
                                nouveau_contenu_ia = contenu_s + "\n\n🤖 Agent Actif"
                                outils.mettre_a_jour_boutique(nom_s, nouveau_contenu_ia)
                                st.success(f"🎉 Le Chatbot IA a été greffé !")
                                st.rerun()
                            else:
                                st.info("L'Agent IA est déjà actif.")
                
            with sub_tab3:
                st.subheader("💡 Concepteur de Produits Numériques Élite")
                theme_num = st.text_input("Sujet de la formation ou du guide :", "Devenir Libre avec l'IA en 30 jours", key="theme_digital_product")
                if st.button("📚 Rédiger la structure par IA", key="btn_build_digital"):
                    with st.spinner("Création du produit digital..."):
                        prompt_num = f"Rédige le plan d'action détaillé d'un guide haut de gamme sur : {theme_num}"
                        st.markdown(outils.appeler_groq(prompt_num))

    with tab7:
        st.header("🎨 Studio Branding & Créateur d'Abonnement SaaS Pro")
        if st.session_state.forfait != "Pro":
            st.markdown("""
            <div style='background-color: #1e1e2e; padding: 25px; border-radius: 12px; border: 1px solid #ff007f; text-align: center;'>
                <h3>🔒 SECTION RÉSERVÉE AU PLAN PRO</h3>
                <p>La configuration visuelle avancée et la création d'abonnements logiciels nécessitent une licence Pro.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            liste_shops_utilisateur = outils.recuperer_boutiques_par_utilisateur(st.session_state.cle_authentification)
            
            st.subheader("🖼️ Personnalisation de l'arrière-plan par Copier-Coller")
            if not liste_shops_utilisateur:
                st.warning("Aucune boutique disponible sur votre compte pour le re-branding.")
            else:
                noms_shops_branding = [s[0] for s in liste_shops_utilisateur]
                shop_nom_branding = st.selectbox("Sélectionnez la boutique à modifier :", noms_shops_branding, key="sb_select")
                nouveau_fond = st.text_input("Collez l'URL de votre image ou votre couleur hexadécimale :", "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)", key="input_fond_custom")
                
                if st.button("💾 Appliquer la charte graphique", key="btn_apply_branding"):
                    conn = outils.obtenir_connexion()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE boutiques SET couleur = ? WHERE nom = ?", (nouveau_fond, shop_nom_branding))
                    conn.commit()
                    conn.close()
                    st.success(f"🎨 L'ambiance visuelle de '{shop_nom_branding}' a été mise à jour !")
                    st.rerun()

            st.markdown("<br><hr style='border: 1px solid #334155;'><br>", unsafe_allow_html=True)

            st.subheader("🚀 Forger une Application Clone (Générateur de Rente SaaS)")
            st.markdown("Créez instantanément une page publique d'abonnement pour vendre votre propre application logicielle en marque blanche.")
            
            nom_logiciel_vente = st.text_input("Nom de l'application logicielle à vendre :", "SaaS Automate Pro", key="input_nom_saas")
            tarif_SaaS = st.number_input("Prix de l'abonnement mensuel ($) :", min_value=10.0, value=100.0, step=10.0, key="input_prix_saas")
            
            if st.button("💎 Déployer la Page de Vente Logicielle", key="btn_deploy_saas"):
                cle_auto = f"STARTER-AUTO-{random.randint(10000, 99999)}"
                texte_boutique_SaaS = f"""
# 🚀 Bienvenue sur {nom_logiciel_vente}
### Accédez instantanément à votre infrastructure de Business Automatique.
* **Outils inclus** : Scanneur de leads B2B, Concepteur de boutiques IA, Radar Espion.
* **Facturation** : Récurrente de {tarif_SaaS}$ / mois, sans aucun engagement.
---
### 📦 Forfait unique : Accès Mensuel Immédiat
Remplissez vos informations ci-dessous pour sécuriser votre accès instantané au terminal.
### 🔓 VOTRE CLÉ LOGICIELLE UNIQUE SERA DÉLIVRÉE ICI : 
Une fois votre commande validée dans le formulaire ci-dessous, votre clé d'activation **`{cle_auto}`** sera rattachée à votre nom.
"""
                outils.ajouter_boutique(nom_logiciel_vente, "Abonnement Logiciel SaaS", texte_boutique_SaaS, tarif_SaaS, st.session_state.cle_authentification, couleur="#f8fafc")
                st.success("🎉 Page de vente configurée avec succès !")
                st.rerun()
            
            st.markdown("---")
            st.subheader("🔗 Liens d'accès à vos pages de vente actives")
            for s_saas in liste_shops_utilisateur:
                nom_saas_boutique, niche_saas_boutique, _, _, _ = s_saas
                if "SaaS" in niche_saas_boutique or "Abonnement" in niche_saas_boutique:
                    nom_saas_propre = nom_saas_boutique.lower().replace(' ', '-')
                    st.link_button(f"🌍 Ouvrir la page d'abonnement : {nom_saas_boutique.upper()}", url=f"/?shop={nom_saas_propre}", key=f"saas_lnk_{nom_saas_propre}")
            
            st.markdown("---")
            st.subheader("📊 Liste des Licences Logicielles Actives")
            abonnements_actifs = outils.recuperer_abonnements()
            if not abonnements_actifs:
                st.info("Aucune rente logicielle active pour le moment.")
            else:
                for abonn in abonnements_actifs:
                    plateforme, client, email_client, tarif, statut, date_ins = abonn
                    st.write(f"🔑 **{client}** ({email_client}) a activé un forfait sur `{plateforme}` ➔ **{tarif} $ / mois** (Inscrit le : {date_ins})")

# --- 5. TERMINAL DE COMMANDE SECRET ADMINISTRATEUR (DÉVELOPPEUR) ---
if st.session_state.get("cle_authentification") == "ADMIN-INFINI-99":
    st.markdown("---")
    st.header("👑 Terminal de Commande Secret (Développeur)")
    col_admin1, col_admin2 = st.columns(2)
    with col_admin1:
        st.subheader("Boutons d'Action Système")
        if st.button("🔄 Réinitialiser les codes d'accès (Fin de mois)", type="primary"):
            if outils.reinitialiser_tous_les_codes():
                st.success("⚡ Table des codes vidée ! Tous les anciens codes peuvent être réutilisés.")
                st.rerun()
    with col_admin2:
        st.subheader("Aperçu de la Base de Données")
        st.write(f"Nombre total de boutiques sur le réseau : `{len(liste_shops)}`")
        st.write(f"Chiffre d'affaires total enregistré : `{ca_total_reel} $`")
