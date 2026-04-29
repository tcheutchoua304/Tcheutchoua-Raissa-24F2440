import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

st.set_page_config(page_title="UniStats", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0d2b6e; }
    [data-testid="stSidebar"] * { color: white !important; }
    .main { background-color: #f5f7ff; }
    .kpi-box { background: white; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 5px solid #0d2b6e; }
    .kpi-number { font-size: 2em; font-weight: bold; color: #0d2b6e; }
    .kpi-label { color: #666; font-size: 0.9em; }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "etudiants.csv"
COLONNES = ["matricule","nom","age","sexe","niveau","filiere","annee","ues","notes","moyenne20","mgpt"]

def charger_donnees():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        for col in COLONNES:
            if col not in df.columns:
                df[col] = ""
        return df
    return pd.DataFrame(columns=COLONNES)

def sauvegarder(df):
    df.to_csv(DATA_FILE, index=False)

def convertir_gpa(moyenne):
    if moyenne >= 18: return 4.0
    elif moyenne >= 16: return 3.7
    elif moyenne >= 14: return 3.3
    elif moyenne >= 12: return 3.0
    elif moyenne >= 10: return 2.7
    elif moyenne >= 8: return 2.0
    elif moyenne >= 6: return 1.0
    else: return 0.0

def valider_matricule(mat):
    return bool(re.match(r"^\d{2}[A-Z]\d{4}$", mat))

st.sidebar.image("https://img.icons8.com/fluency/96/graduation-cap.png", width=80)
st.sidebar.title("🏛️ UniStats")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["📝 Saisie des Notes", "📊 Tableau de Bord", "🔍 Recherche par Matricule"])
st.sidebar.markdown("---")
st.sidebar.caption("⚠️ Données effacées au redémarrage Render (version gratuite).")

df = charger_donnees()

if page == "📝 Saisie des Notes":
    st.title("📝 Saisie des Notes & Unités d'Enseignement")
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👤 Identification")
        matricule = st.text_input("Matricule *", placeholder="Ex: 24F2440").strip().upper()
        nom = st.text_input("Nom complet *", placeholder="Ex: Tcheutchoua Raïssa")
        age = st.number_input("Âge", min_value=15, max_value=60, value=20)
        sexe = st.selectbox("Sexe", ["Masculin", "Féminin"])

    with col2:
        st.subheader("🎓 Parcours Académique")
        niveau = st.selectbox("Niveau", ["L1","L2","L3","M1","M2"])
        filiere = st.selectbox("Filière", ["Informatique","Mathématiques","Physique","Chimie","Biologie","Économie","Droit","Autre"])
        annee = st.selectbox("Année Académique", ["2022-2023","2023-2024","2024-2025","2025-2026"])

    st.markdown("---")
    st.subheader("📚 Unités d'Enseignement (UE)")
    nb_ue = st.number_input("Nombre d'UE à saisir", min_value=1, max_value=15, value=4)

    noms_ue = []
    notes_ue = []
    erreur_notes = False
    cols_ue = st.columns(2)

    for i in range(int(nb_ue)):
        with cols_ue[i % 2]:
            st.markdown(f"**UE {i+1}**")
            nom_ue = st.text_input(f"Nom UE {i+1}", placeholder=f"Ex: INF{i+1}01", key=f"nom_ue_{i}")
            note = st.number_input(f"Note /20", min_value=-1.0, max_value=21.0, value=0.0, step=0.5, key=f"note_{i}")
            if note < 0 or note > 20:
                st.error("❌ Note invalide ! Entre 0 et 20 seulement.")
                erreur_notes = True
            noms_ue.append(nom_ue if nom_ue else f"UE{i+1}")
            notes_ue.append(note)

    notes_valides = [n for n in notes_ue if 0 <= n <= 20]
    if notes_valides:
        moyenne20 = round(sum(notes_valides) / len(notes_valides), 2)
        mgpt = convertir_gpa(moyenne20)
        st.markdown("---")
        st.subheader("📊 Résultats en Temps Réel")
        c1, c2, c3 = st.columns(3)
        c1.metric("📈 Moyenne /20", f"{moyenne20}/20")
        c2.metric("🎯 MGPT /4.0", f"{mgpt}/4.0")
        c3.metric("✅ Statut", "ADMIS" if moyenne20 >= 10 else "AJOURNÉ")
    else:
        moyenne20 = 0.0
        mgpt = 0.0

    st.markdown("---")
    if st.button("💾 Enregistrer l'Étudiant", type="primary", use_container_width=True):
        if not matricule:
            st.error("❌ Le matricule est obligatoire.")
        elif not valider_matricule(matricule):
            st.error("❌ Format invalide. Exemple correct : 24F2440")
        elif not nom:
            st.error("❌ Le nom est obligatoire.")
        elif erreur_notes:
            st.error("❌ Corrigez les notes invalides.")
        elif matricule in df["matricule"].values:
            st.error(f"❌ Matricule {matricule} déjà existant ! Doublon refusé.")
        else:
            nouvelle_ligne = {
                "matricule": matricule, "nom": nom, "age": age, "sexe": sexe,
                "niveau": niveau, "filiere": filiere, "annee": annee,
                "ues": "|".join(noms_ue), "notes": "|".join([str(n) for n in notes_ue]),
                "moyenne20": moyenne20, "mgpt": mgpt
            }
            df = pd.concat([df, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
            sauvegarder(df)
            st.success(f"✅ {nom} ({matricule}) enregistré avec succès !")
            st.balloons()

elif page == "📊 Tableau de Bord":
    st.title("📊 Tableau de Bord Global")
    st.markdown("---")

    if df.empty:
        st.warning("⚠️ Aucune donnée. Commencez par saisir des étudiants.")
    else:
        df["moyenne20"] = pd.to_numeric(df["moyenne20"], errors="coerce").fillna(0)
        df["mgpt"] = pd.to_numeric(df["mgpt"], errors="coerce").fillna(0)
        df["admis"] = df["moyenne20"] >= 10

        total = len(df)
        moy_generale = round(df["moyenne20"].mean(), 2)
        mgpt_moyenne = round(df["mgpt"].mean(), 2)
        taux_reussite = round((df["admis"].sum() / total) * 100, 1)

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f'<div class="kpi-box"><div class="kpi-number">{total}</div><div class="kpi-label">Étudiants inscrits</div></div>', unsafe_allow_html=True)
        with k2:
            st.markdown(f'<div class="kpi-box"><div class="kpi-number">{moy_generale}/20</div><div class="kpi-label">Moyenne Générale</div></div>', unsafe_allow_html=True)
        with k3:
            st.markdown(f'<div class="kpi-box"><div class="kpi-number">{mgpt_moyenne}/4.0</div><div class="kpi-label">MGPT Moyenne</div></div>', unsafe_allow_html=True)
        with k4:
            st.markdown(f'<div class="kpi-box"><div class="kpi-number">{taux_reussite}%</div><div class="kpi-label">Taux de Réussite</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.subheader("📊 Taux de Réussite par Niveau")
        reussite_niveau = df.groupby("niveau")["admis"].apply(lambda x: round(x.sum()/len(x)*100,1)).reset_index()
        reussite_niveau.columns = ["Niveau","Taux (%)"]
        fig1 = px.bar(reussite_niveau, x="Niveau", y="Taux (%)", color="Taux (%)", color_continuous_scale=["#ff4444","#ffaa00","#00cc44"], text="Taux (%)")
        fig1.update_traces(texttemplate='%{text}%', textposition='outside')
        fig1.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig1, use_container_width=True)

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("🥧 Réussite par Filière")
            reussite_filiere = df[df["admis"]].groupby("filiere").size().reset_index(name="Admis")
            fig2 = px.pie(reussite_filiere, names="filiere", values="Admis", color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig2, use_container_width=True)

        with col_g2:
            st.subheader("📈 Distribution des Moyennes")
            fig3 = px.histogram(df, x="moyenne20", nbins=10, color_discrete_sequence=["#0d2b6e"])
            fig3.add_vline(x=10, line_dash="dash", line_color="red", annotation_text="Seuil 10/20")
            fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig3, use_container_width=True)

        st.subheader("📋 Liste des Étudiants")
        df_affichage = df[["matricule","nom","niveau","filiere","moyenne20","mgpt","admis"]].copy()
        df_affichage["admis"] = df_affichage["admis"].map({True:"✅ Admis", False:"❌ Ajourné"})
        df_affichage.columns = ["Matricule","Nom","Niveau","Filière","Moy./20","MGPT/4","Statut"]
        st.dataframe(df_affichage, use_container_width=True)

elif page == "🔍 Recherche par Matricule":
    st.title("🔍 Consultation par Matricule")
    st.markdown("---")

    matricule_recherche = st.text_input("Entrez le matricule", placeholder="Ex: 24F2440").strip().upper()

    if st.button("🔎 Rechercher", type="primary"):
        if not matricule_recherche:
            st.warning("Veuillez entrer un matricule.")
        elif df.empty:
            st.warning("Aucun étudiant enregistré.")
        else:
            resultat = df[df["matricule"] == matricule_recherche]
            if resultat.empty:
                st.error(f"❌ Aucun étudiant trouvé : {matricule_recherche}")
            else:
                etudiant = resultat.iloc[0]
