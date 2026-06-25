import streamlit as st
import outils
import re
import random

# Initialisation automatique de l'infrastructure de la base SQLite locale
outils.initialiser_base_de_donnees()

# Initialisation sécurisée du panier virtuel et des variables d'état
if "panier_client" not in st.session_state:
    st.session_state.panier_client = []
if "compte_actif" not in st.session_state: 
    st.session_state.compte_actif = False
if "forfait" not in st.session_state: 
    st.session_state.forfait = "Aucun"

# --- 1. ROUTAGE D'URL PUBLIC POUR LES VRAIS CLIENTS ---
query_params = st.query_params

if "shop" in query_params:
    shop_public = query_params["shop"]
    liste_shops_publics = outils.recuperer_boutiques()
    boutique_trouvee = None
    
    # Recherche de la boutique demandée par le lien unique
    for s in liste_shops_publics:
        if s[0].lower().replace(" ", "-") == shop_public.lower():
            boutique_trouvee = s
            break
            
    if boutique_trouvee:
        nom, niche, contenu, couleur, prix_bdd = boutique_trouvee
        
        try:
            prix_bdd_propre = float(prix_bdd)
        except (ValueError, TypeError):
            prix_bdd_propre = 0.0
        
        # Nettoyage des balises de code générées par l'IA
        contenu_client = contenu.replace("```html", "").replace("```", "").replace("html", "").strip()

        # DESIGN DE LA VITRINE CLIENT (Habillage personnalisé par le Studio Branding)
        fond_branding = couleur if (couleur and not "@" in couleur) else "#f8fafc"
        st.markdown(f"""
        <style>
        .stApp {{ background: {fond_branding} !important; color: #0f172a !important; }}
        h1, h2, h3, h4, h5, p, span, label, div {{ color: #0f172a !important; }}
        
        div[data-testid="stForm"], .bloc-panier {{ 
            background-color: #ffffff !important; 
            border: 2px solid #e2e8f0 !important; 
            border-radius: 16px !important; 
            padding: 25px !important;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1) !important;
            margin-bottom: 20px;
        }}
        
        .stButton>button {{
            background-color: #00ffcc !important;
            color: #0f172a !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            border: none !important;
        }}
        input {{ background-color: #ffffff !important; color: #0f172a !important; border: 1px solid #cbd5e1 !important; }}
        </style>
        """, unsafe_allow_html=True)
        
        st.title(f"🏬 {nom.upper()}")
        st.subheader(f"✨ Vitrine Officielle : {niche}")
        st.markdown("---")
        # INTERPRÉTATION GRAPHIQUE DU CATALOGUE
        if "### 📦" in contenu_client:
            blocs_produits = contenu_client.split("### 📦")
            for idx, bloc in enumerate(blocs_produits[1:]):
                if bloc.strip():
                    lignes_bloc = bloc.split("\n")
                    nom_produit = lignes_bloc[0].strip()
                    
                    trouver_prix = re.search(r"Prix\s*:\s*([\d[\s,\.]*\d+)", bloc, re.IGNORECASE)
                    if trouver_prix:
                        prix_texte = trouver_prix.group(1).replace(" ", "").replace(",", ".")
                        try:
                            prix_chiffre = float(prix_texte)
                        except ValueError:
                            prix_chiffre = prix_bdd_propre
                    else:
                        prix_chiffre = prix_bdd_propre
                    
                    st.markdown(f"### 📦 {bloc}", unsafe_allow_html=True)
                    
                    if st.button(f"🛒 Ajouter au panier : {nom_produit}", key=f"btn_ajout_{idx}"):
                        st.session_state.panier_client.append({"nom": nom_produit, "prix": prix_chiffre, "vendeur": nom})
                        st.toast(f"✅ {nom_produit} ajouté !", icon="🛒")
        else:
            st.markdown(contenu_client)

        st.markdown("---")
        st.markdown("## 🛒 Votre Panier d'Achat")
        
        if not st.session_state.panier_client:
            st.info("Votre panier est vide. Sélectionnez des articles ci-dessus.")
            total_commande = 0.0
        else:
            total_commande = 0.0
            st.markdown("<div class='bloc-panier'>", unsafe_allow_html=True)
            for idx_p, item in enumerate(st.session_state.panier_client):
                col_item1, col_item2 = st.columns(2)
                with col_item1:
                    st.write(f"🔹 **{item['nom']}** — {item['prix']} $")
                with col_item2:
                    if st.button("❌ Retirer", key=f"del_item_{idx_p}"):
                        st.session_state.panier_client.pop(idx_p)
                        st.rerun()
                total_commande += item['prix']
            
            st.markdown(f"### 💵 Total des articles : {round(total_commande, 2)} $")
            st.caption("💡 Un livreur local de notre réseau prendra en charge votre commande.")
            if st.button("🧹 Vider le panier"):
                st.session_state.panier_client = []
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.panier_client:
            st.markdown("### ⚡ Commander en 1-Clic")
            with st.form("achat_client_form"):
                nom_client = st.text_input("Votre nom complet :", placeholder="Ex: Jean Tremblay")
                adresse_client = st.text_input("Votre adresse de livraison :", placeholder="Ex: 456 rue Principale, Montréal")
                
                texte_bouton = f"🔥 Valider la commande ({round(total_commande, 2)} $)"
                if st.form_submit_button(texte_bouton):
                    if nom_client and adresse_client:
                        for item in st.session_state.panier_client:
                            outils.enregistrer_commande_interne(
                                nom_boutique=item.get('vendeur', nom),
                                nom_client=nom_client,
                                adresse=adresse_client,
                                commande=item['nom'],
                                total=item['prix']
                            )
                        st.session_state.panier_client = []
                        st.balloons()
                        st.success("🎉 Commande enregistrée ! Attendez la validation de la boutique.")
                        st.rerun()
                    else:
                        st.error("⚠️ Veuillez remplir votre nom et votre adresse.")
        st.stop()
