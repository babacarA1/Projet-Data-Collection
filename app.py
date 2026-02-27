"""
╔══════════════════════════════════════════════════════════════╗
║     CoinAfrique Animaux — Application Streamlit              ║
║     Scraping · Dashboard · Téléchargement · Évaluation       ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import re
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# ══════════════════════════════════════════════════════════════
#  CONFIG PAGE
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="CoinAfrique Animaux",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  CSS PERSONNALISÉ  (thème naturel / savane)
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:        #0f1a10;
    --surface:   #162218;
    --card:      #1c2d1e;
    --accent:    #7ec850;
    --accent2:   #f5a623;
    --text:      #e8f0e9;
    --muted:     #8aab8c;
    --border:    #2e4430;
    --danger:    #e05c5c;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Headers */
h1 { font-family:'Playfair Display',serif; font-size:2.4rem !important;
     color: var(--accent) !important; letter-spacing:-1px; }
h2 { font-family:'Playfair Display',serif; color: var(--accent) !important; font-size:1.6rem !important; }
h3 { color: var(--accent2) !important; font-size:1.1rem !important; }

/* Cards métriques */
div[data-testid="metric-container"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px !important;
}
div[data-testid="metric-container"] label { color: var(--muted) !important; font-size:.8rem !important; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-family:'Playfair Display',serif;
    color: var(--accent) !important;
    font-size:2rem !important;
}

/* Boutons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent) 0%, #5da83e 100%);
    color: #0f1a10 !important;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: .9rem;
    padding: 10px 24px;
    transition: all .2s;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(126,200,80,.35);
}

/* Inputs */
.stTextInput input, .stSelectbox select, .stTextArea textarea,
input[type="text"], input[type="number"], textarea {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}

/* Dataframe */
.stDataFrame { border-radius:10px; overflow:hidden; }

/* Progress */
.stProgress > div > div { background: var(--accent) !important; }

/* Tabs */
button[data-baseweb="tab"] { color: var(--muted) !important; }
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* Alerts */
.stSuccess { background: rgba(126,200,80,.12) !important; border-color: var(--accent) !important; }
.stWarning { background: rgba(245,166,35,.12) !important; border-color: var(--accent2) !important; }
.stError   { background: rgba(224,92,92,.12)  !important; border-color: var(--danger) !important; }

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #162218 0%, #1f3320 50%, #162218 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(126,200,80,.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-family:'Playfair Display',serif;
    font-size:2.8rem; font-weight:900;
    color: var(--accent);
    margin:0; line-height:1.1;
}
.hero-sub {
    color: var(--muted);
    margin-top:8px;
    font-size:.95rem;
}

/* Stat pill */
.stat-pill {
    display:inline-block;
    background: rgba(126,200,80,.12);
    border: 1px solid rgba(126,200,80,.3);
    border-radius:20px;
    padding:4px 14px;
    font-size:.8rem;
    color: var(--accent);
    margin-right:8px;
}

/* Section divider */
.section-title {
    display:flex; align-items:center; gap:12px;
    margin: 24px 0 16px;
}
.section-title::after {
    content:''; flex:1; height:1px;
    background: var(--border);
}

/* Download card */
.dl-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius:12px;
    padding:20px;
    margin-bottom:12px;
    transition: border-color .2s;
}
.dl-card:hover { border-color: var(--accent); }

/* Footer */
.footer {
    text-align:center;
    color: var(--muted);
    font-size:.78rem;
    margin-top:40px;
    padding-top:16px;
    border-top:1px solid var(--border);
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  BASE DE DONNÉES SQLite
# ══════════════════════════════════════════════════════════════
DB_PATH = "coinafrique_animaux.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    """Initialise toutes les tables au démarrage."""
    conn = get_conn()
    cur  = conn.cursor()

    # ── Tables de données scrapées (brutes) ──────────────────
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS chiens (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            Nom           TEXT,
            prix          TEXT,
            adresse       TEXT,
            image_lien    TEXT,
            date_scraping DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS moutons (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            Nom           TEXT,
            prix          TEXT,
            adresse       TEXT,
            image_lien    TEXT,
            date_scraping DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS poules_lapins_pigeons (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            details       TEXT,
            prix          TEXT,
            adresse       TEXT,
            image_lien    TEXT,
            date_scraping DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS autres_animaux (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            Nom           TEXT,
            prix          TEXT,
            adresse       TEXT,
            image_lien    TEXT,
            date_scraping DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Table d'évaluations
        CREATE TABLE IF NOT EXISTS evaluations (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nom        TEXT,
            email      TEXT,
            note       INTEGER,
            facilite   INTEGER,
            design     INTEGER,
            dashboard  INTEGER,
            commentaire TEXT,
            soumis_le  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Table de logs de scraping
        CREATE TABLE IF NOT EXISTS scraping_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            categorie  TEXT,
            nb_pages   INTEGER,
            nb_lignes  INTEGER,
            statut     TEXT,
            date_run   DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

init_db()


# ══════════════════════════════════════════════════════════════
#  CONFIGURATION DES CATÉGORIES
# ══════════════════════════════════════════════════════════════
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
}

CATEGORIES = [
    {
        "label":  "🐕 Chiens",
        "nom":    "Chiens",
        "url":    "https://sn.coinafrique.com/categorie/chiens",
        "table":  "chiens",
        "v1":     "Nom",
        "emoji":  "🐕",
        "color":  "#7ec850",
    },
    {
        "label":  "🐑 Moutons",
        "nom":    "Moutons",
        "url":    "https://sn.coinafrique.com/categorie/moutons",
        "table":  "moutons",
        "v1":     "Nom",
        "emoji":  "🐑",
        "color":  "#f5a623",
    },
    {
        "label":  "🐔 Poules / Lapins / Pigeons",
        "nom":    "Poules_Lapins_Pigeons",
        "url":    "https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons",
        "table":  "poules_lapins_pigeons",
        "v1":     "details",
        "emoji":  "🐔",
        "color":  "#e05c5c",
    },
    {
        "label":  "🦜 Autres Animaux",
        "nom":    "Autres_Animaux",
        "url":    "https://sn.coinafrique.com/categorie/autres-animaux",
        "table":  "autres_animaux",
        "v1":     "Nom",
        "emoji":  "🦜",
        "color":  "#8b5cf6",
    },
]

CAT_MAP = {c["nom"]: c for c in CATEGORIES}


# ══════════════════════════════════════════════════════════════
#  FONCTIONS SCRAPING + NETTOYAGE
# ══════════════════════════════════════════════════════════════

def scrape_page(url: str, col_v1: str) -> list[dict]:
    """Scrape une page et retourne une liste de dicts bruts."""
    data = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        containers = soup.find_all("div", class_="col s6 m4 l3")
        for c in containers:
            try:
                a_tag = c.find("a", title=True)
                v1    = a_tag["title"].strip() if a_tag else ""

                prix_el = c.find("p", class_="ad__card-price")
                prix    = prix_el.get_text(strip=True) if prix_el else ""

                adr_el  = c.find("p", class_="ad__card-location")
                adresse = (
                    adr_el.get_text(separator=" ", strip=True)
                    .replace("location_on", "").strip()
                    if adr_el else ""
                )

                img_el = c.find("img", class_="ad__card-img")
                img    = ""
                if img_el:
                    img = img_el.get("src") or img_el.get("data-src") or ""

                data.append({col_v1: v1, "prix": prix,
                             "adresse": adresse, "image_lien": img})
            except Exception:
                continue
    except Exception as e:
        st.warning(f"⚠️ Erreur réseau : {e}")
    return data


def nettoyer_prix(brut: str) -> float | None:
    """Extrait la valeur numérique d'un prix."""
    if not brut:
        return None
    chiffres = re.sub(r"[^\d]", "", brut)
    return float(chiffres) if chiffres else None


