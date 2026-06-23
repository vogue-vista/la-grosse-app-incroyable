import streamlit as st
import outils
import re

# Initialisation de la structure de données SQLite
outils.initialiser_base_de_donnees()

# Initialisation du panier virtuel global pour l'expérience client
if "panier_client" not in st.session_state:
    st.session_state.panier_client = []

# --- 1. ROUTAGE D'URL PUBLIC POUR LES CLIENTS ---
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
        
        # Sécurité sur le prix par défaut de la BDD pour éviter les crashs float()
        try:
            prix_bdd_propre = float(prix_bdd)
        except (ValueError, TypeError):
            prix_bdd_propre = 0.0
        
        # Nettoyage des balises Markdown résiduelles
        contenu_client = contenu.replace("```html", "").replace("```", "").replace("html", "").strip()

        # ✅ DESIGN CLIENT APPLIQUÉ (Couleur personnalisée via Studio Branding ou standard clair)
        fond_branding = couleur if (couleur and not "@" in couleur) else "#f8fafc"
        st.markdown(f"""
        <style>
        .stApp {{ background: {fond_branding} !important; color: #0f172a !important; }}
        h1, h2, h3, h4, h5, p, span, label, div {{ color: #0f172a !important; }}
        
        /* Conteneur blanc du Formulaire et du Panier */
        div[data-testid="stForm"], .bloc-panier {{ 
            background-color: #ffffff !important; 
            border: 2px solid #e2e8f0 !important; 
            border-radius: 16px !important; 
            padding: 25px !important;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1) !important;
            margin-bottom: 20px;
        }}
        
        /* Boutons d'ajout au panier stylisés */
        .stButton>button {{
            background-color: #00ffcc !important;
            color: #0f172a !important;
            font-weight: bold !important;
            border-radius: 8px !important;
        }}
        input {{ background-color: #ffffff !important; color: #0f172a !important; border: 1px solid #cbd5e1 !important; }}
        </style>
        """, unsafe_allow_html=True)
        
        st.title(f"🏬 {nom.upper()}")
        st.subheader(f"✨ Catalogue Officiel : {niche}")
        st.markdown("---")
        
        # ✅ EXTRACTION STRUCTURELLE DES PRODUITS POUR CRÉER LES BOUTONS
        blocs_produits = contenu_client.split("### 📦")
        
        # Affichage de l'introduction si elle existe avant le premier produit
        if blocs_produits[0].strip():
            st.markdown(blocs_produits[0], unsafe_allow_html=True)
            
        for idx, bloc in enumerate(blocs_produits[1:]):
            if bloc.strip():
                lignes_bloc = bloc.split("\n")
                nom_produit = lignes_bloc[0].strip()
                
                # Extraction du prix pour ce produit via Regex
                trouver_prix = re.search(r"Prix\s*:\s*([\d[\s,\.]*\d+)", bloc, re.IGNORECASE)
                if trouver_prix:
                    prix_texte = trouver_prix.group(1).replace(" ", "").replace(",", ".")
                    try:
                        prix_chiffre = float(prix_texte)
                    except ValueError:
                        prix_chiffre = prix_bdd_propre
                else:
                    prix_chiffre = prix_bdd_propre
                
                # Rendu visuel propre du produit sur la page publique
                st.markdown(f"### 📦 {bloc}", unsafe_allow_html=True)
                
                # Bouton dynamique "Ajouter au Panier" exclusif pour chaque article
                if st.button(f"🛒 Ajouter : {nom_produit}", key=f"btn_ajout_{idx}"):
                    st.session_state.panier_client.append({"nom": nom_produit, "prix": prix_chiffre})
                    st.toast(f"✅ {nom_produit} a été ajouté au panier !", icon="🛒")
        st.markdown("---")
        
        # --- EN-TÊTE DU PANIER DE COMMANDE ---
        st.markdown("## 🛒 Votre Panier d'Achat")
        
        if not st.session_state.panier_client:
            st.info("Votre panier est vide actuellement. Cliquez sur 'Ajouter' pour sélectionner des articles.")
            total_commande = 0.0
        else:
            total_commande = 0.0
            st.markdown("<div class='bloc-panier'>", unsafe_allow_html=True)
            for idx_p, item in enumerate(st.session_state.panier_client):
                col_item1, col_item2 = st.columns([4, 1])
                with col_item1:
                    st.write(f"🔹 **{item['nom']}** — {item['prix']} $")
                with col_item2:
                    if st.button("❌ Retirer", key=f"del_item_{idx_p}"):
                        st.session_state.panier_client.pop(idx_p)
                        st.rerun()
                total_commande += item['prix']
            
            st.markdown(f"### 💵 Total à payer : {round(total_commande, 2)} $")
            if st.button("🧹 Vider le panier"):
                st.session_state.panier_client = []
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # --- FORMULAIRE D'ACHAT ULTRA-SIMPLIFIÉ (SANS COURRIEL) ---
        if st.session_state.panier_client:
            st.markdown("### ⚡ Finaliser ma Commande en 1-Clic")
            with st.form("achat_client_form"):
                nom_client = st.text_input("Nom complet de facturation :", placeholder="Ex: Jean Tremblay")
                adresse_client = st.text_input("Adresse complète de livraison :", placeholder="Ex: 123 rue des Lilas, Montréal, QC")
                
                texte_bouton = f"🔥 Valider et Payer ({round(total_commande, 2)} $)"
                bouton_clique = st.form_submit_button(texte_bouton)
                
                if bouton_clique:
                    if nom_client and adresse_client:
                        # Regroupement textuel des articles du panier
                        liste_articles = [i['nom'] for i in st.session_state.panier_client]
                        details_articles_texte = ", ".join(liste_articles)
                        
                        # Stockage direct dans la boîte de réception interne de l'application
                        outils.enregistrer_commande_interne(
                            nom_boutique=nom,
                            nom_client=nom_client,
                            adresse=adresse_client,
                            commande=details_articles_texte,
                            total=round(total_commande, 2)
                        )
                        
                        # Réinitialisation du panier après succès
                        st.session_state.panier_client = []
                        st.balloons()
                        st.success("🎉 Votre commande a été enregistrée avec succès dans notre système !")
                        st.rerun()
                    else:
                        st.error("⚠️ Erreur : Veuillez remplir votre nom et votre adresse de livraison.")
                        
        # --- DISCUSSION INTERACTIVE CLIENT AVEC L'ASSISTANT IA ---
        if "🤖 Agent Actif" in contenu:
            st.markdown("---")
            st.markdown("### 💬 Une question ? Discutez avec notre Assistant IA en direct")
            
            if "historique_chat_public" not in st.session_state:
                st.session_state.historique_chat_public = []
                
            for msg in st.session_state.historique_chat_public:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
            question_client = st.chat_input("Posez votre question sur nos produits ici...")
            if question_client:
                with st.chat_message("user"):
                    st.write(question_client)
                st.session_state.historique_chat_public.append({"role": "user", "content": question_client})
                
                prompt_assistant = f"""Tu es l'assistant commercial virtuel attitré de la boutique en ligne '{nom}'.
                Voici le catalogue de nos produits disponibles :
                {contents_client if 'contents_client' in locals() else contenu_client}
                
                Réponds au client de manière chaleureuse, professionnelle et concise pour l'inciter à acheter.
                Question du client : {question_client}"""
                
                with st.chat_message("assistant"):
                    with st.spinner("L'assistant réfléchit..."):
                        reponse_ia = outils.appeler_groq(prompt_assistant, temperature=0.5)
                        st.write(reponse_ia)
                st.session_state.historique_chat_public.append({"role": "assistant", "content": reponse_ia})
                st.rerun()
        st.stop()

