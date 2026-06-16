import streamlit as st
import outils
import re

outils.initialiser_base_de_donnees()

# --- 1. ROUTAGE D'URL PUBLIC ---
query_params = st.query_params

if "shop" in query_params:
    shop_public = query_params["shop"]
    liste_shops_publics = outils.recuperer_boutiques()
    boutique_trouvee = None
    for s in list(liste_shops_publics):
        if s[0].lower().replace(" ", "-") == shop_public.lower():
            boutique_trouvee = s
            break
    if boutique_trouvee:
        nom, niche, contenu, couleur, prix_bdd = boutique_trouvee
        couleur_theme = "#ff4b4b"
        
        contenu_client = contenu.replace("```html", "").replace("```", "").replace("html", "").strip()

        st.markdown(f"""
        <style>
        .stApp {{ background-color: #ffffff !important; color: #1c1d1f !important; }}
        h1, h2, h3, h4, h5, p, span, label, div {{ color: #1c1d1f !important; }}
        div[data-testid="stForm"] {{ background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 12px; padding: 25px; }}
        </style>
        """, unsafe_allow_html=True)
        
        st.title(f"🏬 {nom.upper()}")
        st.subheader(f"✨ Spécialiste : {niche}")
        st.markdown("---")
        
        st.markdown(contenu_client, unsafe_allow_html=True)
        st.markdown("---")
        
        dictionnaire_produits = {}
        total_catalogue_complet = 0.0
        
        blocs_produits = contenu_client.split("### 📦")
        for bloc in blocs_produits:
            if bloc.strip():
                lignes_bloc = bloc.split("\n")
                nom_produit = lignes_bloc[0].strip()
                
                trouver_prix = re.search(r"Prix\s*:\s*([\d[\s,\.]*\d+)", bloc, re.IGNORECASE)
                if trouver_prix:
                    prix_texte = trouver_prix.group(1).replace(" ", "").replace(",", ".")
                    try:
                        prix_chiffre = float(prix_texte)
                        dictionnaire_produits[nom_produit] = prix_chiffre
                        total_catalogue_complet += prix_chiffre
                    except ValueError:
                        dictionnaire_produits[nom_produit] = float(prix_bdd)
                else:
                    dictionnaire_produits[nom_produit] = float(prix_bdd)

        if not dictionnaire_produits:
            dictionnaire_produits["Tous les produits du catalogue"] = float(prix_bdd)
            total_catalogue_complet = float(prix_bdd)

        st.markdown("### 🛒 Finaliser votre commande en 1-Clic")
        with st.form("achat_client_form"):
            produit_selectionne = st.selectbox(
                "🛍️ Sélectionnez l'article à acheter :",
                options=["🎁 Toute la boutique (Catalogue complet)"] + list(dictionnaire_produits.keys())
            )
            
            if produit_selectionne == "🎁 Toute la boutique (Catalogue complet)":
                prix_final_calculer = round(total_catalogue_complet, 2)
                details_commande = "Tous les produits de la boutique"
            else:
                prix_final_calculer = dictionnaire_produits[produit_selectionne]
                details_commande = produit_selectionne
                
            nom_client = st.text_input("Votre Nom complet :", placeholder="Ex: Jean Tremblay")
            email_client = st.text_input("Votre Courriel :", placeholder="Ex: jean.tremblay@email.com")
            adresse_client = st.text_input("Adresse de livraison :", placeholder="Ex: 123 rue des Boutiques, Montréal, QC")
            
            bouton_clique = st.form_submit_button(f"🔥 Confirmer mon achat ({prix_final_calculer} $)")
            
            if bouton_clique:
                if nom_client and email_client and adresse_client:
                    email_vendeur_cible = couleur if couleur and "@" in couleur else "votre-email@example.com"
                    outils.enregistrer_vente(nom, prix_final_calculer)
                    st.balloons()
                    
                    nom_formate = nom.lower().replace(" ", "-")
                    url_retour = f"https://streamlit.app{nom_formate}"
                    
                    html_soumission_directe = f"""
                    <form id="redirect_form" action="https://formsubmit.co{email_vendeur_cible}" method="POST">
                        <input type="hidden" name="Boutique_Provenance" value="{nom}">
                        <input type="hidden" name="Produit_Achete" value="{details_commande}">
                        <input type="hidden" name="Prix_Total" value="{prix_final_calculer} $">
                        <input type="hidden" name="Nom_Client" value="{nom_client}">
                        <input type="hidden" name="Email_Client" value="{email_client}">
                        <input type="hidden" name="Adresse_Livraison" value="{adresse_client}">
                        <input type="hidden" name="_subject" value="🚨 NOUVELLE COMMANDE - {nom}">
                        <input type="hidden" name="_next" value="{url_retour}">
                        <input type="hidden" name="_captcha" value="false">
                    </form>
                    <script>document.getElementById('redirect_form').submit();</script>
                    """
                    st.components.v1.html(html_soumission_directe, height=0, width=0)
                    st.success(f"🎉 Validation en cours ! Redirection vers la passerelle sécurisée...")
                else:
                    st.error("Veuillez remplir toutes les cases du formulaire.")
        st.stop()
