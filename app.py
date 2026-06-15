import streamlit as st
import outils

# Lancement initial de la base de données SQLite
outils.initialiser_base_de_donnees()

if "compte_actif" not in st.session_state:
    st.session_state.compte_actif = False
if "credits_restants" not in st.session_state:
    st.session_state.credits_restants = 0
if "forfait" not in st.session_state:
    st.session_state.forfait = "Aucun"

st.set_page_config(page_title="Empire Command Center", layout="centered")

# --- BARRE LATÉRALE CONTROLE ---
st.sidebar.title("🎮 Centre de Contrôle")
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Activation de Session")
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

# Chargement visuel
if mode_affichage == "Jeux Vidéo (RPG)":
    st.markdown("<style>.stApp { background-color: #0b0c10; color: #c5c6c7; } h1 { color: #66fcf1; text-shadow: 0 0 10px #66fcf1; text-align: center; } div[data-testid='stMetric'] { background-color: #1f2833; border: 2px solid #45f3ff; border-radius: 10px; padding: 10px; }</style>", unsafe_allow_html=True)
    st.title("🕹️ EMPIRE TYCOON : MISSION CONTROL")
else:
    st.markdown("<style>.stApp { background-color: #ffffff; color: #111111; } h1 { color: #1E3A8A; }</style>", unsafe_allow_html=True)
    st.title("🚀 Business Automatique Dashboard")

# --- ACCUEIL ---
st.markdown("### ⚡ Activité de la communauté en direct")
st.markdown("<div style='background-color: #1e1e24; padding: 12px; border-radius: 8px; border-left: 5px solid #66fcf1; margin-bottom: 20px;'><span style='font-size:13px; color:#c5c6c7;'>• 💰 Utilisateur <b>Alex_MTL</b> a généré <b>340 $</b> en 24h avec son shop !</span><br><span style='font-size:13px; color:#c5c6c7;'>• 📡 Connexion établie avec le réseau de proxies rotatifs de <b>Scrape.do</b>.</span></div>", unsafe_allow_html=True)

st.markdown("### 📊 État de votre Empire")
col1, col2, col3 = st.columns(3)
liste_shops = outils.recuperer_boutiques()

col1.metric(label="💰 Chiffre d'Affaires", value=f"{len(liste_shops) * 145} $")
col2.metric(label="🏬 Boutiques en ligne", value=f"{len(liste_shops)} Actives")
col3.metric(label="🔋 Énergie", value=f"{st.session_state.credits_restants} restants" if st.session_state.compte_actif else "0 restants")

if st.session_state.credits_restants == 0 and st.session_state.compte_actif:
    st.warning("🔋 Énergie épuisée. Envoyez un virement Interac de 50 $ pour obtenir votre code de recharge instantané.")

st.markdown("---")

if not st.session_state.compte_actif:
    st.warning("⚠️ Accès suspendu. Veuillez valider votre accès mensuel par virement Interac.")
else:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["🤖 B1: Prospection", "🏬 B2: Boutique Flash", "👀 Mes Boutiques", "🕵️‍♂️ Radar Espion", "💡 B3: R&D (Élite)", "🎮 Break", "🌍 Traducteur", "💎 Rente (350$)"])

    with tab1:
        st.header("Extracteur Scrape.do & Rédacteur Commercial IA")
        url_cible = st.text_input("URL du site concurrent ou annuaire à scraper :", "https://example.com")
        
        if st.button("🔥 Déclencher le scraping et l'analyse"):
            if st.session_state.credits_restants > 0:
                st.session_state.credits_restants -= 1
                
                # Étape 1 : Appel réel à Scrape.do
                with st.spinner("Scrape.do contourne les anti-bots et récupère la page..."):
                    resultat_html = outils.executer_scraping_real(url_cible)
                    st.info(resultat_html)
                
                # Étape 2 : L'IA prend le relais
                with st.spinner("L'IA de Groq génère votre e-mail stratégique..."):
                    prompt = f"Rédige un court message de vente (max 3 phrases) pour proposer nos services à l'entreprise propriétaire du site '{url_cible}'."
                    st.success("🤖 Message commercial rédigé par l'IA :")
                    st.write(outils.appeler_groq(prompt))
            else: st.error("Plus d'énergie disponible.")

    with tab2:
        st.header("Usine à Magasins Éphémères")
        nom_shop = st.text_input("Nom de la boutique :")
        niche_shop = st.text_input("Thématique :", "Accessoires Sport")
        if st.button("⚡ Déployer la boutique flash"):
            if st.session_state.credits_restants > 0 and nom_shop:
                st.session_state.credits_restants -= 1
                prompt = f"Génère une liste de 3 produits e-commerce pour la thématique '{niche_shop}' avec prix et descriptions."
                resultat = outils.appeler_groq(prompt)
                if outils.ajouter_boutique(nom_shop, niche_shop, resultat):
                    st.success(f"🎉 Boutique '{nom_shop}' déployée et sauvegardée !")
                else: st.error("Nom déjà pris.")

    with tab3:
        st.header("🌐 Vos Serveurs d'Hébergement Actifs")
        if not liste_shops: st.info("Aucun site actif.")
        else:
            choix = st.selectbox("Sélectionnez le site :", [s[0] for s in liste_shops])
            for s in liste_shops:
                if s[0] == choix:
                    st.markdown(f"<div style='border: 2px dashed {s[4]}; padding: 20px; border-radius: 8px;'><h3>🏬 {s[0].upper()}</h3><p>{s[2]}</p></div>", unsafe_allow_html=True)

    with tab4:
        st.header("🕵️‍♂️ Radar Espion")
        mot_espion = st.text_input("Produit à traquer :")
        if st.button("🔍 Extraire les stratégies") and mot_espion:
            prompt = f"Fais un rapport d'espionnage e-commerce pour le produit '{mot_espion}'."
            st.info(outils.appeler_groq(prompt))

    with tab5:
        st.header("💡 Laboratoire de R&D : Concepteur de Produits")
        if st.session_state.forfait != "Élite":
            st.error("🔒 Fonctionnalité réservée au forfait Élite.")
        else:
            idee = st.text_input("Votre idée :")
            if st.button("🚀 Matérialiser la marque") and idee:
                prompt = f"Crée une marque complète et un texte marketing pour : '{idee}'."
                st.info(outils.appeler_groq(prompt))

    with tab6:
        st.header("🎮 Gaming Break")
        jeu = st.selectbox("Jeu :", ["Fortnite", "League of Legends", "Valorant"])
        pseudo = st.text_input("Pseudo :")
        if pseudo:
            url = f"https://tracker.gg{jeu.lower() if jeu != 'League of Legends' else 'lol'}/profile/riot/{pseudo}/overview"
            st.markdown(f'<iframe src="{url}" width="100%" height="500" style="border:none; background:white;"></iframe>', unsafe_allow_html=True)

    with tab7:
        st.header("🌍 Le Conquérant Mondial")
        if not liste_shops: st.info("Aucun site à traduire.")
        else:
            shop_cible = st.selectbox("Site à traduire :", [s[0] for s in liste_shops])
            langue = st.selectbox("Langue :", ["Anglais 🇺🇸", "Espagnol 🇪🇸"])
            if st.button("⚡ Traduire"):
                # Récupère le texte original
                texte_origine = ""
                for s in liste_shops:
                    if s[0] == shop_cible: texte_origine = s[2]
                
                prompt = f"Traduis ce texte de boutique en {langue} de façon très vendeuse : {texte_origine}"
                nouveau_texte = outils.appeler_groq(prompt, temperature=0.3)
                outils.mettre_a_jour_boutique(shop_cible, nouveau_texte)
                st.success("🎉 Traduction injectée avec succès !")

    with tab8:
        st.header("💎 L'Usine à Rente Mensuelle")
        code_premium = st.text_input("Code Premium Rente", type="password")
        if code_premium != "RENTE350": st.warning("🔒 Saisissez le code reçu après votre virement de 350 $.")
        else:
            sujet_rente = st.text_input("Thématique de l'abonnement :")
            if st.button("🚀 Créer la rente") and sujet_rente:
                prompt = f"Génère un plan de box par abonnement pour la niche '{sujet_rente}'."
                st.info(outils.appeler_groq(prompt))
