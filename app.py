import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# ==============================
# CONFIGURATION
# ==============================
st.set_page_config(page_title="Suivi des Caftans", layout="wide")

FICHIER_PRODUITS = "produits.xlsx"
FICHIER_VENTES = "ventes.xlsx"
FICHIER_CHARGES = "charges.xlsx"

# Charger fichiers ou créer si inexistants
def charger_fichier(nom, colonnes):
    try:
        df = pd.read_excel(nom)
        for col in colonnes:
            if col not in df.columns:
                df[col] = 0
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=colonnes)

# Produits
colonnes_produits = ["ID", "Nom", "Prix vente", "Tissu", "Main-d'œuvre", "Accessoires", "Stock"]
produits = charger_fichier(FICHIER_PRODUITS, colonnes_produits)

# Ventes
colonnes_ventes = ["ID", "Date", "Produit_ID", "Quantité", "Canal"]
ventes = charger_fichier(FICHIER_VENTES, colonnes_ventes)

# Charges
colonnes_charges = ["ID", "Date", "Catégorie", "Montant", "Type"]
charges = charger_fichier(FICHIER_CHARGES, colonnes_charges)

# ==============================
# MENU DE NAVIGATION
# ==============================
menu = st.sidebar.radio("📌 Navigation", [
    "🏠 Accueil",
    "📦 Produits",
    "🛒 Ventes",
    "💰 Charges",
    "📊 Rapports"
])

# ==============================
# PAGE ACCUEIL
# ==============================
if menu == "🏠 Accueil":
    st.title("📊 Tableau de bord - Caftans")

    if not ventes.empty and not produits.empty:
        ventes_detail = ventes.merge(produits, left_on="Produit_ID", right_on="ID", suffixes=("_vente", "_prod"))
        ventes_detail["Revenu"] = ventes_detail["Quantité"] * ventes_detail["Prix vente"]
        ventes_detail["Cout_prod"] = ventes_detail["Quantité"] * (ventes_detail["Tissu"] + ventes_detail["Main-d'œuvre"] + ventes_detail["Accessoires"])
    else:
        ventes_detail = pd.DataFrame(columns=["Revenu", "Cout_prod"])

    revenu_total = ventes_detail["Revenu"].sum()
    cout_total = ventes_detail["Cout_prod"].sum()
    charges_total = charges["Montant"].sum() if not charges.empty else 0
    profit_brut = revenu_total - cout_total
    profit_net = profit_brut - charges_total

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Revenu total", f"{revenu_total:,.0f} MAD")
    col2.metric("Coûts production", f"{cout_total:,.0f} MAD")
    col3.metric("Profit brut", f"{profit_brut:,.0f} MAD")
    col4.metric("Profit net", f"{profit_net:,.0f} MAD")

    st.markdown("### 📈 Évolution mensuelle")
    if not ventes.empty:
        ventes["Date"] = pd.to_datetime(ventes["Date"], errors="coerce")
        ventes["Mois"] = ventes["Date"].dt.to_period("M").astype(str)
        resume_mensuel = ventes.merge(produits, left_on="Produit_ID", right_on="ID")
        resume_mensuel["Revenu"] = resume_mensuel["Quantité"] * resume_mensuel["Prix vente"]
        mensuel = resume_mensuel.groupby("Mois")["Revenu"].sum().reset_index()

        fig, ax = plt.subplots(figsize=(8,4))
        ax.plot(mensuel["Mois"], mensuel["Revenu"], marker="o")
        ax.set_title("Revenu mensuel")
        ax.set_ylabel("MAD")
        plt.xticks(rotation=45)
        st.pyplot(fig)