# --- 2. CONFIGURATION DE SESSION ADMINISTRATEUR ---
if "compte_actif" not in st.session_state: st.session_state.compte_actif = False
if "forfait" not in st.session_state: st.session_state.forfait = "Aucun"
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
notif_1 = notifs if (len(notifs) > 0 and isinstance(notifs, list)) else ""
notif_2 = notifs if (len(notifs) > 1 and isinstance(notifs, list)) else ""
notif_3 = notifs if (len(notifs) > 2 and isinstance(notifs, list)) else ""

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
        "🤖 B1: Prospection", "🏬 B2: Boutique Multi-Produits", "👀 Mes Boutiques", 
        "🕵️‍♂️ Radar Espion", "💡 B3: R&D Élite", "🎨 Studio Branding", "💎 Rente Réelle"
    ])

    with tab1:
        st.header("🕵️‍♂️ Agent d'Extraction de Leads & Prospection")
        st.markdown("Scanne le réseau industriel pour cibler des entreprises, extraire leurs métadonnées et bâtir une approche commerciale.")
        
        niche_prospect = st.text_input("Secteur d'activité et zone géographique :", "Agences immobilières Montréal")
        
        if st.button("🔥 Lancer le scanneur de leads"):
            with st.spinner("Analyse du marché en cours..."):
                prompt_recherche = f"Donne-moi une liste de 4 sites web d'entreprises réelles ou typiques dans la niche '{niche_prospect}'. Réponds UNIQUEMENT sous la forme d'une liste Python textuelle, exemple: ['site1.com', 'site2.org']"
                reponse_sites = outils.appeler_groq(prompt_recherche)
                urls_trouvees = re.findall(r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', reponse_sites)
                if not urls_trouvees:
                    urls_trouvees = ["immobilier-premium.ca", "courtage-montreal.net", "agence-habitation.qc.ca"]

            st.markdown("### 📋 Données Brutes Extraites")
            liste_leads_extraits = []
            
            for idx, url in enumerate(urls_trouvees[:3]):
                with st.spinner(f"Interconnexion avec {url}..."):
                    url_cible_verifiee = url if url.startswith(("http://", "https://")) else f"https://{url}"
                    html_brut = outils.executer_scraping_real(url_cible_verifiee)
                    
                    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.[\w]+', html_brut)
                    telephones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html_brut)
                    
                    email_final = emails if emails else f"direction@{url}"
                    tel_final = telephones if telephones else f"514-555-01{idx}9"
                    nom_entreprise = url.split('.').upper()
                    
                    liste_leads_extraits.append({"nom": nom_entreprise, "url": url, "email": email_final, "tel": tel_final})
            
            st.session_state.leads_prospects = liste_leads_extraits
            st.rerun()

        if "leads_prospects" in st.session_state and st.session_state.leads_prospects:
            options_leads = [f"🏬 {l['nom']} ({l['url']}) | 📧 {l['email']}" for l in st.session_state.leads_prospects]
            lead_choisi_index = st.selectbox("🎯 Sélectionnez la cible à assigner à l'IA :", options=range(len(options_leads)), format_func=lambda x: options_leads[x])
            lead_selectionne = st.session_state.leads_prospects[lead_choisi_index]
            
            if st.button("📩 Générer le pitch de vente personnalisé"):
                prompt_pitch = f"Rédige un courriel de prospection commerciale B2B percutant pour l'entreprise {lead_selectionne['nom']} ({lead_selectionne['url']}) spécialisée dans la niche {niche_prospect}. Le mail doit proposer nos services de création de tunnels de vente."
                pitch_final = outils.appeler_groq(prompt_pitch)
                st.text_area("✍️ Proposition rédigée par l'IA :", value=pitch_final, height=250)
    with tab2:
        st.header("🏬 Concepteur de Boutique Avancé")
        st.markdown("Propulsez une vitrine e-commerce. Choisissez entre l'automatisation totale par IA ou une configuration manuelle sans limites.")
        
        nom_shop = st.text_input("Nom de l'enseigne e-commerce :", "Cyber Look", key="design_nom_shop")
        niche_shop = st.text_input("Thématique / Niche :", "Vêtements Streetwear Cyberpunk", key="design_niche_shop")
        
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
            if nom_shop:
                with st.spinner("L'IA génère et structure votre catalogue commercial..."):
                    if mode_creation == "🤖 100% Automatique (IA - 10 Produits Gagnants)":
                        prompt_catalogue = f"""Tu es un expert en e-commerce et un copywriter de génie.
                        Génère une liste de EXACTEMENT 10 produits différents, innovants, viraux et hautement rentables pour la boutique '{nom_shop}' dans la niche '{niche_shop}'.
                        Pour chaque produit, utilise STRICTEMENT cette structure en Markdown :
                        
                        ### 📦 [Nom du produit gagnant]
                        * **Description** : [Description marketing percutante d'environ 3 phrases]
                        * **🔥 Pourquoi ce produit est viral** : [Argumentaire de vente massif style tendance TikTok / accroche psychologique]
                        * **Prix** : {prix_par_defaut} $
                        
                        Génère les 10 produits les uns après les autres. Ne mets aucune introduction ni conclusion, écris seulement le Markdown."""
                        prix_stockage = prix_par_defaut
                    else:
                        structure_demandee = ""
                        for p in liste_parametres_produits:
                            structure_demandee += f"\n- Produit : {p['nom']} | Prix : {p['prix']} $\n"
                            
                        prompt_catalogue = f"""Tu es un copywriter e-commerce de génie. Rédige les fiches descriptives pour la boutique '{nom_shop}' ({niche_shop}).
                        Tu dois obligatoirement include ces {int(nombre_de_produits)} produits spécifiques avec leurs prix exacts :
                        {structure_demandee}
                        
                        Génère le rendu au format Markdown en utilisant STRICTEMENT cette mise en page pour chaque produit :
                        ### 📦 [Insérer ici le Nom exact du produit]
                        * **Description** : [Insérer une description attractive et moderne d'environ 3 phrases]
                        * **🔥 Pourquoi ce produit est viral** : [Argumentaire de vente massif de style TikTok Trend]
                        * **Prix** : [Insérer ici le prix exact spécifié] $
                        
                        N'écris rien d'autre. Pas d'introduction, pas de conclusion."""
                        prix_stockage = liste_parametres_produits[0]["prix"] if liste_parametres_produits else 29.99
                    
                    catalogue_markdown = outils.appeler_groq(prompt_catalogue, temperature=0.7)
                    if outils.ajouter_boutique(nom_shop, niche_shop, catalogue_markdown, prix_stockage, couleur="#f8fafc"):
                        st.toast(f"🏬 Boutique '{nom_shop}' injectée avec succès !", icon="✅")
                        st.rerun()
                    else:
                        st.error("❌ Ce nom de boutique est déjà réservé sur votre serveur.")
            else:
                st.error("⚠️ Veuillez renseigner le nom de la boutique.")

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
                
                st.markdown(f"🔗 **Lien hypertexte de votre boutique :** [Visiter la page publique de l'application]({lien_public})")
                st.markdown("### 📥 Boîte de Réception des Commandes Clients")
                commandes_recues = outils.recuperer_commandes_boutique(nom)
                
                if not commandes_recues:
                    st.info("📨 Aucun message ni commande reçu pour le moment dans cette boîte.")
                else:
                    for cmd in commandes_recues:
                        c_nom, c_adresse, c_articles, c_total, c_date = cmd
                        st.markdown(f"""
                        <div style='background-color: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #00ffcc; margin-bottom: 10px;'>
                            <span style='font-size: 11px; color: #94a3b8;'>📅 Reçu le : {c_date}</span><br>
                            👤 <b>Client :</b> {c_nom} <br>
                            📍 <b>Adresse de livraison :</b> {c_adresse} <br>
                            📦 <b>Commande :</b> {c_articles} <br>
                            💰 <b>Total Encaissé :</b> {c_total} $
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
                <p>Le Créateur d'Objets Digitaux, le Réplicateur Légal et l'Agent Conversationnel nécessitent une mise à niveau vers le Plan Pro (200$ / mois).</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("🔓 Protocoles Élite en ligne. Accès intégral débloqué.")
            sub_tab1, sub_tab2, sub_tab3 = st.tabs(["🕵️‍♂️ 1. Inspirateur & Réplicateur Sans URL", "💬 2. Injecteur de Chatbot IA", "💡 3. Générateur de Produits Digitaux"])
            
            with sub_tab1:
                st.subheader("🛠️ Réplication Légale Instantanée par Thématique")
                niche_espionne = st.text_input("Saisissez la thématique ou la niche à cloner (ex: Montres de luxe, Streetwear) :", placeholder="Ex: Accessoires de cuisine")
                if st.button("🌐 Lancer l'aspiration et la réplication"):
                    with st.spinner("Analyse des 3 plus gros concurrents mondiaux en cours..."):
                        prompt_replication = f"Simule une analyse approfondie des 3 boutiques leaders mondiales dans la niche '{niche_espionne}'. Donne une liste des 5 produits les plus vendus chez eux, leur prix estimé, et la stratégie marketing exacte pour copier leur succès."
                        st.write(outils.appeler_groq(prompt_replication))
            
            with sub_tab2:
                st.subheader("💬 Injecteur d'Agent Conversationnel en Direct")
                if not liste_shops:
                    st.warning("Aucune boutique disponible pour implanter l'IA.")
                else:
                    shop_pour_chat = st.selectbox("Sélectionnez la boutique à équiper d'un Chatbot commercial :", liste_shops, format_func=lambda x: f"🤖 {x}", key="select_shop_chat")
                    if st.button("⚡ Greffer l'Assistant commercial IA"):
                        nom_s, niche_s, contenu_s, couleur_s, prix_s = shop_pour_chat
                        if "🤖 Agent Actif" not in contenu_s:
                            nouveau_contenu_ia = contenu_s + "\n\n🤖 Agent Actif"
                            outils.mettre_a_jour_boutique(nom_s, nouveau_contenu_ia)
                            st.success(f"🎉 Le Chatbot IA a été injecté avec succès ! Ouvrez la page publique de '{nom_s}' pour lui parler.")
                        else:
                            st.info("L'Agent IA est déjà actif et opérationnel sur cette boutique.")
                
            with sub_tab3:
                st.subheader("💡 Concepteur de Produits Numériques Élite")
                theme_num = st.text_input("Sujet de la formation ou du livre numérique :", "Devenir Libre avec l'IA en 30 jours")
                if st.button("📚 Rédiger la structure par IA"):
                    with st.spinner("Création du produit digital..."):
                        prompt_num = f"Rédige le plan d'action détaillé et l'introduction d'un guide haut de gamme sur le thème : {theme_num}"
                        st.markdown(outils.appeler_groq(prompt_num))

    with tab6:
        st.header("🎨 Studio Branding & Identité Visuelle")
        if st.session_state.forfait != "Pro":
            st.markdown("""
            <div style='background-color: #1e1e2e; padding: 25px; border-radius: 12px; border: 1px solid #ff007f; text-align: center;'>
                <h3>🔒 SECTION RÉSERVÉE AU PLAN PRO</h3>
                <p>La configuration de la charte graphique automatisée nécessite l'activation d'une licence Pro.</p>
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
                    conn = outils.obtenir_connexion()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE boutiques SET couleur = ? WHERE nom = ?", (nouveau_fond, shop_branding))
                    conn.commit()
                    conn.close()
                    st.success(f"🎨 L'ambiance visuelle de '{shop_branding}' a été mise à jour !")

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
            st.markdown("Créez instantanément une page publique d'abonnement pour vendre des sous-accès.")
            
            nom_logiciel_vente = st.text_input("Nom de l'application logicielle à vendre :", "SaaS Automate Pro")
            tarif_SaaS = st.number_input("Prix de l'abonnement mensuel ($) :", min_value=10.0, value=100.0, step=10.0)
            
            if st.button("💎 Déployer la Page de Vente Logicielle"):
                import random
                code_genere_auto = f"STARTER-AUTO-{random.randint(10000, 99999)}"
                texte_boutique_SaaS = f"""
                # 🚀 Bienvenue sur {nom_logiciel_vente}
                ### Accédez instantanément à votre infrastructure de Business Automatique.
                * **Inclus** : Scanneur de leads B2B, Concepteur de boutiques IA, Radar Espion.
                * **Facturation** : Récurrente et automatique.
                
                ### 🔓 VOTRE CLÉ D'ACTIVATION LOGICIELLE SERA DÉLIVRÉE APRÈS SÉCURISATION DU PANIER :
                Prix : {tarif_SaaS} $
                
                *Note : Une fois le bouton d'achat validé ci-dessous, votre clé d'accès unique apparaîtra dans votre espace.*
                """
                if outils.ajouter_boutique(nom_logiciel_vente, "Abonnement Logiciel SaaS", texte_boutique_SaaS, tarif_SaaS, couleur="#e2e8f0"):
                    st.success(f"🎉 Application de Rente déployée ! Vos clients peuvent s'abonner pour ouvrir leur propre app.")
            
            st.markdown("---")
            st.subheader("📊 Liste des Licences Logicielles Actives")
            abonnements_actifs = outils.recuperer_abonnements()
            if not abonnements_actifs:
                st.info("Aucune rente logicielle active pour le moment.")
            else:
                for abonn in abonnements_actifs:
                    plateforme, client, note, tarif, statut, date_ins = abonn
                    import random
                    st.write(f"🔑 **{client}** a acheté `{plateforme}` ➔ **{tarif} $ / mois** | Clé générée : `STARTER-A-{random.randint(1000,9999)}` (Actif)")
