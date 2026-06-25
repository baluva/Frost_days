"""Frost Days — bulletin climatique.

Combien de jours de gel une commune française a-t-elle connus sur une période ?
Interface Streamlit. Réalisé par Alexis & Louey.
"""
from __future__ import annotations

import base64
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from frost_days.communes import find_commune, load_communes
from frost_days.config import DEFAULT_END, DEFAULT_START
from frost_days.frost import compute_frost_days

st.set_page_config(
    page_title="Frost Days — bulletin climatique",
    page_icon="❄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# Identité visuelle — « bulletin climatique »
# Le 0 °C est la ligne de référence du sujet ; la couleur encode la température
# (froid = bleu, chaud = ambre) de part et d'autre de ce zéro.
# ──────────────────────────────────────────────────────────────────────────────
INK      = "#0F1E27"   # encre — bleu nuit froid
MUTED    = "#5A6B74"   # texte secondaire
PAPER    = "#EAF0F3"   # fond — givre sur la vitre
SURFACE  = "#FFFFFF"   # carte — fiche climatologique
HAIR     = "#C7D5DC"   # filets
COLD     = "#15598F"   # froid / gel / altitude
COLD_DK  = "#0E3F66"
COLD_SF  = "#A9C8DC"   # froid pâle (aplats)
WARM     = "#C2410C"   # chaud / réchauffement / station ciblée
WARM_SF  = "#E7B48E"
ZERO     = "#243038"   # ligne 0 °C
BLEU     = "#000091"   # Bleu France — charte graphique de l'État
ROUGE    = "#E1000F"   # Rouge Marianne

# Échelle divergente froid → neutre → chaud (langage des cartes climatiques).
TEMP_SCALE = [[0.0, COLD_DK], [0.35, COLD], [0.5, "#E7EDF0"], [0.65, WARM], [1.0, "#8A2C08"]]

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

.stApp {{ background: {PAPER}; color: {INK}; }}

/* Corps en sans technique, titres en grotesque, données en monospace */
html, body, [class*="css"], .stMarkdown, p, label, span, div, input, button {{
  font-family: 'IBM Plex Sans', system-ui, sans-serif;
}}
h1, h2, h3, h4 {{
  font-family: 'Space Grotesk', sans-serif;
  color: {INK};
  font-weight: 600;
  letter-spacing: -0.01em;
}}
.mono {{ font-family: 'IBM Plex Mono', monospace; }}

/* Masthead */
.fd-eyebrow {{
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem; letter-spacing: 0.22em; text-transform: uppercase;
  color: {MUTED};
}}
.fd-title {{
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700; font-size: 3.1rem; line-height: 1; letter-spacing: -0.02em;
  color: {INK}; margin: 0.15rem 0 0.2rem 0;
}}
.fd-sub {{ color: {MUTED}; font-size: 1.02rem; max-width: 60ch; }}
.fd-by {{
  font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem;
  letter-spacing: 0.12em; color: {MUTED}; text-transform: uppercase;
}}
/* Ligne 0 °C : signature structurelle */
.fd-datum {{
  position: relative; height: 1px; background: {HAIR};
  margin: 0.9rem 0 0.4rem 0;
}}
.fd-datum::before {{
  content: "0 °C"; position: absolute; right: 0; top: -0.72rem;
  font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem;
  letter-spacing: 0.12em; color: {MUTED}; background: {PAPER}; padding-left: 0.5rem;
}}
.fd-datum::after {{
  content: ""; position: absolute; left: 0; top: -2px; width: 46px; height: 5px;
  background: {COLD};
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
  background: {SURFACE}; border-right: 1px solid {HAIR};
}}
section[data-testid="stSidebar"] .fd-eyebrow {{ display:block; margin-bottom: 0.4rem; }}

/* Champs */
.stTextInput input, .stDateInput input,
.stSelectbox div[data-baseweb="select"] > div {{
  background: {SURFACE} !important; color: {INK} !important;
  border: 1px solid {HAIR} !important; border-radius: 4px !important;
}}
/* Bouton principal */
.stButton > button {{
  background: {COLD}; color: #fff !important; border: none; border-radius: 4px;
  font-family: 'Space Grotesk', sans-serif; font-weight: 600; letter-spacing: 0.02em;
  padding: 0.55rem 1.2rem; transition: background 0.15s ease;
}}
.stButton > button:hover {{ background: {COLD_DK}; }}

/* Cartes-métriques façon fiche climato */
div[data-testid="stMetric"] {{
  background: {SURFACE}; border: 1px solid {HAIR}; border-left: 3px solid {COLD};
  border-radius: 4px; padding: 0.8rem 1rem;
}}
div[data-testid="stMetricValue"] {{
  font-family: 'Space Grotesk', sans-serif; color: {INK} !important;
  font-size: 1.9rem !important; font-weight: 600;
}}
div[data-testid="stMetricLabel"] p {{
  font-family: 'IBM Plex Mono', monospace !important; color: {MUTED} !important;
  text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.68rem !important;
}}
div[data-testid="stMetricDelta"] {{ font-size: 0.8rem !important; }}

/* Onglets : soulignement net, pas de fioritures */
.stTabs [data-baseweb="tab-list"] {{ gap: 0.4rem; border-bottom: 1px solid {HAIR}; }}
.stTabs [data-baseweb="tab"] {{
  font-family: 'Space Grotesk', sans-serif; font-weight: 500;
  color: {MUTED}; background: transparent; padding: 0.4rem 0.2rem;
}}
.stTabs [aria-selected="true"] {{ color: {INK} !important; }}
.stTabs [data-baseweb="tab-highlight"] {{ background: {COLD} !important; height: 3px; }}

/* Tableaux */
.stDataFrame {{ border: 1px solid {HAIR}; border-radius: 4px; }}

/* Encadrés info */
div[data-testid="stAlert"] {{
  background: {SURFACE}; border: 1px solid {HAIR}; border-left: 3px solid {WARM};
  border-radius: 4px; color: {INK};
}}
.stCaption, [data-testid="stCaptionContainer"] {{ color: {MUTED} !important; }}

/* On masque le chrome décoratif de Streamlit */
[data-testid="stStatusWidget"] {{ display: none; }}

/* Le hero remonte vers le haut de page */
.block-container {{ padding-top: 2.6rem; }}

/* ─── Hero : bandeau givre (vraie macro, duotone froid) + filet tricolore ─── */
.fd-hero {{
  position: relative; border-radius: 8px; overflow: hidden;
  border: 1px solid #21425c; margin: 0.1rem 0 0.5rem 0;
  background-size: cover; background-position: center 62%;
  box-shadow: 0 1px 0 rgba(255,255,255,0.55);
}}
.fd-hero-inner {{ position: relative; padding: 2.5rem 2.6rem 2.2rem 2.9rem; }}
.fd-flag {{
  position: absolute; left: 0; top: 0; bottom: 0; width: 9px;
  background: linear-gradient(to bottom,
     {BLEU} 0 33.33%, #ffffff 33.33% 66.66%, {ROUGE} 66.66% 100%);
}}
.fd-eyebrow-light {{ color: #A9C4D9; }}
.fd-title-hero {{ color: #EEF5FA; font-size: 3.25rem; margin: 0.5rem 0 0.45rem 0; }}
.fd-sub-hero {{ color: #C6D7E5; max-width: 58ch; }}
.fd-by-hero {{ color: #8FB0C8; margin-top: 0.7rem; }}
@media (max-width: 640px) {{
  .fd-hero-inner {{ padding: 1.6rem 1.4rem 1.5rem 1.7rem; }}
  .fd-title-hero {{ font-size: 2.2rem; }}
}}

/* Filet tricolore réutilisable (sidebar, pied de page) */
.fd-tricolore {{
  height: 4px; width: 64px; border-radius: 2px;
  background: linear-gradient(to right,
     {BLEU} 0 33.33%, #ffffff 33.33% 66.66%, {ROUGE} 66.66% 100%);
}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def datum() -> None:
    st.markdown('<div class="fd-datum"></div>', unsafe_allow_html=True)


def _load_b64(rel: str) -> str:
    """Charge un asset binaire en base64 (vide si absent)."""
    try:
        return base64.b64encode((Path(__file__).parent / rel).read_bytes()).decode()
    except Exception:
        return ""


HERO_B64 = _load_b64("assets/hero_frost.jpg")


# ──────────────────────────────────────────────────────────────────────────────
# Masthead — bandeau givre + signature institutionnelle française
# ──────────────────────────────────────────────────────────────────────────────
_hero_bg = (
    "background-image: linear-gradient(100deg, rgba(8,18,30,0.95) 0%, "
    "rgba(8,18,30,0.64) 44%, rgba(11,32,50,0.30) 100%), "
    f"url('data:image/jpeg;base64,{HERO_B64}');"
    if HERO_B64 else "background: #0E2438;"
)
st.markdown(
    f"""
    <div class="fd-hero" style="{_hero_bg}">
      <div class="fd-flag"></div>
      <div class="fd-hero-inner">
        <div class="fd-eyebrow fd-eyebrow-light">République française · Météo-France · Relevé de gel · 1950–2024</div>
        <div class="fd-title fd-title-hero">FROST&nbsp;DAYS</div>
        <div class="fd-sub fd-sub-hero">Combien de jours de gel une commune française a-t-elle connus sur une période donnée&nbsp;?
        Un <b>jour de gel</b> = un jour où la température minimale sous abri (TN) est descendue à <b>0&nbsp;°C ou moins</b>.</div>
        <div class="fd-by fd-by-hero">Alexis &amp; Louey</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
datum()


# ──────────────────────────────────────────────────────────────────────────────
DEPARTMENTS = {
    "01": "Ain", "02": "Aisne", "03": "Allier", "04": "Alpes-de-Haute-Provence",
    "05": "Hautes-Alpes", "06": "Alpes-Maritimes", "07": "Ardèche", "08": "Ardennes",
    "09": "Ariège", "10": "Aube", "11": "Aude", "12": "Aveyron", "13": "Bouches-du-Rhône",
    "14": "Calvados", "15": "Cantal", "16": "Charente", "17": "Charente-Maritime",
    "18": "Cher", "19": "Corrèze", "2A": "Corse-du-Sud", "2B": "Haute-Corse",
    "21": "Côte-d'Or", "22": "Côtes-d'Armor", "23": "Creuse", "24": "Dordogne",
    "25": "Doubs", "26": "Drôme", "27": "Eure", "28": "Eure-et-Loir", "29": "Finistère",
    "30": "Gard", "31": "Haute-Garonne", "32": "Gers", "33": "Gironde", "34": "Hérault",
    "35": "Ille-et-Vilaine", "36": "Indre", "37": "Indre-et-Loire", "38": "Isère",
    "39": "Jura", "40": "Landes", "41": "Loir-et-Cher", "42": "Loire", "43": "Haute-Loire",
    "44": "Loire-Atlantique", "45": "Loiret", "46": "Lot", "47": "Lot-et-Garonne",
    "48": "Lozère", "49": "Maine-et-Loire", "50": "Manche", "51": "Marne",
    "52": "Haute-Marne", "53": "Mayenne", "54": "Meurthe-et-Moselle", "55": "Meuse",
    "56": "Morbihan", "57": "Moselle", "58": "Nièvre", "59": "Nord", "60": "Oise",
    "61": "Orne", "62": "Pas-de-Calais", "63": "Puy-de-Dôme", "64": "Pyrénées-Atlantiques",
    "65": "Hautes-Pyrénées", "66": "Pyrénées-Orientales", "67": "Bas-Rhin", "68": "Haut-Rhin",
    "69": "Rhône", "70": "Haute-Saône", "71": "Saône-et-Loire", "72": "Sarthe",
    "73": "Savoie", "74": "Haute-Savoie", "75": "Paris", "76": "Seine-Maritime",
    "77": "Seine-et-Marne", "78": "Yvelines", "79": "Deux-Sèvres", "80": "Somme",
    "81": "Tarn", "82": "Tarn-et-Garonne", "83": "Var", "84": "Vaucluse", "85": "Vendée",
    "86": "Vienne", "87": "Haute-Vienne", "88": "Vosges", "89": "Yonne",
    "90": "Territoire de Belfort", "91": "Essonne", "92": "Hauts-de-Seine",
    "93": "Seine-Saint-Denis", "94": "Val-de-Marne", "95": "Val-d'Oise",
    "971": "Guadeloupe", "972": "Martinique", "973": "Guyane", "974": "La Réunion",
    "976": "Mayotte",
}


@st.cache_data(show_spinner=False)
def get_communes() -> pd.DataFrame:
    return load_communes()


@st.cache_data(show_spinner="Calcul des jours de gel…")
def run(commune: str, dept: str, lat: float, lon: float, start: str, end: str):
    return compute_frost_days(commune, dept, lat, lon, start, end)


# ──────────────────────────────────────────────────────────────────────────────
# Sidebar — paramètres
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<span class="fd-eyebrow">Paramètres</span>'
        '<div class="fd-tricolore" style="margin:0.45rem 0 1rem 0;"></div>',
        unsafe_allow_html=True,
    )
    communes = get_communes()
    sorted_dept_codes = sorted(DEPARTMENTS.keys(), key=lambda c: DEPARTMENTS[c])
    try:
        default_index = sorted_dept_codes.index("21")
    except ValueError:
        default_index = 0
    dept = st.selectbox(
        "Département", options=sorted_dept_codes, index=default_index,
        format_func=lambda c: f"{DEPARTMENTS[c]} ({c})",
    )
    sub = communes[communes["dept"] == str(dept).zfill(2)]["nom"].sort_values().unique()
    if len(sub):
        default_commune = int(np.where(sub == "Dijon")[0][0]) if "Dijon" in sub else 0
        commune = st.selectbox("Commune", sub, index=default_commune)
    else:
        commune = st.text_input("Commune", "Dijon")
    debut = st.date_input(
        "Début", value=pd.Timestamp(DEFAULT_START),
        min_value=pd.Timestamp("1950-01-01"), max_value=pd.Timestamp("2024-12-31"),
    ).isoformat()
    fin = st.date_input(
        "Fin", value=pd.Timestamp(DEFAULT_END),
        min_value=pd.Timestamp("1950-01-01"), max_value=pd.Timestamp("2024-12-31"),
    ).isoformat()
    run_btn = st.button("Calculer", type="primary", use_container_width=True)
    st.markdown(
        f'<p class="fd-eyebrow" style="margin-top:1rem;">Source<br></p>'
        f'<span style="color:{MUTED};font-size:0.8rem;">data.gouv.fr — Données climatologiques '
        "quotidiennes, producteur Météo-France.</span>",
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Template Plotly cohérent (clair, ligne 0 °C lisible)
# ──────────────────────────────────────────────────────────────────────────────
def style_fig(fig: go.Figure, ytitle: str = "", xtitle: str = "") -> go.Figure:
    fig.update_layout(
        plot_bgcolor=SURFACE, paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, family="IBM Plex Sans, sans-serif", size=13),
        margin=dict(l=50, r=24, t=24, b=46),
        xaxis=dict(title=xtitle, gridcolor="#EAEFF2", linecolor=HAIR, zeroline=False,
                   tickfont=dict(family="IBM Plex Mono, monospace", size=11)),
        yaxis=dict(title=ytitle, gridcolor="#EAEFF2", linecolor=HAIR, zeroline=False,
                   tickfont=dict(family="IBM Plex Mono, monospace", size=11)),
        hoverlabel=dict(bgcolor=INK, font_color="#fff", bordercolor=COLD,
                        font_family="IBM Plex Mono, monospace"),
        legend=dict(font=dict(color=INK, size=12), bgcolor="rgba(255,255,255,0.7)",
                    bordercolor=HAIR, borderwidth=1),
    )
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# Écran d'accueil
# ──────────────────────────────────────────────────────────────────────────────
if not run_btn:
    st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.markdown(
        f"<div class='mono' style='color:{COLD};font-size:0.72rem;letter-spacing:0.14em;'>01 · LA COMMUNE</div>"
        f"<p style='color:{MUTED};'>Combien de jours de gel, à quelle saison, et quels jours de "
        "l'année gèlent le plus souvent.</p>", unsafe_allow_html=True)
    b.markdown(
        f"<div class='mono' style='color:{WARM};font-size:0.72rem;letter-spacing:0.14em;'>02 · LA TEMPÉRATURE</div>"
        f"<p style='color:{MUTED};'>La température minimale d'hiver monte-t-elle, et le gel "
        "recule-t-il en conséquence&nbsp;?</p>", unsafe_allow_html=True)
    c.markdown(
        f"<div class='mono' style='color:{COLD};font-size:0.72rem;letter-spacing:0.14em;'>03 · L'ALTITUDE</div>"
        f"<p style='color:{MUTED};'>Combien de jours de gel gagne-t-on par 100&nbsp;m d'altitude, "
        "station par station.</p>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{MUTED};margin-top:1.5rem;'>→ Choisissez une commune et une plage de dates "
        "dans le panneau de gauche, puis lancez le calcul.</p>", unsafe_allow_html=True)
    st.stop()

# ── Calcul ────────────────────────────────────────────────────────────────────
try:
    lat, lon = find_commune(communes, commune, dept)
    res = run(commune, dept, lat, lon, debut, fin)
except Exception as e:
    st.error(f"Calcul impossible : {e}")
    st.stop()

n_years_span = max(res.end.year - res.start.year + 1, 1)

# ── Bandeau station ───────────────────────────────────────────────────────────
alt_txt = f"{res.station_altitude:.0f} m" if not pd.isna(res.station_altitude) else "altitude n.c."
st.markdown(
    f"""
    <div style="display:flex;align-items:baseline;gap:0.8rem;flex-wrap:wrap;margin-top:0.4rem;">
      <span style="font-family:'Space Grotesk';font-size:1.5rem;font-weight:600;color:{INK};">{res.commune}</span>
      <span class="mono" style="color:{MUTED};font-size:0.85rem;">DÉPT {res.dept}</span>
    </div>
    <div class="mono" style="color:{MUTED};font-size:0.82rem;letter-spacing:0.04em;margin-top:0.15rem;">
      STATION {res.station_name} · {res.station_distance_km:.1f} KM · {alt_txt} ·
      COUVERTURE {(1 - res.missing_ratio):.0%} · {res.start.date()} → {res.end.date()}
    </div>
    """,
    unsafe_allow_html=True,
)
datum()

# ── Métriques ─────────────────────────────────────────────────────────────────
tn_winter_mean = res.tn_per_year["tn_mean_winter"].mean()
top_day = res.per_day_of_year.sort_values("freq", ascending=False).iloc[0]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Jours de gel (total)", res.frost_days_total)
c2.metric("Moyenne par an", f"{res.frost_days_per_year_mean:.1f}")
c3.metric("TN moyenne d'hiver", f"{tn_winter_mean:+.1f} °C" if not pd.isna(tn_winter_mean) else "—")
c4.metric("Jour le plus gélif",
          f"{int(top_day['day']):02d}/{int(top_day['month']):02d}",
          f"{top_day['freq']*100:.0f}% des années", delta_color="off")

st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "La commune", "Température & gel", "Altitude & gel", "Synthèse",
])

# ─────────────────────────────  TAB 1 — La commune  ──────────────────────────
with tab1:
    st.markdown("#### Jours de gel par année")
    st.caption("La réponse directe à la problématique : le décompte annuel à la station retenue.")
    py = res.per_year.copy()
    fig1 = go.Figure()
    fig1.add_bar(
        x=py["year"].astype(int), y=py["frost_days"],
        marker=dict(color=COLD, line=dict(color=COLD_DK, width=0.5)),
        hovertemplate="<b>%{x}</b> · %{y} jours de gel<extra></extra>",
    )
    fig1.add_hline(y=res.frost_days_per_year_mean, line=dict(color=WARM, width=1.5, dash="dash"),
                   annotation_text=f"moyenne {res.frost_days_per_year_mean:.1f}",
                   annotation_font=dict(color=WARM, family="IBM Plex Mono"))
    style_fig(fig1, ytitle="jours de gel", xtitle="année")
    fig1.update_xaxes(tickmode="linear", dtick=max(1, n_years_span // 18))
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("#### Probabilité de gel, jour par jour")
    st.caption("Sur l'ensemble de la période, fréquence du gel pour chaque jour du calendrier "
               "(29 février exclu). Utile pour situer le risque de gel tardif.")
    doy = res.per_day_of_year.copy()
    doy["date_ref"] = pd.to_datetime(
        doy.apply(lambda r: f"2001-{int(r['month']):02d}-{int(r['day']):02d}", axis=1))
    doy = doy.sort_values("date_ref")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=doy["date_ref"], y=doy["freq"] * 100, mode="lines",
        line=dict(color=COLD, width=1.8), fill="tozeroy", fillcolor="rgba(21,89,143,0.16)",
        hovertemplate="%{x|%d %B} · %{y:.0f}% de gel<extra></extra>"))
    style_fig(fig2, ytitle="fréquence (%)", xtitle="jour de l'année")
    fig2.update_xaxes(tickformat="%d %b")
    fig2.update_yaxes(ticksuffix=" %")
    st.plotly_chart(fig2, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Les 10 jours les plus gélifs")
        top = res.per_day_of_year.sort_values("freq", ascending=False).head(10).copy()
        top["jour"] = top.apply(lambda r: f"{int(r['day']):02d}/{int(r['month']):02d}", axis=1)
        top["fréquence"] = (top["freq"] * 100).round(0).astype(int).astype(str) + " %"
        top["gel / obs"] = top["n_frost"].astype(int).astype(str) + " / " + top["n_obs"].astype(int).astype(str)
        st.dataframe(top[["jour", "fréquence", "gel / obs"]], hide_index=True, use_container_width=True)
    with col_b:
        st.markdown("#### Détail par année")
        st.dataframe(res.per_year, hide_index=True, use_container_width=True)

# ───────────────────────────  TAB 2 — Température & gel  ─────────────────────
with tab2:
    st.markdown("#### La température minimale d'hiver monte-t-elle&nbsp;?")
    st.caption("Température minimale (TN) moyenne par année. La courbe DJF (décembre-janvier-février) "
               "est la plus parlante : c'est la saison où se concentre le gel.")
    tn = res.tn_per_year.dropna(subset=["tn_mean_annual"]).sort_values("year").copy()

    fig_t = go.Figure()
    fig_t.add_hline(y=0, line=dict(color=ZERO, width=1.2),
                    annotation_text="0 °C", annotation_font=dict(color=ZERO, family="IBM Plex Mono"))
    fig_t.add_trace(go.Scatter(
        x=tn["year"], y=tn["tn_mean_annual"], mode="lines+markers", name="annuelle",
        line=dict(color=COLD_SF, width=1.8), marker=dict(size=6, color=COLD),
        hovertemplate="<b>%{x}</b> · TN annuelle %{y:.2f} °C<extra></extra>"))
    fig_t.add_trace(go.Scatter(
        x=tn["year"], y=tn["tn_mean_winter"], mode="lines+markers", name="hiver (DJF)",
        line=dict(color=WARM, width=2.6), marker=dict(size=8, color=WARM),
        hovertemplate="<b>%{x}</b> · TN hiver %{y:.2f} °C<extra></extra>"))

    djf = tn.dropna(subset=["tn_mean_winter"])
    slope_tn = np.nan
    if len(djf) >= 3:
        slope_tn, intercept = np.polyfit(djf["year"], djf["tn_mean_winter"], 1)
        fig_t.add_trace(go.Scatter(
            x=djf["year"], y=slope_tn * djf["year"] + intercept, mode="lines",
            name=f"tendance DJF · {slope_tn*10:+.2f} °C/déc.",
            line=dict(color=ZERO, width=1.4, dash="dot"), hoverinfo="skip"))
    style_fig(fig_t, ytitle="TN moyenne (°C)", xtitle="année")
    fig_t.update_xaxes(tickmode="linear", dtick=max(1, n_years_span // 18))
    st.plotly_chart(fig_t, use_container_width=True)

    if len(djf) >= 3:
        k1, k2, k3 = st.columns(3)
        k1.metric("TN hiver — début", f"{djf['tn_mean_winter'].iloc[0]:+.2f} °C")
        k2.metric("TN hiver — fin", f"{djf['tn_mean_winter'].iloc[-1]:+.2f} °C",
                  f"{djf['tn_mean_winter'].iloc[-1]-djf['tn_mean_winter'].iloc[0]:+.2f} °C")
        k3.metric("Tendance / décennie", f"{slope_tn*10:+.2f} °C")

    # Corrélation TN hiver ↔ jours de gel
    merged = res.per_year.merge(
        res.tn_per_year[["year", "tn_mean_winter"]], on="year", how="inner").dropna()
    if len(merged) >= 3:
        r_tn = merged["tn_mean_winter"].corr(merged["frost_days"])
        st.markdown("#### Plus l'hiver est doux, moins il gèle&nbsp;?")
        st.caption("Chaque point = une année. Axe X : TN moyenne d'hiver. Axe Y : nombre de jours de gel.")
        fig_c = go.Figure()
        fig_c.add_trace(go.Scatter(
            x=merged["tn_mean_winter"], y=merged["frost_days"], mode="markers+text",
            text=merged["year"].astype(int), textposition="top center",
            textfont=dict(color=MUTED, size=9, family="IBM Plex Mono"),
            marker=dict(size=11, color=COLD, line=dict(color="#fff", width=1)),
            hovertemplate="%{text} · TN hiver %{x:.2f} °C · %{y} j gel<extra></extra>"))
        if len(merged) >= 3:
            s2, i2 = np.polyfit(merged["tn_mean_winter"], merged["frost_days"], 1)
            xs = np.linspace(merged["tn_mean_winter"].min(), merged["tn_mean_winter"].max(), 40)
            fig_c.add_trace(go.Scatter(x=xs, y=s2 * xs + i2, mode="lines",
                line=dict(color=WARM, width=1.6, dash="dash"),
                name=f"{s2:+.0f} jours par +1 °C", hoverinfo="skip"))
        style_fig(fig_c, ytitle="jours de gel", xtitle="TN moyenne d'hiver (°C)")
        st.plotly_chart(fig_c, use_container_width=True)
        kk1, kk2 = st.columns(2)
        kk1.metric("Corrélation TN hiver × gel", f"{r_tn:+.2f}")
        kk2.metric("Effet d'un hiver +1 °C", f"{s2:+.0f} jours de gel")

    if n_years_span < 25:
        st.info("Sur moins de 25 ans, la variabilité naturelle domine : une tendance n'a de "
                "valeur climatique qu'à partir de ~30 ans (norme OMM). Élargissez la plage de "
                "dates pour un signal plus net.")

# ────────────────────────────  TAB 3 — Altitude & gel  ───────────────────────
with tab3:
    st.markdown("#### Le gel augmente-t-il avec l'altitude&nbsp;?")
    st.caption(f"Toutes les stations valides du département {res.dept} (couverture TN ≥ 65 %). "
               "Chaque point = une station ; la station retenue pour la commune est en ambre.")
    ds = res.dept_stations.copy()
    slope_alt = np.nan
    r_alt = np.nan
    if ds.empty:
        st.warning("Aucune station valide dans ce département sur la plage choisie.")
    else:
        alt_min, alt_max = int(ds["ALTI"].min()), int(ds["ALTI"].max())
        if alt_max > alt_min:
            lo, hi = st.slider("Filtre altitude (m)", alt_min, alt_max, (alt_min, alt_max), step=10)
            ds = ds[(ds["ALTI"] >= lo) & (ds["ALTI"] <= hi)]

        is_cur = ds["NUM_POSTE"] == res.station_id
        colors = [WARM if x else COLD for x in is_cur]
        sizes = [16 if x else 10 for x in is_cur]
        fig_a = go.Figure()
        fig_a.add_trace(go.Scatter(
            x=ds["ALTI"], y=ds["frost_days_per_year"], mode="markers",
            marker=dict(size=sizes, color=colors, line=dict(color="#fff", width=1), opacity=0.92),
            hovertext=[f"{n} · {a:.0f} m · {f:.1f} j gel/an"
                       for n, a, f in zip(ds["NOM_USUEL"], ds["ALTI"], ds["frost_days_per_year"])],
            hoverinfo="text", name="stations"))
        if len(ds) >= 3:
            slope_alt, ia = np.polyfit(ds["ALTI"], ds["frost_days_per_year"], 1)
            xs = np.linspace(ds["ALTI"].min(), ds["ALTI"].max(), 50)
            fig_a.add_trace(go.Scatter(x=xs, y=slope_alt * xs + ia, mode="lines",
                line=dict(color=ZERO, width=1.6, dash="dash"),
                name=f"{slope_alt*100:+.1f} jours par +100 m", hoverinfo="skip"))
            r_alt = ds[["ALTI", "frost_days_per_year"]].corr().iloc[0, 1]
        style_fig(fig_a, ytitle="jours de gel / an", xtitle="altitude (m)")
        st.plotly_chart(fig_a, use_container_width=True)

        kc1, kc2, kc3 = st.columns(3)
        kc1.metric("Stations affichées", len(ds))
        kc2.metric("Corrélation altitude × gel", f"{r_alt:+.2f}" if not pd.isna(r_alt) else "—",
                   "forte" if abs(r_alt) > 0.7 else ("modérée" if abs(r_alt) > 0.3 else "faible")
                   if not pd.isna(r_alt) else None)
        if not pd.isna(slope_alt):
            kc3.metric("Gain par +100 m", f"{slope_alt*100:+.1f} j/an")

        with st.expander("Tableau des stations"):
            tbl = ds[["NOM_USUEL", "ALTI", "frost_days", "frost_days_per_year"]].copy()
            tbl.columns = ["Station", "Altitude (m)", "Total jours gel", "Jours gel/an"]
            tbl["Jours gel/an"] = tbl["Jours gel/an"].round(1)
            st.dataframe(tbl, hide_index=True, use_container_width=True)

# ──────────────────────────────  TAB 4 — Synthèse  ───────────────────────────
with tab4:
    st.markdown("#### Deux forces tirent sur le gel, en sens contraire")
    st.caption("On exprime les deux influences dans la même unité — des jours de gel par an — "
               "pour les comparer directement.")

    # Tendance des jours de gel (normalisée à 365 j pour corriger les années partielles).
    pn = res.per_year.copy()
    pn = pn[pn["total_days"] > 0]
    pn["frost_norm"] = pn["frost_days"] * 365.25 / pn["total_days"]
    slope_frost = np.nan
    if len(pn) >= 3:
        slope_frost, _ = np.polyfit(pn["year"], pn["frost_norm"], 1)
    warm_per_decade = slope_frost * 10 if not pd.isna(slope_frost) else np.nan   # < 0 si le gel recule
    alt_per_100 = slope_alt * 100 if not pd.isna(slope_alt) else np.nan          # > 0 : altitude ajoute du gel

    if pd.isna(warm_per_decade) or pd.isna(alt_per_100):
        st.info("Il faut au moins 3 années valides et 3 stations d'altitudes variées pour cette "
                "synthèse. Élargissez la plage de dates ou changez de département.")
    else:
        fig_s = go.Figure()
        fig_s.add_vline(x=0, line=dict(color=ZERO, width=1.2))
        fig_s.add_trace(go.Bar(
            y=["Tendance temporelle<br>(par décennie)", "Altitude<br>(par +100 m)"],
            x=[warm_per_decade, alt_per_100], orientation="h",
            marker=dict(color=[WARM, COLD]),
            text=[f"{warm_per_decade:+.1f} j/an", f"{alt_per_100:+.1f} j/an"],
            textposition="outside", textfont=dict(family="IBM Plex Mono", size=13),
            hoverinfo="skip"))
        style_fig(fig_s, xtitle="effet sur le nombre de jours de gel / an")
        fig_s.update_layout(showlegend=False, height=260,
                            xaxis=dict(zeroline=False, gridcolor="#EAEFF2"))
        st.plotly_chart(fig_s, use_container_width=True)

        m1, m2 = st.columns(2)
        m1.metric("Altitude — effet sur le gel", f"{alt_per_100:+.1f} j/an / +100 m")
        m2.metric("Temps — tendance du gel", f"{warm_per_decade:+.1f} j/an / décennie")

        # Équivalence parlante temps ↔ espace
        if warm_per_decade < -0.2 and alt_per_100 > 0.2:
            decades = alt_per_100 / abs(warm_per_decade)
            st.markdown(
                f"<div style='background:{SURFACE};border:1px solid {HAIR};border-left:3px solid {COLD};"
                f"border-radius:4px;padding:1rem 1.2rem;margin-top:0.6rem;'>"
                f"<span class='mono' style='color:{MUTED};font-size:0.72rem;letter-spacing:0.14em;'>LECTURE</span>"
                f"<p style='font-family:Space Grotesk;font-size:1.25rem;color:{INK};margin:0.3rem 0 0 0;'>"
                f"Monter de <b style='color:{COLD};'>100 m</b> d'altitude ajoute autant de jours de gel "
                f"que le réchauffement en a retiré en <b style='color:{WARM};'>{decades:.0f} décennie(s)</b>.</p>"
                f"</div>", unsafe_allow_html=True)
        elif warm_per_decade >= -0.2:
            st.info("Sur cette période, le gel ne recule pas nettement (variabilité naturelle "
                    "dominante sur une plage courte) : l'équivalence temps/altitude n'est pas "
                    "interprétable. Essayez une plage d'au moins 30 ans.")

    st.caption("Méthode — Temps : pente de régression des jours de gel/an (normalisés) sur les années. "
               "Espace : pente de régression jours de gel/an vs altitude des stations du département. "
               "Limite : 10 ans ne suffisent pas à isoler un signal climatique (norme OMM : 30 ans).")

# ── Pied de page ──────────────────────────────────────────────────────────────
datum()
st.markdown(
    f"""
    <div style="display:flex;flex-direction:column;align-items:center;gap:0.5rem;padding:0.6rem 0 1.4rem 0;">
      <div class="fd-tricolore"></div>
      <div class="fd-by">Frost Days · Alexis &amp; Louey · données data.gouv.fr — Météo-France</div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.66rem;color:{MUTED};letter-spacing:0.03em;">
        Bandeau&nbsp;: gelée blanche — W.&nbsp;Carter, Wikimedia&nbsp;Commons, CC&nbsp;BY-SA&nbsp;4.0
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