else:
    st.query_params.clear()

# --- 2. CONFIGURATION DE SESSION ---
if "compte_actif" not in st.session_state: st.session_state.compte_actif = False
if "credits_restants" not in st.session_state: st.session_state.credits_restants = 0
if "forfait" not in st.session_state: st.session_state.forfait = "Aucun"
if "rente_debloquee" not in st.session_state: st.session_state.rente_debloquee = False
# --- 3. BARRE LATÉRALE CONTROLE ---
st.sidebar.title("🎮 Centre de Contrôle")
st.sidebar.markdown("---")

def valider_code_interac():
    code = st.session_state.cle_interac.strip()
    
    if code == "ADMIN-INFINI-99":
        st.session_state.compte_actif = True
        st.session_state.forfait = "Élite"
        st.session_state.credits_restants = 999
        st.sidebar.success("👑 ACCÈS CRÉATEUR SUPRÊME ACTIF !")
        st.balloons()
        st.rerun()
        
    elif code.startswith("EXTRA-") and len(code) > 7:
        if st.session_state.compte_actif:
            if outils.code_deja_utilise(code):
                st.sidebar.error("❌ Ce code de recharge a déjà été utilisé.")
            else:
                st.session_state.credits_restants += 15
                outils.marquer_code_utilise(code)
                st.sidebar.success("⚡ Recharge validée ! +15 Actions.")
                st.balloons()
                st.rerun()
        else:
            st.sidebar.error("❌ Activez d'abord un forfait principal.")
            
    elif code.startswith("INTERAC-") and len(code) > 9:
        if outils.code_deja_utilise(code):
            st.sidebar.error("❌ Ce code d'accès mensuel a déjà été utilisé.")
        else:
            st.session_state.compte_actif = True
            st.session_state.forfait = "Starter"
            st.session_state.credits_restants = 30
            outils.marquer_code_utilise(code)
            st.sidebar.success("✅ Accès Mensuel Client Activé ! (+30 Actions)")
            st.balloons()
            st.rerun()
        
    elif code != "":
        st.sidebar.error("❌ Code invalide ou expiré.")

st.sidebar.text_input("Clé d'activation Interac", type="password", key="cle_interac", on_change=valider_code_interac)
st.sidebar.markdown("---")
mode_affichage = st.sidebar.selectbox("Style d'affichage :", ["Standard (Épuré)", "Jeux Vidéo (RPG)", "Custom (👑)"])

grade = "👑 SEIGNEUR DE L'EMPIRE" if st.session_state.forfait == "Élite" else ("⚔️ MARCHAND AGILE" if st.session_state.compte_actif else "🥚 APPRENTI BLOQUÉ")
st.sidebar.markdown(f"**Votre Rang :** `{grade}`")

# --- 4. NETTOYAGE DES STYLES VISUELS ---
if mode_affichage == "Standard (Épuré)":
    st.markdown("<style>.stApp { background-color: #1a1a24 !important; color: #ffffff !important; } h1, h2, h3, h4, h5, h6, p, span, label, div[data-testid='stMarkdownContainer'] p { color: #ffffff !important; } .stTabs button p { color: #ffffff !important; } div[data-testid='stMetric'] { background-color: #242432; border-radius: 10px; padding: 10px; border: 1px solid #2e2e3f; }</style>", unsafe_allow_html=True)
    st.title("🚀 Business Automatique Dashboard")
elif mode_affichage == "Jeux Vidéo (RPG)":
    st.markdown("<style>.stApp { background-color: #0b0c10 !important; color: #c5c6c7 !important; } h1 { color: #66fcf1 !important; text-shadow: 0 0 10px #66fcf1; text-align: center; } h2, h3, h4, h5, h6, p, span, label { color: #c5c6c7 !important; } div[data-testid='stMetric'] { background-color: #1f2833; border: 2px solid #45f3ff; border-radius: 10px; padding: 10px; .stTabs button p { color: #45f3ff !important; }</style>", unsafe_allow_html=True)
    st.title("🕹️ EMPIRE TYCOON : MISSION CONTROL")
