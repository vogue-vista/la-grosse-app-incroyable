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
        st.error("Boutique introuvable ou abonnement expiré.")
        st.stop()
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
    if code == "":
        return
        
    # CORRECTION CRITIQUE : On vérifie en BDD si le code a déjà été consommé
    if outils.code_deja_utilise(code):
        st.sidebar.error("❌ Ce code a déjà été activé par un autre utilisateur !")
        return

    if code == "INTERAC500":
        outils.consommer_code(code) # Bloque le code définitivement
        st.session_state.compte_actif = True
        st.session_state.forfait = "Starter"
        st.session_state.credits_restants = 10
        st.sidebar.success("✅ Forfait Starter Activé !")
    elif code == "INTERAC1000":
        outils.consommer_code(code) # Bloque le code définitivement
        st.session_state.compte_actif = True
        st.session_state.forfait = "Élite"
        st.session_state.credits_restants = 20
        st.sidebar.success("👑 Forfait Élite Activé !")
    elif code == "EXTRA50":
        if st.session_state.compte_actif:
            outils.consommer_code(code) # Bloque le code définitivement
            st.session_state.credits_restants += 1
            st.sidebar.success("⚡ Recharge validée ! +1 Action.")
            st.balloons()
        else:
            st.sidebar.error("❌ Activez d'abord un forfait principal.")
    else:
        st.sidebar.error("❌ Code inconnu ou invalide.")

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
    st.markdown("<style>.stApp { background-color: #0b0c10 !important; color: #c5c6c7 !important; } h1 { color: #66fcf1 !important; text-shadow: 0 0 10px #66fcf1; text-align: center; } h2, h3, h4, h5, h6, p, span, label { color: #c5c6c7 !important; } div[data-testid='stMetric'] { background-color: #1f2833; border: 2px solid #45f3ff; border-radius: 10px; padding: 10px; } .stTabs button p { color: #45f3ff !important; }</style>", unsafe_allow_html=True)
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

col1.metric(label="💰 Chiffre d'Affaires accumulé", value=f"{ca_total_reel} \$")
col2.metric(label="🏬 Boutiques en ligne", value=f"{len(liste_shops)} Actives")
col3.metric(label="🔋 Énergie (Actions)", value=f"{st.session_state.credits_restants} restants" if st.session_state.compte_actif else "0 restants")

if st.session_state.credits_restants == 0 and st.session_state.compte_actif:
    st.warning("🔋 Énergie épuisée. Envoyez un virement Interac de 50 \$ pour obtenir votre code de recharge instantané.")

st.markdown("---")

if not st.session_state.compte_actif:
    st.warning("⚠️ Accès suspendu. Veuillez valider votre accès mensuel par virement Interac.")
else:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["🤖 B1: Prospection", "🏬 B2: Boutique Flash", "👀 Mes Boutiques", "🕵️‍♂️ Radar Espion", "💡 B3: R&D (Élite)", "🎮 Break", "🌍 Traducteur", "💎 Rente (350\$)"])

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
        niche_shop = st.text_input("Thématique / Niche :", "Accessoires Sport")
        email_vendeur = st.text_input("Votre Courriel (pour recevoir les notifications d'achat) :")
        
        st.markdown("---")
        st.subheader("🛠️ Configuration du Catalogue")
        methode_creation = st.radio(
            "Méthode de création de la boutique :",
            ["🔥 Mode Automatique (10 Produits Gagnants & Viraux TikTok/YouTube)", "✍️ Mode Sur-Mesure (Je choisis mes produits)"]
        )
        
        if methode_creation == "🔥 Mode Automatique (10 Produits Gagnants & Viraux TikTok/YouTube)":
            st.info("⚡ L'IA s'occupe de tout : sélection de 10 produits tendances et fixation intelligente des prix.")
            description_souhaitee = "Sélectionne automatiquement les 10 meilleurs produits viraux et gagnants du moment"
            prix_boutique = 0.0
        else:
            description_souhaitee = st.text_area("Décrivez précisément ce que la boutique va vendre :")
            prix_boutique = st.number_input("Définissez le prix unique des produits (\$) :", min_value=1.0, value=49.99, step=1.0)

        st.markdown("---")
        if st.button("⚡ Déployer la boutique flash"):
            if st.session_state.credits_restants > 0 and nom_shop and email_vendeur:
                if methode_creation == "✍️ Mode Sur-Mesure (Je choisis mes produits)" and not description_souhaitee:
                    st.error("Veuillez décrire vos produits pour le mode sur-mesure.")
                else:
                    st.session_state.credits_restants -= 1
                    with st.spinner("L'IA conçoit votre catalogue de produits..."):
                        if methode_creation == "🔥 Mode Automatique (10 Produits Gagnants & Viraux TikTok/YouTube)":
                            consigne_produits = f"Trouve et liste exactement 10 produits très gagnants et viraux sur TikTok dans la niche '{niche_shop}'. Pour chaque produit, détermine et écris un prix public de vente réaliste compris obligatoirement entre 15.00\$ et 65.00\$ au format 'Prix : XX.XX \$'."
                            template_prix = "[Calculé par l'IA]"
                        else:
                            consigne_produits = f"Génère des produits basés sur la description utilisateur : '{description_souhaitee}'."
                            template_prix = f"Prix : {prix_boutique} \$"

                        prompt = f"""
                        Rédige le catalogue de la boutique e-commerce '{nom_shop}', spécialisée dans : {niche_shop}.
                        Consigne : {consigne_produits}
                        
                        Génère ton texte uniquement en Markdown standard sans balise html de bloc de code.
                        Pour chaque produit, utilise la structure exacte suivante :
                        
                        ### 📦 [Nom du Produit]
                        * **Description** : [Rédige une description attractive du produit]
                        * **🔥 Pourquoi ce produit est viral** : [Explique précisément pourquoi ce produit fait fureur sur TikTok/YouTube]
                        * **Prix** : {template_prix}
                        
                        ---
                        """
                        resultat = outils.appeler_groq(prompt)
                        prix_final_bdd = prix_boutique if prix_boutique > 0 else 39.99
                        if outils.ajouter_boutique(nom_shop, niche_shop, resultat, prix_final_bdd, couleur=email_vendeur):
                            st.success(f"🎉 Boutique '{nom_shop}' déployée !")
                            st.rerun()
                        else: st.error("Nom déjà pris.")
            else: st.error("Veuillez remplir le Nom et votre Courriel.")
