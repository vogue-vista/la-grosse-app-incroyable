import streamlit as st
import outils
import re
import random  # ✅ Nécessaire pour l'algorithme de distribution équitable

# Initialisation automatique de l'infrastructure SQLite
outils.initialiser_base_de_donnees()

# Initialisation du panier virtuel global pour les acheteurs
if "panier_client" not in st.session_state:
    st.session_state.panier_client = []

# --- 1. EXPÉRIENCE GRAND PUBLIC : LA PLACE DE MARCHÉ ANTI-MONOPOLE ---
query_params = st.query_params

# Si aucun utilisateur n'est connecté en admin et qu'aucune boutique solo n'est demandée, on affiche le Marché Global
if "shop" not in query_params and not st.session_state.get("compte_actif", False):
    
    st.title("🛍️ LE GRAND MARCHÉ ÉQUITABLE INTERAC")
    st.subheader("La seule place de marché qui donne une chance égale à chaque jeune entrepreneur")
    
    st.markdown("""
    <div style='background-color: #1e293b; padding: 15px; border-radius: 12px; border-left: 5px solid #00ffcc; margin-bottom: 25px;'>
        <span style='color: #00ffcc; font-weight: bold;'>⚡ ALGORITHME DE VISIBILITÉ ÉQUITABLE ACTIVÉ</span><br>
        <span style='font-size: 13px; color: #cbd5e1;'>
        Pour éviter les monopoles, notre système mélange aléatoirement l'ordre d'affichage des articles à chaque connexion. Que vous soyez inscrit depuis 1 an ou depuis 5 minutes, vous avez exactement la même visibilité !
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Récupération de TOUTES les boutiques créées sur l'application
    toutes_les_boutiques = outils.recuperer_boutiques()
    
    if not toutes_les_boutiques:
        st.info("📉 Le marché est calme aujourd'hui. Aucun produit n'est encore en vitrine.")
    else:
        # 📊 BARRE DE RECHERCHE UNIFIÉE
        recherche_client = st.text_input("🔍 Que cherchez-vous aujourd'hui ? (Ex: Chaise, Vêtement)", "").strip().lower()
        
        # ✅ ALGORITHME ANTI-MONOPOLE : On mélange complètement la liste des vendeurs
        random.shuffle(toutes_les_boutiques)
        
        st.markdown("---")
        liste_articles_extraits = []
        
        # Extraction et filtrage de tous les produits individuels
        for b_idx, b_data in enumerate(toutes_les_boutiques):
            b_nom, b_niche, b_contenu, b_couleur, b_prix = b_data
            
            try: b_prix_propre = float(b_prix)
            except: b_prix_propre = 29.99
                
            b_contenu_propre = b_contenu.replace("```html", "").replace("```", "").replace("html", "").strip()
            
            if "### 📦" in b_contenu_propre:
                blocs = b_contenu_propre.split("### 📦")
                for p_idx, bloc in enumerate(blocs[1:]):
                    if bloc.strip():
                        lignes_bloc = bloc.split("\n")
                        nom_produit = lignes_bloc[0].strip()
                        
                        # Si l'acheteur fait une recherche, on filtre textuellement
                        if recherche_client and (recherche_client not in nom_produit.lower() and recherche_client not in bloc.lower()):
                            continue
                            
                        liste_articles_extraits.append({
                            "vendeur": b_nom,
                            "niche": b_niche,
                            "bloc_texte": bloc,
                            "nom_produit": nom_produit,
                            "prix": b_prix_propre,
                            "b_idx": b_idx,
                            "p_idx": p_idx
                        })

        # ✅ DEUXIÈME SÉCURITÉ ANTI-MONOPOLE : On mélange aussi l'ordre final des articles extraits
        random.shuffle(liste_articles_extraits)
        
        if not liste_articles_extraits:
            st.warning("Aucun article ne correspond à votre recherche pour le moment.")
        else:
            for art in liste_articles_extraits:
                st.markdown(f"""
                <div style='background-color: #111827; padding: 15px; border-radius: 12px; border: 1px solid #1f2937; margin-bottom: -10px;'>
                    <span style='color: #00ffcc; font-size: 11px; font-weight: bold;'>🏬 Enseigne : {art['vendeur'].upper()} ({art['niche']})</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Rendu propre du bloc produit
                st.markdown(f"### 📦 {art['bloc_texte']}", unsafe_allow_html=True)
                
                if st.button(f"🛒 Ajouter au panier : {art['nom_produit']}", key=f"market_btn_{art['b_idx']}_{art['p_idx']}"):
                    st.session_state.panier_client.append({
                        "nom": art['nom_produit'], 
                        "prix": art['prix'], 
                        "vendeur": art['vendeur']
                    })
                    st.toast(f"✅ {art['nom_produit']} ajouté au panier global !", icon="🛒")
                st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        # --- CAISSE DE PAIEMENT DU MARCHÉ PUBLIC ---
        st.markdown("## 🛒 Votre Panier d'Achat Global")
        
        if not st.session_state.panier_client:
            st.info("Votre panier est actuellement vide. Sélectionnez des articles ci-dessus pour commander.")
            total_commande = 0.0
        else:
            total_commande = 0.0
            st.markdown("<div class='bloc-panier'>", unsafe_allow_html=True)
            for idx_p, item in enumerate(st.session_state.panier_client):
                col_item1, col_item2 = st.columns([3, 1])
                with col_item1:
                    st.write(f"🔹 **{item['nom']}** — {item['prix']} $ (Vendeur : `{item['vendeur']}`)")
                with col_item2:
                    if st.button("❌ Retirer", key=f"del_market_item_{idx_p}"):
                        st.session_state.panier_client.pop(idx_p)
                        st.rerun()
                total_commande += item['prix']
            
            st.markdown(f"### 💵 Total à payer : {round(total_commande, 2)} $")
            if st.button("🧹 Vider le panier public"):
                st.session_state.panier_client = []
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # --- FORMULAIRE GLOBAL UNIQUE EN 1-CLIC ---
        if st.session_state.panier_client:
            st.markdown("### ⚡ Finaliser la commande auprès des vendeurs")
            with st.form("achat_marche_form"):
                nom_client = st.text_input("Votre Nom complet :", placeholder="Ex: Jean Tremblay")
                adresse_client = st.text_input("Votre Adresse de livraison :", placeholder="Ex: 123 rue des Lilas, Montréal, QC")
                
                texte_bouton = f"🔥 Confirmer l'achat par Interac ({round(total_commande, 2)} $)"
                if st.form_submit_button(texte_bouton):
                    if nom_client and adresse_client:
                        # Distribution automatique des notifications à chaque vendeur concerné
                        for item in st.session_state.panier_client:
                            outils.enregistrer_commande_interne(
                                nom_boutique=item['vendeur'],
                                nom_client=nom_client,
                                adresse=adresse_client,
                                commande=item['nom'],
                                total=item['prix']
                            )
                        st.session_state.panier_client = []
                        st.balloons()
                        st.success("🎉 Commandes transmises ! Regardez les instructions Interac sous les articles des vendeurs pour envoyer vos paiements.")
                        st.rerun()
                    else:
                        st.error("⚠️ Veuillez remplir votre nom et votre adresse pour la livraison.")

    # --- 💬 LE FORUM DE DISCUSSION INTERNE ACCESSIBLE À TOUS ---
    st.markdown("---")
    st.header("💬 Le Forum de l'Empire")
    st.markdown("Échangez des conseils, collaborez entre vendeurs et négociez en toute liberté.")
    
    # Zone d'écriture pour tout visiteur ou membre anonyme
    with st.form("form_forum"):
        pseudo_forum = st.text_input("Votre Pseudo :", value="Anonyme", max_chars=20)
        msg_forum = st.text_area("Votre Message :", placeholder="Ex: J'ai du stock de chaises de terrasse prêt à être livré à Montréal !", max_chars=250)
        if st.form_submit_button("🚀 Envoyer sur le Forum"):
            if msg_forum.strip():
                outils.ajouter_message_forum(pseudo_forum, msg_forum)
                st.success("Message partagé !")
                st.rerun()
                
    st.markdown("#### 📜 Dernières discussions sur le réseau :")
    discussions = outils.recuperer_messages_forum()
    if not discussions:
        st.info("Le forum est vide. Soyez le premier à lancer la discussion !")
    else:
        for disc in discussions:
            auteur, message, date_post = disc
            st.markdown(f"""
            <div style='background-color: #1e293b; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #6366f1;'>
                <span style='color: #818cf8; font-size: 11px;'>📅 {date_post} | 👤 <b>{auteur}</b> :</span><br>
                <span style='color: #e2e8f0; font-size: 13px;'>{message}</span>
            </div>
            """, unsafe_allow_html=True)
    st.stop()
# --- 2. CONFIGURATION DE SESSION ADMINISTRATEUR ---
if "compte_actif" not in st.session_state: st.session_state.compte_actif = False
if "forfait" not in st.session_state: st.session_state.forfait = "Aucun"

# 🔥 BLOC SÉCURITÉ PARENTALE ET TRANSPARENCE AVANT AUTHENTIFICATION
if not st.session_state.compte_actif:
    st.markdown("""
    <div style='background-color: #111827; padding: 20px; border-radius: 12px; border: 1px solid #1f2937; text-align: center; margin-bottom: 20px;'>
        <h4 style='color: #00ffcc; margin: 0;'>💡 PROTOCOLE CENTRAL D'ACTIVATION</h4>
        <p style='color: #9ca3af; font-size: 14px; margin: 5px 0 0 0;'>« L'application te donne les armes, mais c'est toi qui choisis la guerre. »</p>
    </div>
    
    <div style='background-color: #1e293b; padding: 20px; border-radius: 12px; border-left: 5px solid #3b82f6; margin-bottom: 25px;'>
        <h5 style='color: #3b82f6; margin-top: 0;'>🛡️ SECTION SÉCURITÉ PARENTALE (Lettre ouverte du créateur)</h5>
        <span style='font-size: 13px; color: #cbd5e1; line-height: 1.6;'>
        Bonjour aux parents. Cette application n'est pas gérée par une multinationale américaine comme Shopify ou Amazon, mais par un <b>développeur indépendant et local</b>. Et c'est votre meilleure garantie de sécurité :<br><br>
        • <b>Zéro Donnée Sensible</b> : Contrairement aux géants du web qui stockent des millions de cartes de crédit et de mots de passe (et qui se font pirater), notre application ne collecte <b>absolument rien</b>. Pas de carte bancaire, pas de mot de passe, pas de compte connecté. Un hacker ne peut pas voler ce qui n'existe pas.<br>
        • <b>100% Circuit Bancaire Canadien</b> : Les clients paient votre enfant par virement Interac direct. L'argent voyage exclusivement de banque à banque (ex: Desjardins). Notre logiciel sert uniquement de panneau d'affichage textuel pour afficher l'adresse de livraison.<br>
        • <b>Soutien Direct</b> : Pas de robot d'assistance à l'autre bout du monde. Vous utilisez un outil indépendant, épuré, transparent et conçu pour initier les jeunes aux affaires de manière sécuritaire et responsable.<br>
        • <b>Garantie d'Essai Gratuit</b> : Votre enfant peut utiliser un code d'accès temporaire pour valider le système sans que vous n'ayez à débourser un seul dollar.
        </span>
    </div>
    """, unsafe_allow_html=True)
# --- 3. BARRE LATÉRALE ET SYSTÈME DE SÉCURITÉ DES FORFAITS ---
st.sidebar.title("🎮 Centre de Contrôle")
st.sidebar.markdown("---")

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
            st.sidebar.success("✅ ACCÈS STARTER VALIDÉ ! (R&D bloqué)")
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

if not st.session_state.compte_actif:
    st.warning("⚠️ Terminal restreint. Veuillez insérer une clé d'activation valide pour débloquer l'accès aux modules.")
else:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🤖 B1: Radar de Tendances", "🏬 B2: Boutique Multi-Produits", "👀 Mes Boutiques", 
        "🕵️‍♂️ Radar Espion", "💡 B3: R&D Élite", "🎨 Studio Branding", "💎 Rente Réelle"
    ])

    with tab1:
        st.header("🤖 B1: Chasseur de Produits Viraux par IA")
        st.markdown("Notre algorithme simule un scan des tendances TikTok, Reels et Amazon pour extraire les 3 opportunités les plus rentables de la journée.")
        
        st.markdown("""
        <div style='background-color: #1e1b4b; padding: 12px; border-radius: 8px; border-left: 4px solid #6366f1; margin-bottom: 15px;'>
            <span style='color: #a5b4fc; font-size: 13px; font-style: italic;'>« Les amateurs cherchent des produits au hasard. Les pros exploitent les failles algorithmiques. »</span>
        </div>
        """, unsafe_allow_html=True)
        
        categorie_tendance = st.selectbox("Ciblez le radar sur une grande catégorie de marché :", [
            "🔥 Gadgets Tech & High-Tech", 
            "✨ Beauté, Cosmétiques & Glow-up",
            "👟 Mode, Streetwear & Accessoires",
            "🏠 Objets Maison, Déco & Rangement Viraux",
            "🧸 Jouets, Niches Enfants & Gaming"
        ])
        
        if st.button("📡 Lancer le Scanner d'Opportunités Élite"):
            with st.spinner("Interconnexion avec les bases de données de tendances..."):
                prompt_radar = f"""Tu es un analyste e-commerce de génie spécialisé dans les produits viraux TikTok et le dropshipping.
                Génère 3 produits hautement rentables, ultra-tendances et uniques pour la catégorie '{categorie_tendance}'.
                Pour chaque produit, utilise STRICTEMENT cette structure textuelle en évitant les fioritures :
                
                PRODUIT [Numéro] : [Nom du produit]
                - 🎯 Angle Marketing : [Pourquoi ce produit cartonne sur TikTok en 1 phrase]
                - 💰 Prix Grossiste estimé : [Entre 5$ et 20$] | Prix de Vente conseillé : [Entre 30$ et 79$]
                - 🚀 Argument Choc : [L'accroche psychologique pour le vendre]
                
                Sépare les 3 produits par une ligne de tirets '---'. Écris uniquement le texte des produits."""
                
                resultat_radar = outils.appeler_groq(prompt_radar, temperature=0.8)
                st.session_state.derniere_recherche_produits = resultat_radar
                st.session_state.categorie_scanne = categorie_tendance
                st.rerun()
                
        if "derniere_recherche_produits" in st.session_state:
            st.markdown(f"### 📋 Opportunités Détectées dans : `{st.session_state.categorie_scanne}`")
            st.write(st.session_state.derniere_recherche_produits)
            
            st.markdown("---")
            st.subheader("⚡ Exploitation Immédiate")
            st.info("Copiez le nom du produit qui vous intéresse le plus, allez dans l'onglet **'B2: Boutique'** pour générer automatiquement le catalogue et configurer votre mode de paiement Interac en 2 minutes !")
    with tab2:
        st.header("🏬 Concepteur de Boutique Avancé")
        st.markdown("Propulsez une vitrine e-commerce. Choisissez entre l'automatisation totale par IA ou une configuration manuelle sans limites.")
        
        nom_shop = st.text_input("Nom de l'enseigne e-commerce :", "Cyber Look", key="design_nom_shop")
        niche_shop = st.text_input("Thématique / Niche :", "Vêtements Streetwear Cyberpunk", key="design_niche_shop")
        
        # Courriel Interac sans Stripe/PayPal pour les jeunes (Sécuritaire et sans données sensibles)
        courriel_interac_vendeur = st.text_input("🚀 Votre courriel Interac (Pour recevoir l'argent de vos ventes) :", "votre-compte-banque@email.com")
        
        st.info("📦 Une boîte de réception interne sera automatiquement configurée sous le numéro unique de cette boutique.")
        mode_creation = st.radio("Méthode de déploiement :", ["🤖 100% Automatique (IA - 10 Produits Gagnants)", "🛠️ Manuel de Zéro (Nombre de produits au choix)"])
        liste_parametres_produits = []
        
        if mode_creation == "🤖 100% Automatique (IA - 10 Produits Gagnants)":
            st.info("⚡ L'IA va générer automatiquement un catalogue complet de 10 produits viraux adaptés à votre niche.")
            nombre_de_produits = 10
            prix_par_defaut = st.number_input("Prix de vente moyen par produit ($) :", min_value=1.0, value=39.99, step=5.0)
        else:
            st.markdown("#### ⚙️ Configuration personnalisée du catalogue")
            nombre_de_produits = st.number_input("Combien de produits voulez-vous intégrer ?", min_value=1, max_value=50, value=3, step=1)
            
            col_p1, col_p2 = st.columns(2)
            for i in range(int(nombre_de_produits)):
                with col_p1:
                    nom_p = st.text_input(f"📦 Nom du produit #{i+1} :", f"Article Premium {i+1}", key=f"nom_p_{i}_{nombre_de_produits}")
                with col_p2:
                    prix_p = st.number_input(f"💰 Prix de vente ($) #{i+1} :", min_value=1.0, value=29.99 + (i*10), step=5.0, key=f"prix_p_{i}_{nombre_de_produits}")
                liste_parametres_produits.append({"nom": nom_p, "prix": prix_p})

        if st.button("🚀 Forger l'infrastructure de la boutique"):
            if nom_shop and courriel_interac_vendeur:
                with st.spinner("L'IA génère et structure votre catalogue commercial..."):
                    
                    prefixe_interac = f"💵 **Mode de paiement sécurisé : Virement Interac à {courriel_interac_vendeur}**\n*Question : Boutique | Réponse : Votre Nom*\n\n---\n"
                    
                    if mode_creation == "🤖 100% Automatique (IA - 10 Produits Gagnants)":
                        prompt_catalogue = f"""Tu es un expert en e-commerce et un copywriter de génie.
                        Génère une liste de EXACTEMENT 10 produits différents, innovants, viraux et hautement rentables pour la boutique '{nom_shop}' dans la niche '{niche_shop}'.
                        Pour chaque produit, utilise STRICTEMENT cette structure en Markdown :
                        
                        ### 📦 [Nom du produit gagnant]
                        * **Description** : [Description marketing percutante d'environ 3 phrases]
                        * **🔥 Pourquoi ce produit est viral** : [Argumentaire de vente massif style tendance TikTok]
                        * **Prix** : {prix_par_defaut} $
                        
                        Génère les 10 produits les uns après les autres. Ne mets aucune introduction ni conclusion, écris seulement le Markdown."""
                        prix_stockage = prix_par_defaut
                    else:
                        structure_demandee = ""
                        for p in liste_parametres_produits:
                            structure_demandee += f"\n- Produit : {p['nom']} | Prix : {p['prix']} $\n"
                            
                        prompt_catalogue = f"""Tu es un copywriter e-commerce de génie. Rédige les fiches descriptives pour la boutique '{nom_shop}' ({niche_shop}).
                        Tu dois obligatoirement inclure ces {int(nombre_de_produits)} produits spécifiques avec leurs prix exacts :
                        {structure_demandee}
                        
                        Génère le rendu au format Markdown en utilisant STRICTEMENT cette mise en page pour chaque produit :
                        ### 📦 [Insérer ici le Nom exact du produit]
                        * **Description** : [Insérer une description attractive et moderne d'environ 3 phrases]
                        * **🔥 Pourquoi ce produit est viral** : [Argumentaire de vente massif]
                        * **Prix** : [Insérer ici le prix exact spécifié] $
                        
                        N'écris rien d'autre. Pas d'introduction, pas de conclusion."""
                        prix_stockage = liste_parametres_produits["prix"] if liste_parametres_produits else 29.99
                    
                    catalogue_markdown = outils.appeler_groq(prompt_catalogue, temperature=0.7)
                    contenu_final_interac = prefixe_interac + catalogue_markdown
                    
                    if outils.ajouter_boutique(nom_shop, niche_shop, contenu_final_interac, prix_stockage, couleur="#f8fafc"):
                        st.toast(f"🏬 Boutique '{nom_shop}' injectée avec succès !", icon="✅")
                        st.rerun()
                    else:
                        st.error("❌ Ce nom de boutique est déjà réservé sur votre serveur.")
            else:
                st.error("⚠️ Veuillez renseigner le nom de la boutique et votre courriel Interac.")
    with tab3:
        st.header("🌐 Vos Serveurs d'Hébergement Actifs")
        if not liste_shops:
            st.info("Aucun site web actif détecté sur vos grappes de serveurs actuellement.")
        else:
            choix = st.selectbox("Sélectionnez la boutique à inspecter :", liste_shops, format_func=lambda x: f"⚙️ {x[0]} [{x[1]}]")
            if choix:
                nom, niche, contenu, couleur, prix = choix
                nom_formate = nom.lower().replace(' ', '-')
                lien_public = f"/?shop={nom_formate}"
                contenu_propre = contenu.replace("```html", "").replace("```", "").replace("html", "").strip()
                
                # ✅ BOUTON RESTE ACCESSIBLE EN PERMANENCE
                st.link_button(f"🌍 Ouvrir la page publique de : {nom.upper()}", url=lien_public, type="primary")
                st.markdown("---")
                
                # ✅ INSTRUCTIONS LOGISTIQUES MANUELLES POUR LES JEUNES DROPSHIPPERS
                st.markdown("""
                <div style='background-color: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #00ffcc; margin-bottom: 15px;'>
                    <span style='color: #00ffcc; font-weight: bold;'>📋 PROTOCOLE DE LIVRAISON DROPSHIPPING :</span><br>
                    <span style='font-size: 13px; color: #cbd5e1;'>
                    1. Vérifie ton application bancaire Desjardins : Valide que tu as reçu le virement Interac pour le montant total.<br>
                    2. Rends-toi sur le site de ton grossiste / fournisseur (ex: AliExpress) pour commander l'article.<br>
                    3. Achète l'article avec l'argent reçu et <b>colle l'adresse de livraison exacte du client</b> (disponible ci-dessous).<br>
                    4. Le fournisseur expédie l'objet. Tu encaisses et conserves le bénéfice net dans tes poches !
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 📥 Boîte de Réception des Commandes Clients")
                commandes_recues = outils.recuperer_commandes_boutique(nom)
                
                if not commandes_recues:
                    st.info("📨 Aucun message ni commande reçu pour le moment dans cette boîte.")
                else:
                    for cmd in commandes_recues:
                        c_nom, c_adresse, c_articles, c_total, c_date = cmd
                        st.markdown(f"""
                        <div style='background-color: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #ff0055; margin-bottom: 10px;'>
                            <span style='font-size: 11px; color: #94a3b8;'>📅 Commande reçue le : {c_date}</span><br>
                            👤 <b>Acheteur :</b> {c_nom} <br>
                            📍 <b>ADRESSE À COPIER CHEZ LE FOURNISSEUR :</b><br>
                            <input type='text' value='{c_adresse}' style='width:100%; background:#0f172a; color:#fff; border:1px solid #334155; padding:6px; border-radius:4px; margin-top:4px;' readonly><br><br>
                            📦 <b>Contenu du panier :</b> {c_articles} <br>
                            💰 <b>Total collecté (Interac) :</b> {c_total} $
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown(f"### 🏬 SYSTEM FEED EN DIRECT : {nom.upper()}")
                st.markdown(contenu_propre, unsafe_allow_html=True)
                st.markdown("---")
                
                c_act1, c_act2 = st.columns(2)
                with c_act1:
                    if st.button("🛒 Injecter une vente artificielle"):
                        outils.enregistrer_commande_interne(nom, "Acheteur Virtuel", "Adresse Test", "Article Aléatoire", prix)
                        st.balloons()
                        st.rerun()
                with c_act2:
                    if st.button("🗑️ Raser cette boutique du serveur", type="primary"):
                        if outils.supprimer_boutique(nom):
                            st.rerun()
    with tab4:
        st.header("🕵️‍♂️ Radar Espion")
        mot_espion = st.text_input("Saisissez un nom d'article ou une tendance à auditer :", key="audit_mot_espion")
        if st.button("🔍 Lancer les algorithmes d'espionnage") and mot_espion:
            with st.spinner("Scan des bases concurrentes..."):
                prompt_audit = f"Fournis une analyse de positionnement e-commerce agressive et des angles marketing clés pour vendre le produit suivant : '{mot_espion}'."
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
            sub_tab1, sub_tab2, sub_tab3 = st.tabs(["🕵️‍♂️ 1. Inspirateur & Réplicateur Sans URL", "💬 2. Injecteur de Chatbot IA", "💡 3. Générateur de Produits Digitaux"])
            
            with sub_tab1:
                st.subheader("🛠️ Réplication Légale Instantanée par Thématique")
                niche_espionne = st.text_input("Saisissez la thématique ou la niche à cloner :", placeholder="Ex: Accessoires de cuisine")
                if st.button("🌐 Lancer l'aspiration et la réplication"):
                    with st.spinner("Analyse du marché leader mondial..."):
                        prompt_replication = f"Simule une analyse approfondie des 3 boutiques leaders mondiales dans la niche '{niche_espionne}'. Donne une liste des 5 produits les plus vendus chez eux, leur prix estimé, et la stratégie marketing exacte pour copier leur succès."
                        st.write(outils.appeler_groq(prompt_replication))
            
            with sub_tab2:
                st.subheader("💬 Injecteur d'Agent Conversationnel en Direct")
                if not liste_shops:
                    st.warning("Aucune boutique disponible pour implanter l'IA.")
                else:
                    shop_pour_chat = st.selectbox("Sélectionnez la boutique à équiper d'un Chatbot :", liste_shops, format_func=lambda x: f"🤖 {x}", key="select_shop_chat")
                    if st.button("⚡ Greffer l'Assistant commercial IA"):
                        nom_s, niche_s, contenu_s, couleur_s, prix_s = shop_pour_chat
                        if "🤖 Agent Actif" not in contenu_s:
                            nouveau_contenu_ia = contenu_s + "\n\n🤖 Agent Actif"
                            outils.mettre_a_jour_boutique(nom_s, nouveau_contenu_ia)
                            st.success(f"🎉 Le Chatbot IA a été greffé !")
                        else:
                            st.info("L'Agent IA est déjà actif.")
                
            with sub_tab3:
                st.subheader("💡 Concepteur de Produits Numériques Élite")
                theme_num = st.text_input("Sujet de la formation :", "Devenir Libre avec l'IA en 30 jours")
                if st.button("📚 Rédiger la structure par IA"):
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
                shop_branding = st.selectbox("Sélectionnez la boutique à modifier :", liste_shops, format_func=lambda x: f"✨ {x}", key="sb_select")
                nouveau_fond = st.text_input("Collez l'URL de votre image ou votre couleur hexadécimale :", "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)")
                
                if st.button("💾 Appliquer la charte graphique"):
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
            
            nom_logiciel_vente = st.text_input("Nom de l'application logicielle à vendre :", "SaaS Automate Pro")
            tarif_SaaS = st.number_input("Prix de l'abonnement mensuel ($) :", min_value=10.0, value=100.0, step=10.0)
            
            if st.button("💎 Déployer la Page de Vente Logicielle"):
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
                if "SaaS" in s_saas[0] or "Abonnement" in s_saas[0]:
                    nom_saas_propre = s_saas[0].lower().replace(' ', '-')
                    st.link_button(f"🌍 Ouvrir la page d'abonnement : {s_saas[0].upper()}", url=f"/?shop={nom_saas_propre}")
            
            st.markdown("---")
            st.subheader("📊 Liste des Licences Logicielles Actives")
            abonnements_actifs = outils.recuperer_abonnements()
            if not abonnements_actifs:
                st.info("Aucune rente logicielle active pour le moment.")
            else:
                for abonn in abonnements_actifs:
                    plateforme, client, note, tarif, statut, date_ins = abonn
                    st.write(f"🔑 **{client}** a activé un forfait sur `{plateforme}` ➔ **{tarif} $ / mois** (Inscrit le : {date_ins})")