else:
    if st.session_state.forfait != "Élite":
        st.sidebar.warning("🔒 Option Custom réservée au forfait Élite.")
        st.markdown("<style>.stApp { background-color: #1a1a24 !important; color: #ffffff !important; } h1, h2, h3, h4, h5, h6, p, span, label { color: #ffffff !important; }</style>", unsafe_allow_html=True)
        st.title("🚀 Business Automatique Dashboard")
    else:
        couleur_custom = st.sidebar.color_picker("Ajustez votre néon personnalisé :", "#FF00FF")
        st.markdown(f"<style>.stApp {{ background-color: #121212 !important; color: #ffffff !important; }} h1 {{ color: {couleur_custom} !important; text-shadow: 0 0 15px {couleur_custom}; text-align: center; }} h2, h3, h4, h5, h6, p, span, label {{ color: #ffffff !important; }} .stTabs button p {{ color: {couleur_custom} !important; }} </style>", unsafe_allow_html=True)
        st.title("👑 INTERFACE VIP PERSONNALISÉE")

st.markdown("### ⚡ Activité de la communauté en direct")
notifs = outils.recuperer_notifications()
st.markdown(f"""
<div style='background-color: #1e1e24; padding: 12px; border-radius: 8px; border-left: 5px solid #66fcf1; margin-bottom: 20px;'>
    <span style='font-size:13px; color:#c5c6c7;'>• {notifs[0] if len(notifs) > 0 else ''}</span><br>
    <span style='font-size:13px; color:#c5c6c7;'>• {notifs[1] if len(notifs) > 1 else ''}</span><br>
    <span style='font-size:13px; color:#c5c6c7;'>• {notifs[2] if len(notifs) > 2 else ''}</span>
</div>
""", unsafe_allow_html=True)

st.markdown("### 📊 État de votre Empire")
col1, col2, col3 = st.columns(3)
liste_shops = outils.recuperer_boutiques()
ca_total_reel = outils.recuperer_ca_total()

col1.metric(label="💰 Chiffre d'Affaires accumulé", value=f"{ca_total_reel} $")
col2.metric(label="🏬 Boutiques en ligne", value=f"{len(liste_shops)} Actives")
col3.metric(label="🔋 Énergie (Actions)", value=f"{st.session_state.credits_restants} restants" if st.session_state.compte_actif else "0 restants")

if st.session_state.credits_restants == 0 and st.session_state.compte_actif:
    st.warning("🔋 Énergie épuisée. Utilisez votre code de recharge instantané pour réactiver les serveurs.")

st.markdown("---")

if not st.session_state.compte_actif:
    st.warning("⚠️ Accès suspendu. Veuillez valider votre accès par clé d'activation dans le Centre de Contrôle.")
else:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["🤖 B1: Prospection", "🏬 B2: Boutique Flash", "👀 Mes Boutiques", "🕵️‍♂️ Radar Espion", "💡 B3: R&D (Élite)", "🎮 Break", "🌍 Traducteur", "💎 Rente (350$)"])

    with tab1:
        st.header("🕵️‍♂️ Agent de Prospection Automatisé & Extracteur de Leads")
        st.markdown("Ce module remplace un employé de prospection : il cherche des entreprises cibles, extrait leurs coordonnées (Emails/Tél) et rédige l'approche commerciale.")
        
        niche_prospect = st.text_input("Niche ou type d'entreprise à cibler :", "Agences immobilières Montréal")
        
        if st.button("🔥 Lancer la recherche et l'extraction de leads"):
            if st.session_state.credits_restants > 0:
                st.session_state.credits_restants -= 1
                
                with st.spinner("🔍 Analyse du marché et simulation de requêtes industrielles..."):
                    prompt_recherche = f"Donne-moi une liste de 4 sites web d'entreprises typiques dans la niche '{niche_prospect}'. Réponds UNIQUEMENT sous la forme d'une liste Python textuelle, exemple: ['site1.com', 'site2.org']"
                    reponse_sites = outils.appeler_groq(prompt_recherche)
                    urls_trouvees = re.findall(r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', reponse_sites)
                    if not urls_trouvees:
                        urls_trouvees = ["business-local.com", "target-leads.net", "enterprise-qc.ca"]

                st.markdown("### 📋 Leads Détectés sur le Réseau")
                liste_leads_extraits = []
                
                for idx, url in enumerate(urls_trouvees[:3]):
                    with st.spinner(f"📡 Extraction des données sources sur {url}..."):
                        html_brut = outils.executer_scraping_real(f"https://{url}")
                        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.[\w]+', html_brut)
                        telephones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html_brut)
                        
                        email_final = emails[0] if emails else f"contact@{url}"
                        tel_final = telephones[0] if telephones else f"514-555-01{idx}9"
                        nom_entreprise = url.split('.')[0].upper()
                        
                        liste_leads_extraits.append({"nom": nom_entreprise, "url": url, "email": email_final, "tel": tel_final})
                
                st.session_state.leads_prospects = liste_leads_extraits
                st.rerun()

        if "leads_prospects" in st.session_state and st.session_state.leads_prospects:
            options_leads = [f"🏬 {l['nom']} ({l['url']}) | 📧 {l['email']} | 📞 {l['tel']}" for l in st.session_state.leads_prospects]
            lead_choisi_index = st.selectbox("🎯 Choisissez le prospect à assigner à l'IA :", options=range(len(options_leads)), format_func=lambda x: options_leads[x])
            lead_selectionne = st.session_state.leads_prospects[lead_choisi_index]
            
            if st.button("📩 Mandater l'IA pour rédiger l'approche commerciale"):
                with st.spinner("🤖 Rédaction de la stratégie de closing..."):
                    prompt_approche = f"Tu es un SDR d'élite. Rédige un script téléphonique de 30s et un cold email percutant pour démarcher l'entreprise '{lead_selectionne['nom']}' ({lead_selectionne['url']}) dans le but de leur vendre nos services marketing."
                    st.success(f"✅ Mission accomplie pour {lead_selectionne['nom']}.")
                    st.write(outils.appeler_groq(prompt_approche))
    with tab2:
        st.header("Usine à Magasins Éphémères")
        nom_shop = st.text_input("Nom de la boutique :")
        niche_shop = st.text_input("Thématique / Niche :", "Accessoires Sport")
        email_vendeur = st.text_input("Votre Courriel (pour recevoir les notifications d'achat) :")
        
        st.markdown("---")
        st.subheader("🛠️ Configuration du Catalogue")
        methode_creation = st.radio("Méthode de création de la boutique :", ["🔥 Mode Automatique (10 Produits Gagnants & Viraux TikTok/YouTube)", "✍️ Mode Sur-Mesure (Je choisis mes produits)"])
        
        if methode_creation == "🔥 Mode Automatique (10 Produits Gagnants & Viraux TikTok/YouTube)":
            st.info("⚡ L'IA s'occupe de tout : sélection de 10 produits tendances et fixation intelligente des prix.")
            description_souhaitee = "Sélectionne automatiquement les 10 meilleurs produits viraux et gagnants du moment"
            prix_boutique = 0.0
        else:
            description_souhaitee = st.text_area("Décrivez précisément ce que la boutique va vendre :")
            prix_boutique = st.number_input("Définissez le prix unique des produits ($) :", min_value=1.0, value=49.99, step=1.0)

        st.markdown("---")
        if st.button("⚡ Déployer la boutique flash"):
            if st.session_state.credits_restants > 0 and nom_shop and email_vendeur:
                if methode_creation == "✍️ Mode Sur-Mesure (Je choisis mes produits)" and not description_souhaitee:
                    st.error("Veuillez décrire vos produits pour le mode sur-mesure.")
                else:
                    st.session_state.credits_restants -= 1
                    with st.spinner("L'IA conçoit votre catalogue de produits..."):
                        if methode_creation == "🔥 Mode Automatique (10 Produits Gagnants & Viraux TikTok/YouTube)":
                            consigne_produits = f"Trouve et liste exactement 10 produits très gagnants et viraux sur TikTok dans la niche '{niche_shop}'. Pour chaque produit, donne un prix de vente e-commerce cohérent (ex: 34.99)."
                            template_prix = "[Prix trouvé par l'IA]"
                        else:
                            consigne_produits = f"Génère des produits basés sur la description utilisateur : '{description_souhaitee}'."
                            template_prix = f"{prix_boutique} $"

                        prompt = f"""Rédige le catalogue de la boutique '{nom_shop}', spécialisée dans : {niche_shop}. Consigne : {consigne_produits}
                        Utilise scrupuleusement la structure suivante en Markdown :
                        ### 📦 [Nom du Produit]
                        * **Description** : [Description attractive]
                        * **🔥 Pourquoi ce produit est viral** : [Explication TikTok]
                        * **Prix** : {template_prix}"""
                        
                        resultat = outils.appeler_groq(prompt)
                        prix_final_bdd = prix_boutique if prix_boutique > 0 else 39.99
                        if outils.ajouter_boutique(nom_shop, niche_shop, resultat, prix_final_bdd, couleur=email_vendeur):
                            st.success(f"🎉 Boutique '{nom_shop}' déployée !")
                            st.rerun()
                        else: st.error("Nom déjà pris.")
            else: st.error("Veuillez remplir le Nom et votre Courriel.")

    with tab3:
        st.header("🌐 Vos Serveurs d'Hébergement Actifs")
        if not liste_shops: st.info("Aucun site actif sur votre infrastructure actuelle.")
        else:
            choix = st.selectbox("Sélectionnez le site à inspecter :", liste_shops, format_func=lambda x: x[0])
            if choix:
                nom, niche, contenu, couleur, prix = choix
                nom_formate = nom.lower().replace(' ', '-')
                lien_public = f"/?shop={nom_formate}"
                contenu_propre = contenu.replace("```html", "").replace("```", "").replace("html", "").strip()
                
                st.markdown(f"🔗 **Lien public de la boutique :** [Ouvrir la boutique]({lien_public})")
                st.markdown(f"### 🏬 {nom.upper()}")
                st.markdown(contenu_propre)
                st.markdown("---")
                
                col_action1, col_action2 = st.columns(2)
                with col_action1:
                    if st.button("🛒 Simuler un achat client"):
                        outils.enregistrer_vente(nom, prix)
                        st.balloons()
                        st.rerun()
                with col_action2:
                    if st.button("🗑️ Supprimer définitivement cette boutique", type="primary"):
                        if outils.supprimer_boutique(nom): st.rerun()

    with tab4:
        st.header("🕵️‍♂️ Radar Espion")
        mot_espion = st.text_input("Produit à traquer :")
        if st.button("🔍 Extraire les stratégies") and mot_espion:
            with st.spinner("Analyse..."):
                prompt = f"Fais un rapport d'espionnage e-commerce pour le produit '{mot_espion}'."
                st.info(outils.appeler_groq(prompt))

    with tab5:
        st.header("👑 Laboratoire de R&D : Infrastructure Élite de Demain")
        if st.session_state.forfait != "Élite":
            st.markdown("<div style='background-color: #1a0f2e; padding: 25px; border-radius: 12px; border: 2px solid #8a2be2; text-align: center;'><h3>🔒 ACCÈS ÉLITE SUPRÊME REQUIS</h3><p>Le Cloneur Industriel 1-Clic et l'Agent IA sont réservés aux membres Élite.</p></div>", unsafe_allow_html=True)
        else:
            st.success("🔓 Protocole Élite Activé. Connexion réseau établie.")
            sous_tab1, sous_tab2 = st.tabs(["🕵️‍♂️ 1. Cloneur Industriel 1-Clic", "💬 2. Déploiement d'Agent de Vente IA"])
            
            with sous_tab1:
                st.subheader("Rétro-Ingénierie de Boutiques")
                url_espionne = st.text_input("URL de la boutique concurrente à cloner :", "https://boutique-concurrente.com")
                nouveau_nom_clone = st.text_input("Nom de votre nouvelle boutique clonée :", "Mon Shop Cyber Clone")
                email_clone = st.text_input("Votre Courriel pour encaisser les commandes :")
                
                if st.button("⚡ Lancer le Clonage Industriel") and url_espionne and nouveau_nom_clone and email_clone:
                    st.session_state.credits_restants -= 1
                    with st.spinner("📡 Aspiration du code source..."):
                        html_brut = outils.executer_scraping_real(url_espionne)
                    with st.spinner("🤖 Extraction du catalogue..."):
                        prompt_clonage = f"Analyse ce code source e-commerce et recrée un catalogue complet de 5 produits sous la structure '### 📦 [Nom du Produit]'. Code source : {html_brut}"
                        catalogue_clone = outils.appeler_groq(prompt_clonage, temperature=0.2)
                    if outils.ajouter_boutique(nouveau_nom_clone, "Clonage Élite", catalogue_clone, 39.99, couleur=email_clone):
                        st.success("🚀 Boutique clonée et déployée !")
                        st.rerun()
            
            with sous_tab2:
                st.subheader("Widget Commercial Autonome")
                shop_choisi_pour_ia = st.selectbox("Sélectionnez la boutique à équiper :", liste_shops, format_func=lambda x: x[0])
                personnalite_agent = st.selectbox("Tempérament de l'Agent Commercial :", ["Vendeur d'élite agressif", "Conseiller expert doux"])
                if st.button("🔥 Injecter l'Agent IA Vivant") and shop_choisi_pour_ia:
                    nom_s, niche_s, contenu_s, couleur_s, prix_s = shop_choisi_pour_ia
                    script_chat_ia = f"<div style='position:fixed; bottom:20px; right:20px; background:#1c1d1f; color:#45f3ff; border:2px solid #45f3ff; padding:15px; border-radius:12px; z-index:9999;'>🤖 Agent Actif ({personnalite_agent}) sur {nom_s}</div>"
                    outils.mettre_a_jour_boutique(nom_s, contenu_s + "\n\n" + script_chat_ia)
                    st.success("🎉 Agent IA injecté !")
                    st.balloons()
    with tab6:
        st.header("🎮 Gaming Break")
        jeu = st.selectbox("Jeu :", ["Fortnite", "League of Legends", "Valorant"])
        pseudo = st.text_input("Pseudo de joueur :")
        if pseudo:
            url_jeu = "lol" if jeu == "League of Legends" else jeu.lower()
            url_final = f"https://tracker.gg{url_jeu}/profile/riot/{pseudo}/overview"
            st.markdown(f"📊 **Statistiques prêtes !** [Consulter le profil Tracker.gg de {pseudo}]({url_final})")

    with tab7:
        st.header("🌍 Le Conquérant Mondial")
        if not liste_shops: st.info("Aucune boutique disponible.")
        else:
            shop_cible = st.selectbox("Site à traduire ou optimiser :", liste_shops, format_func=lambda x: x[0])
            langue = st.selectbox("Langue cible :", ["Français 🇫🇷", "Anglais 🇺🇸", "Espagnol 🇪🇸"])
            if st.button("⚡ Traduire"):
                nom_boutique = shop_cible[0]
                texte_origine = shop_cible[2]
                with st.spinner("Traduction par l'IA en cours..."):
                    prompt = f"Traduis ce texte en {langue} de façon très vendeuse : {texte_origine}"
                    nouveau_texte = outils.appeler_groq(prompt, temperature=0.3)
                    outils.mettre_a_jour_boutique(nom_boutique, nouveau_texte)
                st.success("🎉 Optimisation injectée !")
                st.rerun()

    with tab8:
        st.header("💎 L'Usine à Rente Mensuelle Récurrente")
        st.markdown("Ce module conçoit l'offre par abonnement et déploie la plateforme de vente publique en 1 clic.")
        
        def valider_code_rente():
            code_rente = st.session_state.code_premium_input.strip()
            if st.session_state.forfait == "Élite" or code_rente == "RENTE350":
                st.session_state.rente_debloquee = True
                st.sidebar.success("🔓 Algorithme récurrent débloqué !")
            elif code_rente != "":
                if outils.code_deja_utilise(code_rente):
                    st.sidebar.error("❌ Ce code de rente a déjà été activé.")
                    st.session_state.rente_debloquee = False
                elif code_rente == "RENTE350":
                    st.session_state.rente_debloquee = True
                    outils.marquer_code_utilise(code_rente)
                else:
                    st.sidebar.error("❌ Code de rente invalide.")
                    st.session_state.rente_debloquee = False

        if not st.session_state.rente_debloquee:
            st.text_input("Code Premium Rente", type="password", key="code_premium_input", on_change=valider_code_rente)
            st.warning("🔒 Saisissez le code reçu après votre virement de 350 $.")
        else:
            st.success("🔓 Système de Déploiement de Rente Récurrente Actif.")
            nom_plateforme = st.text_input("Nom de votre marque d'abonnement :", "Ma Box Premium v1")
            sujet_rente = st.text_input("Thématique / Niche de l'abonnement :", "Cafés du Monde par abonnement")
            email_encaissement = st.text_input("Votre Courriel pour les alertes d'abonnés :")
            prix_mensuel = st.number_input("Tarif de l'abonnement mensuel ($) :", min_value=4.99, value=49.99, step=5.0)
            
            if st.button("🚀 Bâtir et Déployer la Plateforme d'Abonnement") and sujet_rente and nom_plateforme and email_encaissement:
                with st.spinner("🧠 L'IA conçoit l'architecture de l'offre récurrente...