# --- 2. CONFIGURATION DE SESSION ADMINISTRATEUR ---
if "compte_actif" not in st.session_state: st.session_state.compte_actif = False
if "forfait" not in st.session_state: st.session_state.forfait = "Aucun"

# 🔥 BLOC SÉCURITÉ PARENTALE ET TRANSPARENCE AVANT AUTHENTIFICATION
if not st.session_state.compte_actif:
    st.markdown("""
    <div style='background-color: #111827; padding: 20px; border-radius: 12px; border: 1px solid #1f2937; text-align: center; margin-bottom: 20px;'>
        <h4 style='color: #00ffcc; margin: 0;'>💡 PROTOCOLE CENTRAL D'ACTIVATION</h4>
        <p style='color: #9ca3af; font-size: 14px; margin: 5px 0 0 0;'>« L'application te donne les outils, mais c'est toi qui gères le réseau local. »</p>
    </div>
    
    <div style='background-color: #1e293b; padding: 20px; border-radius: 12px; border-left: 5px solid #3b82f6; margin-bottom: 25px;'>
        <h5 style='color: #3b82f6; margin-top: 0;'>🛡️ SECTION SÉCURITÉ PARENTALE (Lettre ouverte du créateur)</h5>
        <span style='font-size: 13px; color: #cbd5e1; line-height: 1.6;'>
        Bonjour aux parents. Notre application ne collecte <b>absolument aucune donnée sensible</b>. Pas de carte bancaire stockée, pas de mot de passe à risque. Tout est transparent :<br><br>
        • <b>Zéro Risque de Fournisseur Étranger</b> : Ce système n'utilise pas de sites obscurs ou de dropshipping international. Vos enfants collaborent avec un réseau de <b>livreurs locaux inscrits sur l'application</b>.<br>
        • <b>Transactions de Banque à Banque</b> : Les clients paient directement par virement Interac sécurisé. Le logiciel sert uniquement de panneau d'affichage textuel pour coordonner la logistique.<br>
        • <b>Éducation Commerciale</b> : Un outil parfait, épuré et sécuritaire pour initier les jeunes à la gestion d'entreprise, à la comptabilité et à la logistique de livraison locale de façon responsable.<br>
        • <b>Garantie d'Essai Gratuit</b> : Votre enfant peut tester l'infrastructure sans frais avec un code d'accès temporaire pour s'assurer que le modèle lui convient.
        </span>
    </div>
    """, unsafe_allow_html=True)

# --- 3. GESTION DES FORFAITS ET BARRE LATÉRALE DE SÉCURITÉ ---
st.sidebar.title("🎮 Centre de Contrôle")
st.sidebar.markdown("---")

def valider_code_acces():
    code = st.session_state.cle_authentification.strip()
    
    # 👑 Clé Maître Développeur / Option Pro (Pour tes propres tests réels et gains)
    if code == "ADMIN-INFINI-99":
        st.session_state.compte_actif = True
        st.session_state.forfait = "Pro"
        st.sidebar.success("👑 MODE CRÉATEUR MAÎTRE ACTIVÉ !")
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