def nettoyer_df(df: pd.DataFrame, col_v1: str) -> pd.DataFrame:
    """Nettoyage complet d'un DataFrame."""
    df = df.copy()
    df.replace("", pd.NA, inplace=True)
    df.dropna(subset=[col_v1], inplace=True)
    df.drop_duplicates(subset=[col_v1, "prix", "adresse"], inplace=True)
    df["prix_num"] = df["prix"].apply(nettoyer_prix)
    df["ville"]    = df["adresse"].str.split(",").str[0].str.strip()
    df.fillna("Non disponible", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def sauvegarder_en_db(df: pd.DataFrame, table: str, col_v1: str) -> int:
    """Insère le DataFrame dans la table SQLite, retourne le nombre de lignes."""
    conn = get_conn()
    cur  = conn.cursor()
    count = 0
    for _, row in df.iterrows():
        try:
            cur.execute(
                f"INSERT INTO {table}({col_v1}, prix, adresse, image_lien) VALUES(?,?,?,?)",
                (row.get(col_v1, ""), row.get("prix", ""),
                 row.get("adresse", ""), row.get("image_lien", ""))
            )
            count += 1
        except Exception:
            pass
    conn.commit()
    cur.execute(
        "INSERT INTO scraping_logs(categorie, nb_pages, nb_lignes, statut) VALUES(?,?,?,?)",
        (table, 0, count, "OK")
    )
    conn.commit()
    conn.close()
    return count


def lire_table(table: str) -> pd.DataFrame:
    """Lit une table depuis SQLite."""
    try:
        conn = get_conn()
        df   = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:16px 0 8px;'>
        <div style='font-size:3rem;'>🐾</div>
        <div style='font-family:"Playfair Display",serif; font-size:1.3rem;
                    color:#7ec850; font-weight:700;'>CoinAfrique</div>
        <div style='color:#8aab8c; font-size:.8rem;'>Animaux — Sénégal</div>
    </div>
    <hr style='border-color:#2e4430; margin:8px 0 20px;'>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        options=[
            "🏠 Accueil",
            "🕷️ Scraper",
            "📥 Téléchargement",
            "📊 Dashboard",
            "📝 Évaluation",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border-color:#2e4430; margin:20px 0 12px;'>", unsafe_allow_html=True)

    # Stats rapides en sidebar
    total = 0
    for cat in CATEGORIES:
        conn = get_conn()
        try:
            n = pd.read_sql_query(f"SELECT COUNT(*) AS n FROM {cat['table']}", conn).iloc[0,0]
        except:
            n = 0
        conn.close()
        total += n
        st.markdown(
            f"<div style='display:flex;justify-content:space-between;"
            f"padding:4px 0;font-size:.82rem;'>"
            f"<span>{cat['emoji']} {cat['nom']}</span>"
            f"<span style='color:#7ec850;font-weight:600;'>{n}</span></div>",
            unsafe_allow_html=True
        )

    st.markdown(
        f"<div style='margin-top:8px;padding:8px 12px;"
        f"background:rgba(126,200,80,.1);border-radius:8px;"
        f"font-size:.85rem;text-align:center;'>"
        f"<b style='color:#7ec850;'>{total}</b> annonces en base</div>",
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════
#  PAGE : ACCUEIL
# ══════════════════════════════════════════════════════════════
if page == "🏠 Accueil":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🐾 CoinAfrique Animaux</div>
        <div class="hero-sub">
            Plateforme de scraping & analyse des annonces animaux au Sénégal
        </div>
        <div style="margin-top:16px;">
            <span class="stat-pill">🕷️ BeautifulSoup</span>
            <span class="stat-pill">📊 Plotly</span>
            <span class="stat-pill">🗄️ SQLite</span>
            <span class="stat-pill">🚀 Streamlit</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    infos = [
        ("🕷️", "Scraper", "Collecte multi-pages par catégorie avec stockage SQLite automatique"),
        ("📥", "Téléchargement", "Export CSV des données brutes issues du scraping"),
        ("📊", "Dashboard", "Visualisations interactives des données nettoyées"),
        ("📝", "Évaluation", "Formulaire de retour utilisateur intégré"),
    ]
    for col, (ico, titre, desc) in zip([col1,col2,col3,col4], infos):
        with col:
            st.markdown(f"""
            <div class="dl-card" style="text-align:center; min-height:160px;">
                <div style="font-size:2.2rem; margin-bottom:8px;">{ico}</div>
                <div style="font-weight:700; color:#7ec850; margin-bottom:8px;">{titre}</div>
                <div style="color:#8aab8c; font-size:.83rem; line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 Sources de données")

    for cat in CATEGORIES:
        st.markdown(f"""
        <div class="dl-card" style="display:flex; align-items:center; gap:20px;">
            <span style="font-size:2rem;">{cat['emoji']}</span>
            <div style="flex:1;">
                <div style="font-weight:600; color:{cat['color']};">{cat['nom']}</div>
                <div style="color:#8aab8c; font-size:.83rem; margin-top:2px;">
                    V1: <b>{cat['v1']}</b> &nbsp;·&nbsp;
                    V2: <b>prix</b> &nbsp;·&nbsp;
                    V3: <b>adresse</b> &nbsp;·&nbsp;
                    V4: <b>image_lien</b>
                </div>
            </div>
            <div style="color:#8aab8c; font-size:.78rem; text-align:right;">
                {cat['url'].replace('https://','')}</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  PAGE : SCRAPER
# ══════════════════════════════════════════════════════════════
elif page == "🕷️ Scraper":
    st.markdown('<h1>🕷️ Scraper des données</h1>', unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#8aab8c;'>Collectez des annonces en temps réel depuis CoinAfrique. "
        "Les données sont sauvegardées dans la base SQLite.</p>",
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns([1, 1])
    with col_a:
        cat_choice = st.selectbox(
            "Catégorie à scraper",
            options=[c["label"] for c in CATEGORIES]
        )
    with col_b:
        nb_pages = st.slider("Nombre de pages", min_value=1, max_value=20, value=5)

    cat = next(c for c in CATEGORIES if c["label"] == cat_choice)
    st.markdown(f"""
    <div class="dl-card" style="margin:12px 0;">
        <b style="color:{cat['color']};">{cat['emoji']} {cat['nom']}</b> &nbsp;·&nbsp;
        <span style="color:#8aab8c; font-size:.85rem;">{cat['url']}</span><br>
        <span style="color:#8aab8c; font-size:.83rem; margin-top:4px; display:block;">
            Colonne V1 : <b style="color:#e8f0e9;">{cat['v1']}</b> &nbsp;·&nbsp;
            {nb_pages} page(s) × ~84 annonces/page ≈ <b style="color:#7ec850;">{nb_pages*84}</b> annonces estimées
        </span>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"🚀 Lancer le scraping — {cat['emoji']} {cat['nom']}"):
        all_data = []
        progress = st.progress(0)
        status   = st.empty()
        log_box  = st.empty()
        logs     = []

        for i in range(1, nb_pages + 1):
            url = f"{cat['url']}?page={i}"
            status.markdown(
                f"<div style='color:#8aab8c; font-size:.85rem;'>"
                f"⏳ Scraping page <b style='color:#7ec850;'>{i}/{nb_pages}</b>…</div>",
                unsafe_allow_html=True
            )
            data = scrape_page(url, cat["v1"])
            all_data.extend(data)
            logs.append(f"Page {i:>2}/{nb_pages} → {len(data):>3} annonces")
            log_box.code("\n".join(logs), language=None)
            progress.progress(i / nb_pages)
            time.sleep(1.0)

        if all_data:
            df_brut = pd.DataFrame(all_data)
            n_saved = sauvegarder_en_db(df_brut, cat["table"], cat["v1"])
            status.success(
                f"✅ Scraping terminé ! **{len(all_data)}** annonces collectées, "
                f"**{n_saved}** insérées en base."
            )
            st.dataframe(df_brut.head(20), use_container_width=True)
        else:
            status.error("❌ Aucune donnée collectée. Vérifiez la connexion réseau.")

    # Logs de scraping
    st.markdown("---")
    st.subheader("📋 Historique des scrapings")
    df_logs = lire_table("scraping_logs")
    if not df_logs.empty:
        st.dataframe(df_logs.tail(20), use_container_width=True)
    else:
        st.info("Aucun scraping effectué pour l'instant.")


# ══════════════════════════════════════════════════════════════
#  PAGE : TÉLÉCHARGEMENT
# ══════════════════════════════════════════════════════════════
elif page == "📥 Téléchargement":
    st.markdown('<h1>📥 Télécharger les données</h1>', unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#8aab8c;'>Téléchargez les données brutes issues du scraping "
        "(non nettoyées) au format CSV.</p>",
        unsafe_allow_html=True
    )

    for cat in CATEGORIES:
        df = lire_table(cat["table"])
        has_data = not df.empty

        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.markdown(f"""
            <div style="padding:10px 0;">
                <span style="font-size:1.6rem;">{cat['emoji']}</span>
                <b style="color:{cat['color']}; margin-left:8px; font-size:1.05rem;">
                    {cat['nom'].replace('_',' ')}</b><br>
                <span style="color:#8aab8c; font-size:.82rem; margin-left:0;">
                    {cat['url']}
                </span>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if has_data:
                st.metric("Annonces en base", len(df))
            else:
                st.markdown(
                    "<div style='color:#8aab8c; padding:16px 0; font-size:.85rem;'>"
                    "Aucune donnée</div>",
                    unsafe_allow_html=True
                )

        with col3:
            if has_data:
                csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
                st.download_button(
                    label=f"⬇️ CSV brut",
                    data=csv_bytes,
                    file_name=f"{cat['table']}_brut.csv",
                    mime="text/csv",
                    key=f"dl_{cat['table']}",
                )
            else:
                st.markdown(
                    "<div style='color:#8aab8c; font-size:.82rem;'>—</div>",
                    unsafe_allow_html=True
                )
        st.markdown("<hr style='border-color:#2e4430; margin:4px 0;'>", unsafe_allow_html=True)

    # Aperçu
    st.markdown("---")
    st.subheader("🔍 Aperçu des données brutes")
    preview_cat = st.selectbox(
        "Sélectionner une catégorie",
        options=[c["label"] for c in CATEGORIES],
        key="preview_cat"
    )
    cat_p = next(c for c in CATEGORIES if c["label"] == preview_cat)
    df_p  = lire_table(cat_p["table"])
    if not df_p.empty:
        nb_show = st.slider("Lignes à afficher", 5, 50, 10)
        st.dataframe(df_p.head(nb_show), use_container_width=True)
        st.caption(f"Affichage de {min(nb_show, len(df_p))} / {len(df_p)} lignes")
    else:
        st.info(f"Aucune donnée disponible pour {cat_p['nom']}. Lancez d'abord un scraping.")


# ══════════════════════════════════════════════════════════════
#  PAGE : DASHBOARD
# ══════════════════════════════════════════════════════════════
elif page == "📊 Dashboard":
    st.markdown('<h1>📊 Dashboard analytique</h1>', unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#8aab8c;'>Visualisations des données nettoyées issues du scraping.</p>",
        unsafe_allow_html=True
    )

    # Sélecteur de catégorie
    cat_choice = st.selectbox(
        "Catégorie à analyser",
        options=[c["label"] for c in CATEGORIES],
        key="dash_cat"
    )
    cat = next(c for c in CATEGORIES if c["label"] == cat_choice)
    df_raw = lire_table(cat["table"])

    if df_raw.empty:
        st.warning(
            f"⚠️ Aucune donnée pour **{cat['nom']}**. "
            "Rendez-vous dans la page **🕷️ Scraper** pour collecter des données."
        )
        st.stop()

    # Nettoyage
    df = nettoyer_df(df_raw, cat["v1"])

    # ── KPIs ──────────────────────────────────────────────────
    df_prix = df[df["prix_num"] != "Non disponible"].copy()
    try:
        df_prix["prix_num"] = pd.to_numeric(df_prix["prix_num"], errors="coerce")
        df_prix = df_prix.dropna(subset=["prix_num"])
        prix_min  = int(df_prix["prix_num"].min()) if not df_prix.empty else 0
        prix_max  = int(df_prix["prix_num"].max()) if not df_prix.empty else 0
        prix_moy  = int(df_prix["prix_num"].mean()) if not df_prix.empty else 0
        nb_villes = df["ville"].nunique()
    except:
        prix_min = prix_max = prix_moy = nb_villes = 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📦 Annonces", f"{len(df):,}")
    k2.metric("💰 Prix min (FCFA)", f"{prix_min:,}")
    k3.metric("💎 Prix max (FCFA)", f"{prix_max:,}")
    k4.metric("📍 Villes", nb_villes)

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📍 Répartition villes",
        "💰 Distribution prix",
        "🏆 Top annonces",
        "📅 Évolution scraping"
    ])

    PLOTLY_THEME = dict(
        paper_bgcolor="#0f1a10",
        plot_bgcolor="#0f1a10",
        font=dict(color="#e8f0e9", family="DM Sans"),
        margin=dict(l=20, r=20, t=40, b=20),
    )

    # ── TAB 1 : Villes ────────────────────────────────────────
    with tab1:
        top_n = st.slider("Top N villes", 5, 20, 10, key="top_villes")
        villes = (
            df[df["ville"] != "Non disponible"]["ville"]
            .value_counts().head(top_n).reset_index()
        )
        villes.columns = ["Ville", "Nombre"]

        if not villes.empty:
            fig = px.bar(
                villes, x="Nombre", y="Ville", orientation="h",
                color="Nombre",
                color_continuous_scale=[[0,"#2e4430"],[1, cat["color"]]],
                title=f"Top {top_n} villes — {cat['nom'].replace('_',' ')}",
            )
            fig.update_layout(**PLOTLY_THEME, coloraxis_showscale=False,
                              yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de villes insuffisantes.")

    # ── TAB 2 : Prix ──────────────────────────────────────────
    with tab2:
        if not df_prix.empty:
            col_h, col_b = st.columns(2)
            with col_h:
                fig2 = px.histogram(
                    df_prix, x="prix_num", nbins=25,
                    title="Distribution des prix",
                    color_discrete_sequence=[cat["color"]],
                    labels={"prix_num": "Prix (FCFA)"},
                )
                fig2.add_vline(
                    x=prix_moy, line_dash="dash",
                    line_color="#f5a623",
                    annotation_text=f"Moy: {prix_moy:,}",
                    annotation_font_color="#f5a623"
                )
                fig2.update_layout(**PLOTLY_THEME)
                st.plotly_chart(fig2, use_container_width=True)

            with col_b:
                # Prix moyen par ville
                prix_ville = (
                    df_prix.groupby("ville")["prix_num"]
                    .mean().round(0).sort_values(ascending=False)
                    .head(10).reset_index()
                )
                prix_ville.columns = ["Ville", "Prix moyen"]
                fig3 = px.bar(
                    prix_ville, x="Ville", y="Prix moyen",
                    title="Prix moyen par ville (Top 10)",
                    color_discrete_sequence=[cat["color"]],
                )
                fig3.update_layout(**PLOTLY_THEME,
                                   xaxis_tickangle=-30)
                st.plotly_chart(fig3, use_container_width=True)

            # Box plot
            fig4 = px.box(
                df_prix, x="ville", y="prix_num",
                title="Distribution des prix par ville",
                color_discrete_sequence=[cat["color"]],
                labels={"prix_num":"Prix (FCFA)","ville":"Ville"},
            )
            fig4.update_layout(**PLOTLY_THEME)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Données de prix insuffisantes.")

    # ── TAB 3 : Top annonces ──────────────────────────────────
    with tab3:
        if not df_prix.empty:
            st.markdown("**🏆 Les 10 annonces les plus chères**")
            top10 = df_prix.nlargest(10, "prix_num")[
                [cat["v1"], "prix", "adresse", "image_lien"]
            ].reset_index(drop=True)
            st.dataframe(top10, use_container_width=True)

            st.markdown("**💚 Les 10 annonces les moins chères**")
            bot10 = df_prix.nsmallest(10, "prix_num")[
                [cat["v1"], "prix", "adresse", "image_lien"]
            ].reset_index(drop=True)
            st.dataframe(bot10, use_container_width=True)
        else:
            st.dataframe(df[[cat["v1"],"prix","adresse"]].head(20), use_container_width=True)

    # ── TAB 4 : Logs ──────────────────────────────────────────
    with tab4:
        df_logs = lire_table("scraping_logs")
        if not df_logs.empty:
            df_logs_cat = df_logs[df_logs["categorie"] == cat["table"]]
            if not df_logs_cat.empty:
                fig5 = px.bar(
                    df_logs_cat, x="date_run", y="nb_lignes",
                    title=f"Évolution des scrapings — {cat['nom'].replace('_',' ')}",
                    color_discrete_sequence=[cat["color"]],
                    labels={"nb_lignes":"Lignes scrapées","date_run":"Date"},
                )
                fig5.update_layout(**PLOTLY_THEME)
                st.plotly_chart(fig5, use_container_width=True)
            else:
                st.info(f"Pas encore de logs pour {cat['nom']}.")
        else:
            st.info("Aucun log de scraping disponible.")


# ══════════════════════════════════════════════════════════════
#  PAGE : ÉVALUATION
# ══════════════════════════════════════════════════════════════
elif page == "📝 Évaluation":
    st.markdown('<h1>📝 Évaluation de l\'application</h1>', unsafe_allow_html=True)

    tab_kobo, tab_resultats = st.tabs([
        "✍️ Formulaire intégré",
        "🔗 Lien externe (Kobo / Google Forms)",
        "📊 Résultats des évaluations"
    ])   

    # ── Lien externe ──────────────────────────────────────────
    with tab_kobo:
        st.markdown("""
        <div style="margin-bottom:20px;">
            <p style="color:#8aab8c;">
                Vous pouvez également soumettre votre évaluation via les formulaires
                externes ci-dessous (KoboToolbox).
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_k, col_g = st.columns(2)

        with col_k:
            st.markdown("""
            <div class="dl-card" style="text-align:center; padding:32px 20px;">
                <div style="font-size:3rem; margin-bottom:12px;">📋</div>
                <div style="font-weight:700; color:#7ec850; font-size:1.1rem; margin-bottom:8px;">
                    KoboToolbox
                </div>
                <div style="color:#8aab8c; font-size:.85rem; margin-bottom:20px; line-height:1.6;">
                    Formulaire d'évaluation hébergé sur la plateforme KoboToolbox,
                    idéal pour la collecte de données terrain.
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.link_button(
                "📋 Ouvrir le formulaire KoboToolbox",
                "https://ee.kobotoolbox.org/x/VOTRE_FORMULAIRE",
                use_container_width=True
            )

        

    # ── Résultats ─────────────────────────────────────────────
    with tab_resultats:
        df_eval = lire_table("evaluations")
        if df_eval.empty:
            st.info("Aucune évaluation soumise pour l'instant.")
        else:
            total_eval = len(df_eval)
            note_moy   = df_eval["note"].mean()
            fac_moy    = df_eval["facilite"].mean()
            des_moy    = df_eval["design"].mean()
            dash_moy   = df_eval["dashboard"].mean()

            e1, e2, e3, e4, e5 = st.columns(5)
            e1.metric("📝 Évaluations", total_eval)
            e2.metric("⭐ Note moy.", f"{note_moy:.1f}/5")
            e3.metric("🖱️ Facilité", f"{fac_moy:.1f}/5")
            e4.metric("🎨 Design", f"{des_moy:.1f}/5")
            e5.metric("📊 Dashboard", f"{dash_moy:.1f}/5")

            # Graphique radar
            categories_radar = ["Facilité", "Design", "Dashboard"]
            values = [fac_moy, des_moy, dash_moy]

            fig_r = go.Figure(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories_radar + [categories_radar[0]],
                fill='toself',
                line_color="#7ec850",
                fillcolor="rgba(126,200,80,0.15)",
                name="Moyenne"
            ))
            fig_r.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 5], color="#8aab8c"),
                    bgcolor="#0f1a10",
                    angularaxis=dict(color="#8aab8c"),
                ),
                paper_bgcolor="#0f1a10",
                font=dict(color="#e8f0e9"),
                title="Radar des évaluations",
                showlegend=False,
            )
            st.plotly_chart(fig_r, use_container_width=True)

            st.markdown("**📋 Toutes les évaluations**")
            st.dataframe(
                df_eval[["nom","note","facilite","design","dashboard","commentaire","soumis_le"]],
                use_container_width=True
            )

            # Export
            csv_eval = df_eval.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                "⬇️ Exporter les évaluations (CSV)",
                data=csv_eval,
                file_name="evaluations.csv",
                mime="text/csv"
            )


# ══════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown(
    "<div class='footer'>"
    "🐾 CoinAfrique Animaux · Sénégal &nbsp;|&nbsp; "
    "Powered by Streamlit + BeautifulSoup + SQLite + Plotly &nbsp;|&nbsp; "
    f"{datetime.now().strftime('%Y')}"
    "</div>",
    unsafe_allow_html=True
)
