import streamlit as st
import outils

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
        nom, niche, contenu, couleur, prix = boutique_trouvee
        couleur_theme = couleur if couleur else "#45f3ff"
        st.markdown(f"""
        <style>
        .stApp {{ background-color: #ffffff !important; color: #1c1d1f !important; }}
        h1, h2, h3, p, span, label {{ color: #1c1d1f !important; }}
        </style>
        <div style='border: 3px solid {couleur_theme}; padding: 30px; border-radius: 12px; margin-top: 20px;'>
            <h1 style='text-align: center; color: {couleur_theme} !important;'>🏬 {nom.upper()}</h1>
            <p style='text-align: center; font-style: italic; color: #555555 !important;'>Spécialiste : {niche}</p>
            <hr style='border: 1px solid {couleur_theme};'>
            <div style='font-size: 16px; margin: 20px 0; color: #1c1d1f !important;'>{contenu}</div>
            <p style='font-size: 22px; font-weight: bold; color: green !important; text-align: center;'>Prix unique : {prix} $</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("achat_client"):
            st.markdown("### 🛒 Finaliser votre commande en 1-Clic")
            nom_client = st.text_input("Votre Nom complet :")
            email_client = st.text_input("Votre Courriel :")
            adresse_client = st.text_input("Adresse de livraison :")
            if st.form_submit_button("🔥 Confirmer mon achat"):
                if nom_client and email_client and adresse_client:
                    outils.enregistrer_vente(nom, prix)
                    st.balloons()
                    st.success(f"🎉 Merci {nom_client} ! Votre commande a été transmise au vendeur.")
                else: st.error("Veuillez remplir toutes les cases.")
        st.stop()
    else:
        st.error("Boutique introuvable ou abonnement expiré.")
        st.stop()

# --- 2. CONFIGURATION DE SESSION ---
if "compte_actif" not in st.session_state: st.session_state.compte_actif = False
if "credits_restants" not in st.session_state: st.session_state.credits_restants = 0
if "forfait" not in st.session_state: st.session_state.forfait = "Aucun"

# --- 3. BARRE LATÉRALE CONTROLE ---
st.sidebar.title("🎮 Centre de Contrôle")
st.sidebar.markdown("---")
code_entre = st.sidebar.text_input("Clé d'activation Interac", type="password")

if code_entre == "INTERAC500":
    st.session_state.compte_actif = True
    st.session_state.forfait = "Starter"
    if st.session_state.credits_restants == 0: st.session_state.credits_restants = 10
    st.sidebar.success("✅ Forfait Starter Activé !")
elif code_entre == "INTERAC1000":
    st.session_state.compte_actif = True
    st.session_state.forfait = "Élite"
    if st.session_state.credits_restants == 0: st.session_state.credits_restants = 20
    st.sidebar.success("👑 Forfait Élite Activé !")
elif code_entre == "EXTRA50":
    st.session_state.credits_restants += 1
    st.sidebar.success("⚡ Recharge validée ! +1 Action.")
    st.balloons()

st.sidebar.markdown("---")
mode_affichage = st.sidebar.selectbox("Style d'affichage :", ["Standard (Épuré)", "Jeux Vidéo (RPG)", "Custom (👑)"])

grade = "👑 SEIGNEUR DE L'EMPIRE" if st.session_state.forfait == "Élite" else ("⚔️ MARCHAND AGILE" if st.session_state.compte_actif else "🥚 APPRENTI BLOQUÉ")
st.sidebar.markdown(f"**Votre Rang :** `{grade}`")

# --- 4. NETTOYAGE DES STYLES VISUELS ---
if mode_affichage == "Standard (Épuré)":
    st.markdown("<style>.stApp { background-color: #ffffff !important; color: #1c1d1f !important; } h1, h2, h3, h4, h5, h6, p, span, label { color: #1c1d1f !important; } .stTabs button p { color: #1c1d1f !important; }</style>", unsafe_allow_html=True)
    st.title("🚀 Business Automatique Dashboard")
elif mode_affichage == "Jeux Vidéo (RPG)":
    st.markdown("<style>.stApp { background-color: #0b0c10 !important; color: #c5c6c7 !important; } h1 { color: #66fcf1 !important; text-shadow: 0 0 10px #66fcf1; text-align: center; } h2, h3, h4, h5, h6, p, span, label { color: #c5c6c7 !important; } div[data-testid='stMetric'] { background-color: #1f2833; border: 2px solid #45f3ff; border-radius: 10px; padding: 10px; } .stTabs button p { color: #45f3ff !important; }</style>", unsafe_allow_html=True)
    st.title("🕹️ EMPIRE TYCOON : MISSION CONTROL")
else:
    if st.session_state.forfait != "Élite":
        st.sidebar.warning("🔒 Option Custom réservée au forfait Élite.")
        st.markdown("<style>.stApp { background-color: #ffffff !important; color: #1c1d1f !important; } h1, h2, h3, h4, h5, h6, p, span, label { color: #1c1d1f !important; }</style>", unsafe_allow_html=True)
        st.title("🚀 Business Automatique Dashboard")
    else:
        couleur_custom = st.sidebar.color_picker("Ajustez votre néon personnalisé :", "#FF00FF")
        st.markdown(f"<style>.stApp {{ background-color: #121212 !important; color: #ffffff !important; }} h1 {{ color: {couleur_custom} !important; text-shadow: 0 0 15px {couleur_custom}; text-align: center; }} h2, h3, h4, h5, h6, p, span, label {{ color: #ffffff !important; }} .stTabs button p {{ color: {couleur_custom} !important; }} </style>", unsafe_allow_html=True)
        st.title("👑 INTERFACE VIP PERSONNALISÉE")

# --- 5. COMPOSANTS D'ACCUEIL ---
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

col1.metric(label="💰 Chiffre d'Affaires accumulé", value=f"{ca_total_reel[0] if isinstance(ca_total_reel, tuple) else ca_total_reel} $")
col2.metric(label="🏬 Boutiques en ligne", value=f"{len(liste_shops)} Actives")
col3.metric(label="🔋 Énergie (Actions)", value=f"{st.session_state.credits_restants} restants" if st.session_state.compte_actif else "0 restants")

if st.session_state.credits_restants == 0 and st.session_state.compte_actif:
    st.warning("🔋 Énergie épuisée. Envoyez un virement Interac de 50 $ pour obtenir votre code de recharge instantané.")

st.markdown("---")
if not st.session_state.compte_actif:
    st.warning("⚠️ Accès suspendu. Veuillez valider votre accès mensuel par virement Interac.")
else:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["🤖 B1: Prospection", "🏬 B2: Boutique Flash", "👀 Mes Boutiques", "🕵️‍♂️ Radar Espion", "💡 B3: R&D (Élite)", "🎮 Break", "🌍 Traducteur", "💎 Rente (350$)"])

    with tab1:
        st.header("Extracteur Scrape.do & Rédacteur Commercial IA")
        url_cible = st.text_input("URL du site concurrent à scraper :", "https://example.com")
        if st.button("🔥 Déclencher le scraping et l'analyse"):
            if st.session_state.credits_restants > 0:
                st.session_state.credits_restants -= 1
                with st.spinner("Scrape.do récupère la page..."):
                    st.info(outils.executer_scraping_real(url_cible))
                with st.spinner("L'IA de Groq génère votre e-mail..."):
                    prompt = f"Rédige un court message de vente (max 3 phrases) pour proposer nos services marketing à l'entreprise propriétaire du site '{url_cible}'."
                    st.success("🤖 Message commercial rédigé par l'IA :")
                    st.write(outils.appeler_groq(prompt))
                st.rerun()
            else: st.error("Plus d'énergie disponible.")

    with tab2:
        st.header("Usine à Magasins Éphémères")
        nom_shop = st.text_input("Nom de la boutique :")
        niche_shop = st.text_input("Thématique des produits :", "Accessoires Sport")
        prix_boutique = st.number_input("Définissez le prix de vente de vos produits ($) :", min_value=1.0, value=49.99, step=1.0)
        
        if st.button("⚡ Déployer la boutique flash"):
            if st.session_state.credits_restants > 0 and nom_shop:
                st.session_state.credits_restants -= 1
                with st.spinner("L'IA génère vos produits..."):
                    prompt = f"Génère une liste de 3 produits de e-commerce pour la thématique '{niche_shop}' vendus à {prix_boutique}$. Donne leurs noms et descriptions."
                    resultat = outils.appeler_groq(prompt)
                    if outils.ajouter_boutique(nom_shop, niche_shop, resultat, prix_boutique):
                        st.success(f"🎉 Boutique '{nom_shop}' déployée !")
                        st.rerun()
                    else: st.error("Nom déjà pris.")
            else: st.error("Champs vides ou énergie insuffisante.")

    with tab3:
        st.header("🌐 Vos Serveurs d'Hébergement Actifs")
        if not liste_shops: st.info("Aucun site actif sur votre infrastructure actuelle.")
        else:
            choix = st.selectbox("Sélectionnez le site à inspecter :", liste_shops, format_func=lambda x: x[0])
            if choix:
                nom, niche, contenu, couleur, prix = choix
                couleur_theme = couleur if couleur else "#45f3ff"
                lien_public = f"https://streamlit.app{nom.lower().replace(' ', '-')}"
                st.success(f"🔗 Lien public : `{lien_public}`")
                st.markdown(f"<div style='border: 2px dashed {couleur_theme}; padding: 20px; border-radius: 8px;'><h3>🏬 {nom.upper()}</h3><p><b>Thématique :</b> {niche} | 🟢 Hébergement Actif | <b>Prix configuré :</b> {prix}$</p><hr style='border: 1px solid {couleur_theme};'><div>{contenu}</div></div>", unsafe_allow_html=True)
                
                if st.button("🛒 Simuler un achat client"):
                    outils.enregistrer_vente(nom, prix)
                    st.balloons()
                    st.success(f"Panier de {prix}$ encaissé avec succès via l'Upsell !")
                    st.rerun()

    with tab4:
        st.header("🕵️‍♂️ Radar Espion")
        mot_espion = st.text_input("Produit à traquer :")
        if st.button("🔍 Extraire les stratégies") and mot_espion:
            with st.spinner("Analyse..."):
                prompt = f"Fais un rapport d'espionnage e-commerce pour le produit '{mot_espion}'."
                st.info(outils.appeler_groq(prompt))

    with tab5:
        st.header("💡 Laboratoire de R&D : Concepteur de Produits")
        if st.session_state.forfait != "Élite":
            st.markdown("<div style='background-color: #2c1a1a; padding: 20px; border-radius: 10px; border: 2px solid #ff4b4b; text-align: center;'><h3>🔒 Réservé aux Membres Élite</h3><p>La R&D par IA est réservée au forfait Élite.</p></div>", unsafe_allow_html=True)
        else:
            st.success("🔓 Accès Élite Validé.")
            idee = st.text_input("Votre idée :")
            if st.button("🚀 Matérialiser la marque") and idee:
                prompt = f"Crée une marque complète et un texte marketing pour : '{idee}'."
                st.info(outils.appeler_groq(prompt))

    with tab6:
        st.header("🎮 Gaming Break")
        jeu = st.selectbox("Jeu :", ["Fortnite", "League of Legends", "Valorant"])
        pseudo = st.text_input("Pseudo de joueur :")
        if pseudo:
            url = f"https://tracker.gg{jeu.lower() if jeu != 'League of Legends' else 'lol'}/profile/riot/{pseudo}/overview"
            st.markdown(f'<iframe src="{url}" width="100%" height="500" style="border:none; background:white; border-radius:8px;"></iframe>', unsafe_allow_html=True)

    with tab7:
        st.header("🌍 Le Conquérant Mondial")
        if not liste_shops: st.info("Aucune boutique disponible.")
        else:
            shop_cible = st.selectbox("Site à traduire :", liste_shops, format_func=lambda x: x[0])
            langue = st.selectbox("Langue cible :", ["Anglais 🇺🇸", "Espagnol 🇪🇸"])
            if st.button("⚡ Traduire"):
                texte_origine = ""
                for s in liste_shops:
                    if s[0] == shop_cible: texte_origine = s[2]
                prompt = f"Traduis ce texte de boutique en {langue} de façon très vendeuse : {texte_origine}"
                nouveau_texte = outils.appeler_groq(prompt, temperature=0.3)
                outils.mettre_a_jour_boutique(shop_cible, nouveau_texte)
                st.success("🎉 Traduction injectée ! Rafraîchissez l'onglet 'Mes Boutiques'.")
                st.rerun()

    with tab8:
        st.header("💎 L'Usine à Rente Mensuelle Récurrente")
        code_premium = st.text_input("Code Premium Rente", type="password")
        if code_premium != "RENTE350": st.warning("🔒 Saisissez le code reçu après votre virement de 350 $.")
        else:
            st.success("🔓 Algorithme récurrent activé.")
            sujet_rente = st.text_input("Thématique de l'abonnement :")
            if st.button("🚀 Créer la rente") and sujet_rente:
                prompt = f"Génère un plan de box par abonnement pour la niche '{sujet_rente}'."
                st.info(outils.appeler_groq(prompt))