st.sidebar.text_input("Clé d'activation (Licence Mensuelle)", type="password", key="cle_authentification", on_change=valider_code_acces)
st.sidebar.markdown("---")
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
# Le marché est sorti de la restriction pour que tout le monde (même non-abonné) puisse le voir !
if not st.session_state.compte_actif:
    tab1, = st.tabs(["🛍️ B1: Marché & Forum"])
else:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🛍️ B1: Marché & Forum", "🏬 B2: Concepteur de Boutique IA", "👀 Mes Boutiques", 
        "🕵️‍♂️ Radar Espion", "💡 B3: R&D Élite", "🎨 Studio Branding", "💎 Rente Réelle"
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
                        nom_produit = bloc.split("\n")[0].strip()
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
                
                # Lien direct pour commander en situation réelle sur cette boutique
                nom_boutique_url = art['vendeur'].lower().replace(" ", "-")
                st.link_button(f"🛒 Ouvrir la page de commande réelle : {art['nom_produit']}", url=f"/?shop={nom_boutique_url}")
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

# Arrêt de l'exécution ici si la personne n'est pas abonnée (elle ne verra que le marché public)
if not st.session_state.compte_actif:
    st.stop()
with tab2:
    st.header("🏬 Concepteur de Boutique Multi-Commerce")
    st.markdown("Propulsez une vitrine e-commerce unique. Configurez les détails réels pour empêcher l'IA d'inventer de fausses caractéristiques.")
    
    # Sécurité anti-abus pour protéger tes clés API et ton budget
    conn = outils.obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM boutiques")
    total_boutiques_reseau = cursor.fetchone()[0]
    conn.close()
    
    if st.session_state.forfait == "Starter" and total_boutiques_reseau >= 3:
        st.error("⚠️ Limite atteinte : Le plan Starter est bridé à un maximum de 3 boutiques pour protéger l'infrastructure API. Passez au plan Pro pour un déploiement illimité.")
    else:
        nom_shop = st.text_input("Nom de l'enseigne commerciale :", "Mon Commerce Élite", key="design_nom_shop")
        niche_shop = st.text_input("Thématique / Niche :", "Éléments et accessoires de style", key="design_niche_shop")
        courriel_interac_vendeur = st.text_input("🚀 Votre courriel Interac (Pour recevoir tes gains réels) :", "ton-email@banque.com")
        
        # Choix du type de commerce (Fin du tout-dropshipping)
        type_commerce = st.selectbox("Type de modèle d'affaires :", [
            "📦 Objets Réels & Artisanat Local (Livrés en personne ou par Postes Canada)", 
            "💻 Services Numériques & Prestations (Montage, Coaching, Logo, Aide)",
            "📚 Infoproduits & Guides PDF (Formations, E-books)"
        ])
        
        # FORMULAIRE DE PRÉCISION STRICT (Anti-mensonge de l'IA)
        st.markdown("#### 🛡️ Cadrage Véridique des Produits")
        details_reels = st.text_area(
            "Décris les caractéristiques exactes, matériaux, limites et détails réels de tes produits :", 
            placeholder="Ex: Mes chaises sont strictement en plastique rigide bleu, elles ne sont PAS pliables et mesurent 80cm de haut. Soyez précis pour guider l'IA.",
            key="details_reels_ia"
        )
        
        mode_creation = st.radio("Méthode de rédaction du catalogue :", ["🤖 Génération Automatique par IA (10 Produits)", "🛠️ Configuration Manuelle Assistée"])
        liste_parametres_produits = []
        
        if mode_creation == "🤖 Génération Automatique par IA (10 Produits)":
            st.info("⚡ L'IA va structurer un catalogue de 10 produits optimisés respectant STRICTEMENT tes détails réels.")
            nombre_de_produits = 10
            prix_par_defaut = st.number_input("Prix de vente moyen par produit ($) :", min_value=1.0, value=39.99, step=5.0)
        else:
            nombre_de_produits = st.number_input("Combien de produits voulez-vous intégrer ?", min_value=1, max_value=20, value=3, step=1)
            col_p1, col_p2 = st.columns(2)
            for i in range(int(nombre_de_produits)):
                with col_p1:
                    nom_p = st.text_input(f"📦 Nom du produit #{i+1} :", f"Article Premium {i+1}", key=f"nom_p_{i}_{nombre_de_produits}")
                with col_p2:
                    prix_p = st.number_input(f"💰 Prix de vente ($) #{i+1} :", min_value=1.0, value=29.99 + (i*10), step=5.0, key=f"prix_p_{i}_{nombre_de_produits}")
                liste_parametres_produits.append({"nom": nom_p, "prix": prix_p})

        if st.button("🚀 Forger l'infrastructure de la boutique"):
            if nom_shop and courriel_interac_vendeur and details_reels.strip():
                with st.spinner("L'IA applique le protocole de vérité et structure ton catalogue commercial..."):
                    
                    prefixe_interac = f"💵 **Paiement 100% Sécurisé : Virement Interac à : {courriel_interac_vendeur}**\n*Note : Entrez le numéro de votre commande dans la description du virement.*\n\n---\n"
                    
                    # R&D Prompt de cadrage strict anti-hallucination
                    prompt_catalogue = f"""Tu es un copywriter de génie spécialisé dans le commerce de type : {type_commerce}.
                    Rédige un catalogue pour la boutique '{nom_shop}' axée sur la thématique '{niche_shop}'.
                    
                    ⚠️ CONSIGNE DE SÉCURITÉ ET DE VÉRITÉ CRITIQUE :
                    Tu dois te baser UNIQUEMENT et STRICTEMENT sur les détails réels fournis par l'utilisateur ci-dessous.
                    Il est FORMELLEMENT INTERDIT d'inventer des matériaux, des fonctionnalités ou des options fausses. Si l'information n'est pas mentionnée, n'en parle pas. Ne mens jamais sur les caractéristiques.
                    
                    DÉTAILS RÉELS À RESPECTER COMPLÈTEMENT : 
                    {details_reels}
                    
                    Génère EXACTEMENT {int(nombre_de_produits)} fiches de produits. Pour chaque produit, utilise STRICTEMENT cette structure en Markdown :
                    
                    ### 📦 [Nom du produit]
                    * **Description** : [Description commerciale percutante et 100% VRAIE d'environ 3 phrases]
                    * **⚡ Pourquoi ce produit est unique** : [Argument de vente honnête basé sur les faits fournis]
                    * **Prix** : [Insérer ici le prix correspondant] $
                    
                    Ne mets aucune introduction ni conclusion, écris seulement le Markdown."""
                    
                    prix_stockage = prix_par_defaut if mode_creation == "🤖 Génération Automatique par IA (10 Produits)" else (liste_parametres_produits[0]["prix"] if liste_parametres_produits else 29.99)
                    
                    catalogue_markdown = outils.appeler_groq(prompt_catalogue, temperature=0.5)
                    contenu_final_interac = prefixe_interac + catalogue_markdown
                    
                    if outils.ajouter_boutique(nom_shop, niche_shop, contenu_final_interac, prix_stockage, couleur="#f8fafc"):
                        st.toast(f"🏬 Boutique '{nom_shop}' injectée avec succès !", icon="✅")
                        st.rerun()
                    else:
                        st.error("❌ Ce nom de boutique est déjà réservé sur le serveur central.")
            else:
                st.error("⚠️ Veuillez remplir le nom de l'enseigne, votre courriel Interac et fournir les détails réels des produits.")
    with tab3:
        st.header("🌐 Vos Serveurs d'Hébergement Actifs")
        if not liste_shops:
            st.info("Aucun site web actif détecté sur vos grappes de serveurs actuellement.")
        else:
            # Correction du bug du tuple : on extrait proprement les noms de boutiques pour l'affichage
            noms_boutiques_propres = [b[0] for b in liste_shops]
            choix_nom = st.selectbox("Sélectionnez la boutique à inspecter :", noms_boutiques_propres, key="select_inspect_shop")
            
            # Récupération des données complètes de la boutique sélectionnée
            choix = None
            for s in liste_shops:
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
                
                # NOUVEAU PROTOCOLE DE LOGISTIQUE LOCALE ET NUMÉRIQUE (Anti-AliExpress)
                st.markdown("""
                <div style='background-color: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #00ffcc; margin-bottom: 15px;'>
                    <span style='color: #00ffcc; font-weight: bold;'>📋 PROTOCOLE DE LIVRAISON SÉCURISÉ (RÉSEAU LOCAL) :</span><br>
                    <span style='font-size: 13px; color: #cbd5e1;'>
                    1. <b>Vérifie ton compte bancaire</b> : Valide que le client t'a envoyé le virement Interac réel pour sa commande.<br>
                    2. <b>Prépare l'article ou le service</b> : S'il s'agit d'un objet que tu as chez toi ou d'un service numérique (montage, logo), prépare-le.<br>
                    3. <b>Option Livreur Indépendant</b> : Si l'adresse est trop loin, utilise le formulaire ci-dessous pour déléguer la course à un livreur inscrit sur l'application. Il prendra l'objet, ira le porter à vélo/à pied, et l'application prélèvera sa prime de livraison !<br>
                    4. <b>Zéro Carte de Crédit sur Internet</b> : Tout voyage de main en main ou par virement local. Sécurité maximale pour les parents.
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 📥 Boîte de Réception des Commandes Clients")
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
                            📍 <b>ADRESSE DE LIVRAISON DU CLIENT :</b><br>
                            <input type='text' value='{c_adresse}' style='width:100%; background:#0f172a; color:#fff; border:1px solid #334155; padding:6px; border-radius:4px; margin-top:4px;' readonly><br><br>
                            📦 <b>Contenu du panier :</b> {c_articles} <br>
                            💰 <b>Total collecté (Interac) :</b> {c_total} $
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # MODULE DE DÉLÉGATION À UN LIVREUR DU RÉSEAU LOCAL
                        with st.expander(f"⚡ Assigner un livreur indépendant pour la commande #{idx_c+1}"):
                            prime_livraison = st.slider(f"Prime pour le livreur ($) :", min_value=5.0, max_value=20.0, value=5.0, step=1.0, key=f"prime_{nom}_{idx_c}")
                            nom_livreur_choisi = st.text_input("Nom du livreur désigné (ou pseudonyme réseau) :", placeholder="Ex: Nathan_Velo", key=f"livreur_{nom}_{idx_c}")
                            
                            if st.button("🚀 Transmettre l'ordre de livraison au coursier", key=f"btn_livreur_{nom}_{idx_c}"):
                                if nom_livreur_choisi.strip():
                                    # Simule l'envoi de la notification et de la commission au livreur
                                    outils.marquer_code_utilise(f"LIVRAISON-{nom_livreur_choisi}-{random.randint(1000,9999)}")
                                    st.success(f"📦 Commande transmise à **{nom_livreur_choisi}** ! Il recevra ses {prime_livraison} $ dès la validation de la livraison.")
                                    st.toast("Commission logistique enregistrée !", icon="💰")
                                else:
                                    st.error("⚠️ Saisissez le nom du livreur à assigner.")
                
                st.markdown("---")
                st.markdown(f"### 🏬 FICHE VISUELLE DE LA VITRINE : {nom.upper()}")
                st.markdown(contenu_propre, unsafe_allow_html=True)
                st.markdown("---")
                
                c_act1, c_act2 = st.columns(2)
                with c_act1:
                    if st.button("🛒 Injecter une commande de test réel", key=f"test_vente_{nom}"):
                        outils.enregistrer_commande_interne(nom, "Acheteur Réel de Test", "123 rue de la Validation, Montréal", "Article de Démonstration", prix)
                        st.balloons()
                        st.rerun()
                with c_act2:
                    if st.button("🗑️ Raser cette boutique du serveur", type="primary", key=f"delete_shop_{nom}"):
                        if outils.supprimer_boutique(nom):
                            st.rerun()

    with tab4:
        st.header("🕵️‍♂️ Radar Espion Local et Numérique")
        mot_espion = st.text_input("Saisissez un type d'article, de service ou une tendance à auditer :", key="audit_mot_espion")
        if st.button("🔍 Lancer les algorithmes d'espionnage") and mot_espion:
            with st.spinner("Scan des demandes du marché local..."):
                prompt_audit = f"Fournis une analyse de positionnement commercial agressive et des angles marketing clés en français pour vendre le produit ou service suivant localement ou en ligne sans fournisseur international : '{mot_espion}'."
                st.info(outils.appeler_groq(prompt_audit))

    with tab5:
        st.header("👑 Laboratoire de R&D : Outils Avancés Élite")
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
                        prompt_replication = f"Simule une analyse approfondie des 3 boutiques leaders dans la niche '{niche_espionne}'. Donne une liste des 5 produits les plus vendus chez eux, leur prix estimé, et la stratégie marketing exacte pour copier leur succès localement."
                        st.write(outils.appeler_groq(prompt_replication))
            
            with sub_tab2:
                st.subheader("💬 Injecteur d'Agent Conversationnel en Direct")
                if not liste_shops:
                    st.warning("Aucune boutique disponible pour implanter l'IA.")
                else:
                    shop_pour_chat = st.selectbox("Sélectionnez la boutique à équiper d'un Chatbot :", liste_shops, format_func=lambda x: f"🤖 {x[0]}", key="select_shop_chat")
                    if st.button("⚡ Greffer l'Assistant commercial IA", key="btn_greffe_chatbot"):
                        nom_s, niche_s, contenu_s, couleur_s, prix_s = shop_pour_chat
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

    with tab6:
        st.header("🎨 Studio Branding & Identité Visuelle")
        if st.session_state.forfait != "Pro":
            st.markdown("""
            <div style='background-color: #1e1e2e; padding: 25px; border-radius: 12px; border: 1px solid #ff007f; text-align: center;'>
                <h3>🔒 SECTION RÉSERVÉE AU PLAN PRO</h3>
                <p>La configuration visuelle avancée nécessite l'activation d'une licence Pro.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.subheader("🖼️ Personnalisation de l'arrière-plan par Copier-Coller")
            if not liste_shops:
                st.warning("Aucune boutique disponible pour le re-branding.")
            else:
                shop_branding = st.selectbox("Sélectionnez la boutique à modifier :", liste_shops, format_func=lambda x: f"✨ {x[0]}", key="sb_select")
                nouveau_fond = st.text_input("Collez l'URL de votre image ou votre couleur hexadécimale :", "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)", key="input_fond_custom")
                
                if st.button("💾 Appliquer la charte graphique", key="btn_apply_branding"):
                    nom_boutique_selectionnee = shop_branding[0]
                    
                    conn = outils.obtenir_connexion()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE boutiques SET couleur = ? WHERE nom = ?", (nouveau_fond, nom_boutique_selectionnee))
                    conn.commit()
                    conn.close()
                    st.success(f"🎨 L'ambiance visuelle de '{nom_boutique_selectionnee}' a été mise à jour !")
                    st.rerun()

    with tab7:
        st.header("💎 Rente Réelle : Déploiement de Logiciels Micro-SaaS")
        if st.session_state.forfait != "Pro":
            st.markdown("""
            <div style='background-color: #1a1c23; padding: 25px; border-radius: 12px; border: 1px solid #00ffcc; text-align: center;'>
                <h3>🔒 MODULE DE REVENU PASSIF VERROUILLÉ</h3>
                <p>Le système de génération de licences logicielles automatisées nécessite l'infrastructure Pro.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.subheader("🚀 Forger une Application Clone (Générateur de Rente)")
            st.markdown("Créez instantanément une page publique d'abonnement pour vendre votre propre application en marque blanche.")
            
            nom_logiciel_vente = st.text_input("Nom de l'application logicielle à vendre :", "SaaS Automate Pro", key="input_nom_saas")
            tarif_SaaS = st.number_input("Prix de l'abonnement mensuel ($) :", min_value=10.0, value=100.0, step=10.0, key="input_prix_saas")
            
            if st.button("💎 Déployer la Page de Vente Logicielle", key="btn_deploy_saas"):
                import random
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
                outils.ajouter_boutique(nom_logiciel_vente, "Abonnement Logiciel SaaS", texte_boutique_SaaS, tarif_SaaS, couleur="#f8fafc")
                st.success("🎉 Page de vente configurée avec succès !")
                st.rerun()
            
            st.markdown("---")
            st.subheader("🔗 Liens d'accès à vos pages de vente actives")
            
            for s_saas in liste_shops:
                nom_saas_boutique = s_saas[0]
                niche_saas_boutique = s_saas[1]
                if "SaaS" in niche_saas_boutique or "Abonnement" in niche_saas_boutique:
                    nom_saas_propre = nom_saas_boutique.lower().replace(' ', '-')
                    st.link_button(f"🌍 Ouvrir la page d'abonnement : {nom_saas_boutique.upper()}", url=f"/?shop={nom_saas_propre}")
            
            st.markdown("---")
            st.subheader("📊 Liste des Licences Logicielles Actives")
            abonnements_actifs = outils.recuperer_abonnements()
            if not abonnements_actifs:
                st.info("Aucune rente logicielle active pour le moment.")
            else:
                for abonn in abonnements_actifs:
                    plateforme, client, email_client, tarif, statut, date_ins = abonn
                    st.write(f"🔑 **{client}** ({email_client}) a activé un forfait sur `{plateforme}` ➔ **{tarif} $ / mois** (Inscrit le : {date_ins})")