# ==============================
# PAGE PRODUITS
# ==============================
elif menu == "📦 Produits":
    st.title("📦 Produits")

    st.subheader("📋 Liste des produits")
    st.dataframe(produits)

    st.subheader("➕ Ajouter / Modifier un produit")
    with st.form("ajout_produit"):
        nom = st.text_input("Nom du produit")
        prix_vente = st.number_input("Prix de vente (MAD)", min_value=0.0, step=100.0)
        tissu = st.number_input("Coût tissu (MAD)", min_value=0.0, step=10.0)
        mo = st.number_input("Main-d'œuvre (MAD)", min_value=0.0, step=10.0)
        accessoires = st.number_input("Accessoires (MAD)", min_value=0.0, step=10.0)
        stock = st.number_input("Stock disponible", min_value=0, step=1)
        submit = st.form_submit_button("💾 Sauvegarder")

        if submit and nom != "":
            new_id = int(produits["ID"].max()) + 1 if not produits.empty else 1
            new_row = {"ID": new_id, "Nom": nom, "Prix vente": prix_vente, "Tissu": tissu,
                       "Main-d'œuvre": mo, "Accessoires": accessoires, "Stock": stock}
            produits = pd.concat([produits, pd.DataFrame([new_row])], ignore_index=True)
            produits.to_excel(FICHIER_PRODUITS, index=False)
            st.success("✅ Produit ajouté avec succès !")

# ==============================
# PAGE VENTES
# ==============================
elif menu == "🛒 Ventes":
    st.title("🛒 Ventes")

    st.subheader("📋 Historique des ventes")
    st.dataframe(ventes)

    st.subheader("➕ Ajouter une vente")
    with st.form("ajout_vente"):
        produit = st.selectbox("Produit", produits["Nom"] if not produits.empty else [])
        quantite = st.number_input("Quantité", min_value=1, step=1)
        canal = st.selectbox("Canal", ["Boutique", "En ligne", "Marché"])
        submit = st.form_submit_button("💾 Sauvegarder")

        if submit and produit != "":
            produit_id = produits.loc[produits["Nom"] == produit, "ID"].iloc[0]
            new_id = int(ventes["ID"].max()) + 1 if not ventes.empty else 1
            new_row = {"ID": new_id, "Date": datetime.now().strftime("%Y-%m-%d"),
                       "Produit_ID": produit_id, "Quantité": quantite, "Canal": canal}
            ventes = pd.concat([ventes, pd.DataFrame([new_row])], ignore_index=True)
            ventes.to_excel(FICHIER_VENTES, index=False)
            st.success("✅ Vente enregistrée !")

# ==============================
# PAGE CHARGES
# ==============================
elif menu == "💰 Charges":
    st.title("💰 Charges")

    st.subheader("📋 Liste des charges")
    st.dataframe(charges)

    st.subheader("➕ Ajouter une charge")
    with st.form("ajout_charge"):
        categorie = st.text_input("Catégorie (Marketing, Loyer, etc.)")
        montant = st.number_input("Montant (MAD)", min_value=0.0, step=100.0)
        type_charge = st.selectbox("Type", ["Fixe", "Variable"])
        submit = st.form_submit_button("💾 Sauvegarder")

        if submit and categorie != "":
            new_id = int(charges["ID"].max()) + 1 if not charges.empty else 1
            new_row = {"ID": new_id, "Date": datetime.now().strftime("%Y-%m-%d"),
                       "Catégorie": categorie, "Montant": montant, "Type": type_charge}
            charges = pd.concat([charges, pd.DataFrame([new_row])], ignore_index=True)
            charges.to_excel(FICHIER_CHARGES, index=False)
            st.success("✅ Charge ajoutée avec succès !")

# ==============================
# PAGE RAPPORTS
# ==============================
elif menu == "📊 Rapports":
    st.title("📊 Rapports & Statistiques")

    if not ventes.empty and not produits.empty:
        ventes_detail = ventes.merge(produits, left_on="Produit_ID", right_on="ID")
        ventes_detail["Revenu"] = ventes_detail["Quantité"] * ventes_detail["Prix vente"]

        st.subheader("🏆 Top produits par revenu")
        top_produits = ventes_detail.groupby("Nom")["Revenu"].sum().sort_values(ascending=False).reset_index()
        st.dataframe(top_produits)

        fig, ax = plt.subplots(figsize=(8,4))
        ax.bar(top_produits["Nom"], top_produits["Revenu"])
        ax.set_title("Revenu par produit")
        ax.set_ylabel("MAD")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    if not charges.empty:
        st.subheader("📌 Répartition des charges")
        charges_par_cat = charges.groupby("Catégorie")["Montant"].sum().reset_index()
        fig, ax = plt.subplots()
        ax.pie(charges_par_cat["Montant"], labels=charges_par_cat["Catégorie"], autopct='%1.1f%%')
        ax.set_title("Répartition des charges")
        st.pyplot(fig)